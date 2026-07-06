from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from agent_workbench.heartbeat import (
    load_heartbeat_jsonl,
    render_nudge,
    summarize_heartbeat_records,
    validate_heartbeat_records,
)


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )


def valid_records() -> list[dict]:
    return [
        {
            "timestamp": "2026-07-06T08:00:00Z",
            "checklist_item": "P67.1 heartbeat contract",
            "status": "thinking",
            "action": "Read ticket",
            "artifact_path": "runtime/agent_jobs/example_result.md",
            "command_summary": "none",
            "next_intended_action": "Write result skeleton",
        },
        {
            "timestamp": "2026-07-06T08:05:00Z",
            "checklist_item": "P67.1 heartbeat contract",
            "status": "completed",
            "action": "Wrote result skeleton",
            "artifact_path": "runtime/agent_jobs/example_result.md",
            "command_summary": "edited result file only",
            "next_intended_action": "Reconcile checklist",
        },
    ]


def test_load_and_validate_heartbeat_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "heartbeat.jsonl"
    write_jsonl(path, valid_records())

    records = load_heartbeat_jsonl(path)
    result = validate_heartbeat_records(records)

    assert result.ok, result.errors
    assert len(result.records) == 2


def test_validate_rejects_missing_required_field() -> None:
    records = valid_records()
    del records[0]["artifact_path"]

    result = validate_heartbeat_records(records)

    assert not result.ok
    assert any("artifact_path" in error for error in result.errors)


def test_summarize_detects_stale_no_progress() -> None:
    records = valid_records()
    records[-1]["status"] = "no_progress"

    summary = summarize_heartbeat_records(
        records,
        stale_after_seconds=60,
        now=datetime(2026, 7, 6, 8, 10, tzinfo=UTC),
    )

    assert summary["validation_ok"] is True
    assert summary["stale"] is True
    assert summary["stall_count"] == 2
    assert summary["recommended_nudge_type"] == "stop-summarizing"


def test_nudge_stop_rule_after_repeated_nudges() -> None:
    records = valid_records()
    records[0]["nudge_type"] = "continue-next-subtask"
    records[1]["nudge_type"] = "stop-summarizing"

    summary = summarize_heartbeat_records(
        records,
        stale_after_seconds=900,
        now=datetime(2026, 7, 6, 8, 6, tzinfo=UTC),
    )
    rendered = render_nudge(summary)

    assert summary["stop_rule_triggered"] is True
    assert "repeated-nudge stop rule" in rendered
