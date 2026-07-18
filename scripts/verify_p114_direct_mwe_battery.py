"""Verify the three-row P114 direct-MWE capability battery from raw artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_FILES = {
    "ticket.md",
    "result.md",
    "heartbeat.jsonl",
    "archive_manifest.json",
    "deployment_proof.json",
    "codex_events.jsonl",
    "adapter_events.jsonl",
    "adapter_requests.jsonl",
    "final.txt",
    "target/p114_host_proof.txt",
}


def load_json_lines(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8"
    return [json.loads(line) for line in raw.decode(encoding).splitlines() if line.strip()]


def verify_row(run_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_FILES if not (run_dir / name).is_file())
    if missing:
        return {"run_dir": str(run_dir), "accepted": False, "errors": ["missing:" + ",".join(missing)]}
    events = load_json_lines(run_dir / "codex_events.jsonl")
    commands = [event["item"] for event in events if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "command_execution"]
    patches = [event["item"] for event in events if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "file_change"]
    threads = [event.get("thread_id") for event in events if event.get("type") == "thread.started" and isinstance(event.get("thread_id"), str)]
    proof = json.loads((run_dir / "deployment_proof.json").read_text(encoding="utf-8"))
    archive = json.loads((run_dir / "archive_manifest.json").read_text(encoding="utf-8"))
    heartbeat = load_json_lines(run_dir / "heartbeat.jsonl")
    target = (run_dir / "target/p114_host_proof.txt").read_text(encoding="utf-8")
    marker = (run_dir / "final.txt").read_text(encoding="utf-8").strip()
    if [command.get("exit_code") for command in commands] != [0, 17, 0]:
        errors.append("command_exit_codes")
    if len(patches) != 2:
        errors.append("native_patch_count")
    if target != "after\n":
        errors.append("target_content")
    if not marker.startswith("P114_CORE_") or not marker.endswith("_DONE"):
        errors.append("terminal_marker")
    if not proof.get("core_adapter") or proof.get("command_count") != 3 or proof.get("native_patch_count") != 2:
        errors.append("deployment_proof_counts")
    if not proof.get("adapter_teardown_observed") or not proof.get("normal_config_restored"):
        errors.append("deployment_proof_lifecycle")
    if archive.get("archive_kind") != "direct_codex_exec" or not archive.get("raw_artifacts_retained"):
        errors.append("archive_manifest")
    if len(heartbeat) != 1 or heartbeat[0].get("status") != "accepted-candidate":
        errors.append("heartbeat")
    if "Status: accepted-candidate" not in (run_dir / "result.md").read_text(encoding="utf-8"):
        errors.append("result")
    return {
        "run_dir": str(run_dir),
        "accepted": not errors,
        "errors": errors,
        "thread_id": threads[0] if len(threads) == 1 else None,
        "command_exit_codes": [command.get("exit_code") for command in commands],
        "native_patch_count": len(patches),
        "terminal_marker": marker,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [verify_row(path) for path in args.run_dir]
    thread_ids = [row["thread_id"] for row in rows]
    accepted = len(rows) == 3 and all(row["accepted"] for row in rows) and None not in thread_ids and len(set(thread_ids)) == len(thread_ids)
    report = {"schema_version": 1, "accepted": accepted, "row_count": len(rows), "distinct_fresh_threads": len(set(thread_ids)) if None not in thread_ids else 0, "rows": rows}
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not accepted:
        raise SystemExit("P114 direct-MWE capability battery rejected")


if __name__ == "__main__":
    main()
