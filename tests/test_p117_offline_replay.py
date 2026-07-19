import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from agent_workbench.p117_offline_replay import ReplayPolicy, SanitizedEventSnapshot, replay_policy


def load_fixture():
    path = Path(__file__).parent / "fixtures" / "p117_offline_replay.json"
    raw = json.loads(path.read_text())
    events = tuple(
        SanitizedEventSnapshot(
            sequence=item["sequence"],
            timestamp=datetime.fromisoformat(item["timestamp"]),
            kind=item["kind"],
            packet_id=item.get("packet_id"),
            packet_valid=item.get("packet_valid", True),
        )
        for item in raw["events"]
    )
    policy = ReplayPolicy(
        max_events=raw["policy"]["max_events"],
        max_pending_age=timedelta(seconds=raw["policy"]["max_pending_age_seconds"]),
    )
    return events, policy, datetime.fromisoformat(raw["replay_at"])


def test_fixture_scores_review_latency_duplicates_and_packet_validity():
    events, policy, replay_at = load_fixture()
    result = replay_policy(events, policy, replay_at=replay_at)
    assert result.review_count == 1
    assert result.flush_count == 1
    assert result.flush_latency_seconds == (10.0,)
    assert result.duplicate_risk == pytest.approx(1 / 3)
    assert result.packet_validity_friendly is False
    assert result.valid_packet_count == 2


def test_replay_is_order_independent_and_does_not_mutate_inputs():
    events, policy, replay_at = load_fixture()
    before = events
    result = replay_policy(reversed(events), policy, replay_at=replay_at)
    assert result.review_count == 1
    assert events == before


def test_snapshot_rejects_naive_timestamps():
    with pytest.raises(ValueError, match="timezone-aware"):
        SanitizedEventSnapshot(1, datetime(2026, 7, 18), "terminal")
