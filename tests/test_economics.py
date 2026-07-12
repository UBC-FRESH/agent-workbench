"""Tests for src/agent_workbench/economics.py (P99)."""

from __future__ import annotations


from agent_workbench.economics import (
    IndexedCostReport,
    IndexedCostStage,
    compute_indexed_cost,
    render_economics_markdown,
    validate_economics_report,
)


# ---------------------------------------------------------------------------
# Minimal fixtures
# ---------------------------------------------------------------------------

_MINIMAL_ACCOUNTING = {
    "pilot_id": "test-pilot-1",
    "token_accounting": {
        "direct_supervisor_input_tokens": 1000,
        "direct_supervisor_output_tokens": 500,
        "delegated_supervisor_input_tokens": 0,
        "delegated_supervisor_output_tokens": 0,
        "verification_supervisor_input_tokens": 0,
        "verification_supervisor_output_tokens": 0,
        "cleanup_supervisor_input_tokens": 0,
        "cleanup_supervisor_output_tokens": 0,
        "retry_supervisor_input_tokens": 0,
        "retry_supervisor_output_tokens": 0,
        "supervisor_input_price_per_1m_usd": 3.0,
        "supervisor_output_price_per_1m_usd": 15.0,
    },
}

_MINIMAL_TOKEN_RECORD = {
    "record_id": "test-token-1",
    "usage": {
        "supervisor_input_tokens": 200,
        "supervisor_output_tokens": 100,
    },
    "prices": {
        "supervisor_input_price_per_1m_usd": 3.0,
        "supervisor_output_price_per_1m_usd": 15.0,
    },
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_compute_indexed_cost_basic() -> None:
    """compute_indexed_cost with minimal records returns tokens-per-record > 0."""
    record = compute_indexed_cost(
        accounting_records=[_MINIMAL_ACCOUNTING],
        token_records=[_MINIMAL_TOKEN_RECORD],
        promoted_record_count=10,
        corpus_id="test-corpus",
    )
    assert record.corpus_id == "test-corpus"
    assert record.promoted_record_count == 10
    tokens_per_record = record.stage_token_costs[IndexedCostStage.total]
    assert tokens_per_record > 0, "tokens-per-record should be > 0 with non-zero input"
    assert record.price_assumptions["total_cost_usd"] > 0


def test_compute_indexed_cost_zero_records() -> None:
    """compute_indexed_cost with promoted_record_count=0 must not raise ZeroDivisionError."""
    record = compute_indexed_cost(
        accounting_records=[_MINIMAL_ACCOUNTING],
        token_records=[],
        promoted_record_count=0,
        corpus_id="empty-corpus",
    )
    assert record.promoted_record_count == 0
    assert record.stage_token_costs[IndexedCostStage.total] == 0.0
    assert "0" in record.notes or "zero" in record.notes.lower()


def test_render_economics_markdown_contains_corpus_id() -> None:
    """render_economics_markdown output contains the corpus_id."""
    record = compute_indexed_cost(
        accounting_records=[_MINIMAL_ACCOUNTING],
        token_records=[],
        promoted_record_count=5,
        corpus_id="my-unique-corpus",
    )
    report = IndexedCostReport(corpora=[record], aggregate={})
    md = render_economics_markdown(report)
    assert "my-unique-corpus" in md
    assert "PUBLIC SAFETY NOTE" in md


def test_validate_economics_report_missing_field() -> None:
    """validate_economics_report returns a non-empty error list for missing 'corpora'."""
    errors = validate_economics_report({"aggregate": {}})
    assert len(errors) > 0
    assert any("corpora" in e for e in errors)
