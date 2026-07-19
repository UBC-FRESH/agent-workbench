from __future__ import annotations

from agent_workbench.supervision import SCHEMA_VERSION
from agent_workbench.supervision_review import (
    build_supervisor_review_request,
    validate_delta_review_packet,
)


BOUNDARY = "Edit only src/agent_workbench/example.py and run the declared unit test."
MANIFEST = {
    "schema_version": SCHEMA_VERSION,
    "run_id": "p116-review-run",
    "worker_session_id": "worker-session",
    "supervisor_session_id": "supervisor-session",
    "assigned_root": "C:/workspace",
    "supervision_dir": "C:/workspace/supervision",
    "events_path": "supervision/events.jsonl",
    "cursor_path": "supervision/cursor.json",
    "packets_path": "supervision/packets.jsonl",
    "actions_path": "supervision/actions.jsonl",
}


def delta() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "cursor_start_sequence": 2,
        "cursor_end_sequence": 3,
        "event_count": 1,
        "run_id": "p116-review-run",
        "events": [{"sequence": 3, "kind": "tool_failed", "stage": "validation"}],
        "signals": {"tool_failed": 1},
    }


def packet(*, classification: str = "productive_repair", action: str = "continue") -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": "p116-review-run",
        "event_start_sequence": 3,
        "event_end_sequence": 3,
        "classification": classification,
        "recommended_action": action,
        "confidence": "medium",
        "evidence_citation": "events:3-3",
        "evidence_summary": "The validation failed once after a changed-file milestone.",
    }


def test_request_preserves_normal_repair_and_advisory_boundary() -> None:
    request = build_supervisor_review_request(delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST)

    assert request["delta"] == delta()
    assert "productive_repair" in request["instructions"][1]
    assert "Do not issue commands" in request["instructions"][-1]
    assert validate_delta_review_packet(packet(), delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST).ok


def test_constructive_nudge_requires_all_evidence_and_boundary_fields() -> None:
    value = packet(classification="material_repeat", action="nudge")
    value["nudge"] = {
        "observed_fact": "The same validation fingerprint appeared in the new delta.",
        "relevant_feedback": "The tool reported the unchanged validation failure.",
        "validation_seam": "The declared unit test is the next validation seam.",
        "ticket_boundary": BOUNDARY,
    }

    assert validate_delta_review_packet(value, delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST).ok


def test_rejects_uncited_or_inappropriate_recommendations_and_freeform_nudges() -> None:
    value = packet(classification="productive_repair", action="nudge")
    value["evidence_citation"] = "events:1-2"
    value["nudge"] = "please retry"

    result = validate_delta_review_packet(value, delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST)

    assert not result.ok
    assert any("evidence_citation" in error for error in result.errors)
    assert any("does not match classification" in error for error in result.errors)
    assert any("nudge must be an object" in error for error in result.errors)


def test_rejects_empty_delta_and_nudge_boundary_expansion() -> None:
    empty = delta()
    empty["event_count"] = 0
    empty["events"] = []
    value = packet(classification="blocked", action="nudge")
    value["nudge"] = {
        "observed_fact": "The run is blocked.",
        "relevant_feedback": "The same error remains.",
        "validation_seam": "Inspect the declared test result.",
        "ticket_boundary": "Edit any repository file.",
    }

    result = validate_delta_review_packet(value, delta=empty, ticket_boundary=BOUNDARY, manifest=MANIFEST)

    assert not result.ok
    assert any("event_count" in error for error in result.errors)
    assert any("ticket boundary" in error for error in result.errors)


def test_rejects_unsanitized_delta_fields_before_a_review_request() -> None:
    unsafe = delta()
    unsafe["events"] = [{"sequence": 3, "command": "Get-Content private.txt"}]

    try:
        build_supervisor_review_request(unsafe, ticket_boundary=BOUNDARY, manifest=MANIFEST)
    except ValueError as exc:
        assert "non-safe fields" in str(exc)
    else:
        raise AssertionError("unsafe delta unexpectedly became a review request")


def test_accepts_directive_deviation_escalation_and_terminal_review() -> None:
    deviation = packet(classification="directive_deviation", action="escalate")
    terminal = packet(classification="terminal", action="terminal")

    assert validate_delta_review_packet(deviation, delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST).ok
    assert validate_delta_review_packet(terminal, delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST).ok


def test_rejects_imperative_command_style_nudge() -> None:
    value = packet(classification="blocked", action="nudge")
    value["nudge"] = {
        "observed_fact": "The declared validation remains blocked.",
        "relevant_feedback": "Run the unit test again.",
        "validation_seam": "The declared test result is the next seam.",
        "ticket_boundary": BOUNDARY,
    }

    result = validate_delta_review_packet(value, delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST)

    assert not result.ok
    assert any("must not prescribe a command" in error for error in result.errors)


def test_rejects_command_after_sentence_boundary() -> None:
    value = packet(classification="blocked", action="nudge")
    value["nudge"] = {
        "observed_fact": "The declared validation remains blocked.",
        "relevant_feedback": "The prior attempt failed. Run the unit test again.",
        "validation_seam": "The declared test result is the next seam.",
        "ticket_boundary": BOUNDARY,
    }

    result = validate_delta_review_packet(value, delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST)

    assert not result.ok
    assert any("must not prescribe a command" in error for error in result.errors)


def test_binds_packet_to_manifest_and_rejects_extra_fields() -> None:
    value = packet()
    value["unexpected"] = "not part of the contract"
    value["run_id"] = "other-run"

    result = validate_delta_review_packet(value, delta=delta(), ticket_boundary=BOUNDARY, manifest=MANIFEST)

    assert not result.ok
    assert any("unknown or extra fields" in error for error in result.errors)
    assert any("run_id must match" in error for error in result.errors)


def test_malformed_delta_is_rejected_without_raising() -> None:
    malformed = {"cursor_start_sequence": "not-a-number"}

    result = validate_delta_review_packet(packet(), delta=malformed, ticket_boundary=BOUNDARY, manifest=MANIFEST)

    assert not result.ok
    assert any("usable cursor range" in error for error in result.errors)
