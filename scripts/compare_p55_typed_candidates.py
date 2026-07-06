"""Compare P55 typed fact candidate JSON outputs without tracking raw values.

Raw worker outputs include source quotes and extracted public-document values,
so they remain under ignored ``runtime/`` paths. This script emits only
sanitized field-level comparison metadata: statuses, value hashes,
presence/shape flags, quote word counts, and agreement classes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


QUOTE_WORD_LIMIT = 25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two P55 typed fact candidates and render sanitized metrics.",
    )
    parser.add_argument("--packet-index", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--packet-id", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet_index = load_json(args.packet_index)
    packet = find_packet(packet_index, args.packet_id)
    candidates = load_candidates(args.eval_root, args.packet_id, packet)
    report = build_report(packet, candidates, args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


def find_packet(packet_index: dict[str, Any], packet_id: str) -> dict[str, Any]:
    for packet in packet_index.get("packets", []):
        if packet.get("packet_id") == packet_id:
            return packet
    raise ValueError(f"packet not found in packet index: {packet_id}")


def load_candidates(eval_root: Path, packet_id: str, packet: dict[str, Any]) -> list[dict[str, Any]]:
    summary_path = eval_root / packet_id / "summary.json"
    summary = load_json(summary_path)
    rows = summary.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"summary rows must be a list: {summary_path}")
    candidates: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        model = str(row.get("model") or packet.get("models", ["unknown"])[index])
        assistant_message = str(row.get("assistant_message", ""))
        parsed, parse_error = parse_candidate_json(assistant_message)
        result_file = Path(str(row.get("result_file", "")))
        usage = parse_usage(eval_root, packet_id, result_file)
        candidates.append(
            {
                "model": model,
                "status": row.get("status", "missing"),
                "classification": row.get("classification", ""),
                "parse_status": "parsed" if parsed is not None else "parse_failed",
                "parse_error": parse_error,
                "field_count": len(parsed.get("fields", {})) if isinstance(parsed, dict) else 0,
                "candidate": parsed,
                "worker_input_tokens": usage["input_tokens"],
                "worker_output_tokens": usage["output_tokens"],
                "runtime_result_file": runtime_path(resolve_result_file(eval_root, packet_id, result_file)),
            }
        )
    return candidates


def parse_candidate_json(text: str) -> tuple[dict[str, Any] | None, str]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
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
    if not isinstance(value.get("fields"), dict):
        return None, "missing-fields-object"
    return value, ""


def build_report(
    packet: dict[str, Any],
    candidates: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    comparisons = compare_candidates(candidates, packet)
    totals = summarize_totals(candidates, comparisons)
    return {
        "summary_id": f"p55_{packet['wave_id']}_comparison",
        "generated_utc": now_utc(),
        "phase": "P55",
        "packet_id": packet["packet_id"],
        "wave_id": packet["wave_id"],
        "document_id": packet["document_id"],
        "shape_id": packet["shape_id"],
        "packet_index": slash_path(args.packet_index),
        "runtime_output_root": slash_path(args.eval_root),
        "raw_output_policy": "Raw candidate values and source quotes remain ignored under runtime/.",
        "models": [candidate["model"] for candidate in candidates],
        "candidate_summaries": [
            {
                key: candidate[key]
                for key in [
                    "model",
                    "status",
                    "classification",
                    "parse_status",
                    "parse_error",
                    "field_count",
                    "worker_input_tokens",
                    "worker_output_tokens",
                    "runtime_result_file",
                ]
            }
            for candidate in candidates
        ],
        "field_comparisons": comparisons,
        "totals": totals,
        "gate_result": gate_result(candidates, comparisons),
        "recommended_next_move": recommendation(candidates, comparisons),
    }


def compare_candidates(
    candidates: list[dict[str, Any]],
    packet: dict[str, Any],
) -> list[dict[str, Any]]:
    if len(candidates) < 2:
        return []
    left, right = candidates[0], candidates[1]
    left_fields = candidate_fields(left)
    right_fields = candidate_fields(right)
    field_names = sorted(set(left_fields) | set(right_fields))
    expected_chunks = expected_chunk_ids(packet)
    rows: list[dict[str, Any]] = []
    for field in field_names:
        left_field = field_payload(left_fields.get(field))
        right_field = field_payload(right_fields.get(field))
        rows.append(
            {
                "field": field,
                "left_model": left["model"],
                "right_model": right["model"],
                "left": field_summary(left_field, expected_chunks),
                "right": field_summary(right_field, expected_chunks),
                "agreement_class": agreement_class(left_field, right_field),
            }
        )
    return rows


def candidate_fields(candidate: dict[str, Any]) -> dict[str, Any]:
    parsed = candidate.get("candidate")
    if not isinstance(parsed, dict):
        return {}
    fields = parsed.get("fields")
    return fields if isinstance(fields, dict) else {}


def field_payload(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def field_summary(field: dict[str, Any], expected_chunks: set[str]) -> dict[str, Any]:
    value = field.get("value")
    quote = field.get("source_quote")
    chunk_id = field.get("chunk_id")
    status = str(field.get("status", "missing"))
    source_quote_word_count = word_count(str(quote or ""))
    return {
        "status": status,
        "value_present": value is not None,
        "value_type": type(value).__name__ if value is not None else "null",
        "value_hash": stable_hash(value) if value is not None else "",
        "units_present": bool(field.get("units")),
        "page_anchor_present": bool(field.get("page_anchor")),
        "chunk_id_present": bool(chunk_id),
        "chunk_id_valid": chunk_id in expected_chunks if isinstance(chunk_id, str) else False,
        "source_quote_present": bool(quote),
        "source_quote_word_count": source_quote_word_count,
        "source_quote_over_limit": source_quote_word_count > QUOTE_WORD_LIMIT,
        "confidence_bucket": confidence_bucket(field.get("confidence")),
        "schema_issue": field_schema_issue(status, value, quote, chunk_id, field),
    }


def agreement_class(left: dict[str, Any], right: dict[str, Any]) -> str:
    left_status = str(left.get("status", "missing"))
    right_status = str(right.get("status", "missing"))
    left_value = left.get("value")
    right_value = right.get("value")
    if not left and not right:
        return "both_missing_field"
    if left_status == "not_found" and right_status == "not_found":
        return "both_not_found"
    if left_status != right_status:
        return "status_disagreement"
    if stable_normalize(left_value) == stable_normalize(right_value):
        return "value_agreement"
    if left_value is None or right_value is None:
        return "one_value_missing"
    return "value_disagreement"


def summarize_totals(
    candidates: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    agreement_counts: dict[str, int] = {}
    for row in comparisons:
        key = str(row["agreement_class"])
        agreement_counts[key] = agreement_counts.get(key, 0) + 1
    return {
        "candidate_count": len(candidates),
        "parsed_candidates": sum(1 for candidate in candidates if candidate["parse_status"] == "parsed"),
        "field_count": len(comparisons),
        "agreement_counts": agreement_counts,
        "fields_requiring_verification": sum(
            1
            for row in comparisons
            if requires_verification(row)
        ),
        "quote_over_limit_fields": sum(
            1
            for row in comparisons
            if row["left"]["source_quote_over_limit"] or row["right"]["source_quote_over_limit"]
        ),
        "invalid_chunk_id_fields": sum(
            1
            for row in comparisons
            if (row["left"]["chunk_id_present"] and not row["left"]["chunk_id_valid"])
            or (row["right"]["chunk_id_present"] and not row["right"]["chunk_id_valid"])
        ),
        "schema_issue_fields": sum(
            1 for row in comparisons if row["left"]["schema_issue"] or row["right"]["schema_issue"]
        ),
        "worker_input_tokens": sum(int(candidate["worker_input_tokens"]) for candidate in candidates),
        "worker_output_tokens": sum(int(candidate["worker_output_tokens"]) for candidate in candidates),
        "worker_cash_cost_usd": 0.0,
    }


def gate_result(candidates: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> str:
    if len(candidates) < 2:
        return "wave7-missing-candidate"
    if any(candidate["parse_status"] != "parsed" for candidate in candidates):
        return "wave7-candidate-parse-failed"
    if not comparisons:
        return "wave7-no-fields-compared"
    return "wave7-ready-for-disagreement-verification"


def recommendation(candidates: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> str:
    if any(candidate["parse_status"] != "parsed" for candidate in candidates):
        return "Repair typed candidate prompt or switch model before disagreement verification."
    verify_count = sum(1 for row in comparisons if requires_verification(row))
    return (
        f"Build a verifier ticket for {verify_count} disagreement or weak-evidence fields; "
        "do not send both full raw candidates to the paid supervisor unless the verifier fails."
    )


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Phase 55 {report['wave_id']} Comparison",
        "",
        "Raw candidate values and source quotes remain ignored under runtime paths.",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- packet_id: `{report['packet_id']}`",
        f"- gate_result: `{report['gate_result']}`",
        f"- models: `{', '.join(report['models'])}`",
        "",
        "## Candidate Summaries",
        "",
        "| Model | Status | Parse | Fields | Input Tokens | Output Tokens |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for candidate in report["candidate_summaries"]:
        lines.append(
            "| {model} | `{status}` | `{parse}` | {fields} | {input_tokens} | {output_tokens} |".format(
                model=candidate["model"],
                status=candidate["status"],
                parse=candidate["parse_status"],
                fields=candidate["field_count"],
                input_tokens=candidate["worker_input_tokens"],
                output_tokens=candidate["worker_output_tokens"],
            )
        )
    lines.extend(["", "## Aggregate Totals", ""])
    for key, value in report["totals"].items():
        rendered = json.dumps(value, sort_keys=True) if isinstance(value, dict) else str(value)
        lines.append(f"- {key}: `{rendered}`")
    lines.extend(
        [
            "",
            "## Field Comparison",
            "",
            "| Field | Agreement Class | Left Status | Right Status | Left Quote Words | Right Quote Words | Schema Issue |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in report["field_comparisons"]:
        lines.append(
            "| {field} | `{klass}` | `{left}` | `{right}` | {left_words} | {right_words} | `{schema_issue}` |".format(
                field=row["field"],
                klass=row["agreement_class"],
                left=row["left"]["status"],
                right=row["right"]["status"],
                left_words=row["left"]["source_quote_word_count"],
                right_words=row["right"]["source_quote_word_count"],
                schema_issue=row["left"]["schema_issue"] or row["right"]["schema_issue"],
            )
        )
    lines.extend(["", "## Recommendation", "", str(report["recommended_next_move"]), ""])
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


def expected_chunk_ids(packet: dict[str, Any]) -> set[str]:
    ticket_path = Path(str(packet.get("ticket_path", "")))
    if ticket_path.exists():
        text = ticket_path.read_text(encoding="utf-8-sig")
        matches = re.findall(r"- `([^`]+::pages_\d{3}_\d{3})`", text)
        if matches:
            return set(matches)
    return set()


def requires_verification(row: dict[str, Any]) -> bool:
    if row["agreement_class"] not in {"both_not_found", "value_agreement"}:
        return True
    return bool(
        row["left"]["schema_issue"]
        or row["right"]["schema_issue"]
        or row["left"]["source_quote_over_limit"]
        or row["right"]["source_quote_over_limit"]
        or (row["left"]["chunk_id_present"] and not row["left"]["chunk_id_valid"])
        or (row["right"]["chunk_id_present"] and not row["right"]["chunk_id_valid"])
    )


def field_schema_issue(
    status: str,
    value: Any,
    quote: Any,
    chunk_id: Any,
    field: dict[str, Any],
) -> bool:
    if status == "not_found":
        return any(
            [
                value is not None,
                bool(field.get("units")),
                bool(field.get("page_anchor")),
                bool(chunk_id),
                bool(quote),
                confidence_bucket(field.get("confidence")) != "zero",
            ]
        )
    if status in {"found", "uncertain"}:
        return value is None or not quote or not chunk_id or not field.get("page_anchor")
    return True


def resolve_result_file(eval_root: Path, packet_id: str, result_file: Path) -> Path:
    if result_file.is_absolute():
        return result_file
    if result_file.exists():
        return result_file
    return eval_root / packet_id / result_file.name


def stable_hash(value: Any) -> str:
    normalized = stable_normalize(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def stable_normalize(value: Any) -> str:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value.strip().lower())
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


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


def runtime_path(path: Path) -> str:
    return slash_path(path) if not path.is_absolute() else slash_path(Path(*path.parts[-6:]))


def slash_path(path: Path) -> str:
    return path.as_posix()


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
