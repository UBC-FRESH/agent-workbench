import json
from pathlib import Path

from agent_workbench.native_session_events import ingest_worker_session, initialize_session_cursor
from agent_workbench.supervision import SCHEMA_VERSION, validate_events


def setup(tmp_path: Path):
    root = tmp_path / "run"; supervision = root / "supervision"; supervision.mkdir(parents=True)
    manifest = {"schema_version": SCHEMA_VERSION, "run_id": "run-native", "worker_session_id": "worker-native", "supervisor_session_id": "supervisor-native", "assigned_root": str(root), "supervision_dir": "supervision", "events_path": "supervision/events.jsonl", "cursor_path": "supervision/cursor.json", "packets_path": "supervision/packets.jsonl", "actions_path": "supervision/actions.jsonl"}
    (supervision / "manifest.json").write_text(json.dumps(manifest)); return root, manifest, supervision


def test_tail_failure_is_safe_and_deduplicated(tmp_path, monkeypatch):
    root, manifest, supervision = setup(tmp_path); home = tmp_path / "home"; session_dir = home / ".codex" / "sessions"; session_dir.mkdir(parents=True)
    session = session_dir / "2026-worker-native.jsonl"
    session.write_text(json.dumps({"type": "response_item", "payload": {"type": "custom_tool_call_output", "output": {"text": "Exit code: 17 secret"}}}) + "\n")
    first = ingest_worker_session(manifest=manifest, root=root, sessions_root=session_dir)
    second = ingest_worker_session(manifest=manifest, root=root, sessions_root=session_dir)
    assert first[0]["kind"] == "tool_failed" and second == []
    assert "secret" not in json.dumps(first[0])
    assert validate_events(first, assigned_root=root).ok


def test_incomplete_final_line_waits(tmp_path):
    root, manifest, supervision = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    session = sessions / "worker-native.jsonl"; session.write_text('{"type":"response_item","payload":{"type":"custom_tool_call_output","output":"Exit code: 17"}}')
    assert ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions) == []
    session.write_text(session.read_text() + "\n")
    assert ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)[0]["kind"] == "tool_failed"


def test_initial_checkpoint_ignores_historical_failure(tmp_path):
    root, manifest, _ = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    session = sessions / "worker-native.jsonl"
    session.write_text('{"type":"custom_tool_call_output","output":"Exit code: 17 historical"}\n')
    initialize_session_cursor(manifest=manifest, root=root, sessions_root=sessions)
    assert ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions) == []
    with session.open("a", encoding="utf-8") as stream:
        stream.write('{"type":"response_item","payload":{"type":"custom_tool_call_output","output":"Exit code: 17 new"}}\n')
    events = ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)
    assert len(events) == 1 and events[0]["kind"] == "tool_failed"
    assert ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions) == []


def test_one_tail_batch_gets_strictly_increasing_sequences(tmp_path):
    root, manifest, _ = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    session = sessions / "worker-native.jsonl"
    session.write_text(
        "\n".join(json.dumps({"type": "response_item", "payload": {"type": "custom_tool_call_output", "output": f"Exit code: {code}"}}) for code in (0, 1)) + "\n"
    )
    events = ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)
    assert [event["sequence"] for event in events] == [1, 2]
    assert validate_events(events, assigned_root=root).ok
