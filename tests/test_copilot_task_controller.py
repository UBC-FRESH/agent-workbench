from __future__ import annotations

import json
from pathlib import Path

from agent_workbench.copilot_task_controller import (
    build_launch_prompt,
    generate_prompt_file,
    load_run_manifest,
    render_review_packet,
    validate_run_manifest,
)


def write_manifest_fixture(tmp_path: Path) -> Path:
    ticket = tmp_path / "ticket.md"
    ticket.write_text("Do exactly one child task.\n", encoding="utf-8")
    heartbeat = tmp_path / "heartbeat.jsonl"
    heartbeat.write_text(
        json.dumps(
            {
                "timestamp": "2026-07-06T00:00:00Z",
                "checklist_item": "P68.4 review",
                "status": "completed",
                "action": "wrote result",
                "artifact_path": "result.md",
                "command_summary": "pytest passed",
                "next_intended_action": "stop",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "result.md").write_text("done\n", encoding="utf-8")
    archive = tmp_path / "archive.json"
    archive.write_text(
        json.dumps(
            {
                "session_id": "session-1",
                "model_ids_detected": ["ollama/qwen3.6:35b-a3b-bf16"],
                "permission_levels_detected": ["autopilot"],
                "user_message_count": 1,
                "assistant_message_count_with_text": 2,
                "tool_request_count": 3,
                "keep_going_user_messages": [],
                "stall_nudge_user_messages": [],
            }
        ),
        encoding="utf-8",
    )
    manifest = {
        "run_id": "p68-test-run-20260706",
        "ticket_path": "ticket.md",
        "child_issue": "#449",
        "expected_model": "ollama/qwen3.6:35b-a3b-bf16",
        "permission_mode": "autopilot",
        "heartbeat_path": "heartbeat.jsonl",
        "result_path": "result.md",
        "blocker_path": "blocker.md",
        "archive_manifest_path": "archive.json",
        "token_ledger_path": "tokens.md",
        "workspace_root": ".",
        "prompt_marker": "P68_TEST",
        "economics_claim": False,
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_validate_run_manifest_accepts_complete_manifest(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_run_manifest(manifest_path)

    result = validate_run_manifest(manifest, manifest_path=manifest_path)

    assert result.ok, result.errors


def test_validate_run_manifest_rejects_short_run_id(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_run_manifest(manifest_path)
    manifest["run_id"] = "short"

    result = validate_run_manifest(manifest, manifest_path=manifest_path)

    assert not result.ok
    assert "run_id" in result.errors[0]


def test_build_launch_prompt_contains_directive_and_no_maximize(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_run_manifest(manifest_path)

    prompt = build_launch_prompt(manifest, "Do one thing.")

    assert "Execute the child-task ticket below exactly." in prompt
    assert "Do not complete sibling tasks" in prompt
    assert "--maximize" not in prompt


def test_generate_prompt_file_and_review_packet(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path)
    prompt_output = tmp_path / "prompt.md"
    review_output = tmp_path / "review.md"

    prompt_result = generate_prompt_file(manifest_path, prompt_output)
    packet = render_review_packet(manifest_path, review_output)

    assert prompt_output.exists()
    assert "--maximize" not in prompt_result["launch_command"]
    assert packet["recommended_decision"] == "accept"
    assert review_output.exists()
