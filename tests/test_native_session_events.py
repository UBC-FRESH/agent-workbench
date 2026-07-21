import json
from pathlib import Path

from agent_workbench import native_session_events
from agent_workbench.native_session_events import ingest_worker_session, initialize_session_cursor
from agent_workbench.diagnostic_policy import NORMALIZER_VERSION, POLICY_SCHEMA_VERSION, command_digest, freeze_policy
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


def test_tail_legacy_function_call_output_is_normalized(tmp_path):
    root, manifest, _ = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    session = sessions / "worker-native.jsonl"
    session.write_text(
        json.dumps({"type": "response_item", "payload": {
            "type": "function_call", "call_id": "call_1", "name": "shell_command",
        }}) + "\n" + json.dumps({"type": "response_item", "payload": {
            "type": "function_call_output", "call_id": "call_1",
            "output": "Exit code: 1\nParserError: unexpected token",
        }}) + "\n"
    )
    events = ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)
    assert len(events) == 1 and events[0]["kind"] == "tool_failed"
    assert events[0]["tool_name"] == "shell_command"
    assert events[0]["exit_code"] == 1 and events[0]["failure_class"] == "syntax_error"
    assert validate_events(events, assigned_root=root).ok


def test_incomplete_final_line_waits(tmp_path):
    root, manifest, supervision = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    session = sessions / "worker-native.jsonl"; session.write_text('{"type":"response_item","payload":{"type":"custom_tool_call_output","output":"Exit code: 17"}}')
    assert ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions) == []
    session.write_text(session.read_text() + "\n")
    assert ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)[0]["kind"] == "tool_failed"


def test_v2_policy_classifies_only_declared_check_without_raw_command(tmp_path):
    root, manifest, supervision = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    policy_id, policy = freeze_policy({"schema_version": POLICY_SCHEMA_VERSION, "normalizer_version": NORMALIZER_VERSION,
        "allowed_tools": ["shell_command", "apply_patch"], "edit_paths": ["src/allowed.py"],
        "checks": [{"check_id": "focused-tests", "command_sha256": command_digest("python -m pytest -q tests/test_allowed.py")}],})
    (supervision / "policy.json").write_text(json.dumps(policy), encoding="utf-8")
    manifest.update({"diagnostic_policy_id": policy_id, "diagnostic_policy_path": "supervision/policy.json"})
    session = sessions / "worker-native.jsonl"
    session.write_text("\n".join(json.dumps(item) for item in [
        {"type": "response_item", "payload": {"type": "function_call", "call_id": "check", "name": "shell_command", "arguments": json.dumps({"command": "python -m pytest -q tests/test_allowed.py"})}},
        {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "check", "output": "Exit code: 1\nSyntaxError: hidden detail"}},
    ]) + "\n")
    event = ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)[0]
    assert event["schema_version"] == "p116_supervision_event_v2"
    assert event["operation_class"] == "test" and event["scope_status"] == "within_ticket"
    assert event["check_id"] == "focused-tests" and event["failure_class"] == "syntax_error"
    assert "pytest" not in json.dumps(event) and "hidden detail" not in json.dumps(event)
    assert validate_events([event], assigned_root=root).ok


def test_v2_policy_marks_undeclared_patch_outside_ticket(tmp_path):
    root, manifest, supervision = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    policy_id, policy = freeze_policy({"schema_version": POLICY_SCHEMA_VERSION, "normalizer_version": NORMALIZER_VERSION,
        "allowed_tools": ["apply_patch"], "edit_paths": ["src/allowed.py"], "checks": []})
    (supervision / "policy.json").write_text(json.dumps(policy), encoding="utf-8")
    manifest.update({"diagnostic_policy_id": policy_id, "diagnostic_policy_path": "supervision/policy.json"})
    session = sessions / "worker-native.jsonl"
    session.write_text("\n".join(json.dumps(item) for item in [
        {"type": "response_item", "payload": {"type": "function_call", "call_id": "patch", "name": "apply_patch", "arguments": json.dumps({"patch": "*** Begin Patch\n*** Add File: private.txt\n+x\n*** End Patch"})}},
        {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "patch", "output": "Exit code: 0"}},
    ]) + "\n")
    event = ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)[0]
    assert event["operation_class"] == "edit" and event["scope_status"] == "outside_ticket"
    assert "private.txt" not in json.dumps(event)


def test_v2_policy_marks_undeclared_agent_call_outside_ticket(tmp_path):
    root, manifest, supervision = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    policy_id, policy = freeze_policy({"schema_version": POLICY_SCHEMA_VERSION, "normalizer_version": NORMALIZER_VERSION,
        "allowed_tools": ["shell_command"], "edit_paths": [], "checks": []})
    (supervision / "policy.json").write_text(json.dumps(policy), encoding="utf-8")
    manifest.update({"diagnostic_policy_id": policy_id, "diagnostic_policy_path": "supervision/policy.json"})
    session = sessions / "worker-native.jsonl"
    session.write_text("\n".join(json.dumps(item) for item in [
        {"type": "response_item", "payload": {"type": "function_call", "call_id": "agent", "name": "multi_agent_v1", "arguments": json.dumps({"secret": "not emitted"})}},
        {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "agent", "output": "Exit code: 0"}},
    ]) + "\n")
    event = ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)[0]
    assert event["operation_class"] == "agent_manage" and event["scope_status"] == "outside_ticket"
    assert "not emitted" not in json.dumps(event)


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


def test_initial_checkpoint_waits_for_worker_transcript(tmp_path, monkeypatch):
    root, manifest, supervision = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    session = sessions / "worker-native.jsonl"
    calls = {"count": 0}

    def find_later(worker_id, sessions_root):
        calls["count"] += 1
        if calls["count"] == 2:
            session.write_text('{"type":"thread.started"}\n', encoding="utf-8")
        return session if session.exists() else None

    monkeypatch.setattr(native_session_events, "_find_session", find_later)
    monkeypatch.setattr(native_session_events.time, "sleep", lambda _: None)
    cursor = native_session_events.initialize_session_cursor(
        manifest=manifest, root=root, sessions_root=sessions, discovery_timeout_seconds=1
    )

    assert cursor == supervision / "native_session_cursor.json"
    assert calls["count"] == 2


def test_one_tail_batch_gets_strictly_increasing_sequences(tmp_path):
    root, manifest, _ = setup(tmp_path); sessions = tmp_path / "sessions"; sessions.mkdir()
    session = sessions / "worker-native.jsonl"
    session.write_text(
        "\n".join(json.dumps({"type": "response_item", "payload": {"type": "custom_tool_call_output", "output": f"Exit code: {code}"}}) for code in (0, 1)) + "\n"
    )
    events = ingest_worker_session(manifest=manifest, root=root, sessions_root=sessions)
    assert [event["sequence"] for event in events] == [1, 2]
    assert validate_events(events, assigned_root=root).ok
