import json
from pathlib import Path

import pytest

from agent_workbench.supervision import SCHEMA_VERSION
from agent_workbench.supervision_event_broker import SupervisionEventBroker


def setup_manifest(tmp_path: Path) -> Path:
    root = tmp_path / "run"; (root / "supervision").mkdir(parents=True)
    data = {"schema_version": SCHEMA_VERSION, "run_id": "run-broker", "worker_session_id": "worker-broker", "supervisor_session_id": "supervisor-broker", "assigned_root": str(root), "supervision_dir": str(root / "supervision"), "events_path": "supervision/events.jsonl", "cursor_path": "supervision/cursor.json", "packets_path": "supervision/packets.jsonl", "actions_path": "supervision/actions.jsonl"}
    path = root / "supervision" / "manifest.json"; path.write_text(json.dumps(data)); return path


def event(kind="tool_failed", stage="validation", sequence=1):
    return {"schema_version": SCHEMA_VERSION, "sequence": sequence, "event_id": f"e-{sequence}", "timestamp": "2026-07-20T00:00:00Z", "kind": kind, "stage": stage, "outcome": "failed" if kind == "tool_failed" else "succeeded", "redaction_applied": True, "run_id": "run-broker", "hook_event": "host", "tool_name": "test", "root_match": True}


def write_events(path: Path, events):
    events_path = path.parent.parent / "supervision" / "events.jsonl"
    events_path.write_text("".join(json.dumps(item) + "\n" for item in events))


def test_wakes_on_failure(tmp_path):
    manifest = setup_manifest(tmp_path); write_events(manifest, [event()])
    delta = SupervisionEventBroker(manifest, poll_interval=0).wait_for_trigger(timeout=0)
    assert delta["event_count"] == 1 and delta["events"][0]["kind"] == "tool_failed"
    assert "tool_name" in delta["events"][0] and "raw" not in delta["events"][0]


def test_ignores_routine_progress_until_trigger(tmp_path):
    manifest = setup_manifest(tmp_path); write_events(manifest, [event("tool_completed", "implementation")])
    with pytest.raises(TimeoutError):
        SupervisionEventBroker(manifest, poll_interval=0).wait_for_trigger(timeout=0)
    write_events(manifest, [event("tool_completed", "implementation"), event(sequence=2)])
    assert SupervisionEventBroker(manifest, poll_interval=0).wait_for_trigger(timeout=0)["cursor_end_sequence"] == 2


def test_timeout(tmp_path):
    with pytest.raises(TimeoutError, match="timeout"):
        SupervisionEventBroker(setup_manifest(tmp_path), poll_interval=0).wait_for_trigger(timeout=0)


def test_wait_reloads_manifest_after_native_binding(tmp_path, monkeypatch):
    manifest_path = setup_manifest(tmp_path)
    broker = SupervisionEventBroker(manifest_path, poll_interval=0)
    bound = json.loads(manifest_path.read_text())
    bound["worker_session_id"] = "worker-bound"
    manifest_path.write_text(json.dumps(bound))

    def bound_event(*, manifest, root):
        assert manifest["worker_session_id"] == "worker-bound"
        return [event()]

    monkeypatch.setattr("agent_workbench.supervision_event_broker.ingest_worker_session", bound_event)
    assert broker.wait_for_trigger(timeout=0)["event_count"] == 1


def test_malformed_input_fails_closed(tmp_path):
    manifest = setup_manifest(tmp_path)
    events_path = manifest.parent / "events.jsonl"; events_path.write_text('{"broken":\n')
    with pytest.raises(ValueError):
        SupervisionEventBroker(manifest, poll_interval=0).wait_for_trigger(timeout=0)
