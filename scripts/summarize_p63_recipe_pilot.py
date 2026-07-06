"""Summarize the ignored P63 bounded TSA23 recipe pilot runtime output.

This script reads ignored SDK/Ollama worker output and ignored supervisor-token
spans, then writes public-safe aggregate summaries. It must not copy raw source
text, source quotes, prompts, provider URLs, headers, or transcripts into
tracked outputs.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path(
    "benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_plan.json"
)
DEFAULT_RUNTIME_ROOT = Path("runtime/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot")
DEFAULT_TOKEN_ROOT = Path("runtime/supervisor_tokens/p63_bounded_tsa23_recipe_pilot")
DEFAULT_OUTPUT_JSON = Path(
    "benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_execution_summary.json"
)
DEFAULT_OUTPUT_MD = Path(
    "benchmarks/document_library/tsa23_tsr/phase63_bounded_tsa23_recipe_pilot_execution_results.md"
)
QUOTE_WORD_TARGET = 25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write sanitized P63 bounded TSA23 recipe pilot execution summaries."
    )
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--token-root", type=Path, default=DEFAULT_TOKEN_ROOT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = load_json(args.plan)
    eval_summary_path = args.runtime_root / "eval" / "section_map_typed_fact" / "summary.json"
    eval_summary = load_json(eval_summary_path)
    row = first_row(eval_summary)
    result_file = Path(str(row.get("result_file", "")))
    if not result_file.exists():
        raise FileNotFoundError(f"runtime result file not found: {result_file}")

    assistant_message = str(row.get("assistant_message", ""))
    records, malformed_lines = parse_jsonl_records(assistant_message)
    allowed_chunks = {chunk["chunk_id"] for chunk in plan["selected_chunks"]}
    expected_document_id = str(plan["selected_document"]["document_id"])
    expected_corpus_id = str(plan["corpus"]["corpus_id"])
    expected_model = str(eval_summary["models"][0])

    validation = validate_records(
        records=records,
        allowed_chunks=allowed_chunks,
        expected_document_id=expected_document_id,
        expected_corpus_id=expected_corpus_id,
        expected_model=expected_model,
    )
    result_text = result_file.read_text(encoding="utf-8-sig", errors="replace")
    observed_errors = observed_error_messages(result_text)
    worker_usage = worker_usage_from_result(result_text)
    supervisor_spans = [
        load_token_span(args.token_root / "ticket_build.tokens.json"),
        load_token_span(args.token_root / "worker_run_orchestration.tokens.json"),
        load_token_span(args.token_root / "worker_output_summarize.tokens.json"),
        load_token_span(args.token_root / "tracked_update.tokens.json"),
    ]
    fact_review_counts = fact_counts(validation, malformed_lines)

    report = {
        "schema_version": 1,
        "summary_id": "p63_bounded_tsa23_recipe_pilot_execution",
        "generated_utc": now_utc(),
        "phase": "P63",
        "github_parent_issue": 414,
        "github_child_issue": 418,
        "pilot_id": plan["pilot_id"],
        "selected_document": {
            "document_id": expected_document_id,
            "document_type": plan["selected_document"]["document_type"],
            "cycle_year": plan["selected_document"]["cycle_year"],
        },
        "selected_chunk_count": len(plan["selected_chunks"]),
        "raw_output_policy": (
            "Raw worker records, source quotes, prompts, provider details, and transcripts "
            "remain ignored under runtime/."
        ),
        "attempt": {
            "attempt_count": 1,
            "max_attempts": 1,
            "model": expected_model,
            "harness_status": row.get("status", ""),
            "harness_blocker": row.get("blocker", ""),
            "harness_classification": row.get("classification", ""),
            "observed_error_count": len(observed_errors),
            "observed_error_kinds": sorted(error_kind(error) for error in observed_errors),
            "fenced_output_detected": "```" in assistant_message,
            "preamble_detected": bool(
                assistant_message.strip()
                and not assistant_message.lstrip().startswith("{")
            ),
        },
        "candidate_metrics": {
            "parseable_json_records": len(records),
            "malformed_lines": malformed_lines,
            **validation,
        },
        "fact_review_counts": fact_review_counts,
        "worker_tokens": {
            "input_tokens": worker_usage["input_tokens"],
            "output_tokens": worker_usage["output_tokens"],
            "cash_cost_usd": 0.0,
        },
        "supervisor_token_spans": supervisor_spans,
        "supervisor_totals": supervisor_totals(supervisor_spans),
        "baseline_comparison": baseline_comparison(),
        "outcome": outcome(row, observed_errors, validation, malformed_lines),
        "public_safety": {
            "raw_source_text_tracked": false(),
            "raw_source_quotes_tracked": false(),
            "raw_prompts_tracked": false(),
            "provider_urls_tracked": false(),
            "headers_tracked": false(),
            "personal_paths_tracked": false(),
        },
        "runtime_evidence": {
            "runtime_summary_path": slash_path(eval_summary_path),
            "runtime_result_path": slash_path(result_file),
            "tracked_summary_json": slash_path(args.output_json),
            "tracked_summary_md": slash_path(args.output_md),
        },
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


def validate_records(
    records: list[dict[str, Any]],
    allowed_chunks: set[str],
    expected_document_id: str,
    expected_corpus_id: str,
    expected_model: str,
) -> dict[str, Any]:
    chunk_counts = Counter(str(record.get("chunk_id", "")) for record in records)
    record_type_counts = Counter(str(record.get("record_type", "")) for record in records)
    invalid_chunk_ids = Counter(
        str(record.get("chunk_id", ""))
        for record in records
        if str(record.get("chunk_id", "")) not in allowed_chunks
    )
    quote_word_counts = [word_count(str(record.get("source_quote", ""))) for record in records]
    required_fields = {
        "record_type",
        "document_id",
        "corpus_id",
        "chunk_id",
        "page_start",
        "page_end",
        "title_or_label",
        "normalized_key",
        "value_summary",
        "source_quote",
        "source_anchor",
        "confidence",
        "worker_model",
        "review_status",
        "notes",
    }
    return {
        "valid_chunk_records": sum(
            1 for record in records if str(record.get("chunk_id", "")) in allowed_chunks
        ),
        "invalid_chunk_id_records": sum(invalid_chunk_ids.values()),
        "invalid_chunk_id_values": sorted(invalid_chunk_ids),
        "covered_chunks": sorted(set(chunk_counts) & allowed_chunks),
        "missing_chunks": sorted(allowed_chunks - set(chunk_counts)),
        "wrong_document_id_records": sum(
            1 for record in records if record.get("document_id") != expected_document_id
        ),
        "wrong_corpus_id_records": sum(
            1 for record in records if record.get("corpus_id") != expected_corpus_id
        ),
        "worker_model_field_match_records": sum(
            1 for record in records if record.get("worker_model") == expected_model
        ),
        "wrong_review_status_records": sum(
            1 for record in records if record.get("review_status") != "raw_worker_candidate"
        ),
        "records_missing_required_fields": sum(
            1 for record in records if required_fields - set(record)
        ),
        "records_with_source_quote": sum(1 for count in quote_word_counts if count > 0),
        "source_quote_over_target_records": sum(
            1 for count in quote_word_counts if count > QUOTE_WORD_TARGET
        ),
        "source_quote_max_words": max(quote_word_counts, default=0),
        "record_type_counts": dict(sorted(record_type_counts.items())),
        "chunk_record_counts": {
            chunk_id: chunk_counts[chunk_id] for chunk_id in sorted(chunk_counts)
        },
    }


def fact_counts(validation: dict[str, Any], malformed_lines: int) -> dict[str, Any]:
    invalid = int(validation["invalid_chunk_id_records"])
    valid = int(validation["valid_chunk_records"])
    return {
        "accepted": 0,
        "repaired": 0,
        "rejected": invalid,
        "escalated": 0,
        "unresolved": valid,
        "malformed_lines": malformed_lines,
        "basis": (
            "No source audit or repair pass was run after the single-attempt stop rule. "
            "Valid raw records remain unresolved; invalid chunk-ID records are rejected "
            "by deterministic validation."
        ),
    }


def parse_jsonl_records(text: str) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    malformed = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        if not line.startswith("{"):
            malformed += 1
            continue
        if not line.endswith("}"):
            malformed += 1
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            malformed += 1
    return records, malformed


def observed_error_messages(result_text: str) -> list[str]:
    match = re.search(r"## Observed Errors\s+```json\s+(\[.*?\])\s+```", result_text, re.S)
    if not match:
        return []
    try:
        parsed = json.loads(match.group(1))
    except json.JSONDecodeError:
        return ["unparseable-observed-errors-block"]
    return [str(item) for item in parsed]


def worker_usage_from_result(result_text: str) -> dict[str, int]:
    input_tokens = [int(value) for value in re.findall(r'"input_tokens":\s*(\d+)', result_text)]
    output_tokens = [int(value) for value in re.findall(r'"output_tokens":\s*(\d+)', result_text)]
    return {
        "input_tokens": input_tokens[-1] if input_tokens else 0,
        "output_tokens": output_tokens[-1] if output_tokens else 0,
    }


def load_token_span(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "span_id": path.stem.replace(".tokens", ""),
            "present": False,
            "cash_cost_usd": None,
        }
    data = load_json(path)
    usage = data["usage"]
    prices = data["prices"]
    fresh_input = int(usage["supervisor_input_tokens"])
    cached_input = int(usage["supervisor_cached_input_tokens"])
    output = int(usage["supervisor_output_tokens"])
    reasoning = int(usage["supervisor_reasoning_output_tokens"])
    cost = (
        fresh_input / 1_000_000 * float(prices["supervisor_input_price_per_1m_usd"])
        + cached_input
        / 1_000_000
        * float(prices["supervisor_cached_input_price_per_1m_usd"])
        + (output + reasoning)
        / 1_000_000
        * float(prices["supervisor_output_price_per_1m_usd"])
    )
    return {
        "span_id": data["scope"]["span_id"],
        "present": True,
        "fresh_input_tokens": fresh_input,
        "cached_input_tokens": cached_input,
        "output_tokens": output,
        "reasoning_output_tokens": reasoning,
        "cash_cost_usd": round(cost, 6),
    }


def supervisor_totals(spans: list[dict[str, Any]]) -> dict[str, Any]:
    present = [span for span in spans if span.get("present")]
    return {
        "span_count": len(present),
        "fresh_input_tokens": sum(int(span["fresh_input_tokens"]) for span in present),
        "cached_input_tokens": sum(int(span["cached_input_tokens"]) for span in present),
        "output_tokens": sum(int(span["output_tokens"]) for span in present),
        "reasoning_output_tokens": sum(int(span["reasoning_output_tokens"]) for span in present),
        "cash_cost_usd": round(sum(float(span["cash_cost_usd"]) for span in present), 6),
    }


def baseline_comparison() -> dict[str, Any]:
    return {
        "direct_supervisor_baseline_status": "not_run_stop_rule_triggered",
        "direct_supervisor_baseline_cost_usd": None,
        "delegated_workflow_cost_usd": None,
        "net_delta_usd": None,
        "comparison_decision": "not_comparable",
        "reason": (
            "P63.2 produced diagnostic evidence rather than an accepted delegated "
            "candidate. Running a direct-supervisor baseline now would answer a "
            "different question and spend additional paid tokens after the declared "
            "maintainer checkpoint."
        ),
    }


def outcome(
    row: dict[str, Any],
    observed_errors: list[str],
    validation: dict[str, Any],
    malformed_lines: int,
) -> dict[str, Any]:
    rejection_reasons: list[str] = []
    if row.get("status") != "completed":
        rejection_reasons.append(str(row.get("blocker") or "harness-not-completed"))
    if observed_errors:
        rejection_reasons.extend(sorted(error_kind(error) for error in observed_errors))
    if validation["invalid_chunk_id_records"]:
        rejection_reasons.append("invalid_chunk_id")
    if malformed_lines:
        rejection_reasons.append("malformed_or_truncated_jsonl")
    return {
        "quality_validated_candidate": False,
        "protocol_accepted_candidate": False,
        "economics_usable": False,
        "final_decision": "stop_after_single_attempt_model_call_failure",
        "rejection_reasons": sorted(set(rejection_reasons)),
        "maintainer_checkpoint_required": True,
        "follow_on_live_run_allowed_without_maintainer": False,
    }


def render_markdown(report: dict[str, Any]) -> str:
    candidate = report["candidate_metrics"]
    attempt = report["attempt"]
    totals = report["supervisor_totals"]
    worker = report["worker_tokens"]
    outcome_data = report["outcome"]
    fact_counts_data = report["fact_review_counts"]
    baseline = report["baseline_comparison"]
    lines = [
        "# Phase 63 Bounded TSA23 Recipe Pilot Execution Results",
        "",
        "Raw worker records, source quotes, prompts, provider details, and transcripts remain ignored.",
        "",
        "## Attempt Status",
        "",
        f"- model: `{attempt['model']}`",
        f"- harness_status: `{attempt['harness_status']}`",
        f"- harness_blocker: `{attempt['harness_blocker']}`",
        f"- harness_classification: `{attempt['harness_classification']}`",
        f"- observed_error_kinds: `{', '.join(attempt['observed_error_kinds'])}`",
        f"- fenced_output_detected: `{attempt['fenced_output_detected']}`",
        f"- preamble_detected: `{attempt['preamble_detected']}`",
        "",
        "## Candidate Metrics",
        "",
        f"- parseable_json_records: `{candidate['parseable_json_records']}`",
        f"- malformed_lines: `{candidate['malformed_lines']}`",
        f"- valid_chunk_records: `{candidate['valid_chunk_records']}`",
        f"- invalid_chunk_id_records: `{candidate['invalid_chunk_id_records']}`",
        f"- missing_chunks: `{', '.join(candidate['missing_chunks']) or 'none'}`",
        f"- source_quote_over_target_records: `{candidate['source_quote_over_target_records']}`",
        f"- source_quote_max_words: `{candidate['source_quote_max_words']}`",
        "",
        "## Fact Review Counts",
        "",
        f"- accepted: `{fact_counts_data['accepted']}`",
        f"- repaired: `{fact_counts_data['repaired']}`",
        f"- rejected: `{fact_counts_data['rejected']}`",
        f"- escalated: `{fact_counts_data['escalated']}`",
        f"- unresolved: `{fact_counts_data['unresolved']}`",
        f"- basis: {fact_counts_data['basis']}",
        "",
        "## Token And Cost Lines",
        "",
        "| Lane | Fresh Input | Cached Input | Output | Reasoning Output | Worker Input | Worker Output | Cash Cost USD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for span in report["supervisor_token_spans"]:
        if not span.get("present"):
            continue
        lines.append(
            "| supervisor `{span}` | {fresh} | {cached} | {output} | {reasoning} | 0 | 0 | {cost:.6f} |".format(
                span=span["span_id"],
                fresh=span["fresh_input_tokens"],
                cached=span["cached_input_tokens"],
                output=span["output_tokens"],
                reasoning=span["reasoning_output_tokens"],
                cost=float(span["cash_cost_usd"]),
            )
        )
    lines.append(
        "| local worker | 0 | 0 | 0 | 0 | {input_tokens} | {output_tokens} | {cost:.6f} |".format(
            input_tokens=worker["input_tokens"],
            output_tokens=worker["output_tokens"],
            cost=float(worker["cash_cost_usd"]),
        )
    )
    lines.append(
        "| supervisor total | {fresh} | {cached} | {output} | {reasoning} | 0 | 0 | {cost:.6f} |".format(
            fresh=totals["fresh_input_tokens"],
            cached=totals["cached_input_tokens"],
            output=totals["output_tokens"],
            reasoning=totals["reasoning_output_tokens"],
            cost=float(totals["cash_cost_usd"]),
        )
    )
    lines.extend(
        [
            "",
            "## Outcome",
            "",
            f"- quality_validated_candidate: `{outcome_data['quality_validated_candidate']}`",
            f"- protocol_accepted_candidate: `{outcome_data['protocol_accepted_candidate']}`",
            f"- economics_usable: `{outcome_data['economics_usable']}`",
            f"- final_decision: `{outcome_data['final_decision']}`",
            f"- rejection_reasons: `{', '.join(outcome_data['rejection_reasons'])}`",
            f"- maintainer_checkpoint_required: `{outcome_data['maintainer_checkpoint_required']}`",
            "",
            "## Baseline Comparison",
            "",
            f"- direct_supervisor_baseline_status: `{baseline['direct_supervisor_baseline_status']}`",
            f"- comparison_decision: `{baseline['comparison_decision']}`",
            f"- reason: {baseline['reason']}",
            "",
            "## Interpretation",
            "",
            "The single allowed live attempt produced partial parseable JSONL but did not complete cleanly. "
            "Because the attempt hit a model-call failure and produced protocol-noisy fenced output with an invalid chunk ID, "
            "P63 must stop at the maintainer checkpoint before any retry, repair expansion, broader slice, or model-lane change.",
            "",
        ]
    )
    return "\n".join(lines)


def first_row(summary: dict[str, Any]) -> dict[str, Any]:
    rows = summary.get("rows", [])
    if not rows:
        raise ValueError("eval summary contains no rows")
    row = rows[0]
    if not isinstance(row, dict):
        raise ValueError("eval summary row is not an object")
    return row


def error_kind(error: str) -> str:
    if "524" in error:
        return "provider_524_model_call_failure"
    return re.sub(r"[^a-z0-9]+", "_", error.lower()).strip("_") or "unknown_error"


def word_count(value: str) -> int:
    return len([word for word in re.split(r"\s+", value.strip()) if word])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def false() -> bool:
    return False


def slash_path(path: Path) -> str:
    return path.as_posix()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
