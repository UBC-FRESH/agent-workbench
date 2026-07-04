"""Codex supervisor-token checkpoint helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .tokens import synthesize_token_markdown


DEFAULT_SUPERVISOR_INPUT_PRICE_PER_1M_USD = 1.75
DEFAULT_SUPERVISOR_CACHED_INPUT_PRICE_PER_1M_USD = 0.175
DEFAULT_SUPERVISOR_OUTPUT_PRICE_PER_1M_USD = 14.0

USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


@dataclass(frozen=True)
class SupervisorTokenSnapshot:
    timestamp: str
    source_session_path: Path
    source_session_file: str
    usage: dict[str, int]
    last_usage: dict[str, int]
    model_context_window: int | None


def default_codex_session_root() -> Path:
    return Path.home() / ".codex" / "sessions"


def latest_session_jsonl(session_root: Path | None = None) -> Path:
    root = session_root or default_codex_session_root()
    paths = sorted(
        root.glob("**/rollout-*.jsonl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not paths:
        raise FileNotFoundError(f"no Codex session JSONL files found under {root}")
    return paths[0]


def latest_snapshot(
    session_jsonl: Path | None = None,
    session_root: Path | None = None,
) -> SupervisorTokenSnapshot:
    path = session_jsonl or latest_session_jsonl(session_root)
    snapshots = list(iter_token_snapshots(path))
    if not snapshots:
        raise ValueError(f"no token_count events found in {path}")
    return snapshots[-1]


def iter_token_snapshots(path: Path) -> list[SupervisorTokenSnapshot]:
    snapshots: list[SupervisorTokenSnapshot] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{path}:{line_number}: invalid JSONL line: {exc}"
            ) from exc
        if not isinstance(event, dict):
            continue
        if event.get("type") != "event_msg":
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict) or payload.get("type") != "token_count":
            continue
        info = payload.get("info")
        if not isinstance(info, dict):
            continue
        total = normalize_usage(info.get("total_token_usage"))
        last = normalize_usage(info.get("last_token_usage"))
        if not total:
            continue
        context_window = info.get("model_context_window")
        snapshots.append(
            SupervisorTokenSnapshot(
                timestamp=str(event.get("timestamp", "")),
                source_session_path=path,
                source_session_file=path.name,
                usage=total,
                last_usage=last,
                model_context_window=(
                    int(context_window)
                    if isinstance(context_window, (int, float))
                    else None
                ),
            )
        )
    return snapshots


def write_checkpoint(
    *,
    span_id: str,
    event: str,
    output: Path,
    session_jsonl: Path | None = None,
    session_root: Path | None = None,
) -> dict[str, Any]:
    if event not in {"start", "end"}:
        raise ValueError("event must be 'start' or 'end'")
    snapshot = latest_snapshot(session_jsonl=session_jsonl, session_root=session_root)
    checkpoint = {
        "schema_version": 1,
        "checkpoint_type": "codex_supervisor_token_checkpoint",
        "span_id": span_id,
        "event": event,
        "captured_utc": now_utc(),
        "source": {
            "source_type": "codex-session-jsonl",
            "source_session_file": snapshot.source_session_file,
            "source_session_path_recorded": False,
        },
        "snapshot_timestamp": snapshot.timestamp,
        "model_context_window": snapshot.model_context_window,
        "usage": snapshot.usage,
        "last_usage": snapshot.last_usage,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
    return checkpoint


def span_record_from_checkpoints(
    *,
    start_path: Path,
    end_path: Path,
    output: Path,
    project: str = "agent-workbench",
    phase: str = "",
    task_id: str = "",
    span_kind: str = "",
    supervisor_input_price_per_1m_usd: float = DEFAULT_SUPERVISOR_INPUT_PRICE_PER_1M_USD,
    supervisor_cached_input_price_per_1m_usd: float = (
        DEFAULT_SUPERVISOR_CACHED_INPUT_PRICE_PER_1M_USD
    ),
    supervisor_output_price_per_1m_usd: float = DEFAULT_SUPERVISOR_OUTPUT_PRICE_PER_1M_USD,
) -> dict[str, Any]:
    start = load_checkpoint(start_path)
    end = load_checkpoint(end_path)
    validate_checkpoint_pair(start, end)
    delta_total = usage_delta(start["usage"], end["usage"])
    cached_input = delta_total["cached_input_tokens"]
    fresh_input = max(delta_total["input_tokens"] - cached_input, 0)
    output_tokens = delta_total["output_tokens"]
    reasoning_output = delta_total["reasoning_output_tokens"]
    span_id = str(start["span_id"])
    record = {
        "record_id": f"{span_id}-supervisor-token-span",
        "source_type": "codex-session",
        "generated_utc": now_utc(),
        "scope": {
            "project": project,
            "phase": phase,
            "task_id": task_id or span_id,
            "span_id": span_id,
            "span_kind": span_kind,
            "model_or_worker": "codex-supervisor",
            "protocol": "codex-session-token-checkpoint",
        },
        "usage": {
            "supervisor_input_tokens": fresh_input,
            "supervisor_cached_input_tokens": cached_input,
            "supervisor_output_tokens": output_tokens,
            "supervisor_reasoning_output_tokens": reasoning_output,
            "worker_input_tokens": 0,
            "worker_output_tokens": 0,
            "codex_total_input_token_delta": delta_total["input_tokens"],
            "codex_total_token_delta": delta_total["total_tokens"],
        },
        "prices": {
            "supervisor_input_price_per_1m_usd": supervisor_input_price_per_1m_usd,
            "supervisor_cached_input_price_per_1m_usd": (
                supervisor_cached_input_price_per_1m_usd
            ),
            "supervisor_output_price_per_1m_usd": supervisor_output_price_per_1m_usd,
            "worker_input_price_per_1m_usd": 0.0,
            "worker_output_price_per_1m_usd": 0.0,
        },
        "public_safety": {
            "raw_prompts_excluded": True,
            "raw_traces_excluded": True,
            "provider_urls_excluded": True,
            "headers_excluded": True,
            "personal_paths_excluded": True,
        },
        "checkpoint_evidence": {
            "start_snapshot_timestamp": start.get("snapshot_timestamp", ""),
            "end_snapshot_timestamp": end.get("snapshot_timestamp", ""),
            "source_session_file": start.get("source", {}).get(
                "source_session_file", ""
            ),
            "source_session_path_recorded": False,
        },
        "notes": [
            "Supervisor input_tokens are fresh billable input after subtracting cached input.",
            "Supervisor reasoning output tokens are priced at the supervisor output-token rate.",
            "Raw Codex session paths, prompts, messages, and traces are not copied into this record.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def synthesize_supervisor_token_spans(input_dir: Path, output: Path) -> str:
    paths = sorted(input_dir.glob("*.tokens.json"))
    if not paths:
        raise ValueError(f"no *.tokens.json files found in {input_dir}")
    report = synthesize_token_markdown(paths)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def load_checkpoint(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    required = {"checkpoint_type", "span_id", "event", "usage"}
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"{path} is missing fields: {', '.join(missing)}")
    if data["checkpoint_type"] != "codex_supervisor_token_checkpoint":
        raise ValueError(f"{path} is not a Codex supervisor token checkpoint")
    if not isinstance(data.get("usage"), dict):
        raise ValueError(f"{path} usage must be an object")
    return data


def validate_checkpoint_pair(start: dict[str, Any], end: dict[str, Any]) -> None:
    if start.get("span_id") != end.get("span_id"):
        raise ValueError("checkpoint span_id values do not match")
    if start.get("event") != "start":
        raise ValueError("start checkpoint event must be 'start'")
    if end.get("event") != "end":
        raise ValueError("end checkpoint event must be 'end'")
    usage_delta(start["usage"], end["usage"])


def usage_delta(
    start_usage: dict[str, Any], end_usage: dict[str, Any]
) -> dict[str, int]:
    start = normalize_usage(start_usage)
    end = normalize_usage(end_usage)
    delta: dict[str, int] = {}
    for key in USAGE_KEYS:
        value = end[key] - start[key]
        if value < 0:
            raise ValueError(f"negative token delta for {key}: {value}")
        delta[key] = value
    return delta


def normalize_usage(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {key: 0 for key in USAGE_KEYS}
    usage: dict[str, int] = {}
    for key in USAGE_KEYS:
        raw_value = value.get(key, 0)
        if not isinstance(raw_value, (int, float)):
            raise ValueError(f"token usage field {key} must be numeric")
        if raw_value < 0:
            raise ValueError(f"token usage field {key} must be nonnegative")
        usage[key] = int(raw_value)
    return usage


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
