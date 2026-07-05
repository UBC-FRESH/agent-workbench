"""Summarize P55 verifier output without tracking raw final values or quotes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


QUOTE_WORD_LIMIT = 25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a P55 Wave 8 verifier run.")
    parser.add_argument("--packet-index", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = load_json(args.packet_index)
    summary_path = args.eval_root / packet["packet_id"] / "summary.json"
    summary = load_json(summary_path)
    rows = summary.get("rows", [])
    row = rows[0] if isinstance(rows, list) and rows else {}
    assistant_message = str(row.get("assistant_message", ""))
    parsed, parse_error = parse_json_object(assistant_message)
    verdicts = parsed.get("verdicts", {}) if isinstance(parsed, dict) else {}
    field_rows = summarize_verdicts(verdicts, packet)
    usage = parse_usage(args.eval_root, packet["packet_id"], Path(str(row.get("result_file", ""))))
    report = {
        "summary_id": "p55_wave8_disagreement_verification",
        "generated_utc": now_utc(),
        "phase": "P55",
        "wave_id": packet["wave_id"],
        "packet_id": packet["packet_id"],
        "source_packet_id": packet["source_packet_id"],
        "document_id": packet["document_id"],
        "verifier_model": packet["verifier_model"],
        "raw_output_policy": "Raw verifier output, final values, and source quotes remain ignored under runtime/.",
        "status": row.get("status", "missing-summary"),
        "harness_classification": row.get("classification", ""),
        "parse_status": "parsed" if parsed is not None else "parse_failed",
        "parse_error": parse_error,
        "expected_field_count": len(packet["fields"]),
        "verdict_field_count": len(field_rows),
        "missing_fields": sorted(set(packet["fields"]) - {field["field"] for field in field_rows}),
        "extra_fields": sorted({field["field"] for field in field_rows} - set(packet["fields"])),
        "field_verdicts": field_rows,
        "totals": summarize_totals(field_rows, usage),
        "gate_result": gate_result(packet, parsed, field_rows),
        "recommended_next_move": recommendation(packet, parsed, field_rows),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


def parse_json_object(text: str) -> tuple[dict[str, Any] | None, str]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        return None, "no-json-object-found"
    try:
        value = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        return None, f"json-decode-error:{exc.msg}"
    if not isinstance(value, dict):
        return None, "top-level-not-object"
    if not isinstance(value.get("verdicts"), dict):
        return None, "missing-verdicts-object"
    return value, ""


def summarize_verdicts(verdicts: Any, packet: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(verdicts, dict):
        return []
    rows: list[dict[str, Any]] = []
    for field, payload in verdicts.items():
        if not isinstance(payload, dict):
            payload = {}
        quote = str(payload.get("source_quote") or "")
        final_value = payload.get("final_value")
        final_chunk_id = payload.get("final_chunk_id")
        rows.append(
            {
                "field": str(field),
                "verdict": str(payload.get("verdict", "missing")),
                "final_status": str(payload.get("final_status", "missing")),
                "final_value_present": final_value is not None,
                "final_value_type": type(final_value).__name__ if final_value is not None else "null",
                "final_value_hash": stable_hash(final_value) if final_value is not None else "",
                "final_units_present": bool(payload.get("final_units")),
                "final_page_anchor_present": bool(payload.get("final_page_anchor")),
                "final_chunk_id_present": bool(final_chunk_id),
                "final_chunk_id_valid": chunk_id_valid(final_chunk_id),
                "source_quote_present": bool(quote),
                "source_quote_word_count": word_count(quote),
                "source_quote_over_limit": word_count(quote) > QUOTE_WORD_LIMIT,
                "confidence_bucket": confidence_bucket(payload.get("confidence")),
                "reason_code": str(payload.get("reason_code", "")),
            }
        )
    return sorted(rows, key=lambda row: row["field"])


def summarize_totals(field_rows: list[dict[str, Any]], usage: dict[str, int]) -> dict[str, Any]:
    verdict_counts = Counter(row["verdict"] for row in field_rows)
    return {
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "resolved_fields": sum(
            1
            for row in field_rows
            if row["verdict"]
            in {"left_correct", "right_correct", "both_correct_equivalent", "both_wrong"}
        ),
        "needs_supervisor_fields": sum(
            1 for row in field_rows if row["verdict"] in {"needs_supervisor", "insufficient_evidence"}
        ),
        "quote_over_limit_fields": sum(1 for row in field_rows if row["source_quote_over_limit"]),
        "invalid_chunk_id_fields": sum(
            1
            for row in field_rows
            if row["final_chunk_id_present"] and not row["final_chunk_id_valid"]
        ),
        "worker_input_tokens": usage["input_tokens"],
        "worker_output_tokens": usage["output_tokens"],
        "worker_cash_cost_usd": 0.0,
    }


def gate_result(
    packet: dict[str, Any],
    parsed: dict[str, Any] | None,
    field_rows: list[dict[str, Any]],
) -> str:
    if parsed is None:
        return "wave8-verifier-parse-failed"
    if set(packet["fields"]) != {field["field"] for field in field_rows}:
        return "wave8-field-set-mismatch"
    if any(row["source_quote_over_limit"] for row in field_rows):
        return "wave8-quote-repair-needed"
    if any(row["final_chunk_id_present"] and not row["final_chunk_id_valid"] for row in field_rows):
        return "wave8-chunk-id-repair-needed"
    return "wave8-ready-for-supervisor-audit-sampling"


def recommendation(
    packet: dict[str, Any],
    parsed: dict[str, Any] | None,
    field_rows: list[dict[str, Any]],
) -> str:
    if parsed is None:
        return "Repair verifier ticket or switch verifier model before supervisor audit."
    needs_supervisor = [
        row["field"]
        for row in field_rows
        if row["verdict"] in {"needs_supervisor", "insufficient_evidence"}
    ]
    if needs_supervisor:
        return (
            "Send only unresolved verifier fields to paid supervisor audit: "
            + ", ".join(needs_supervisor)
        )
    return "Use supervisor audit sampling to check verifier correctness before final JSON normalization."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 55 Wave 8 Disagreement Verification Results",
        "",
        "Raw verifier values and source quotes remain ignored under runtime paths.",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- gate_result: `{report['gate_result']}`",
        f"- verifier_model: `{report['verifier_model']}`",
        f"- parse_status: `{report['parse_status']}`",
        "",
        "## Aggregate Totals",
        "",
    ]
    for key, value in report["totals"].items():
        rendered = json.dumps(value, sort_keys=True) if isinstance(value, dict) else str(value)
        lines.append(f"- {key}: `{rendered}`")
    lines.extend(
        [
            "",
            "## Verdicts",
            "",
            "| Field | Verdict | Final Status | Quote Words | Reason Code |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for row in report["field_verdicts"]:
        lines.append(
            "| {field} | `{verdict}` | `{status}` | {words} | `{reason}` |".format(
                field=row["field"],
                verdict=row["verdict"],
                status=row["final_status"],
                words=row["source_quote_word_count"],
                reason=row["reason_code"],
            )
        )
    lines.extend(["", "## Recommendation", "", report["recommended_next_move"], ""])
    return "\n".join(lines)


def parse_usage(eval_root: Path, packet_id: str, result_file: Path) -> dict[str, int]:
    path = resolve_result_file(eval_root, packet_id, result_file)
    if not path.exists():
        return {"input_tokens": 0, "output_tokens": 0}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    input_matches = [int(value) for value in re.findall(r'"input_tokens":\s*(\d+)', text)]
    output_matches = [int(value) for value in re.findall(r'"output_tokens":\s*(\d+)', text)]
    return {
        "input_tokens": input_matches[-1] if input_matches else 0,
        "output_tokens": output_matches[-1] if output_matches else 0,
    }


def resolve_result_file(eval_root: Path, packet_id: str, result_file: Path) -> Path:
    if result_file.is_absolute():
        return result_file
    if result_file.exists():
        return result_file
    return eval_root / packet_id / result_file.name


def chunk_id_valid(value: Any) -> bool:
    return isinstance(value, str) and bool(re.match(r"^tsa23_2012_23ts13ra::pages_\d{3}_\d{3}$", value))


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


def word_count(value: str) -> int:
    return len([word for word in re.split(r"\s+", value.strip()) if word])


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
