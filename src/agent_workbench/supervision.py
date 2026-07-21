"""P116 contracts for sanitized, cursor-driven Worker supervision."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


SCHEMA_VERSION = "p116_supervision_v1"
EVENT_SCHEMA_VERSION_V2 = "p116_supervision_event_v2"
SUPPORTED_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION})
# A migration entry is required before a new version can be accepted.  Keeping
# this explicit makes version changes auditable instead of silently coercing
# old artifacts.
SCHEMA_MIGRATIONS: dict[str, str] = {}
EVENT_KINDS = {
    "tool_started",
    "tool_completed",
    "tool_failed",
    "stage_transition",
    "workspace_mismatch",
    "terminal",
}
OUTCOME_CLASSES = {"started", "succeeded", "failed", "denied", "terminal"}
SUPERVISOR_CLASSIFICATIONS = {
    "productive_repair",
    "material_repeat",
    "directive_deviation",
    "blocked",
    "terminal",
}
COORDINATOR_ACTIONS = {"continue", "nudge", "escalate", "terminal"}
FORBIDDEN_EVENT_KEYS = {
    "arguments",
    "command",
    "environment",
    "headers",
    "raw_output",
    "output",
    "provider_headers",
    "secret",
    "token",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_TEXT_LENGTH = 512
MAX_TOTAL_PAYLOAD_BYTES = 16 * 1024


@dataclass(frozen=True)
class SupervisionValidation:
    ok: bool
    errors: list[str]


@dataclass(frozen=True)
class RunLease:
    """The explicit authority boundary for one supervised run."""

    run_id: str
    worker_id: str
    supervisor_id: str
    root: Path
    armed: bool
    closed: bool
    expires_at: datetime

    def capture_eligible(self, *, run_id: str, now: datetime | None = None) -> bool:
        """Return whether a capture belongs to this still-live lease."""
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        return (
            run_id == self.run_id
            and self.armed
            and not self.closed
            and current < self.expires_at
        )

    def close(self) -> "RunLease":
        return RunLease(self.run_id, self.worker_id, self.supervisor_id, self.root, self.armed, True, self.expires_at)


class SupervisionJournal:
    """Small append-only state journal; unknown delivery always pauses."""

    _allowed = {
        "armed": {"capturing", "closed", "paused_reconciliation"},
        "capturing": {"capturing", "closed", "paused_reconciliation"},
        "paused_reconciliation": {"paused_reconciliation", "capturing", "closed"},
        "closed": set(),
    }

    def __init__(self, path: Path, *, root: Path, run_id: str) -> None:
        self.path = path.resolve()
        self.root = root.resolve()
        self.run_id = run_id
        try:
            self.path.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("journal path must stay within run root") from exc

    def state(self) -> str:
        if not self.path.exists():
            return "armed"
        lines = self.path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return "armed"
        for line in reversed(lines):
            record = json.loads(line)
            if "state" in record:
                return record["state"]
        return "armed"

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line]

    def append(self, kind: str, **payload: Any) -> dict[str, Any]:
        """Persist one run-scoped receipt before it can affect a restart."""
        if not isinstance(kind, str) or not kind:
            raise ValueError("journal record kind must be non-empty")
        record = {"schema_version": SCHEMA_VERSION, "run_id": self.run_id, "kind": kind, **payload}
        _reject_forbidden_payload(record, [], "journal")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        return record

    def transition(self, state: str, *, delivery_uncertain: bool = False) -> dict[str, Any]:
        target = "paused_reconciliation" if delivery_uncertain else state
        current = self.state()
        if target not in self._allowed[current]:
            raise ValueError(f"invalid journal transition: {current} -> {target}")
        record = {"schema_version": SCHEMA_VERSION, "run_id": self.run_id, "kind": "state", "from_state": current, "state": target}
        _reject_forbidden_payload(record, [], "journal")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        return record


def create_run_lease(*, run_id: str, worker_id: str, supervisor_id: str, root: Path, expires_at: datetime, armed: bool = True) -> RunLease:
    """Construct a sanitized lease; callers must explicitly provide its expiry."""
    for label, value in (("run_id", run_id), ("worker_id", worker_id), ("supervisor_id", supervisor_id)):
        if not isinstance(value, str) or not SAFE_ID.match(value):
            raise ValueError(f"{label} must be a safe identifier")
    if not root.is_absolute():
        raise ValueError("root must be absolute")
    if expires_at.tzinfo is None:
        raise ValueError("expires_at must be timezone-aware")
    return RunLease(run_id, worker_id, supervisor_id, root.resolve(), armed, False, expires_at)


def validate_schema_version(value: Any) -> SupervisionValidation:
    """Expose the version/migration gate used by every contract validator."""
    if value in SUPPORTED_SCHEMA_VERSIONS:
        return SupervisionValidation(ok=True, errors=[])
    if isinstance(value, str) and value in SCHEMA_MIGRATIONS:
        return SupervisionValidation(ok=False, errors=[
            f"schema_version {value!r} requires migration to {SCHEMA_MIGRATIONS[value]!r}"
        ])
    return SupervisionValidation(ok=False, errors=[
        f"schema_version must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)!r}"
    ])


def validate_manifest(manifest: dict[str, Any]) -> SupervisionValidation:
    """Validate a local-only run binding before any event is accepted."""
    errors: list[str] = []
    required = (
        "schema_version",
        "run_id",
        "worker_session_id",
        "supervisor_session_id",
        "assigned_root",
        "supervision_dir",
        "events_path",
        "cursor_path",
        "packets_path",
        "actions_path",
    )
    _required_strings(manifest, required, errors)
    errors.extend(f"manifest: {error}" for error in validate_schema_version(manifest.get("schema_version")).errors)
    for field in ("run_id", "worker_session_id", "supervisor_session_id"):
        value = manifest.get(field)
        if isinstance(value, str) and not SAFE_ID.match(value):
            errors.append(f"{field} must be a safe identifier")

    root_text = manifest.get("assigned_root")
    if isinstance(root_text, str):
        root = Path(root_text)
        if not root.is_absolute():
            errors.append("assigned_root must be absolute")

    supervision_text = manifest.get("supervision_dir")
    if isinstance(supervision_text, str) and not Path(supervision_text).is_absolute():
        errors.append("supervision_dir must be absolute")

    for field in ("events_path", "cursor_path", "packets_path", "actions_path"):
        value = manifest.get(field)
        if isinstance(value, str) and not _is_relative_path(value):
            errors.append(f"{field} must be a relative path within the run directory")
    _validate_total_payload(manifest, errors, "manifest")

    return SupervisionValidation(ok=not errors, errors=errors)


def validate_events(
    events: list[dict[str, Any]], *, assigned_root: Path
) -> SupervisionValidation:
    """Validate a strictly ordered, redacted event sequence."""
    errors: list[str] = []
    previous_sequence = 0
    event_ids: set[str] = set()
    for index, event in enumerate(events, 1):
        prefix = f"event {index}"
        _required_strings(
            event,
            ("schema_version", "event_id", "timestamp", "kind", "stage", "outcome"),
            errors,
            prefix=prefix,
        )
        if event.get("schema_version") not in {SCHEMA_VERSION, EVENT_SCHEMA_VERSION_V2}:
            errors.append(f"{prefix}: unsupported event schema_version")
        event_id = event.get("event_id")
        if isinstance(event_id, str):
            if event_id in event_ids:
                errors.append(f"{prefix}: duplicate event_id: {event_id}")
            event_ids.add(event_id)
        sequence = event.get("sequence")
        if not isinstance(sequence, int) or sequence < 1:
            errors.append(f"{prefix}: sequence must be a positive integer")
        elif sequence <= previous_sequence:
            errors.append(f"{prefix}: sequence must be strictly increasing")
        else:
            previous_sequence = sequence
        for field in ("event_id", "stage"):
            value = event.get(field)
            if isinstance(value, str) and not SAFE_ID.match(value):
                errors.append(f"{prefix}: {field} must be a safe identifier")
        if event.get("kind") not in EVENT_KINDS:
            errors.append(f"{prefix}: invalid kind")
        if event.get("outcome") not in OUTCOME_CLASSES:
            errors.append(f"{prefix}: invalid outcome")
        if event.get("redaction_applied") is not True:
            errors.append(f"{prefix}: redaction_applied must be true")
        if event.get("schema_version") == EVENT_SCHEMA_VERSION_V2:
            if not isinstance(event.get("policy_id"), str) or not SAFE_ID.match(event["policy_id"]):
                errors.append(f"{prefix}: v2 policy_id must be safe")
            if event.get("operation_class") not in {"inspect", "edit", "test", "agent_manage", "unknown"}:
                errors.append(f"{prefix}: v2 operation_class is invalid")
            if event.get("scope_status") not in {"within_ticket", "outside_ticket", "unclassified"}:
                errors.append(f"{prefix}: v2 scope_status is invalid")
            if "check_id" in event and (not isinstance(event["check_id"], str) or not SAFE_ID.match(event["check_id"])):
                errors.append(f"{prefix}: v2 check_id must be safe")
            if "failure_class" in event and event["failure_class"] not in {"syntax_error", "assertion_failure", "missing_file", "permission_denied", "tool_unavailable", "nonzero_exit", "unknown"}:
                errors.append(f"{prefix}: v2 failure_class is invalid")
            if "exit_code" in event and (not isinstance(event["exit_code"], int) or isinstance(event["exit_code"], bool)):
                errors.append(f"{prefix}: v2 exit_code must be an integer")
        _reject_forbidden_payload(event, errors, prefix)
        _validate_observed_path(event, assigned_root, errors, prefix)
        _validate_bounded_text(event, errors, prefix)
        for finding in find_private_values(event):
            errors.append(f"{prefix}: private-looking value detected: {finding}")
    _validate_total_payload(events, errors, "events")
    return SupervisionValidation(ok=not errors, errors=errors)


def validate_cursor(cursor: dict[str, Any], *, max_sequence: int) -> SupervisionValidation:
    errors: list[str] = []
    errors.extend(f"cursor: {error}" for error in validate_schema_version(cursor.get("schema_version")).errors)
    last_sequence = cursor.get("last_sequence")
    if not isinstance(last_sequence, int) or not 0 <= last_sequence <= max_sequence:
        errors.append("cursor: last_sequence must be within observed event range")
    _validate_total_payload(cursor, errors, "cursor")
    return SupervisionValidation(ok=not errors, errors=errors)


def validate_supervisor_packet(packet: dict[str, Any]) -> SupervisionValidation:
    errors: list[str] = []
    _required_strings(
        packet,
        ("schema_version", "run_id", "classification", "recommended_action", "evidence_summary"),
        errors,
        prefix="packet",
    )
    errors.extend(f"packet: {error}" for error in validate_schema_version(packet.get("schema_version")).errors)
    if packet.get("classification") not in SUPERVISOR_CLASSIFICATIONS:
        errors.append("packet: invalid classification")
    if packet.get("recommended_action") not in COORDINATOR_ACTIONS:
        errors.append("packet: invalid recommended_action")
    start = packet.get("event_start_sequence")
    end = packet.get("event_end_sequence")
    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
        errors.append("packet: invalid event cursor range")
    _reject_forbidden_payload(packet, errors, "packet")
    _validate_bounded_text(packet, errors, "packet")
    for finding in find_private_values(packet):
        errors.append(f"packet: private-looking value detected: {finding}")
    _validate_total_payload(packet, errors, "packet")
    return SupervisionValidation(ok=not errors, errors=errors)


def validate_coordinator_action(action: dict[str, Any]) -> SupervisionValidation:
    errors: list[str] = []
    _required_strings(
        action,
        ("schema_version", "run_id", "packet_sha256", "decision"),
        errors,
        prefix="action",
    )
    errors.extend(f"action: {error}" for error in validate_schema_version(action.get("schema_version")).errors)
    if action.get("decision") not in COORDINATOR_ACTIONS:
        errors.append("action: invalid decision")
    digest = action.get("packet_sha256")
    if isinstance(digest, str) and not SHA256.match(digest):
        errors.append("action: packet_sha256 must be a lowercase SHA-256 digest")
    _reject_forbidden_payload(action, errors, "action")
    _validate_bounded_text(action, errors, "action")
    for finding in find_private_values(action):
        errors.append(f"action: private-looking value detected: {finding}")
    _validate_total_payload(action, errors, "action")
    return SupervisionValidation(ok=not errors, errors=errors)


def _required_strings(
    value: dict[str, Any], fields: tuple[str, ...], errors: list[str], *, prefix: str = ""
) -> None:
    for field in fields:
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{prefix + ': ' if prefix else ''}{field} must be a non-empty string")


def _reject_forbidden_payload(value: Any, errors: list[str], prefix: str, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_EVENT_KEYS:
                errors.append(f"{prefix}: forbidden payload key: {path}.{key}")
            _reject_forbidden_payload(child, errors, prefix, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_payload(child, errors, prefix, f"{path}[{index}]")


def _validate_observed_path(event: dict[str, Any], root: Path, errors: list[str], prefix: str) -> None:
    path_text = event.get("observed_path")
    if path_text is None:
        return
    if not isinstance(path_text, str) or not path_text:
        errors.append(f"{prefix}: observed_path must be a non-empty relative path")
        return
    if not _is_relative_path(path_text):
        errors.append(f"{prefix}: observed_path must stay within assigned_root")
        return
    resolved = (root / path_text).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{prefix}: observed_path escapes assigned_root")


def _validate_bounded_text(value: Any, errors: list[str], prefix: str, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_bounded_text(child, errors, prefix, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_bounded_text(child, errors, prefix, f"{path}[{index}]")
    elif isinstance(value, str) and len(value) > MAX_TEXT_LENGTH:
        errors.append(f"{prefix}: text exceeds {MAX_TEXT_LENGTH} characters at {path}")


def _validate_total_payload(value: Any, errors: list[str], prefix: str) -> None:
    try:
        size = len(json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))
    except (TypeError, ValueError):
        errors.append(f"{prefix}: payload must be JSON serializable")
        return
    if size > MAX_TOTAL_PAYLOAD_BYTES:
        errors.append(f"{prefix}: total payload exceeds {MAX_TOTAL_PAYLOAD_BYTES} bytes")


def _is_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and not re.match(r"^[A-Za-z]:", value) and ".." not in path.parts
