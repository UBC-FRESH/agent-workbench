from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from agent_workbench.supervision import SCHEMA_VERSION
from agent_workbench.supervision_controller import (
    acknowledge_cursor,
    build_review_delta,
    load_cursor,
    prepare_review_delta,
)


def event(sequence: int, *, kind: str = "tool_completed") -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "sequence": sequence,
        "event_id": f"event-{sequence}",
        "timestamp": "2026-07-19T01:00:00Z",
        "kind": kind,
        "stage": "tool",
        "outcome": "failed" if kind == "workspace_mismatch" else "succeeded",
        "redaction_applied": True,
        "run_id": "p116-controller-probe",
        "hook_event": "PostToolUse",
        "tool_name": "Bash",
        "root_match": kind != "workspace_mismatch",
    }


def write_events(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def test_delta_keeps_only_unacknowledged_safe_events(tmp_path: Path) -> None:
    events_path = tmp_path / "events.jsonl"
    write_events(events_path, [event(1), event(2, kind="workspace_mismatch")])
    acknowledge_cursor(
        tmp_path / "cursor.json", last_sequence=1, assigned_root=tmp_path
    )

    delta, maximum = prepare_review_delta(
        events_path=events_path,
        cursor_path=tmp_path / "cursor.json",
        assigned_root=tmp_path,
    )

    assert maximum == 2
    assert delta["cursor_start_sequence"] == 1
    assert delta["cursor_end_sequence"] == 2
    assert delta["event_count"] == 1
    assert delta["signals"]["workspace_mismatch"] == 1
    assert "redaction_applied" not in delta["events"][0]


def test_acknowledged_events_are_not_replayed_after_restart(tmp_path: Path) -> None:
    events_path = tmp_path / "events.jsonl"
    cursor_path = tmp_path / "cursor.json"
    write_events(events_path, [event(1), event(2)])
    acknowledge_cursor(cursor_path, last_sequence=2, assigned_root=tmp_path)

    delta, maximum = prepare_review_delta(
        events_path=events_path, cursor_path=cursor_path, assigned_root=tmp_path
    )

    assert maximum == 2
    assert delta["event_count"] == 0
    assert delta["cursor_start_sequence"] == 2
    assert delta["cursor_end_sequence"] == 2


def test_rejects_invalid_cursor_or_reordered_events(tmp_path: Path) -> None:
    events_path = tmp_path / "events.jsonl"
    cursor_path = tmp_path / "cursor.json"
    write_events(events_path, [event(2), event(1)])

    with pytest.raises(ValueError, match="strictly increasing"):
        prepare_review_delta(events_path=events_path, cursor_path=cursor_path, assigned_root=tmp_path)

    write_events(events_path, [event(1)])
    cursor_path.write_text(json.dumps({"schema_version": SCHEMA_VERSION, "last_sequence": 2}), encoding="utf-8")
    with pytest.raises(ValueError, match="within observed event range"):
        prepare_review_delta(events_path=events_path, cursor_path=cursor_path, assigned_root=tmp_path)


def test_cursor_write_is_atomic_and_valid(tmp_path: Path) -> None:
    cursor_path = tmp_path / "nested" / "cursor.json"
    acknowledge_cursor(cursor_path, last_sequence=4, assigned_root=tmp_path)

    assert load_cursor(cursor_path, max_sequence=4) == 4
    assert not cursor_path.with_suffix(".json.tmp").exists()


def test_rejects_event_or_cursor_paths_outside_assigned_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.jsonl"
    outside.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="events path must stay within assigned_root"):
        prepare_review_delta(
            events_path=outside,
            cursor_path=tmp_path / "cursor.json",
            assigned_root=tmp_path,
        )
    with pytest.raises(ValueError, match="cursor path must stay within assigned_root"):
        acknowledge_cursor(outside, last_sequence=0, assigned_root=tmp_path)


def test_controller_script_renders_and_acknowledges(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    events_path = tmp_path / "events.jsonl"
    cursor_path = tmp_path / "cursor.json"
    write_events(events_path, [event(1)])

    completed = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "p116_supervision_controller.py"),
            "--events",
            str(events_path),
            "--cursor",
            str(cursor_path),
            "--assigned-root",
            str(tmp_path),
            "--ack",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["event_count"] == 1
    assert output["acknowledged_through_sequence"] == 1
    assert load_cursor(cursor_path, max_sequence=1) == 1
