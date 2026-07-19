"""Offline scoring of sanitized supervision-policy replays.

This module deliberately operates on immutable snapshots only.  It has no
clock, filesystem, provider, session, or daemon dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable


@dataclass(frozen=True)
class SanitizedEventSnapshot:
    sequence: int
    timestamp: datetime
    kind: str
    review_required: bool = True
    packet_valid: bool = True
    packet_id: str | None = None

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")


@dataclass(frozen=True)
class ReplayPolicy:
    max_events: int = 12
    max_pending_age: timedelta = timedelta(seconds=30)

    def __post_init__(self) -> None:
        if self.max_events < 1:
            raise ValueError("max_events must be positive")
        if self.max_pending_age < timedelta(0):
            raise ValueError("policy durations must be non-negative")


@dataclass(frozen=True)
class ReplaySummary:
    review_count: int
    flush_latency_seconds: tuple[float, ...]
    duplicate_risk: float
    packet_validity_friendly: bool
    valid_packet_count: int
    packet_count: int
    flush_count: int


def replay_policy(
    snapshots: Iterable[SanitizedEventSnapshot],
    policy: ReplayPolicy,
    *,
    replay_at: datetime | None = None,
) -> ReplaySummary:
    """Replay snapshots in sequence order and return deterministic metrics.

    A review is emitted at terminal/stage events, at the event-count threshold,
    or after quiet/age thresholds.  Duplicate risk is the fraction of packet
    occurrences whose packet id repeats; missing ids do not create duplicates.
    """
    events = tuple(sorted(snapshots, key=lambda item: item.sequence))
    if replay_at is None:
        replay_at = events[-1].timestamp if events else datetime(1970, 1, 1, tzinfo=timezone.utc)
    if replay_at.tzinfo is None:
        raise ValueError("replay_at must be timezone-aware")
    pending: list[SanitizedEventSnapshot] = []
    latencies: list[float] = []
    flush_count = 0
    for event in events:
        pending.append(event)
        age = replay_at - pending[0].timestamp
        should_flush = (
            event.kind in {"terminal", "stage_transition"}
            or len(pending) >= policy.max_events
            or age >= policy.max_pending_age
        )
        if should_flush:
            latencies.append(max(0.0, (replay_at - pending[0].timestamp).total_seconds()))
            flush_count += 1
            pending.clear()
    packet_ids = [event.packet_id for event in events if event.packet_id is not None]
    repeated = len(packet_ids) - len(set(packet_ids))
    duplicate_risk = repeated / len(packet_ids) if packet_ids else 0.0
    valid = sum(event.packet_valid for event in events)
    packet_count = len(events)
    return ReplaySummary(
        # A review is an emitted bundle, not an input event annotation.
        review_count=flush_count,
        flush_latency_seconds=tuple(latencies),
        duplicate_risk=duplicate_risk,
        packet_validity_friendly=valid == packet_count,
        valid_packet_count=valid,
        packet_count=packet_count,
        flush_count=flush_count,
    )
