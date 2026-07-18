"""Verify fresh P114.4 C4 battery rows from raw child and adapter artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_FILES = {
    "ticket.md",
    "cli_parent_events.jsonl",
    "cli_parent_final.txt",
    "role_binding_manifest.json",
    "adapter_events.jsonl",
    "adapter_requests.jsonl",
    "adapter_verdicts.jsonl",
    "adapter_upstream.jsonl",
    "target/p114_host_proof.txt",
}


def json_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def child_items(path: Path) -> list[dict[str, Any]]:
    return [
        row["payload"]
        for row in json_lines(path)
        if row.get("type") == "response_item" and isinstance(row.get("payload"), dict)
    ]


def verify_row(run_dir: Path, session: Path) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_FILES if not (run_dir / name).is_file())
    if missing:
        return {"run_dir": str(run_dir), "accepted": False, "errors": ["missing:" + ",".join(missing)]}
    manifest = json.loads((run_dir / "role_binding_manifest.json").read_text(encoding="utf-8"))
    items = child_items(session)
    calls = [item for item in items if item.get("type") in {"function_call", "custom_tool_call"}]
    outputs = [item for item in items if item.get("type") in {"function_call_output", "custom_tool_call_output"}]
    call_names = [item.get("name") for item in calls]
    command_outputs = [item.get("output", "") for item in outputs if item.get("call_id") in {call.get("call_id") for call in calls if call.get("type") == "function_call"}]
    exit_codes = [int(match.group(1)) for output in command_outputs if isinstance(output, str) for match in [re.search(r"Exit code: (\d+)", output)] if match]
    terminal = [item for item in items if item.get("type") == "message" and item.get("role") == "assistant"]
    terminal_text = terminal[-1].get("content", [{}])[0].get("text") if terminal and isinstance(terminal[-1].get("content"), list) else None
    adapter_calls = [
        (row.get("item_name"), row.get("item_type"))
        for row in json_lines(run_dir / "adapter_events.jsonl")
        if row.get("type") == "response.output_item.added"
    ]
    upstream = json_lines(run_dir / "adapter_upstream.jsonl")
    if manifest.get("battery") is not True:
        errors.append("manifest_battery")
    if call_names != ["shell_command", "apply_patch", "shell_command", "apply_patch", "shell_command"]:
        errors.append("child_call_sequence")
    if exit_codes != [0, 17, 0]:
        errors.append("command_exit_codes")
    if terminal_text != "P114_C4_BATTERY_DONE":
        errors.append("terminal_marker")
    if (run_dir / "target/p114_host_proof.txt").read_text(encoding="utf-8") != "after\n":
        errors.append("target_content")
    if adapter_calls != [("exec", "function_call"), ("apply_patch", "function_call"), ("exec", "function_call"), ("apply_patch", "function_call"), ("exec", "function_call"), (None, "message")]:
        errors.append("adapter_call_sequence")
    if any(row.get("status") != 200 for row in upstream if row.get("kind") == "response_headers"):
        errors.append("upstream_status")
    return {
        "run_dir": str(run_dir),
        "session": str(session),
        "accepted": not errors,
        "errors": errors,
        "exit_codes": exit_codes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", action="append", type=Path, required=True)
    parser.add_argument("--session", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.run_dir) != len(args.session):
        parser.error("run-dir and session counts must match")
    rows = [verify_row(run_dir, session) for run_dir, session in zip(args.run_dir, args.session)]
    sessions = [row.get("session") for row in rows]
    accepted = len(rows) == 3 and all(row["accepted"] for row in rows) and len(set(sessions)) == len(sessions)
    args.output.write_text(json.dumps({"schema_version": 1, "accepted": accepted, "row_count": len(rows), "rows": rows}, indent=2) + "\n", encoding="utf-8")
    if not accepted:
        raise SystemExit("P114 C4 capability battery rejected")


if __name__ == "__main__":
    main()
