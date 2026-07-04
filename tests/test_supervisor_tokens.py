from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_workbench.supervisor_tokens import (
    latest_snapshot,
    span_record_from_checkpoints,
    usage_delta,
    write_checkpoint,
)
from agent_workbench.tokens import calculate_token_costs, validate_token_record


def test_latest_snapshot_reads_codex_token_count_events(tmp_path: Path) -> None:
    session = tmp_path / "rollout-2026-07-04T00-00-00-test.jsonl"
    write_session(
        session,
        [
            usage(1000, 300, 50, 10, 1050),
            usage(2500, 900, 125, 40, 2625),
        ],
    )

    snapshot = latest_snapshot(session_jsonl=session)

    assert snapshot.source_session_file == session.name
    assert snapshot.usage == usage(2500, 900, 125, 40, 2625)
    assert snapshot.last_usage == usage(100, 50, 5, 2, 105)


def test_checkpoint_span_record_uses_fresh_cached_and_reasoning_costs(
    tmp_path: Path,
) -> None:
    session = tmp_path / "rollout-2026-07-04T00-00-00-test.jsonl"
    write_session(session, [usage(1000, 400, 100, 20, 1100)])
    start = write_checkpoint(
        span_id="supervisor-audit",
        event="start",
        output=tmp_path / "start.json",
        session_jsonl=session,
    )
    assert start["source"]["source_session_path_recorded"] is False

    write_session(session, [usage(2500, 900, 250, 80, 2750)])
    end_path = tmp_path / "end.json"
    write_checkpoint(
        span_id="supervisor-audit",
        event="end",
        output=end_path,
        session_jsonl=session,
    )

    output = tmp_path / "supervisor-audit.tokens.json"
    record = span_record_from_checkpoints(
        start_path=tmp_path / "start.json",
        end_path=end_path,
        output=output,
        project="agent-delegation-lab",
        phase="p1",
        task_id="appendix-a-opening-structure",
        span_kind="supervisor_audit",
    )

    assert record["usage"]["supervisor_input_tokens"] == 1000
    assert record["usage"]["supervisor_cached_input_tokens"] == 500
    assert record["usage"]["supervisor_output_tokens"] == 150
    assert record["usage"]["supervisor_reasoning_output_tokens"] == 60
    assert record["usage"]["codex_total_input_token_delta"] == 1500
    assert validate_token_record(record).ok
    costs = calculate_token_costs(record)
    expected = (1000 / 1_000_000 * 1.75) + (500 / 1_000_000 * 0.175)
    expected += (150 + 60) / 1_000_000 * 14.0
    assert costs.supervisor_cost_usd == pytest.approx(expected)


def test_usage_delta_fails_closed_on_negative_delta() -> None:
    with pytest.raises(ValueError, match="negative token delta"):
        usage_delta(
            usage(2000, 1000, 200, 20, 2200),
            usage(1000, 500, 100, 10, 1100),
        )


def write_session(path: Path, totals: list[dict[str, int]]) -> None:
    lines = []
    for index, total in enumerate(totals):
        event = {
            "timestamp": f"2026-07-04T00:00:0{index}Z",
            "type": "event_msg",
            "payload": {
                "type": "token_count",
                "info": {
                    "total_token_usage": total,
                    "last_token_usage": usage(100, 50, 5, 2, 105),
                    "model_context_window": 258400,
                },
                "rate_limits": None,
            },
        }
        lines.append(json.dumps(event))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def usage(
    input_tokens: int,
    cached_input_tokens: int,
    output_tokens: int,
    reasoning_output_tokens: int,
    total_tokens: int,
) -> dict[str, int]:
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "output_tokens": output_tokens,
        "reasoning_output_tokens": reasoning_output_tokens,
        "total_tokens": total_tokens,
    }
