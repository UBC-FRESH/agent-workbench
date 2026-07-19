from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from agent_workbench.supervision import SCHEMA_VERSION
from agent_workbench.supervision_controller import acknowledge_cursor, prepare_review_delta


def event(sequence: int) -> dict[str, object]:
    return {"schema_version": SCHEMA_VERSION, "sequence": sequence, "event_id": f"event-{sequence}", "timestamp": "2026-07-19T01:00:00Z", "kind": "tool_completed", "stage": "tool", "outcome": "succeeded", "redaction_applied": True, "run_id": "run-1", "hook_event": "PostToolUse", "tool_name": "Bash", "root_match": True}


def setup_run(tmp_path: Path, events: list[dict[str, object]]) -> Path:
    root = tmp_path / "run"
    root.mkdir()
    supervision = root / "supervision"
    supervision.mkdir()
    (supervision / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    manifest = {"schema_version": SCHEMA_VERSION, "run_id": "run-1", "worker_session_id": "worker-1", "supervisor_session_id": "supervisor-1", "assigned_root": str(root), "supervision_dir": str(supervision), "events_path": "supervision/events.jsonl", "cursor_path": "supervision/cursor.json", "packets_path": "supervision/supervisor_packets.jsonl", "actions_path": "supervision/coordinator_actions.jsonl"}
    path = supervision / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def packet(end: int) -> dict[str, object]:
    return {"schema_version": SCHEMA_VERSION, "run_id": "run-1", "classification": "productive_repair", "recommended_action": "continue", "evidence_summary": "validated event delta", "event_start_sequence": 1, "event_end_sequence": end}


def action(value: dict[str, object]) -> dict[str, object]:
    digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"schema_version": SCHEMA_VERSION, "run_id": "run-1", "packet_sha256": digest, "decision": "continue"}


def test_manifest_bound_review_and_ack_chain(tmp_path: Path) -> None:
    manifest = setup_run(tmp_path, [event(1), event(2)])
    delta, maximum = prepare_review_delta(manifest_path=manifest)
    assert delta["event_count"] == 2 and maximum == 2
    p = packet(2)
    acknowledge_cursor(manifest_path=manifest, last_sequence=2, packet=p, action=action(p))
    assert json.loads((manifest.parent / "cursor.json").read_text())["last_sequence"] == 2
    assert len((manifest.parent / "supervisor_packets.jsonl").read_text().splitlines()) == 1


def test_manifest_rejects_location_outside_declared_supervision_dir(tmp_path: Path) -> None:
    manifest = setup_run(tmp_path, [event(1)])
    outside = manifest.parent.parent / "manifest.json"
    outside.write_text(manifest.read_text(), encoding="utf-8")
    with pytest.raises(ValueError, match="within supervision_dir"):
        prepare_review_delta(manifest_path=outside)


def test_ack_requires_reviewed_packet_action_chain(tmp_path: Path) -> None:
    manifest = setup_run(tmp_path, [event(1)])
    p = packet(1)
    with pytest.raises(ValueError, match="packet_sha256"):
        acknowledge_cursor(manifest_path=manifest, last_sequence=1, packet=p, action={**action(p), "packet_sha256": "0" * 64})
    assert not (manifest.parent / "cursor.json").exists()


def test_ack_rejects_sequence_beyond_observed_events(tmp_path: Path) -> None:
    manifest = setup_run(tmp_path, [event(1)])
    p = packet(2)
    with pytest.raises(ValueError, match="observed validated event maximum"):
        acknowledge_cursor(manifest_path=manifest, last_sequence=2, packet=p, action=action(p))
    assert not (manifest.parent / "cursor.json").exists()
    assert not (manifest.parent / "supervisor_packets.jsonl").exists()


def test_truncated_event_log_fails_closed_after_restart(tmp_path: Path) -> None:
    manifest = setup_run(tmp_path, [event(1)])
    events = manifest.parent / "events.jsonl"
    events.write_bytes(events.read_bytes().rstrip(b"\n"))
    with pytest.raises(ValueError, match="truncated"):
        prepare_review_delta(manifest_path=manifest)


def test_manifest_rejects_absolute_artifact_path(tmp_path: Path) -> None:
    manifest = setup_run(tmp_path, [event(1)])
    value = json.loads(manifest.read_text())
    value["events_path"] = str(manifest.parent / "events.jsonl")
    manifest.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="relative path"):
        prepare_review_delta(manifest_path=manifest)
