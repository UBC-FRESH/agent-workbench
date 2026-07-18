"""Verify one P114.5 qualification from raw run and child-session evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


BASELINE = "139e725ee069c27cf68c797dd66aa88b5bb2824d"
PATCH_PATHS = {
    "src/agent_workbench/source_audit.py",
    "src/agent_workbench/cli.py",
    "tests/test_source_audit.py",
    "README.md",
}
VALIDATIONS = [
    "python -m pytest -q tests/test_source_audit.py",
    "python runtime/agent_jobs/p107_suite_provenance_audit_bundle_acceptance.py",
]


def lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _walk_calls(value: object) -> list[dict[str, Any]]:
    """Extract actual provider child calls from the adapter's raw request trace."""

    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if value.get("type") in {"function_call", "tool_search_call"} and isinstance(value.get("call_id"), str):
            found.append(value)
        for nested in value.values():
            found.extend(_walk_calls(nested))
    elif isinstance(value, list):
        for nested in value:
            found.extend(_walk_calls(nested))
    return found


def verify(run_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    required = ["qualification_manifest.json", "role_binding_manifest.json", "mcp_events.jsonl", "transaction.json", "config.before.toml", "ollama_qwen_coder_worker.before.toml"]
    missing = [name for name in required if not (run_dir / name).is_file()]
    if missing:
        return {"accepted": False, "errors": ["missing:" + ",".join(missing)]}
    qualification = json.loads((run_dir / "qualification_manifest.json").read_text(encoding="utf-8"))
    binding = json.loads((run_dir / "role_binding_manifest.json").read_text(encoding="utf-8"))
    worktree = Path(str(qualification.get("literal_worktree", "")))
    if qualification.get("baseline_commit") != BASELINE or not worktree.is_dir():
        errors.append("literal_baseline_worktree")
    elif subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"], text=True, capture_output=True).stdout.strip() != BASELINE:
        errors.append("baseline_commit")
    if binding.get("package_mcp_qualification") is not True or binding.get("literal_worktree") != str(worktree).replace("\\", "/"):
        errors.append("qualification_binding")
    for path, expected in qualification.get("materialized_inputs", {}).items():
        candidate = worktree / path
        if not candidate.is_file() or digest(candidate) != expected:
            errors.append("frozen_input_hash")
            break
    events = lines(run_dir / "mcp_events.jsonl")
    policies = [row for row in events if row.get("kind") == "policy_decision"]
    outcomes = [row for row in events if row.get("kind") == "tool_outcome"]
    policy_enforced = bool(policies) and all(row.get("decision") in {"allow", "deny"} for row in policies)
    if not policy_enforced:
        errors.append("mcp_policy_log")
    policy_denials = [row for row in policies if row.get("decision") == "deny"]
    changed = {Path(path).as_posix() for row in outcomes for path in row.get("changed_files", []) if isinstance(path, str)}
    patch_scope_ok = bool(changed) and all(path.split(str(worktree).replace("\\", "/") + "/", 1)[-1] in PATCH_PATHS for path in changed)
    if not patch_scope_ok:
        errors.append("patch_scope")
    exec_codes = {row.get("command"): row.get("exit_code") for row in outcomes if row.get("tool") == "exec"}
    quality_ok = all(exec_codes.get(command) == 0 for command in VALIDATIONS)
    if not quality_ok:
        errors.append("validation_outcomes")
    transaction = json.loads((run_dir / "transaction.json").read_text(encoding="utf-8"))
    if transaction.get("state") != "restored":
        errors.append("transaction_state")
    for target in transaction.get("targets", []):
        path, backup = Path(target["path"]), Path(target["backup_path"])
        if not path.is_file() or not backup.is_file() or digest(path) != digest(backup):
            errors.append("byte_restore")
            break
    raw_request_log = run_dir / "adapter_raw_requests.jsonl"
    if not raw_request_log.is_file():
        errors.append("raw_child_trace")
        calls: list[dict[str, Any]] = []
    else:
        calls_by_id: dict[str, dict[str, Any]] = {}
        for row in lines(raw_request_log):
            for call in _walk_calls(row):
                calls_by_id[call["call_id"]] = call
        calls = list(calls_by_id.values())
    namespace = "mcp__" + str(binding.get("package_mcp_server", ""))
    searches = [call for call in calls if call.get("type") == "tool_search_call"]
    mcp_calls = [call for call in calls if call.get("type") == "function_call"]
    observed_tools = {str(call.get("name")) for call in mcp_calls}
    route_ok = (
        bool(searches)
        and {"read_file", "apply_patch", "exec"}.issubset(observed_tools)
        and all(call.get("namespace") == namespace and call.get("name") in {"read_file", "apply_patch", "exec"} for call in mcp_calls)
    )
    if not route_ok:
        errors.append("child_mcp_route")
    protocol_ok = (
        policy_enforced
        and patch_scope_ok
        and route_ok
        and transaction.get("state") == "restored"
        and "byte_restore" not in errors
    )
    return {
        "accepted": protocol_ok,
        "quality_validated_candidate": quality_ok,
        "protocol_accepted_candidate": protocol_ok,
        "economics_usable": False,
        "policy_denials": [
            {"tool": row.get("tool"), "reason": row.get("reason"), "command": row.get("command"), "path": row.get("path")}
            for row in policy_denials
        ],
        "errors": errors,
        "worktree": str(worktree),
        "calls": [item.get("name") for item in mcp_calls],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.run_dir)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if not result["accepted"]:
        raise SystemExit("P114 qualification rejected")


if __name__ == "__main__":
    main()
