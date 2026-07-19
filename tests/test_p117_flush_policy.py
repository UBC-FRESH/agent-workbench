from datetime import datetime, timezone, timedelta

from agent_workbench.p117_flush_policy import choose_flush


NOW = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)


def event(sequence, *, kind="tool_completed", outcome="succeeded", seconds=0, stage="build"):
    return {"sequence": sequence, "timestamp": (NOW - timedelta(seconds=seconds)).isoformat(), "kind": kind, "outcome": outcome, "stage": stage}


def test_terminal_and_stage_transition_are_immediate():
    assert choose_flush([event(1, kind="terminal", outcome="terminal")], now=NOW).reason == "terminal"
    assert choose_flush([event(1, kind="stage_transition")], now=NOW).reason == "stage_transition"


def test_failure_waits_for_grace_but_flushes_after_ten_seconds():
    pending = [event(1, kind="tool_failed", outcome="failed")]
    assert choose_flush(pending, now=NOW).reason == "failure_grace"
    assert choose_flush(pending, now=NOW + timedelta(seconds=10)).flush


def test_failure_flushes_when_completion_arrives():
    result = choose_flush([event(1, kind="tool_failed", outcome="failed"), event(2)], now=NOW)
    assert result.reason == "failure_completed"
    assert (result.start_sequence, result.end_sequence) == (1, 2)


def test_thresholds_and_ack_cursor_select_one_nonoverlapping_range():
    events = [event(i) for i in range(1, 15)]
    result = choose_flush(events, acknowledged_sequence=2, now=NOW)
    assert result.reason == "event_count"
    assert (result.start_sequence, result.end_sequence) == (3, 14)
    assert not choose_flush(events, acknowledged_sequence=12, now=NOW).flush


def test_root_mismatch_fails_closed():
    result = choose_flush([], now=NOW, expected_root="C:/assigned", lease={"root": "C:/other"})
    assert (result.flush, result.reason) == (False, "root_mismatch")
