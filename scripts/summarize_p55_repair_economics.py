"""Render P55 repair-prepass economics as line-item token/cost deltas."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_WAVE7 = Path(
    "benchmarks/document_library/tsa23_tsr/"
    "p55_wave7_dual_model_typed_fact_ensemble_comparison.json"
)
DEFAULT_WAVE8 = Path(
    "benchmarks/document_library/tsa23_tsr/"
    "p55_wave8_disagreement_verification_qwen36_summary.json"
)
DEFAULT_REPAIR = Path(
    "benchmarks/document_library/tsa23_tsr/"
    "p55_wave10_quote_repair_prepass_summary.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "benchmarks/document_library/tsa23_tsr/"
    "p55_wave10_quote_repair_economics.json"
)
DEFAULT_OUTPUT_MD = Path("planning/phase55_wave10_quote_repair_economics.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize P55 quote-repair economics.")
    parser.add_argument("--wave7", type=Path, default=DEFAULT_WAVE7)
    parser.add_argument("--wave8", type=Path, default=DEFAULT_WAVE8)
    parser.add_argument("--repair", type=Path, default=DEFAULT_REPAIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    wave7 = load_json(args.wave7)
    wave8 = load_json(args.wave8)
    repair = load_json(args.repair)
    report = build_report(wave7, wave8, repair)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


def build_report(
    wave7: dict[str, Any],
    wave8: dict[str, Any],
    repair: dict[str, Any],
) -> dict[str, Any]:
    baseline_rows = [
        node_row(
            lane="baseline_two_pass",
            node="wave7_candidate_generation",
            owner="local_ollama",
            model=", ".join(wave7.get("models", [])),
            totals=wave7["totals"],
            quality={
                "candidate_count": wave7["totals"].get("candidate_count", 0),
                "fields": wave7["totals"].get("field_count", 0),
                "quote_over_limit_fields": wave7["totals"].get("quote_over_limit_fields", 0),
                "invalid_chunk_id_fields": wave7["totals"].get("invalid_chunk_id_fields", 0),
                "needs_supervisor_fields": 0,
            },
        ),
        node_row(
            lane="baseline_two_pass",
            node="wave8_disagreement_verification",
            owner="local_ollama",
            model=wave8.get("verifier_model", ""),
            totals=wave8["totals"],
            quality={
                "resolved_fields": wave8["totals"].get("resolved_fields", 0),
                "quote_over_limit_fields": wave8["totals"].get("quote_over_limit_fields", 0),
                "invalid_chunk_id_fields": wave8["totals"].get("invalid_chunk_id_fields", 0),
                "needs_supervisor_fields": wave8["totals"].get("needs_supervisor_fields", 0),
            },
        ),
        supervisor_placeholder("baseline_two_pass", wave8["totals"].get("needs_supervisor_fields", 0)),
    ]
    mutated_rows = [
        node_row(
            lane="repair_prepass_trial",
            node="wave7_candidate_generation_reused",
            owner="local_ollama",
            model=", ".join(wave7.get("models", [])),
            totals=wave7["totals"],
            quality={
                "candidate_count": wave7["totals"].get("candidate_count", 0),
                "fields": wave7["totals"].get("field_count", 0),
                "quote_over_limit_fields": wave7["totals"].get("quote_over_limit_fields", 0),
                "invalid_chunk_id_fields": wave7["totals"].get("invalid_chunk_id_fields", 0),
                "needs_supervisor_fields": 0,
            },
        ),
        node_row(
            lane="repair_prepass_trial",
            node="wave10_quote_repair_prepass",
            owner="local_ollama",
            model=repair.get("repair_model", ""),
            totals=repair["totals"],
            quality={
                "target_fields": repair.get("expected_field_count", 0),
                "repaired_or_unchanged_fields": repair["totals"].get("repaired_or_unchanged_fields", 0),
                "quote_over_limit_fields": repair["totals"].get("quote_over_limit_fields", 0),
                "invalid_chunk_id_fields": repair["totals"].get("invalid_chunk_id_fields", 0),
                "needs_supervisor_fields": repair["totals"].get("needs_supervisor_fields", 0),
                "needs_verifier_fields": repair["totals"].get("needs_verifier_fields", 0),
            },
        ),
        {
            "lane": "repair_prepass_trial",
            "node": "post_repair_verifier",
            "owner": "not_run",
            "model": "not_run",
            "worker_input_tokens": 0,
            "worker_output_tokens": 0,
            "worker_cash_cost_usd": 0.0,
            "quality": {
                "status": "not_run",
                "note": "Run required before claiming full three-pass workflow economics.",
            },
        },
        supervisor_placeholder(
            "repair_prepass_trial",
            repair["totals"].get("needs_supervisor_fields", 0),
        ),
    ]
    baseline = aggregate_rows(baseline_rows)
    mutated = aggregate_rows(mutated_rows)
    return {
        "summary_id": "p55_wave10_quote_repair_economics",
        "generated_utc": now_utc(),
        "phase": "P55",
        "baseline_gate_result": wave8.get("gate_result", ""),
        "repair_gate_result": repair.get("gate_result", ""),
        "line_items": baseline_rows + mutated_rows,
        "totals": {
            "baseline_two_pass": baseline,
            "repair_prepass_trial": mutated,
            "delta_repair_minus_baseline": {
                "worker_input_tokens": mutated["worker_input_tokens"] - baseline["worker_input_tokens"],
                "worker_output_tokens": mutated["worker_output_tokens"] - baseline["worker_output_tokens"],
                "worker_cash_cost_usd": 0.0,
            },
        },
        "interpretation": interpretation(wave8, repair),
    }


def node_row(
    *,
    lane: str,
    node: str,
    owner: str,
    model: str,
    totals: dict[str, Any],
    quality: dict[str, Any],
) -> dict[str, Any]:
    return {
        "lane": lane,
        "node": node,
        "owner": owner,
        "model": model,
        "worker_input_tokens": int(totals.get("worker_input_tokens", 0)),
        "worker_output_tokens": int(totals.get("worker_output_tokens", 0)),
        "worker_cash_cost_usd": float(totals.get("worker_cash_cost_usd", 0.0)),
        "quality": quality,
    }


def supervisor_placeholder(lane: str, fields: Any) -> dict[str, Any]:
    return {
        "lane": lane,
        "node": "paid_supervisor_audit",
        "owner": "paid_supervisor",
        "model": "codex",
        "worker_input_tokens": 0,
        "worker_output_tokens": 0,
        "worker_cash_cost_usd": 0.0,
        "quality": {
            "needs_supervisor_fields": int(fields or 0),
            "token_cost_status": "not_measured_in_this_worker_trial",
            "required_measurement": "wrap actual supervisor audit with supervisor-token checkpoints",
        },
    }


def aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "worker_input_tokens": sum(int(row["worker_input_tokens"]) for row in rows),
        "worker_output_tokens": sum(int(row["worker_output_tokens"]) for row in rows),
        "worker_cash_cost_usd": 0.0,
    }


def interpretation(wave8: dict[str, Any], repair: dict[str, Any]) -> str:
    baseline_supervisor = wave8["totals"].get("needs_supervisor_fields", 0)
    repair_supervisor = repair["totals"].get("needs_supervisor_fields", 0)
    if repair.get("gate_result") != "wave10-ready-for-post-repair-verifier":
        return "Repair prepass is not ready for post-repair verification; inspect gate result before scaling."
    if repair_supervisor > baseline_supervisor:
        return "Repair prepass increased supervisor-escalated fields and should not scale unchanged."
    return (
        "Repair prepass is eligible for a post-repair verifier trial. Full economics "
        "cannot be claimed until the post-repair verifier and supervisor audit spans are measured."
    )


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 55 Wave 10 Quote Repair Economics",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- baseline_gate_result: `{report['baseline_gate_result']}`",
        f"- repair_gate_result: `{report['repair_gate_result']}`",
        "",
        "## Line Items",
        "",
        "| Lane | Node | Owner | Model | Worker Input | Worker Output | Worker Cost | Quality |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in report["line_items"]:
        lines.append(
            "| {lane} | `{node}` | `{owner}` | `{model}` | {wi} | {wo} | ${cost:.6f} | `{quality}` |".format(
                lane=row["lane"],
                node=row["node"],
                owner=row["owner"],
                model=row["model"],
                wi=row["worker_input_tokens"],
                wo=row["worker_output_tokens"],
                cost=row["worker_cash_cost_usd"],
                quality=json.dumps(row["quality"], sort_keys=True),
            )
        )
    lines.extend(["", "## Totals", ""])
    for lane, totals in report["totals"].items():
        lines.append(f"### {lane}")
        lines.append("")
        for key, value in totals.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")
    lines.extend(["## Interpretation", "", report["interpretation"], ""])
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
