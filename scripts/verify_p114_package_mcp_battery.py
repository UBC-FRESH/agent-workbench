"""Verify the fresh package-MCP P114.4 battery from raw run artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_FILES = {
    "ticket.md",
    "cli_parent_events.jsonl",
    "cli_parent_final.txt",
    "role_binding_manifest.json",
    "mcp_events.jsonl",
    "adapter_events.jsonl",
    "adapter_requests.jsonl",
    "adapter_verdicts.jsonl",
    "adapter_upstream.jsonl",
    "transaction.json",
    "config.before.toml",
    "ollama_qwen_coder_worker.before.toml",
    "target/p114_host_proof.txt",
}
EXPECTED_CALLS = ["tool_search", "exec", "apply_patch", "exec", "apply_patch", "exec"]
EXPECTED_MCP_TOOLS = ["exec", "apply_patch", "exec", "apply_patch", "exec"]
TERMINAL_MARKER = "P114_C4_PACKAGE_MCP_BATTERY_DONE"


def json_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def child_items(path: Path) -> list[dict[str, Any]]:
    return [
        row["payload"]
        for row in json_lines(path)
        if row.get("type") == "response_item" and isinstance(row.get("payload"), dict)
    ]


def terminal_text(items: list[dict[str, Any]]) -> str | None:
    messages = [item for item in items if item.get("type") == "message" and item.get("role") == "assistant"]
    if not messages:
        return None
    content = messages[-1].get("content")
    if not isinstance(content, list) or not content or not isinstance(content[0], dict):
        return None
    value = content[0].get("text")
    return value if isinstance(value, str) else None


def verify_row(run_dir: Path, session: Path) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_FILES if not (run_dir / name).is_file())
    if missing:
        return {"run_dir": str(run_dir), "session": str(session), "accepted": False, "errors": ["missing:" + ",".join(missing)]}

    manifest = json.loads((run_dir / "role_binding_manifest.json").read_text(encoding="utf-8"))
    mcp_rows = json_lines(run_dir / "mcp_events.jsonl")
    items = child_items(session)
    namespace = "mcp__" + str(manifest.get("package_mcp_server", ""))
    calls: list[str] = []
    invalid_namespace = False
    for item in items:
        if item.get("type") == "tool_search_call":
            calls.append("tool_search")
        elif item.get("type") in {"function_call", "custom_tool_call"}:
            calls.append(str(item.get("name", "")))
            if item.get("namespace") != namespace:
                invalid_namespace = True

    policies = [row for row in mcp_rows if row.get("kind") == "policy_decision"]
    outcomes = [row for row in mcp_rows if row.get("kind") == "tool_outcome"]
    policy_tools = [str(row.get("tool", "")) for row in policies]
    outcome_tools = [str(row.get("tool", "")) for row in outcomes]
    exit_codes = [int(row["exit_code"]) for row in outcomes if row.get("tool") == "exec" and isinstance(row.get("exit_code"), int)]
    outcome_errors = [row.get("is_error") for row in outcomes]
    transaction = json.loads((run_dir / "transaction.json").read_text(encoding="utf-8"))
    restored = transaction.get("state") == "restored"
    for target in transaction.get("targets", []):
        if not isinstance(target, dict):
            restored = False
            continue
        path = Path(str(target.get("path", "")))
        backup = Path(str(target.get("backup_path", "")))
        if not path.is_file() or not backup.is_file() or sha256_path(path) != sha256_path(backup):
            restored = False

    upstream = json_lines(run_dir / "adapter_upstream.jsonl")
    if manifest.get("battery") is not True or manifest.get("package_mcp_battery") is not True:
        errors.append("manifest_package_mcp_battery")
    if calls != EXPECTED_CALLS:
        errors.append("child_call_sequence")
    if invalid_namespace:
        errors.append("child_namespace")
    if [row.get("method") for row in mcp_rows if row.get("kind") == "request" and row.get("method") == "tools/call"] != ["tools/call"] * 5:
        errors.append("mcp_request_count")
    if policy_tools != EXPECTED_MCP_TOOLS or any(row.get("decision") != "allow" for row in policies):
        errors.append("mcp_policy_sequence")
    if outcome_tools != EXPECTED_MCP_TOOLS or exit_codes != [0, 17, 0] or outcome_errors != [False, False, True, False, False]:
        errors.append("mcp_outcome_sequence")
    if terminal_text(items) != TERMINAL_MARKER:
        errors.append("terminal_marker")
    if (run_dir / "target/p114_host_proof.txt").read_text(encoding="utf-8") != "after\n":
        errors.append("target_content")
    if not restored:
        errors.append("byte_restore")
    if any(row.get("status") != 200 for row in upstream if row.get("kind") == "response_headers"):
        errors.append("upstream_status")
    return {"run_dir": str(run_dir), "session": str(session), "accepted": not errors, "errors": errors, "exit_codes": exit_codes}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", action="append", type=Path, required=True)
    parser.add_argument("--session", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.run_dir) != len(args.session):
        parser.error("run-dir and session counts must match")
    rows = [verify_row(run_dir, session) for run_dir, session in zip(args.run_dir, args.session)]
    sessions = [row["session"] for row in rows]
    accepted = len(rows) == 3 and len(set(sessions)) == len(sessions) and all(row["accepted"] for row in rows)
    args.output.write_text(json.dumps({"schema_version": 1, "accepted": accepted, "row_count": len(rows), "rows": rows}, indent=2) + "\n", encoding="utf-8")
    if not accepted:
        raise SystemExit("P114 package-MCP battery rejected")


if __name__ == "__main__":
    main()
