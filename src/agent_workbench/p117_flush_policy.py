"""Pure, deterministic selection of one pending supervision event bundle."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


MAX_EVENTS = 12
MAX_BYTES = 12 * 1024
MAX_PENDING_AGE = timedelta(seconds=30)
FAILURE_GRACE = timedelta(seconds=10)
QUIET_INTERVAL = timedelta(seconds=5)


@dataclass(frozen=True)
class FlushDecision:
    """The one contiguous, unacknowledged range selected by the policy."""

    flush: bool
    reason: str
    start_sequence: int | None = None
    end_sequence: int | None = None
    events: tuple[Mapping[str, Any], ...] = ()
    payload_bytes: int = 0


def choose_flush(
    events: Sequence[Mapping[str, Any]],
    *,
    acknowledged_sequence: int = 0,
    now: datetime,
    lease: Mapping[str, Any] | Any | None = None,
    run_id: str | None = None,
    expected_root: Path | str | None = None,
) -> FlushDecision:
    """Choose at most one pending bundle; no I/O or clock reads occur here.

    ``events`` must already be validated and ordered.  ``lease`` may be a
    mapping or an existing RunLease-like object.  A root mismatch is always a
    fail-closed decision, including when there are no pending events.
    """
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if acknowledged_sequence < 0:
        raise ValueError("acknowledged_sequence must be non-negative")
    if expected_root is not None and lease is not None:
        actual = _value(lease, "root")
        if actual is None or Path(actual).resolve() != Path(expected_root).resolve():
            return FlushDecision(False, "root_mismatch")
    if lease is not None and run_id is not None and _value(lease, "run_id") != run_id:
        return FlushDecision(False, "lease_run_mismatch")
    if lease is not None and (_value(lease, "closed") or _value(lease, "armed") is False):
        return FlushDecision(False, "lease_inactive")

    pending = tuple(event for event in events if int(event["sequence"]) > acknowledged_sequence)
    if not pending:
        return FlushDecision(False, "no_pending_events")
    first = pending[0]
    first_time = _timestamp(first)
    terminal = any(event.get("kind") == "terminal" for event in pending)
    stage_transition = any(event.get("kind") == "stage_transition" for event in pending)
    failure = any(event.get("kind") == "tool_failed" or event.get("outcome") == "failed" for event in pending)
    completion_or_stage = any(
        event.get("kind") in {"tool_completed", "stage_transition"} or event.get("outcome") in {"succeeded", "terminal"}
        for event in pending
    )
    if terminal:
        reason = "terminal"
    elif failure and not completion_or_stage and now < first_time + FAILURE_GRACE:
        return FlushDecision(False, "failure_grace")
    elif stage_transition:
        reason = "stage_transition"
    elif failure and completion_or_stage:
        reason = "failure_completed"
    elif failure:
        reason = "failure_grace_expired"
    elif len(pending) >= MAX_EVENTS:
        reason = "event_count"
    elif _bundle_size(pending) >= MAX_BYTES:
        reason = "byte_size"
    elif now >= first_time + MAX_PENDING_AGE:
        reason = "pending_age"
    elif _quiet(pending, now) and not _has_open_lifecycle(pending):
        reason = "quiet"
    else:
        return FlushDecision(False, "threshold_not_reached")

    selected = _fit_bundle(pending)
    return FlushDecision(True, reason, int(selected[0]["sequence"]), int(selected[-1]["sequence"]), selected, _bundle_size(selected))


def _value(value: Any, name: str) -> Any:
    return value.get(name) if isinstance(value, Mapping) else getattr(value, name, None)


def _timestamp(event: Mapping[str, Any]) -> datetime:
    value = datetime.fromisoformat(str(event["timestamp"]).replace("Z", "+00:00"))
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _bundle_size(events: Sequence[Mapping[str, Any]]) -> int:
    return len(json.dumps(list(events), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode())


def _fit_bundle(events: tuple[Mapping[str, Any], ...]) -> tuple[Mapping[str, Any], ...]:
    selected: list[Mapping[str, Any]] = []
    for event in events[:MAX_EVENTS]:
        candidate = tuple(selected + [event])
        if selected and _bundle_size(candidate) > MAX_BYTES:
            break
        selected.append(event)
    return tuple(selected)


def _quiet(events: Sequence[Mapping[str, Any]], now: datetime) -> bool:
    return now - _timestamp(events[-1]) >= QUIET_INTERVAL


def _has_open_lifecycle(events: Sequence[Mapping[str, Any]]) -> bool:
    return bool(events) and events[-1].get("kind") in {"tool_started", "tool_failed"}
