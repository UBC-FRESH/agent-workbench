"""Summarize P55 Codex-vs-Copilot supervisor A/B benchmark artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent_workbench.tokens import calculate_token_costs, load_token_record


QUOTE_WORD_LIMIT = 25
QUOTE_PENALTY_SCALE = 10.0
MAX_SCORE = 100.0
PENALTY_WEIGHTS = {
    "missing_required_field": 200.0,
    "extra_field": 40.0,
    "invalid_action": 100.0,
    "value_type_mismatch": 120.0,
    "found_null_value": 120.0,
    "invalid_chunk_id": 80.0,
    "missing_chunk_id_on_found": 30.0,
    "missing_quote_on_found": 20.0,
    "needs_supervisor": 15.0,
    "low_confidence_repaired": 10.0,
    "model_provenance_mismatch": 25.0,
    "quote_excess": 1.0,
}
EXPECTED_FIELDS = (
    "aac_value",
    "base_case_harvest_forecast",
    "decision_rationale",
    "inventory_reference_year",
)
EXPECTED_TYPES = {
    "aac_value": "list",
    "base_case_harvest_forecast": "dict",
    "decision_rationale": "str",
    "inventory_reference_year": "int",
}
ALLOWED_ACTIONS = {"repaired", "unchanged", "needs_verifier", "needs_supervisor"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codex-output",
        type=Path,
        default=Path("runtime/agent_jobs/p55_ab_codex_supervisor_repair_output.json"),
    )
    parser.add_argument(
        "--copilot-output",
        type=Path,
        default=Path("runtime/agent_jobs/p55_ab_copilot_supervisor_repair_output.json"),
    )
    parser.add_argument(
        "--bridge-report",
        type=Path,
        default=Path("runtime/agent_jobs/p55_ab_copilot_supervisor_repair_bridge_report.md"),
    )
    parser.add_argument(
        "--token-dir",
        type=Path,
        default=Path("runtime/supervisor_tokens/p55_codex_vs_copilot_wave10_ab"),
    )
    parser.add_argument(
        "--field-spec",
        type=Path,
        help="Optional JSON object mapping expected field names to expected value types.",
    )
    parser.add_argument(
        "--summary-id",
        default="p55_codex_vs_copilot_supervisor_ab",
    )
    parser.add_argument(
        "--benchmark-scope",
        default=(
            "Four-field Wave 10 quote/value repair supervisor task over "
            "tsa23_2012_23ts13ra."
        ),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path(
            "benchmarks/document_library/tsa23_tsr/"
            "p55_codex_vs_copilot_supervisor_ab_summary.json"
        ),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("planning/phase55_codex_vs_copilot_supervisor_ab_results.md"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected_types = load_expected_types(args.field_spec)
    codex = summarize_lane("codex_supervisor_direct", load_json(args.codex_output), expected_types)
    copilot = summarize_lane("copilot_free_supervisor", load_json(args.copilot_output), expected_types)
    bridge = parse_bridge_report(args.bridge_report)
    attach_model_provenance(copilot, bridge)
    token_rows = load_token_rows(args.token_dir)
    report = {
        "summary_id": args.summary_id,
        "generated_utc": now_utc(),
        "phase": "P55",
        "benchmark_scope": args.benchmark_scope,
        "quote_word_limit": QUOTE_WORD_LIMIT,
        "scoring_rubric": scoring_rubric(),
        "raw_output_policy": (
            "Raw supervisor outputs remain ignored under runtime/; tracked summary "
            "stores hashes, counts, model evidence, and defect classes only."
        ),
        "lanes": [codex, copilot],
        "bridge_evidence": bridge,
        "token_line_items": token_rows,
        "totals": summarize_totals(token_rows, codex, copilot),
        "interpretation": interpret(codex, copilot, bridge, token_rows),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


def summarize_lane(
    lane_id: str,
    data: dict[str, Any],
    expected_types: dict[str, str],
) -> dict[str, Any]:
    repairs = data.get("repairs", {})
    if not isinstance(repairs, dict):
        repairs = {}
    expected_fields = tuple(expected_types)
    fields = [
        summarize_field(field, repairs.get(field), expected_types[field])
        for field in expected_fields
    ]
    action_counts = Counter(row["action"] for row in fields)
    field_scores = [score_field(row) for row in fields]
    missing_field_penalty = len(set(expected_fields) - set(repairs)) * PENALTY_WEIGHTS[
        "missing_required_field"
    ]
    extra_field_penalty = len(set(repairs) - set(expected_fields)) * PENALTY_WEIGHTS[
        "extra_field"
    ]
    total_penalty = sum(score["total_penalty"] for score in field_scores)
    total_penalty += missing_field_penalty + extra_field_penalty
    hard_penalty = sum(score["hard_penalty"] for score in field_scores)
    hard_penalty += missing_field_penalty + extra_field_penalty
    soft_penalty = sum(score["soft_penalty"] for score in field_scores)
    return {
        "lane_id": lane_id,
        "repair_model": str(data.get("repair_model", "")),
        "model_provenance": default_model_provenance(str(data.get("repair_model", ""))),
        "review_status": str(data.get("review_status", "")),
        "document_id": str(data.get("document_id", "")),
        "source_packet_id": str(data.get("source_packet_id", "")),
        "field_count": len(fields),
        "missing_fields": sorted(set(expected_fields) - set(repairs)),
        "extra_fields": sorted(set(repairs) - set(expected_fields)),
        "field_repairs": fields,
        "field_scores": field_scores,
        "rubric_score": {
            "max_score": MAX_SCORE,
            "total_penalty": round(total_penalty, 6),
            "hard_penalty": round(hard_penalty, 6),
            "soft_penalty": round(soft_penalty, 6),
            "score": round(max(MAX_SCORE - total_penalty, 0.0), 6),
        },
        "quality": {
            "action_counts": dict(sorted(action_counts.items())),
            "parse_status": "parsed",
            "invalid_action_fields": sum(1 for row in fields if row["action"] not in ALLOWED_ACTIONS),
            "quote_over_limit_fields": sum(1 for row in fields if row["source_quote_over_limit"]),
            "invalid_chunk_id_fields": sum(
                1
                for row in fields
                if row["repaired_chunk_id_present"] and not row["repaired_chunk_id_valid"]
            ),
            "status_value_inconsistency_fields": sum(
                1
                for row in fields
                if row["repaired_status"] == "found" and not row["repaired_value_present"]
            ),
            "type_mismatch_fields": sum(1 for row in fields if row["type_mismatch"]),
            "needs_supervisor_fields": sum(1 for row in fields if row["action"] == "needs_supervisor"),
            "clean_repaired_or_unchanged_fields": sum(
                1
                for row in fields
                if row["action"] in {"repaired", "unchanged"}
                and not row["source_quote_over_limit"]
                and not row["type_mismatch"]
                and not (
                    row["repaired_status"] == "found" and not row["repaired_value_present"]
                )
            ),
        },
    }


def summarize_field(field: str, payload: Any, expected_type: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}
    value = payload.get("repaired_value")
    quote = str(payload.get("source_quote") or "")
    chunk_id = payload.get("repaired_chunk_id")
    action = str(payload.get("action", "missing"))
    value_type = python_type_name(value)
    type_mismatch = (
        action in {"repaired", "unchanged"}
        and value is not None
        and value_type != expected_type
    )
    return {
        "field": field,
        "action": action,
        "repaired_status": str(payload.get("repaired_status", "missing")),
        "repaired_value_present": value is not None,
        "repaired_value_type": value_type,
        "expected_value_type": expected_type,
        "type_mismatch": type_mismatch,
        "repaired_value_hash": stable_hash(value) if value is not None else "",
        "repaired_units_present": bool(payload.get("repaired_units")),
        "repaired_page_anchor_present": bool(payload.get("repaired_page_anchor")),
        "repaired_chunk_id_present": bool(chunk_id),
        "repaired_chunk_id_valid": chunk_id_valid(chunk_id),
        "source_quote_present": bool(quote),
        "source_quote_word_count": word_count(quote),
        "source_quote_over_limit": word_count(quote) > QUOTE_WORD_LIMIT,
        "confidence_bucket": confidence_bucket(payload.get("confidence")),
        "reason_code": str(payload.get("reason_code", "")),
    }


def score_field(row: dict[str, Any]) -> dict[str, Any]:
    terms: dict[str, float] = {}
    hard_terms = {
        "invalid_action",
        "value_type_mismatch",
        "found_null_value",
        "invalid_chunk_id",
        "missing_chunk_id_on_found",
    }
    if row["action"] not in ALLOWED_ACTIONS:
        terms["invalid_action"] = PENALTY_WEIGHTS["invalid_action"]
    if row["type_mismatch"]:
        terms["value_type_mismatch"] = PENALTY_WEIGHTS["value_type_mismatch"]
    if row["repaired_status"] == "found" and not row["repaired_value_present"]:
        terms["found_null_value"] = PENALTY_WEIGHTS["found_null_value"]
    if row["repaired_chunk_id_present"] and not row["repaired_chunk_id_valid"]:
        terms["invalid_chunk_id"] = PENALTY_WEIGHTS["invalid_chunk_id"]
    if row["repaired_status"] == "found" and not row["repaired_chunk_id_present"]:
        terms["missing_chunk_id_on_found"] = PENALTY_WEIGHTS["missing_chunk_id_on_found"]
    if row["repaired_status"] == "found" and not row["source_quote_present"]:
        terms["missing_quote_on_found"] = PENALTY_WEIGHTS["missing_quote_on_found"]
    if row["action"] == "needs_supervisor":
        terms["needs_supervisor"] = PENALTY_WEIGHTS["needs_supervisor"]
    if row["action"] in {"repaired", "unchanged"} and row["confidence_bucket"] == "low":
        terms["low_confidence_repaired"] = PENALTY_WEIGHTS["low_confidence_repaired"]
    quote_penalty = quote_length_penalty(row["source_quote_word_count"])
    if quote_penalty:
        terms["quote_excess"] = quote_penalty
    hard_penalty = sum(value for key, value in terms.items() if key in hard_terms)
    soft_penalty = sum(value for key, value in terms.items() if key not in hard_terms)
    return {
        "field": row["field"],
        "terms": {key: round(value, 6) for key, value in sorted(terms.items())},
        "hard_penalty": round(hard_penalty, 6),
        "soft_penalty": round(soft_penalty, 6),
        "total_penalty": round(hard_penalty + soft_penalty, 6),
    }


def quote_length_penalty(words: int) -> float:
    if words <= QUOTE_WORD_LIMIT:
        return 0.0
    excess = words - QUOTE_WORD_LIMIT
    return PENALTY_WEIGHTS["quote_excess"] * (math.exp(excess / QUOTE_PENALTY_SCALE) - 1.0)


def scoring_rubric() -> dict[str, Any]:
    return {
        "max_score": MAX_SCORE,
        "quote_word_target": QUOTE_WORD_LIMIT,
        "quote_penalty": {
            "kind": "exponential_excess",
            "scale": QUOTE_PENALTY_SCALE,
            "formula": "weight * (exp((words - target) / scale) - 1) for words > target",
        },
        "penalty_weights": PENALTY_WEIGHTS,
        "interpretation": (
            "Hard penalties represent trust or schema failures. Soft penalties represent "
            "objective-function misses that should guide optimization rather than dominate "
            "pass/fail reporting."
        ),
    }


def default_model_provenance(reported_model: str) -> dict[str, Any]:
    return {
        "reported_model": reported_model,
        "observed_model": "",
        "authoritative_model": reported_model,
        "status": "self_reported_only",
        "mismatch_penalty": 0.0,
    }


def attach_model_provenance(lane: dict[str, Any], bridge: dict[str, Any]) -> None:
    reported_model = str(lane.get("repair_model", ""))
    observed_model = str(bridge.get("resolved_model", ""))
    if lane.get("lane_id") != "copilot_free_supervisor":
        lane["model_provenance"] = default_model_provenance(reported_model)
        return

    normalized_reported = normalize_model_label(reported_model)
    normalized_observed = normalize_model_label(observed_model)
    mismatch = bool(
        normalized_reported
        and normalized_observed
        and normalized_observed != "unknown"
        and normalized_reported != normalized_observed
    )
    penalty = PENALTY_WEIGHTS["model_provenance_mismatch"] if mismatch else 0.0
    lane["model_provenance"] = {
        "reported_model": reported_model,
        "observed_model": observed_model,
        "authoritative_model": observed_model or reported_model,
        "status": "mismatch" if mismatch else "matched_or_unavailable",
        "mismatch_penalty": penalty,
    }
    if not penalty:
        return

    score = lane["rubric_score"]
    score["soft_penalty"] = round(float(score["soft_penalty"]) + penalty, 6)
    score["total_penalty"] = round(float(score["total_penalty"]) + penalty, 6)
    score["score"] = round(max(MAX_SCORE - float(score["total_penalty"]), 0.0), 6)
    lane["quality"]["model_provenance_mismatch"] = True


def normalize_model_label(value: str) -> str:
    return value.strip().removeprefix("ollama-models/Ollama/").removesuffix(":latest").casefold()


def parse_bridge_report(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig", errors="replace") if path.exists() else ""
    return {
        "bridge_report_path": path.as_posix(),
        "status": match_line(text, "status") or "missing",
        "resolved_model": match_line(text, "resolved_model") or "unknown",
        "permission_levels": match_line(text, "permission_levels") or "unknown",
        "completed": match_line(text, "completed") or "unknown",
        "final_marker_present": match_line(text, "final_marker_present") or "unknown",
        "numeric_token_status": "unavailable_from_vscode_chat_session",
        "supervisor_token_price_per_1m_usd": 0.0,
        "supervisor_cash_cost_usd": 0.0,
    }


def load_token_rows(token_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(token_dir.glob("*.tokens.json")):
        data = load_token_record(path)
        scope = data.get("scope", {})
        usage = data.get("usage", {})
        costs = calculate_token_costs(data)
        rows.append(
            {
                "record_path": path.as_posix(),
                "span_id": str(scope.get("span_id", "")) if isinstance(scope, dict) else "",
                "span_kind": str(scope.get("span_kind", "")) if isinstance(scope, dict) else "",
                "model_or_worker": str(scope.get("model_or_worker", "")) if isinstance(scope, dict) else "",
                "supervisor_input_tokens": int(usage.get("supervisor_input_tokens", 0))
                if isinstance(usage, dict)
                else 0,
                "supervisor_cached_input_tokens": int(
                    usage.get("supervisor_cached_input_tokens", 0)
                )
                if isinstance(usage, dict)
                else 0,
                "supervisor_output_tokens": int(usage.get("supervisor_output_tokens", 0))
                if isinstance(usage, dict)
                else 0,
                "supervisor_reasoning_output_tokens": int(
                    usage.get("supervisor_reasoning_output_tokens", 0)
                )
                if isinstance(usage, dict)
                else 0,
                "supervisor_cost_usd": costs.supervisor_cost_usd,
            }
        )
    return rows


def summarize_totals(
    token_rows: list[dict[str, Any]],
    codex: dict[str, Any],
    copilot: dict[str, Any],
) -> dict[str, Any]:
    by_span = {row["span_kind"]: row for row in token_rows}
    setup_cost = by_span.get("setup", {}).get("supervisor_cost_usd", 0.0)
    codex_cost = by_span.get("codex_supervisor_extraction", {}).get("supervisor_cost_usd", 0.0)
    codex_cost += by_span.get("codex_supervisor_adjudication", {}).get(
        "supervisor_cost_usd", 0.0
    )
    delegation_cost = by_span.get("copilot_supervisor_delegation", {}).get(
        "supervisor_cost_usd", 0.0
    )
    delegation_success_cost = sum(
        row["supervisor_cost_usd"]
        for row in token_rows
        if row["span_kind"].startswith("copilot_supervisor_delegation")
        and "failed" not in row["span_kind"]
    )
    delegation_failed_cost = sum(
        row["supervisor_cost_usd"]
        for row in token_rows
        if row["span_kind"].startswith("copilot_supervisor_delegation")
        and "failed" in row["span_kind"]
    )
    if delegation_success_cost:
        delegation_cost = delegation_success_cost
    return {
        "shared_setup_codex_supervisor_cost_usd": setup_cost,
        "codex_direct_paid_supervisor_cost_usd": codex_cost,
        "copilot_lane_paid_codex_delegation_cost_usd": delegation_cost,
        "copilot_lane_failed_retry_paid_codex_cost_usd": delegation_failed_cost,
        "copilot_lane_paid_codex_delegation_cost_usd_including_retries": (
            delegation_cost + delegation_failed_cost
        ),
        "copilot_lane_local_supervisor_cost_usd": 0.0,
        "copilot_lane_total_cash_cost_usd_excluding_shared_setup": delegation_cost,
        "copilot_lane_total_cash_cost_usd_including_retries_excluding_shared_setup": (
            delegation_cost + delegation_failed_cost
        ),
        "codex_lane_total_cash_cost_usd_excluding_shared_setup": codex_cost,
        "copilot_minus_codex_cash_delta_usd_excluding_shared_setup": delegation_cost
        - codex_cost,
        "copilot_minus_codex_cash_delta_including_retries_usd_excluding_shared_setup": (
            delegation_cost + delegation_failed_cost - codex_cost
        ),
        "codex_clean_repaired_or_unchanged_fields": codex["quality"][
            "clean_repaired_or_unchanged_fields"
        ],
        "copilot_clean_repaired_or_unchanged_fields": copilot["quality"][
            "clean_repaired_or_unchanged_fields"
        ],
        "codex_needs_supervisor_fields": codex["quality"]["needs_supervisor_fields"],
        "copilot_needs_supervisor_fields": copilot["quality"]["needs_supervisor_fields"],
        "codex_quote_over_limit_fields": codex["quality"]["quote_over_limit_fields"],
        "copilot_quote_over_limit_fields": copilot["quality"]["quote_over_limit_fields"],
        "codex_status_value_inconsistency_fields": codex["quality"][
            "status_value_inconsistency_fields"
        ],
        "copilot_status_value_inconsistency_fields": copilot["quality"][
            "status_value_inconsistency_fields"
        ],
    }


def interpret(
    codex: dict[str, Any],
    copilot: dict[str, Any],
    bridge: dict[str, Any],
    token_rows: list[dict[str, Any]],
) -> str:
    if bridge["status"] != "accepted-candidate":
        return "Copilot lane did not satisfy bridge process checks; do not use quality result."
    if copilot.get("model_provenance", {}).get("status") == "mismatch":
        return (
            "Scoped Copilot supervisor followed the process, but its self-reported model "
            "identity disagreed with bridge evidence. Treat bridge-observed model identity "
            "as authoritative before comparing model performance."
        )
    copilot_quality = copilot["quality"]
    codex_quality = codex["quality"]
    if (
        copilot_quality["quote_over_limit_fields"]
        or copilot_quality["status_value_inconsistency_fields"]
        or copilot_quality["type_mismatch_fields"]
    ):
        return (
            "Scoped Copilot supervisor followed the process but did not meet repair-quality "
            "criteria. This supports tighter role prompts and/or a separate local audit node "
            "before allowing free-supervisor output to replace paid supervision."
        )
    if copilot_quality["clean_repaired_or_unchanged_fields"] >= codex_quality[
        "clean_repaired_or_unchanged_fields"
    ]:
        return "Scoped Copilot supervisor matched the direct Codex lane on clean field repairs."
    if not token_rows:
        return "No Codex token rows were available; economics are incomplete."
    return "Copilot lane was process-compliant but lower quality than direct Codex supervision."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 55 Codex vs Copilot Supervisor A/B",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- benchmark_scope: {report['benchmark_scope']}",
        f"- quote_word_limit: `{report['quote_word_limit']}`",
        f"- raw_output_policy: {report['raw_output_policy']}",
        "",
        "## Bridge Evidence",
        "",
    ]
    for key, value in report["bridge_evidence"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(
        [
            "",
            "## Lane Quality",
            "",
            "| Lane | Reported Model | Authoritative Model | Score | Hard Penalty | Soft Penalty | Clean Fields | Needs Supervisor | Quote Defects | Status/Value Defects |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for lane in report["lanes"]:
        quality = lane["quality"]
        score = lane["rubric_score"]
        provenance = lane["model_provenance"]
        lines.append(
            "| {lane} | `{model}` | `{authoritative}` | {score:.2f} | {hard:.2f} | {soft:.2f} | {clean} | {needs} | {quote} | {status} |".format(
                lane=lane["lane_id"],
                model=lane["repair_model"],
                authoritative=provenance["authoritative_model"],
                score=score["score"],
                hard=score["hard_penalty"],
                soft=score["soft_penalty"],
                clean=quality["clean_repaired_or_unchanged_fields"],
                needs=quality["needs_supervisor_fields"],
                quote=quality["quote_over_limit_fields"],
                status=quality["status_value_inconsistency_fields"],
            )
        )

    lines.extend(
        [
            "",
            "## Model Provenance",
            "",
            "| Lane | Reported Model | Observed Model | Authoritative Model | Status | Penalty |",
            "| --- | --- | --- | --- | --- | ---: |",
        ]
    )
    for lane in report["lanes"]:
        provenance = lane["model_provenance"]
        lines.append(
            "| {lane} | `{reported}` | `{observed}` | `{authoritative}` | `{status}` | {penalty:.2f} |".format(
                lane=lane["lane_id"],
                reported=provenance["reported_model"],
                observed=provenance["observed_model"],
                authoritative=provenance["authoritative_model"],
                status=provenance["status"],
                penalty=provenance["mismatch_penalty"],
            )
        )

    lines.extend(
        [
            "",
            "## Scoring Rubric",
            "",
            f"- max_score: `{report['scoring_rubric']['max_score']}`",
            f"- quote_word_target: `{report['scoring_rubric']['quote_word_target']}`",
            "- quote_penalty: `weight * (exp((words - target) / scale) - 1)` for words over target",
            f"- quote_penalty_scale: `{report['scoring_rubric']['quote_penalty']['scale']}`",
            "",
            "| Penalty Term | Weight |",
            "| --- | ---: |",
        ]
    )
    for key, value in sorted(report["scoring_rubric"]["penalty_weights"].items()):
        lines.append(f"| `{key}` | {value} |")

    lines.extend(
        [
            "",
            "## Field-Level Quality",
            "",
            "| Lane | Field | Action | Status | Value Type | Quote Words | Defects |",
            "| --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for lane in report["lanes"]:
        for row in lane["field_repairs"]:
            defects = []
            if row["source_quote_over_limit"]:
                defects.append("quote_over_limit")
            if row["type_mismatch"]:
                defects.append("type_mismatch")
            if row["repaired_status"] == "found" and not row["repaired_value_present"]:
                defects.append("found_null_value")
            if row["repaired_chunk_id_present"] and not row["repaired_chunk_id_valid"]:
                defects.append("invalid_chunk_id")
            lines.append(
                "| {lane} | `{field}` | `{action}` | `{status}` | `{value_type}` | {words} | `{defects}` |".format(
                    lane=lane["lane_id"],
                    field=row["field"],
                    action=row["action"],
                    status=row["repaired_status"],
                    value_type=row["repaired_value_type"],
                    words=row["source_quote_word_count"],
                    defects=", ".join(defects) if defects else "none",
                )
            )

    lines.extend(
        [
            "",
            "## Field-Level Penalties",
            "",
            "| Lane | Field | Hard Penalty | Soft Penalty | Total Penalty | Terms |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for lane in report["lanes"]:
        for score in lane["field_scores"]:
            lines.append(
                "| {lane} | `{field}` | {hard:.2f} | {soft:.2f} | {total:.2f} | `{terms}` |".format(
                    lane=lane["lane_id"],
                    field=score["field"],
                    hard=score["hard_penalty"],
                    soft=score["soft_penalty"],
                    total=score["total_penalty"],
                    terms=json.dumps(score["terms"], sort_keys=True),
                )
            )

    lines.extend(
        [
            "",
            "## Supervisor Token/Cost Line Items",
            "",
            "| Span | Kind | Fresh Input | Cached Input | Output | Reasoning Output | Cost |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["token_line_items"]:
        lines.append(
            "| `{span}` | `{kind}` | {fresh} | {cached} | {output} | {reasoning} | ${cost:.6f} |".format(
                span=row["span_id"],
                kind=row["span_kind"],
                fresh=row["supervisor_input_tokens"],
                cached=row["supervisor_cached_input_tokens"],
                output=row["supervisor_output_tokens"],
                reasoning=row["supervisor_reasoning_output_tokens"],
                cost=row["supervisor_cost_usd"],
            )
        )

    lines.extend(["", "## Cost Delta", ""])
    for key, value in report["totals"].items():
        if key.endswith("_usd") or "cost" in key or "delta" in key:
            lines.append(f"- {key}: `${float(value):.6f}`")
        else:
            lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Interpretation", "", report["interpretation"], ""])
    return "\n".join(lines)


def match_line(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def python_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, str):
        return "str"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def chunk_id_valid(value: Any) -> bool:
    return isinstance(value, str) and bool(re.match(r"^tsa23_2012_23ts13ra::pages_\d{3}_\d{3}$", value))


def word_count(value: str) -> int:
    return len([word for word in re.split(r"\s+", value.strip()) if word])


def stable_hash(value: Any) -> str:
    normalized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def confidence_bucket(value: Any) -> str:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return "missing"
    if confidence >= 0.8:
        return "high"
    if confidence >= 0.5:
        return "medium"
    if confidence > 0:
        return "low"
    return "zero"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_expected_types(path: Path | None) -> dict[str, str]:
    if path is None:
        return dict(EXPECTED_TYPES)
    data = load_json(path)
    result = {}
    for key, value in data.items():
        if not isinstance(value, str):
            raise ValueError(f"field spec value must be string for {key}")
        result[str(key)] = value
    if not result:
        raise ValueError("field spec must not be empty")
    return result


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
