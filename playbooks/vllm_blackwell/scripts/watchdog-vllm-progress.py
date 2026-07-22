#!/usr/bin/env python3
"""Restart vLLM when EngineCore is alive but no longer making progress."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


METRIC_RE = re.compile(
    r"^(?P<name>[A-Za-z_:][A-Za-z0-9_:]*)(?:\{(?P<labels>[^}]*)\})?\s+"
    r"(?P<value>[-+0-9.eE]+)$"
)


@dataclass(frozen=True)
class Snapshot:
    health_ok: bool
    running: float
    waiting: float
    token_total: float
    prompt_tokens: float
    generation_tokens: float
    accepted_spec_tokens: float
    gpu_util: float | None
    gpu_power_w: float | None
    gpu_temp_c: float | None


def log(message: str) -> None:
    stamp = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
    print(f"{stamp} {message}", flush=True)


def fetch_text(url: str, timeout: float) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return 200 <= response.status < 300, body
    except (urllib.error.URLError, TimeoutError) as exc:
        return False, str(exc)


def parse_metrics(text: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = METRIC_RE.match(line.strip())
        if not match:
            continue
        name = match.group("name")
        labels = match.group("labels") or ""
        value = float(match.group("value"))
        key = name
        if name == "vllm:request_success_total":
            key = f"{name}{{{labels}}}"
        values[key] = values.get(key, 0.0) + value
    return values


def run_command(command: list[str], timeout: float) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        return completed.returncode, completed.stdout
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return 124, output + f"\nTIMEOUT after {timeout}s\n"
    except OSError as exc:
        return 127, str(exc)


def read_gpu(timeout: float) -> tuple[float | None, float | None, float | None, str]:
    command = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,power.draw,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]
    code, output = run_command(command, timeout)
    if code != 0:
        return None, None, None, output
    first_line = output.strip().splitlines()[0] if output.strip() else ""
    parts = [part.strip() for part in first_line.split(",")]
    if len(parts) < 3:
        return None, None, None, output
    try:
        return float(parts[0]), float(parts[1]), float(parts[2]), output
    except ValueError:
        return None, None, None, output


def collect_snapshot(args: argparse.Namespace) -> tuple[Snapshot | None, str]:
    health_ok, health_body = fetch_text(args.health_url, args.http_timeout)
    metrics_ok, metrics_body = fetch_text(args.metrics_url, args.http_timeout)
    gpu_util, gpu_power_w, gpu_temp_c, gpu_raw = read_gpu(args.command_timeout)
    if not metrics_ok:
        detail = json.dumps(
            {
                "health_ok": health_ok,
                "health": health_body,
                "metrics": metrics_body,
                "gpu": gpu_raw,
            },
            indent=2,
        )
        return None, detail
    metrics = parse_metrics(metrics_body)
    prompt_tokens = metrics.get("vllm:prompt_tokens_total", 0.0)
    generation_tokens = metrics.get("vllm:generation_tokens_total", 0.0)
    accepted_spec_tokens = metrics.get("vllm:spec_decode_num_accepted_tokens_total", 0.0)
    snapshot = Snapshot(
        health_ok=health_ok,
        running=metrics.get("vllm:num_requests_running", 0.0),
        waiting=metrics.get("vllm:num_requests_waiting", 0.0),
        token_total=prompt_tokens + generation_tokens + accepted_spec_tokens,
        prompt_tokens=prompt_tokens,
        generation_tokens=generation_tokens,
        accepted_spec_tokens=accepted_spec_tokens,
        gpu_util=gpu_util,
        gpu_power_w=gpu_power_w,
        gpu_temp_c=gpu_temp_c,
    )
    detail = json.dumps(
        {
            "snapshot": snapshot.__dict__,
            "health": health_body[:1000],
            "gpu": gpu_raw,
        },
        indent=2,
    )
    return snapshot, detail


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_evidence(args: argparse.Namespace, snapshot_detail: str) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S")
    evidence_dir = Path(args.evidence_dir) / f"wedged-{stamp}"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write_file(evidence_dir / "snapshot.json", snapshot_detail)

    commands = {
        "nvidia-smi.txt": ["nvidia-smi"],
        "service-status.txt": ["systemctl", "--no-pager", "--lines=80", "status", args.service_name],
        "journal.txt": [
            "journalctl",
            "-u",
            args.service_name,
            "-n",
            str(args.journal_lines),
            "--no-pager",
        ],
    }
    for filename, command in commands.items():
        code, output = run_command(command, args.evidence_command_timeout)
        write_file(evidence_dir / filename, f"$ {' '.join(command)}\nexit={code}\n\n{output}")

    metrics_ok, metrics_body = fetch_text(args.metrics_url, args.http_timeout)
    write_file(
        evidence_dir / "metrics.txt",
        f"ok={metrics_ok}\nurl={args.metrics_url}\n\n{metrics_body}",
    )
    return evidence_dir


def wait_ready(args: argparse.Namespace) -> bool:
    deadline = time.monotonic() + args.ready_timeout
    while time.monotonic() < deadline:
        ok, _ = fetch_text(args.models_url, args.http_timeout)
        if ok:
            return True
        time.sleep(args.ready_interval)
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics-url", default=os.getenv("VLLM_WATCHDOG_METRICS_URL", "http://127.0.0.1:18000/metrics"))
    parser.add_argument("--health-url", default=os.getenv("VLLM_WATCHDOG_HEALTH_URL", "http://127.0.0.1:18000/health"))
    parser.add_argument("--models-url", default=os.getenv("VLLM_WATCHDOG_MODELS_URL", "http://127.0.0.1:18000/v1/models"))
    parser.add_argument("--service-name", default=os.getenv("VLLM_WATCHDOG_SERVICE", "vllm-blackwell.service"))
    parser.add_argument("--evidence-dir", default=os.getenv("VLLM_WATCHDOG_EVIDENCE_DIR", "/srv/shared-data/vllm/watchdog"))
    parser.add_argument("--interval", type=float, default=float(os.getenv("VLLM_WATCHDOG_INTERVAL", "20")))
    parser.add_argument("--stall-seconds", type=float, default=float(os.getenv("VLLM_WATCHDOG_STALL_SECONDS", "240")))
    parser.add_argument("--gpu-threshold", type=float, default=float(os.getenv("VLLM_WATCHDOG_GPU_THRESHOLD", "80")))
    parser.add_argument("--cooldown-seconds", type=float, default=float(os.getenv("VLLM_WATCHDOG_COOLDOWN_SECONDS", "900")))
    parser.add_argument("--max-restarts", type=int, default=int(os.getenv("VLLM_WATCHDOG_MAX_RESTARTS", "3")))
    parser.add_argument("--restart-window-seconds", type=float, default=float(os.getenv("VLLM_WATCHDOG_RESTART_WINDOW_SECONDS", "3600")))
    parser.add_argument("--http-timeout", type=float, default=float(os.getenv("VLLM_WATCHDOG_HTTP_TIMEOUT", "5")))
    parser.add_argument("--command-timeout", type=float, default=float(os.getenv("VLLM_WATCHDOG_COMMAND_TIMEOUT", "5")))
    parser.add_argument("--evidence-command-timeout", type=float, default=float(os.getenv("VLLM_WATCHDOG_EVIDENCE_COMMAND_TIMEOUT", "20")))
    parser.add_argument("--journal-lines", type=int, default=int(os.getenv("VLLM_WATCHDOG_JOURNAL_LINES", "250")))
    parser.add_argument("--ready-timeout", type=float, default=float(os.getenv("VLLM_WATCHDOG_READY_TIMEOUT", "900")))
    parser.add_argument("--ready-interval", type=float, default=float(os.getenv("VLLM_WATCHDOG_READY_INTERVAL", "5")))
    parser.add_argument("--dry-run", action="store_true", default=os.getenv("VLLM_WATCHDOG_DRY_RUN", "0") == "1")
    parser.add_argument("--once", action="store_true", help="Collect one snapshot and exit without restarting.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    last_snapshot: Snapshot | None = None
    stalled_since: float | None = None
    restart_times: list[float] = []
    last_restart = 0.0

    log(
        "watchdog start "
        f"service={args.service_name} interval={args.interval}s "
        f"stall={args.stall_seconds}s gpu_threshold={args.gpu_threshold}%"
    )

    while True:
        now = time.monotonic()
        snapshot, detail = collect_snapshot(args)
        if snapshot is None:
            stalled_since = None
            log("metrics unavailable; skipping wedge decision")
            if args.once:
                print(detail)
                return 2
            time.sleep(args.interval)
            continue

        if args.once:
            print(json.dumps(snapshot.__dict__, indent=2))
            return 0

        gpu_high = snapshot.gpu_util is not None and snapshot.gpu_util >= args.gpu_threshold
        running = snapshot.running > 0
        progressed = (
            last_snapshot is None
            or snapshot.token_total > last_snapshot.token_total
            or snapshot.token_total < last_snapshot.token_total
        )
        wedged_sample = snapshot.health_ok and running and gpu_high and not progressed

        if wedged_sample:
            if stalled_since is None:
                stalled_since = now
            stalled_for = now - stalled_since
        else:
            stalled_since = None
            stalled_for = 0.0

        log(
            "sample "
            f"health={snapshot.health_ok} running={snapshot.running:.0f} "
            f"waiting={snapshot.waiting:.0f} gpu={snapshot.gpu_util} "
            f"tokens={snapshot.token_total:.0f} progressed={progressed} "
            f"stalled_for={stalled_for:.0f}s"
        )

        restart_times = [t for t in restart_times if now - t <= args.restart_window_seconds]
        can_restart = (
            stalled_for >= args.stall_seconds
            and now - last_restart >= args.cooldown_seconds
            and len(restart_times) < args.max_restarts
        )
        if can_restart:
            evidence_dir = collect_evidence(args, detail)
            log(f"wedge detected; evidence={evidence_dir}")
            if args.dry_run:
                log("dry-run enabled; not restarting")
            else:
                code, output = run_command(
                    ["systemctl", "restart", args.service_name],
                    args.evidence_command_timeout,
                )
                write_file(evidence_dir / "restart.txt", f"exit={code}\n\n{output}")
                last_restart = time.monotonic()
                restart_times.append(last_restart)
                ready = wait_ready(args)
                write_file(evidence_dir / "ready.txt", f"ready={ready}\n")
                log(f"restart complete ready={ready}")
            stalled_since = None
            last_snapshot = None
        else:
            last_snapshot = snapshot

        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
