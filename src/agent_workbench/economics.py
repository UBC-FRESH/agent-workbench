"""Indexed-cost metrics and economics dashboard for Agent Workbench."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IndexedCostStage(str, Enum):
    extraction = "extraction"
    repair_prepass = "repair_prepass"
    audit = "audit"
    index_assembly = "index_assembly"
    total = "total"


@dataclass
class IndexedCostRecord:
    corpus_id: str
    promoted_record_count: int
    stage_token_costs: dict[
        str, float
    ]  # paid supervisor tokens per promoted record per stage
    price_assumptions: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class IndexedCostReport:
    corpora: list[IndexedCostRecord]
    aggregate: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SUPERVISOR_INPUT_FIELDS = (
    "direct_supervisor_input_tokens",
    "delegated_supervisor_input_tokens",
    "verification_supervisor_input_tokens",
    "cleanup_supervisor_input_tokens",
    "retry_supervisor_input_tokens",
)

_SUPERVISOR_OUTPUT_FIELDS = (
    "direct_supervisor_output_tokens",
    "delegated_supervisor_output_tokens",
    "verification_supervisor_output_tokens",
    "cleanup_supervisor_output_tokens",
    "retry_supervisor_output_tokens",
)

_DEFAULT_PRICE_ASSUMPTIONS = {
    "supervisor_input_price_per_1m_usd": 3.0,
    "supervisor_output_price_per_1m_usd": 15.0,
}


def _extract_supervisor_tokens_from_accounting(
    records: list[dict[str, Any]],
) -> dict[str, float]:
    """Return total paid supervisor input/output tokens across all accounting records."""
    totals: dict[str, float] = {"input": 0.0, "output": 0.0}
    for rec in records:
        ta = rec.get("token_accounting", {}) if isinstance(rec, dict) else {}
        for f in _SUPERVISOR_INPUT_FIELDS:
            totals["input"] += float(ta.get(f, 0) or 0)
        for f in _SUPERVISOR_OUTPUT_FIELDS:
            totals["output"] += float(ta.get(f, 0) or 0)
    return totals


def _extract_supervisor_tokens_from_token_records(
    records: list[dict[str, Any]],
) -> dict[str, float]:
    """Return total paid supervisor input/output tokens across all token records."""
    totals: dict[str, float] = {"input": 0.0, "output": 0.0}
    for rec in records:
        usage = rec.get("usage", {}) if isinstance(rec, dict) else {}
        totals["input"] += float(usage.get("supervisor_input_tokens", 0) or 0)
        totals["output"] += float(usage.get("supervisor_output_tokens", 0) or 0)
    return totals


def _price_assumptions_from_records(
    accounting_records: list[dict[str, Any]],
    token_records: list[dict[str, Any]],
) -> dict[str, float]:
    """Pull price assumptions from the first record that has them, or use defaults."""
    for rec in (*token_records, *accounting_records):
        prices = rec.get("prices") or rec.get("token_accounting") or {}
        if isinstance(prices, dict):
            inp = float(prices.get("supervisor_input_price_per_1m_usd", 0) or 0)
            out = float(prices.get("supervisor_output_price_per_1m_usd", 0) or 0)
            if inp > 0 or out > 0:
                return {
                    "supervisor_input_price_per_1m_usd": inp
                    or _DEFAULT_PRICE_ASSUMPTIONS["supervisor_input_price_per_1m_usd"],
                    "supervisor_output_price_per_1m_usd": out
                    or _DEFAULT_PRICE_ASSUMPTIONS["supervisor_output_price_per_1m_usd"],
                }
    return dict(_DEFAULT_PRICE_ASSUMPTIONS)


def compute_indexed_cost(
    accounting_records: list[dict[str, Any]],
    token_records: list[dict[str, Any]],
    promoted_record_count: int,
    corpus_id: str = "corpus",
) -> IndexedCostRecord:
    """Compute per-promoted-record indexed cost from accounting and token records.

    Tokens are summed across all supplied records and attributed to the ``total``
    stage.  No stage-level breakdown is available without structured stage
    annotations in the source records, so the other stage buckets default to
    ``None`` (represented as 0.0 here) unless the records carry explicit stage
    keys.

    When ``promoted_record_count`` is 0 the per-record ratios are set to ``None``
    and a note is added instead of dividing by zero.
    """
    acc_tokens = _extract_supervisor_tokens_from_accounting(accounting_records)
    tok_tokens = _extract_supervisor_tokens_from_token_records(token_records)

    total_input = acc_tokens["input"] + tok_tokens["input"]
    total_output = acc_tokens["output"] + tok_tokens["output"]
    total_tokens = total_input + total_output

    price_assumptions = _price_assumptions_from_records(
        accounting_records, token_records
    )
    inp_price = price_assumptions.get("supervisor_input_price_per_1m_usd", 3.0)
    out_price = price_assumptions.get("supervisor_output_price_per_1m_usd", 15.0)

    total_cost_usd = (total_input * inp_price + total_output * out_price) / 1_000_000.0

    if promoted_record_count > 0:
        tokens_per_record = total_tokens / promoted_record_count
        cost_per_record_usd = total_cost_usd / promoted_record_count
        notes = ""
    else:
        tokens_per_record = 0.0
        cost_per_record_usd = 0.0
        notes = "promoted_record_count is 0; per-record ratios are undefined (set to 0)"

    stage_token_costs: dict[str, float] = {
        IndexedCostStage.extraction: 0.0,
        IndexedCostStage.repair_prepass: 0.0,
        IndexedCostStage.audit: 0.0,
        IndexedCostStage.index_assembly: 0.0,
        IndexedCostStage.total: tokens_per_record,
    }

    price_assumptions["total_supervisor_input_tokens"] = total_input
    price_assumptions["total_supervisor_output_tokens"] = total_output
    price_assumptions["total_cost_usd"] = total_cost_usd
    price_assumptions["cost_per_record_usd"] = cost_per_record_usd

    return IndexedCostRecord(
        corpus_id=corpus_id,
        promoted_record_count=promoted_record_count,
        stage_token_costs=stage_token_costs,
        price_assumptions=price_assumptions,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_economics_markdown(report: IndexedCostReport) -> str:
    """Render an IndexedCostReport as a Markdown dashboard table."""
    lines: list[str] = [
        "<!-- PUBLIC SAFETY NOTE: This document contains only sanitized token counts",
        "and cost estimates. No raw prompts, traces, provider URLs, or credentials",
        "are included. -->",
        "",
        "# Economics Dashboard — Indexed-Cost Report",
        "",
        "| Corpus | Promoted Records | Total Tokens | Total Cost USD | $/Record | Tokens/Record (total stage) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    def _row(rec: IndexedCostRecord) -> str:
        total_tokens = float(
            rec.price_assumptions.get("total_supervisor_input_tokens", 0)
        ) + float(rec.price_assumptions.get("total_supervisor_output_tokens", 0))
        total_cost = float(rec.price_assumptions.get("total_cost_usd", 0.0))
        cost_per_rec = float(rec.price_assumptions.get("cost_per_record_usd", 0.0))
        tokens_per_rec = rec.stage_token_costs.get(IndexedCostStage.total, 0.0)
        note = f" _{rec.notes}_" if rec.notes else ""
        return (
            f"| {rec.corpus_id}{note} "
            f"| {rec.promoted_record_count:,} "
            f"| {total_tokens:,.0f} "
            f"| ${total_cost:.4f} "
            f"| ${cost_per_rec:.6f} "
            f"| {tokens_per_rec:.2f} |"
        )

    for rec in report.corpora:
        lines.append(_row(rec))

    if report.aggregate:
        agg_tokens = float(report.aggregate.get("total_tokens", 0))
        agg_cost = float(report.aggregate.get("total_cost_usd", 0.0))
        agg_count = int(report.aggregate.get("promoted_record_count", 0))
        agg_cost_per = agg_cost / agg_count if agg_count > 0 else 0.0
        agg_tok_per = agg_tokens / agg_count if agg_count > 0 else 0.0
        lines.append(
            f"| **AGGREGATE** | {agg_count:,} | {agg_tokens:,.0f} "
            f"| ${agg_cost:.4f} | ${agg_cost_per:.6f} | {agg_tok_per:.2f} |"
        )

    lines.append("")
    lines.append(
        "_Stage-level breakdown requires structured stage annotations in source records._"
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_REPORT_REQUIRED_FIELDS = ("corpora",)
_RECORD_REQUIRED_FIELDS = ("corpus_id", "promoted_record_count", "stage_token_costs")


def validate_economics_report(report_dict: dict[str, Any]) -> list[str]:
    """Validate an IndexedCostReport represented as a plain dict.

    Returns a list of error strings (empty list means valid).
    """
    errors: list[str] = []
    if not isinstance(report_dict, dict):
        return ["report must be a JSON object"]

    for f in _REPORT_REQUIRED_FIELDS:
        if f not in report_dict:
            errors.append(f"missing required field: {f}")

    corpora = report_dict.get("corpora")
    if not isinstance(corpora, list):
        errors.append("corpora must be a list")
    else:
        for i, rec in enumerate(corpora):
            if not isinstance(rec, dict):
                errors.append(f"corpora[{i}] must be an object")
                continue
            for f in _RECORD_REQUIRED_FIELDS:
                if f not in rec:
                    errors.append(f"corpora[{i}] missing required field: {f}")
            count = rec.get("promoted_record_count")
            if count is not None and (not isinstance(count, int) or count < 0):
                errors.append(
                    f"corpora[{i}].promoted_record_count must be a nonnegative integer"
                )

    return errors
