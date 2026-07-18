from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_p114_qualification", ROOT / "scripts" / "verify_p114_c4_qualification.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_protocol_admission_is_independent_of_frozen_workload_quality(
    tmp_path: Path, monkeypatch
) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    source = worktree / "README.md"
    source.write_text("frozen\n", encoding="utf-8")
    target = tmp_path / "config.toml"
    backup = tmp_path / "config.before.toml"
    target.write_bytes(b"same\n")
    backup.write_bytes(b"same\n")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    run_dir.joinpath("qualification_manifest.json").write_text(
        json.dumps(
            {
                "baseline_commit": "test-baseline",
                "literal_worktree": str(worktree),
                "materialized_inputs": {
                    "README.md": hashlib.sha256(source.read_bytes()).hexdigest()
                },
            }
        ),
        encoding="utf-8",
    )
    run_dir.joinpath("role_binding_manifest.json").write_text(
        json.dumps(
            {
                "package_mcp_qualification": True,
                "literal_worktree": worktree.as_posix(),
                "package_mcp_server": "agent_bridge_test",
            }
        ),
        encoding="utf-8",
    )
    run_dir.joinpath("transaction.json").write_text(
        json.dumps(
            {
                "state": "restored",
                "targets": [{"path": str(target), "backup_path": str(backup)}],
            }
        ),
        encoding="utf-8",
    )
    run_dir.joinpath("config.before.toml").write_bytes(b"same\n")
    run_dir.joinpath("ollama_qwen_coder_worker.before.toml").write_bytes(b"same\n")
    _write_jsonl(
        run_dir / "mcp_events.jsonl",
        [
            {"kind": "policy_decision", "decision": "allow", "tool": "read_file"},
            {"kind": "policy_decision", "decision": "allow", "tool": "apply_patch"},
            {"kind": "policy_decision", "decision": "allow", "tool": "exec"},
            {
                "kind": "policy_decision",
                "decision": "deny",
                "tool": "exec",
                "reason": "command_not_granted",
                "command": "git status",
            },
            {
                "kind": "tool_outcome",
                "tool": "apply_patch",
                "changed_files": [str(worktree / "README.md")],
            },
            {
                "kind": "tool_outcome",
                "tool": "exec",
                "command": MODULE.VALIDATIONS[0],
                "exit_code": 1,
            },
            {
                "kind": "tool_outcome",
                "tool": "exec",
                "command": MODULE.VALIDATIONS[1],
                "exit_code": 1,
            },
        ],
    )
    _write_jsonl(
        run_dir / "adapter_raw_requests.jsonl",
        [
            {
                "output": [
                    {"type": "tool_search_call", "call_id": "search"},
                    {
                        "type": "function_call",
                        "call_id": "read",
                        "namespace": "mcp__agent_bridge_test",
                        "name": "read_file",
                    },
                    {
                        "type": "function_call",
                        "call_id": "patch",
                        "namespace": "mcp__agent_bridge_test",
                        "name": "apply_patch",
                    },
                    {
                        "type": "function_call",
                        "call_id": "exec",
                        "namespace": "mcp__agent_bridge_test",
                        "name": "exec",
                    },
                ]
            }
        ],
    )
    monkeypatch.setattr(MODULE, "BASELINE", "test-baseline")
    monkeypatch.setattr(
        MODULE.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="test-baseline\n"),
    )

    result = MODULE.verify(run_dir)

    assert result["accepted"] is True
    assert result["protocol_accepted_candidate"] is True
    assert result["quality_validated_candidate"] is False
    assert result["economics_usable"] is False
    assert "validation_outcomes" in result["errors"]
    assert result["policy_denials"] == [
        {
            "tool": "exec",
            "reason": "command_not_granted",
            "command": "git status",
            "path": None,
        }
    ]
