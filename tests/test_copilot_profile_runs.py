from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from agent_workbench.cli import run_copilot_sdk_profile_run
from agent_workbench.copilot_profile_runs import (
    render_profile_run_evidence_markdown,
    summarize_profile_run,
)


def write_profile(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "---",
                "name: worker",
                "description: Test worker.",
                "model: qwen3.6",
                "tools: ['read']",
                "---",
                "",
                "Do the assigned work.",
            ]
        ),
        encoding="utf-8",
    )


def write_manifest(tmp_path: Path) -> Path:
    profile = tmp_path / "worker.agent.md"
    write_profile(profile)
    manifest = {
        "schema_version": 1,
        "run_id": "p73-run-summary-test",
        "phase": "P73",
        "governing_issue": 480,
        "child_issue": "",
        "target_project": "agent-workbench",
        "target_task": "profile run summary",
        "workspace_root": ".",
        "sdk": {
            "provider": "github-copilot-sdk",
            "session_id": "sdk-session-1",
            "resumable": True,
            "model": "",
            "permission_mode": "operator-configured",
            "mode": "empty",
            "base_directory": "runtime/copilot_sdk_home/p73-run-summary-test",
            "agent_profiles": {
                "source_paths": [str(profile)],
                "selected": "worker",
                "custom_tools": [],
                "task_overlay": {"text": "Use the evidence contract."},
            },
        },
        "paths": {
            "ticket": "ticket.md",
            "result": "result.md",
            "blocker": "blocker.md",
            "heartbeat": "run.heartbeat.jsonl",
            "event_log": "run.sdk_events.jsonl",
            "status_summary": "run.sdk_status.json",
            "nudge_log": "run.nudges.jsonl",
        },
        "control": {"stop_condition": "result or blocker"},
        "state": {"latest_status": "completion_candidate"},
        "privacy": {"raw_events_local_only": True},
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "run.sdk_events.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"type": "session.custom_agents_updated", "data": {}}),
                json.dumps({"type": "user.message", "data": {"content": "ticket"}}),
                json.dumps(
                    {
                        "type": "assistant.message",
                        "data": {"content": "done", "agent_name": "worker"},
                    }
                ),
                json.dumps({"type": "tool.execution_start", "data": {}}),
                json.dumps({"type": "subagent.started", "data": {}}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "run.sdk_status.json").write_text(
        json.dumps({"latest_status": "completion_candidate", "observed_errors": []}),
        encoding="utf-8",
    )
    (tmp_path / "result.md").write_text(
        "Final status: accepted-candidate\n\nSummary: done.\n",
        encoding="utf-8",
    )
    return manifest_path


def test_profile_run_summary_extracts_public_safe_evidence(tmp_path: Path) -> None:
    manifest_path = write_manifest(tmp_path)

    evidence = summarize_profile_run(manifest_path)
    markdown = render_profile_run_evidence_markdown(evidence)

    assert evidence.ok, evidence.errors
    assert evidence.run_id == "p73-run-summary-test"
    assert evidence.selected_agent == "worker"
    assert evidence.controller_health == "healthy"
    assert evidence.result_status == "accepted-candidate"
    assert evidence.event_count == 5
    assert evidence.assistant_messages == 1
    assert evidence.custom_agent_events == 1
    assert evidence.subagent_events == 1
    assert evidence.agent_metadata_messages == 1
    assert "# Copilot SDK Profile Run Evidence" in markdown
    assert "Do the assigned work." not in markdown
    assert "ticket" not in markdown


def test_profile_run_summary_accepts_markdown_heading_final_status(
    tmp_path: Path,
) -> None:
    manifest_path = write_manifest(tmp_path)
    (tmp_path / "result.md").write_text(
        "# Final status: accepted-candidate\n\nSummary: done.\n",
        encoding="utf-8",
    )

    evidence = summarize_profile_run(manifest_path)

    assert evidence.result_status == "accepted-candidate"


def test_profile_run_summary_cli_writes_preview(tmp_path: Path, capsys: object) -> None:
    manifest_path = write_manifest(tmp_path)
    output = tmp_path / "profile_run.md"

    exit_code = run_copilot_sdk_profile_run(
        Namespace(manifest=manifest_path, output=output)
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "selected=worker" in captured.out
    assert "controller_health=healthy" in captured.out
    assert output.exists()
