"""Summarize P55 quote-repair prepass output without tracking raw values."""

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
ALLOWED_ACTIONS = {"repaired", "unchanged", "needs_verifier", "needs_supervisor"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a P55 quote repair run.")
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
    repairs = parsed.get("repairs", {}) if isinstance(parsed, dict) else {}
    field_rows = summarize_repairs(repairs)
    usage = parse_usage(args.eval_root, packet["packet_id"], Path(str(row.get("result_file", ""))))
    report = {
        "summary_id": "p55_wave10_quote_repair_prepass",
        "generated_utc": now_utc(),
        "phase": "P55",
        "wave_id": packet["wave_id"],
        "packet_id": packet["packet_id"],
        "source_packet_id": packet["source_packet_id"],
        "source_verifier_packet_id": packet["source_verifier_packet_id"],
        "document_id": packet["document_id"],
        "repair_model": packet["repair_model"],
        "raw_output_policy": "Raw repair values and quotes remain ignored under runtime/.",
        "status": row.get("status", "missing-summary"),
        "harness_classification": row.get("classification", ""),
        "parse_status": "parsed" if parsed is not None else "parse_failed",
        "parse_error": parse_error,
        "expected_field_count": len(packet["fields"]),
        "repair_field_count": len(field_rows),
        "missing_fields": sorted(set(packet["fields"]) - {row["field"] for row in field_rows}),
        "extra_fields": sorted({row["field"] for row in field_rows} - set(packet["fields"])),
        "field_repairs": field_rows,
        "totals": summarize_totals(field_rows, usage),
        "gate_result": gate_result(packet, parsed, field_rows),
        "recommended_next_move": recommendation(field_rows),
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
    if not isinstance(value.get("repairs"), dict):
        return None, "missing-repairs-object"
    return value, ""


def summarize_repairs(repairs: Any) -> list[dict[str, Any]]:
    if not isinstance(repairs, dict):
        return []
    rows = []
    for field, payload in repairs.items():
        if not isinstance(payload, dict):
            payload = {}
        quote = str(payload.get("source_quote") or "")
        value = payload.get("repaired_value")
        chunk_id = payload.get("repaired_chunk_id")
        rows.append(
            {
                "field": str(field),
                "action": str(payload.get("action", "missing")),
                "repaired_status": str(payload.get("repaired_status", "missing")),
                "repaired_value_present": value is not None,
                "repaired_value_type": type(value).__name__ if value is not None else "null",
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
        )
    return sorted(rows, key=lambda row: row["field"])


def summarize_totals(field_rows: list[dict[str, Any]], usage: dict[str, int]) -> dict[str, Any]:
    action_counts = Counter(row["action"] for row in field_rows)
    return {
        "action_counts": dict(sorted(action_counts.items())),
        "repaired_or_unchanged_fields": sum(
            1 for row in field_rows if row["action"] in {"repaired", "unchanged"}
        ),
        "needs_verifier_fields": sum(1 for row in field_rows if row["action"] == "needs_verifier"),
        "needs_supervisor_fields": sum(1 for row in field_rows if row["action"] == "needs_supervisor"),
        "invalid_action_fields": sum(1 for row in field_rows if row["action"] not in ALLOWED_ACTIONS),
        "quote_over_limit_fields": sum(1 for row in field_rows if row["source_quote_over_limit"]),
        "invalid_chunk_id_fields": sum(
            1
            for row in field_rows
            if row["repaired_chunk_id_present"] and not row["repaired_chunk_id_valid"]
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
        return "wave10-repair-parse-failed"
    if set(packet["fields"]) != {row["field"] for row in field_rows}:
        return "wave10-field-set-mismatch"
    if any(row["action"] not in ALLOWED_ACTIONS for row in field_rows):
        return "wave10-invalid-action-label"
    if any(row["source_quote_over_limit"] for row in field_rows):
        return "wave10-quote-limit-failed"
    if any(row["repaired_chunk_id_present"] and not row["repaired_chunk_id_valid"] for row in field_rows):
        return "wave10-chunk-id-repair-needed"
    return "wave10-ready-for-post-repair-verifier"


def recommendation(field_rows: list[dict[str, Any]]) -> str:
    supervisor_fields = [row["field"] for row in field_rows if row["action"] == "needs_supervisor"]
    if supervisor_fields:
        return "Keep these fields in supervisor lane: " + ", ".join(supervisor_fields)
    return "Run a post-repair verifier on repaired/unchanged fields before supervisor sampling."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 55 Wave 10 Quote Repair Results",
        "",
        "Raw repair values and source quotes remain ignored under runtime paths.",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- gate_result: `{report['gate_result']}`",
        f"- repair_model: `{report['repair_model']}`",
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
            "## Field Repairs",
            "",
            "| Field | Action | Status | Quote Words | Reason Code |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for row in report["field_repairs"]:
        lines.append(
            "| {field} | `{action}` | `{status}` | {words} | `{reason}` |".format(
                field=row["field"],
                action=row["action"],
                status=row["repaired_status"],
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
