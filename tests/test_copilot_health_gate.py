from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from agent_workbench.cli import run_copilot_sdk_health_gate
from agent_workbench.copilot_health_gate import (
    build_health_gate_report,
    render_health_gate_markdown,
)


def write_manifest(
    tmp_path: Path,
    run_id: str,
    *,
    status: str = "completion_candidate",
    observed_errors: list[object] | None = None,
    write_status: bool = True,
    write_events: bool = True,
) -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    workspace = run_dir / "workspace"
    workspace.mkdir()
    (run_dir / "ticket.md").write_text("Do one bounded task.\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "phase": "P81",
        "governing_issue": 518,
        "child_issue": 520,
        "target_project": "agent-workbench",
        "target_task": "health gate fixture",
        "workspace_root": "workspace",
        "sdk": {
            "provider": "github-copilot-sdk",
            "session_id": f"session-{run_id}",
            "resumable": True,
            "model": "",
            "permission_mode": "operator-configured",
            "mode": "empty",
            "base_directory": f"runtime/copilot_sdk_home/{run_id}",
            "available_tools": "default",
            "working_directory": "",
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
        "control": {
            "stall_seconds": 1,
            "nonprogress_event_limit": 5,
            "max_nudges": 2,
            "max_retries": 1,
            "stop_condition": "result or blocker",
        },
        "state": {
            "latest_status": status,
            "latest_event_at": "",
            "latest_nudge_at": "",
            "accepted_candidate": False,
        },
        "privacy": {
            "raw_events_local_only": True,
            "publish_sanitized_summary_only": True,
        },
    }
    if write_events:
        (run_dir / "run.sdk_events.jsonl").write_text(
            json.dumps({"type": "session.idle", "data": {}}) + "\n",
            encoding="utf-8",
        )
    if write_status:
        (run_dir / "run.sdk_status.json").write_text(
            json.dumps(
                {
                    "latest_status": status,
                    "observed_errors": observed_errors or [],
                    "event_count": 1 if write_events else 0,
                }
            ),
            encoding="utf-8",
        )
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def quota_error() -> str:
    return json.dumps(
        {
            "error": {
                "message": "Provider quota limit reached.",
                "code": "quota_exceeded",
            }
        }
    )


def test_health_gate_passes_healthy_manifest(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, "p81_healthy")

    report = build_health_gate_report([manifest], required_count=1)
    markdown = render_health_gate_markdown(report)

    assert report.go
    assert report.decision == "go"
    assert report.controller_health == {"healthy": 1}
    assert report.repeated_error_signatures == {}
    assert "decision: `go`" in markdown


def test_health_gate_blocks_repeated_quota_errors(tmp_path: Path) -> None:
    first = write_manifest(
        tmp_path,
        "p81_quota_1",
        status="blocked",
        observed_errors=[quota_error()],
    )
    second = write_manifest(
        tmp_path,
        "p81_quota_2",
        status="blocked",
        observed_errors=["Provider quota limit reached."],
    )

    report = build_health_gate_report([first, second], required_count=2)

    assert not report.go
    assert report.decision == "no-go"
    assert report.controller_health == {"error": 2}
    assert report.repeated_error_signatures == {"quota_exceeded": 2}
    assert "repeated_error_signature:quota_exceeded:2" in report.reasons


def test_health_gate_blocks_missing_status_evidence(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, "p81_missing_status", write_status=False)

    report = build_health_gate_report([manifest])

    assert not report.go
    assert report.rows[0].decision == "block"
    assert "status_summary_missing" in report.rows[0].reasons


def test_health_gate_blocks_required_count_shortfall(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, "p81_shortfall")

    report = build_health_gate_report([manifest], required_count=2)

    assert not report.go
    assert "manifest_count_below_required:1<2" in report.reasons


def test_health_gate_cli_writes_reports_and_returns_no_go(tmp_path: Path) -> None:
    manifest = write_manifest(
        tmp_path,
        "p81_cli_quota",
        status="blocked",
        observed_errors=[quota_error()],
    )
    json_output = tmp_path / "health.json"
    markdown_output = tmp_path / "health.md"

    exit_code = run_copilot_sdk_health_gate(
        Namespace(
            manifest=[manifest],
            required_count=1,
            json_output=json_output,
            markdown_output=markdown_output,
        )
    )

    assert exit_code == 2
    payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert payload["decision"] == "no-go"
    assert payload["rows"][0]["error_signatures"] == ["quota_exceeded"]
    assert "quota_exceeded" in markdown_output.read_text(encoding="utf-8")
