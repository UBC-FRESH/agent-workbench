"""Local P116.4 contract for structured Supervisor delta reviews."""

from __future__ import annotations

import re
from typing import Any

from .evidence import find_private_values
from .supervision import (
    MAX_TEXT_LENGTH,
    SupervisionValidation,
    validate_manifest,
    validate_supervisor_packet,
)


CONFIDENCE_LEVELS = {"low", "medium", "high"}
CLASSIFICATION_ACTIONS = {
    "productive_repair": {"continue"},
    "material_repeat": {"nudge", "escalate"},
    "directive_deviation": {"nudge", "escalate"},
    "blocked": {"nudge", "escalate"},
    "terminal": {"terminal"},
}
NUDGE_FIELDS = ("observed_fact", "relevant_feedback", "validation_seam", "ticket_boundary")
COMMAND_STYLE_NUDGE = re.compile(
    r"(?:^|[.!?]\s+)(?:please\s+)?(?:run|execute|invoke|call|open|edit|write|delete|send|message)\b",
    re.IGNORECASE,
)
SAFE_DELTA_EVENT_FIELDS = {
    "sequence",
    "event_id",
    "timestamp",
    "kind",
    "stage",
    "outcome",
    "run_id",
    "hook_event",
    "tool_name",
    "root_match",
}
REVIEW_PACKET_FIELDS = {
    "schema_version", "run_id", "event_start_sequence", "event_end_sequence",
    "classification", "recommended_action", "confidence", "evidence_citation",
    "evidence_summary", "nudge",
}


def build_supervisor_review_request(
    delta: dict[str, Any], *, ticket_boundary: str, manifest: dict[str, Any]
) -> dict[str, Any]:
    """Render the local-only review request; it neither invokes nor messages an agent."""
    errors = _validate_delta(delta) + _validate_ticket_boundary(ticket_boundary)
    errors.extend(f"manifest: {error}" for error in validate_manifest(manifest).errors)
    if delta.get("run_id") != manifest.get("run_id"):
        errors.append("delta: run_id must match the supplied manifest")
    if errors:
        raise ValueError("invalid review request: " + "; ".join(errors))
    return {
        "ticket_boundary": ticket_boundary,
        "run_id": manifest["run_id"],
        "delta": delta,
        "instructions": [
            "Review only the supplied unacknowledged event delta.",
            "An ordinary tool error followed by repair is productive_repair, not failure.",
            "Return a structured packet with the exact cursor range and evidence citation.",
            "Use a nudge only for a material repeat, directive deviation, or real block.",
            "A nudge must state an observed fact, relevant feedback, next validation seam, and ticket boundary.",
            "Do not issue commands, expand authority, edit files, or contact the Worker.",
        ],
        "required_packet_fields": [
            "classification",
            "recommended_action",
            "confidence",
            "evidence_citation",
            "evidence_summary",
            "nudge",
        ],
    }


def validate_delta_review_packet(
    packet: dict[str, Any], *, delta: dict[str, Any], ticket_boundary: str,
    manifest: dict[str, Any],
) -> SupervisionValidation:
    """Validate a Supervisor recommendation against its one supplied review delta."""
    errors = _validate_delta(delta) + _validate_ticket_boundary(ticket_boundary)
    errors.extend(f"manifest: {error}" for error in validate_manifest(manifest).errors)
    packet_validation = validate_supervisor_packet(packet)
    errors.extend(packet_validation.errors)
    unexpected = set(packet) - REVIEW_PACKET_FIELDS
    if unexpected:
        errors.append("packet: contains unknown or extra fields")
    if packet.get("run_id") != manifest.get("run_id"):
        errors.append("packet: run_id must match the supplied manifest")
    if delta.get("run_id") != manifest.get("run_id"):
        errors.append("delta: run_id must match the supplied manifest")
    start = delta.get("cursor_start_sequence")
    end = delta.get("cursor_end_sequence")
    if not isinstance(start, int) or not isinstance(end, int):
        errors.append("packet: supplied delta has no usable cursor range")
    elif packet.get("event_start_sequence") != start + 1:
        errors.append("packet: event_start_sequence must cite the supplied delta")
    elif packet.get("event_end_sequence") != end:
        errors.append("packet: event_end_sequence must cite the supplied delta")
    if isinstance(start, int) and isinstance(end, int) and packet.get("evidence_citation") != _citation(delta):
        errors.append("packet: evidence_citation must cite the supplied delta")
    if packet.get("confidence") not in CONFIDENCE_LEVELS:
        errors.append("packet: confidence must be low, medium, or high")

    classification = packet.get("classification")
    action = packet.get("recommended_action")
    allowed_actions = CLASSIFICATION_ACTIONS.get(classification)
    if allowed_actions is not None and action not in allowed_actions:
        errors.append("packet: recommended_action does not match classification")

    nudge = packet.get("nudge")
    if action == "nudge":
        errors.extend(_validate_nudge(nudge, ticket_boundary=ticket_boundary))
    elif nudge is not None:
        errors.append("packet: nudge is only permitted with recommended_action nudge")
    return SupervisionValidation(ok=not errors, errors=errors)


