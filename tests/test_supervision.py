from __future__ import annotations

from pathlib import Path

from agent_workbench.supervision import (
    SCHEMA_VERSION,
    validate_coordinator_action,
    validate_cursor,
    validate_events,
    validate_manifest,
    validate_schema_version,
    validate_supervisor_packet,
)


def manifest() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": "p116-contract-run",
        "worker_session_id": "worker-019f77d9",
        "supervisor_session_id": "supervisor-019f77db",
        "assigned_root": str(Path.cwd()),
        "events_path": "supervision/events.jsonl",
        "cursor_path": "supervision/cursor.json",
        "packets_path": "supervision/packets.jsonl",
        "actions_path": "supervision/actions.jsonl",
    }


def event(sequence: int = 1) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "sequence": sequence,
        "event_id": f"event-{sequence}",
        "timestamp": "2026-07-19T01:00:00Z",
        "kind": "tool_failed",
        "stage": "implementation",
        "outcome": "failed",
        "redaction_applied": True,
        "observed_path": "src/agent_workbench/source_audit.py",
        "error_fingerprint": "python-syntax-error",
    }


def packet() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": "p116-contract-run",
        "event_start_sequence": 1,
        "event_end_sequence": 1,
        "classification": "productive_repair",
        "recommended_action": "continue",
        "evidence_summary": "The Worker corrected a syntax error and has not repeated it.",
    }


def action() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": "p116-contract-run",
        "packet_sha256": "a" * 64,
        "decision": "continue",
    }


def test_contract_accepts_bounded_productive_repair() -> None:
    assert validate_manifest(manifest()).ok
    assert validate_events([event()], assigned_root=Path.cwd()).ok
    assert validate_cursor({"schema_version": SCHEMA_VERSION, "last_sequence": 1}, max_sequence=1).ok
    assert validate_supervisor_packet(packet()).ok
    assert validate_coordinator_action(action()).ok


def test_manifest_requires_absolute_root_and_relative_artifacts() -> None:
    value = manifest()
    value["assigned_root"] = "runtime/worktree"
    value["events_path"] = "C:/temp/events.jsonl"

    result = validate_manifest(value)

    assert not result.ok
    assert any("assigned_root" in error for error in result.errors)
    assert any("events_path" in error for error in result.errors)


def test_events_reject_reordered_sequence_and_out_of_root_path() -> None:
    first = event(2)
    second = event(1)
    second["observed_path"] = "../outside.py"

    result = validate_events([first, second], assigned_root=Path.cwd())

    assert not result.ok
    assert any("strictly increasing" in error for error in result.errors)
    assert any("assigned_root" in error for error in result.errors)


def test_schema_version_requires_explicit_migration_surface() -> None:
    assert validate_schema_version(SCHEMA_VERSION).ok
    result = validate_schema_version("p116_supervision_v0")
    assert not result.ok
    assert any("schema_version" in error for error in result.errors)


def test_representative_event_fixtures_cover_progress_repair_repeat_deviation_terminal() -> None:
    fixtures = [
        {**event(1), "kind": "tool_completed", "outcome": "succeeded"},
        {**event(2), "kind": "tool_failed", "outcome": "failed", "error_fingerprint": "syntax-error"},
        {**event(3), "kind": "tool_failed", "outcome": "failed", "error_fingerprint": "syntax-error"},
        {**event(4), "kind": "workspace_mismatch", "outcome": "denied", "observed_path": "src/ok.py"},
        {**event(5), "kind": "terminal", "outcome": "terminal"},
    ]
    result = validate_events(fixtures, assigned_root=Path.cwd())
    assert result.ok, result.errors


def test_events_reject_duplicate_ids_and_bounded_total_payload() -> None:
    duplicate = [event(1), {**event(2), "event_id": "event-1"}]
    result = validate_events(duplicate, assigned_root=Path.cwd())
    assert not result.ok
    assert any("duplicate event_id" in error for error in result.errors)

    oversized = {**event(), "details": "x" * 512}
    result = validate_events([oversized] * 40, assigned_root=Path.cwd())
    assert not result.ok
    assert any("total payload" in error for error in result.errors)


def test_events_reject_raw_tool_payload_and_private_values() -> None:
    value = event()
    value["arguments"] = "Get-Content C:/Users/example/.agent-workbench-env.txt"
    value["note"] = "token=not-for-events"

    result = validate_events([value], assigned_root=Path.cwd())

    assert not result.ok
    assert any("forbidden payload key" in error for error in result.errors)
    assert any("private-looking value" in error for error in result.errors)


def test_cursor_rejects_unobserved_event_sequence() -> None:
    result = validate_cursor({"schema_version": SCHEMA_VERSION, "last_sequence": 2}, max_sequence=1)

    assert not result.ok
    assert any("within observed event range" in error for error in result.errors)


def test_packet_and_action_require_structured_decisions() -> None:
    bad_packet = packet()
    bad_packet["classification"] = "worker_failed"
    bad_action = action()
    bad_action["packet_sha256"] = "not-a-digest"

    packet_result = validate_supervisor_packet(bad_packet)
    action_result = validate_coordinator_action(bad_action)

    assert not packet_result.ok
    assert any("classification" in error for error in packet_result.errors)
    assert not action_result.ok
    assert any("packet_sha256" in error for error in action_result.errors)
