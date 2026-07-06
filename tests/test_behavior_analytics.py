from __future__ import annotations

import json
from pathlib import Path

from agent_workbench.behavior_analytics import (
    analyze_archive_manifest,
    load_archive_manifest,
    render_behavior_markdown,
    render_synthesis_markdown,
    synthesize_behavior_summaries,
)


def archive_manifest() -> dict:
    return {
        "session_id": "session-1",
        "run_id": "run-1",
        "model_ids_detected": ["ollama/qwen3.6:35b-a3b-bf16"],
        "permission_levels_detected": ["autopilot"],
        "user_message_count": 3,
        "assistant_message_count_with_text": 4,
        "tool_request_count": 2,
        "tool_completion_statuses": {"success": 2},
        "keep_going_user_messages": ["keep going"],
        "stall_nudge_user_messages": [],
        "user_message_snippets": ["start", "keep going", "done?"],
        "assistant_message_snippets": ["I successfully completed the task."],
        "tool_request_snippets": ["git status"],
    }


def test_analyze_archive_manifest_classifies_repair_needed() -> None:
    summary = analyze_archive_manifest(
        archive_manifest(),
        ticket_type="child-task",
        task_size="small",
        authority_level="L3",
    )

    assert summary["nudge_count"] == 1
    assert summary["premature_completion_claim_count"] == 1
    assert summary["behavior_outcome"] == "repair-needed"
    assert summary["coordinator_review_burden"] >= 1


def test_analyze_archive_manifest_classifies_smooth() -> None:
    manifest = archive_manifest()
    manifest["user_message_count"] = 1
    manifest["keep_going_user_messages"] = []
    manifest["user_message_snippets"] = ["start"]
    manifest["assistant_message_snippets"] = ["result written"]

    summary = analyze_archive_manifest(manifest)

    assert summary["behavior_outcome"] == "smooth"
    assert summary["nudge_count"] == 0


def test_load_render_and_synthesize_behavior(tmp_path: Path) -> None:
    path = tmp_path / "archive.json"
    path.write_text(json.dumps(archive_manifest()), encoding="utf-8")

    manifest = load_archive_manifest(path)
    summary = analyze_archive_manifest(manifest)
    rendered = render_behavior_markdown(summary)
    synthesis = synthesize_behavior_summaries([summary])
    rendered_synthesis = render_synthesis_markdown(synthesis)

    assert "Copilot Behavior Summary" in rendered
    assert synthesis["run_count"] == 1
    assert "collect more archives" in synthesis["policy_feedback"]
    assert "Copilot Behavior Synthesis" in rendered_synthesis