def build_packet_repair_request(
    delta: dict[str, Any], *, ticket_boundary: str, manifest: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    """Render one bounded same-Supervisor repair request for a malformed packet."""
    request = build_supervisor_review_request(delta, ticket_boundary=ticket_boundary, manifest=manifest)
    safe_errors = [error for error in errors if isinstance(error, str) and error][:16]
    if not safe_errors:
        raise ValueError("packet repair requires at least one validation error")
    if any(len(error) > MAX_TEXT_LENGTH for error in safe_errors):
        raise ValueError("packet repair error exceeds bounded length")
    request["instructions"] = [
        "Your prior packet was rejected. Return a corrected JSON packet only.",
        "Keep the same supplied delta, exact cursor range, evidence citation, and ticket boundary.",
        "Do not explain, issue commands, edit files, or contact the Worker.",
    ]
    request["validation_errors"] = safe_errors
    return request


def _validate_delta(delta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    start = delta.get("cursor_start_sequence")
    end = delta.get("cursor_end_sequence")
    count = delta.get("event_count")
    events = delta.get("events")
    if not isinstance(start, int) or start < 0 or not isinstance(end, int) or end <= start:
        errors.append("delta: must contain a non-empty increasing cursor range")
    if not isinstance(count, int) or count < 1:
        errors.append("delta: event_count must be positive")
    if not isinstance(events, list) or len(events) != count:
        errors.append("delta: events must match event_count")
    elif isinstance(start, int) and isinstance(end, int):
        for index, event in enumerate(events, 1):
            if not isinstance(event, dict):
                errors.append(f"delta: event {index} must be an object")
                continue
            unexpected = set(event) - SAFE_DELTA_EVENT_FIELDS
            if unexpected:
                errors.append(f"delta: event {index} contains non-safe fields")
            sequence = event.get("sequence")
            if not isinstance(sequence, int) or not start < sequence <= end:
                errors.append(f"delta: event {index} sequence must stay within cursor range")
            for finding in find_private_values(event):
                errors.append(f"delta: event {index} private-looking value detected: {finding}")
    return errors


def _validate_ticket_boundary(ticket_boundary: str) -> list[str]:
    if not isinstance(ticket_boundary, str) or not ticket_boundary.strip():
        return ["ticket_boundary must be a non-empty string"]
    if len(ticket_boundary) > MAX_TEXT_LENGTH:
        return ["ticket_boundary exceeds bounded length"]
    return [f"ticket_boundary: private-looking value detected: {finding}" for finding in find_private_values(ticket_boundary)]


def _citation(delta: dict[str, Any]) -> str:
    return f"events:{delta['cursor_start_sequence'] + 1}-{delta['cursor_end_sequence']}"


def _validate_nudge(nudge: Any, *, ticket_boundary: str) -> list[str]:
    if not isinstance(nudge, dict):
        return ["packet: nudge must be an object"]
    errors: list[str] = []
    if set(nudge) != set(NUDGE_FIELDS):
        errors.append("packet: nudge must contain only the constructive-nudge fields")
    for field in NUDGE_FIELDS:
        value = nudge.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"packet: nudge {field} must be a non-empty string")
        elif len(value) > MAX_TEXT_LENGTH:
            errors.append(f"packet: nudge {field} exceeds bounded length")
        elif field != "ticket_boundary" and COMMAND_STYLE_NUDGE.search(value):
            errors.append(f"packet: nudge {field} must not prescribe a command")
    if nudge.get("ticket_boundary") != ticket_boundary:
        errors.append("packet: nudge must retain the supplied ticket boundary")
    for finding in find_private_values(nudge):
        errors.append(f"packet: nudge private-looking value detected: {finding}")
    return errors
