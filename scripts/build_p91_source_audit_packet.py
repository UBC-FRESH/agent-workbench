"""Build the P91 source-audit sample and decision packet.

The script reads ignored P90 repaired JSONL and ignored P89 source tickets, but
tracked outputs contain sanitized identifiers, counts, hashes, and supervisor
audit classifications only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_P90_SUMMARY = Path(
    "benchmarks/document_library/p90_full_document_candidate_packet_summary.json"
)
DEFAULT_OUTPUT_DIR = Path("benchmarks/document_library")
DEFAULT_SAMPLE_MANIFEST = DEFAULT_OUTPUT_DIR / "p91_source_audit_sample_manifest.json"
DEFAULT_AUDIT_PACKET = DEFAULT_OUTPUT_DIR / "p91_supervisor_source_audit_packet.json"
DEFAULT_REPORTING_DRAFT = DEFAULT_OUTPUT_DIR / "p91_reporting_worker_draft_packet.json"
DEFAULT_DECISION_PACKET = DEFAULT_OUTPUT_DIR / "p91_source_audit_decision_packet.json"
DEFAULT_SCORING_DELTA = (
    DEFAULT_OUTPUT_DIR / "p91_source_quote_scoring_recalibration_delta.json"
)
SAMPLE_SHAPE = {
    "valid_structure_records": 6,
    "valid_content_metadata_records": 6,
    "invalid_run_records": 4,
}
AUDITABLE_STATUSES = {"accepted", "repairable", "rejected", "needs_review"}
ORIGINAL_BINARY_SCORING_BASELINE = {
    "accepted_record_count": 8,
    "repairable_record_count": 2,
    "rejected_record_count": 6,
    "needs_review_record_count": 0,
    "sample_useful_yield": 0.625,
    "decision": "promote_seed",
    "defect_class_counts": {
        "none": 8,
        "schema_or_protocol_defect": 2,
        "source_quote_not_found": 6,
        "zero_record_defect": 6,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build P91 source-audit sample and decision packet."
    )
    parser.add_argument("--p90-summary", type=Path, default=DEFAULT_P90_SUMMARY)
    parser.add_argument("--sample-manifest", type=Path, default=DEFAULT_SAMPLE_MANIFEST)
    parser.add_argument("--audit-packet", type=Path, default=DEFAULT_AUDIT_PACKET)
    parser.add_argument("--reporting-draft", type=Path, default=DEFAULT_REPORTING_DRAFT)
    parser.add_argument("--decision-packet", type=Path, default=DEFAULT_DECISION_PACKET)
    parser.add_argument("--scoring-delta", type=Path, default=DEFAULT_SCORING_DELTA)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p90_summary = load_json(args.p90_summary)
    sample_entries = select_sample_entries(p90_summary)
    audit_rows = [audit_entry(entry) for entry in sample_entries]
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    sample_manifest = build_sample_manifest(generated_utc, p90_summary, sample_entries)
    audit_packet = build_audit_packet(generated_utc, p90_summary, audit_rows)
    reporting_draft = build_reporting_draft(generated_utc, audit_packet)
    decision_packet = build_decision_packet(
        generated_utc, audit_packet, reporting_draft
    )
    scoring_delta = build_scoring_delta(generated_utc, audit_packet, decision_packet)

    write_json(args.sample_manifest, sample_manifest)
    write_json(args.audit_packet, audit_packet)
    write_json(args.reporting_draft, reporting_draft)
    write_json(args.decision_packet, decision_packet)
    write_json(args.scoring_delta, scoring_delta)
    print(f"wrote {args.sample_manifest}")
    print(f"wrote {args.audit_packet}")
    print(f"wrote {args.reporting_draft}")
    print(f"wrote {args.decision_packet}")
    print(f"wrote {args.scoring_delta}")
    print(
        "audited="
        f"{audit_packet['record_audit_count']} records, "
        f"{audit_packet['run_defect_count']} run defects"
    )
    return 0


def select_sample_entries(p90_summary: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    valid_structure = collect_records(
        p90_summary, ticket_type="structure", validation_status="valid"
    )
    valid_content = collect_records(
        p90_summary, ticket_type="content_metadata", validation_status="valid"
    )
    invalid_records = collect_records(
        p90_summary, ticket_type=None, validation_status="invalid"
    )

    for record in spread_select(
        valid_structure, SAMPLE_SHAPE["valid_structure_records"]
    ):
        entries.append(sample_record("valid_structure", record))
    for record in spread_select(
        valid_content, SAMPLE_SHAPE["valid_content_metadata_records"]
    ):
        entries.append(sample_record("valid_content_metadata", record))
    for record in spread_select(invalid_records, SAMPLE_SHAPE["invalid_run_records"]):
        entries.append(sample_record("invalid_run_record", record))

    for run in p90_summary["zero_repaired_record_runs"]:
        entries.append(
            {
                "sample_id": "",
                "sample_class": "zero_record_run",
                "sample_kind": "run_defect",
                "run_id": run["run_id"],
                "ticket_id": run["ticket_id"],
                "ticket_type": run["ticket_type"],
                "validation_status": run["validation_status"],
                "fatal_error_count": run["fatal_error_count"],
            }
        )

    for index, entry in enumerate(entries, start=1):
        entry["sample_id"] = f"p91_sample_{index:03d}"
    return entries


def collect_records(
    p90_summary: dict[str, Any], ticket_type: str | None, validation_status: str
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    runs = sorted(p90_summary["runs"], key=lambda item: str(item["run_id"]))
    for run in runs:
        if ticket_type is not None and run["ticket_type"] != ticket_type:
            continue
        if run["validation_status"] != validation_status:
            continue
        repaired_path = Path(run["repaired_jsonl_path"])
        if not repaired_path.exists():
            continue
        for record_index, record in enumerate(read_jsonl(repaired_path), start=1):
            records.append(
                {
                    "run": run,
                    "record": record,
                    "record_index": record_index,
                }
            )
    return records


def spread_select(records: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    if len(records) <= count:
        return records
    if count <= 1:
        return [records[0]]
    indexes = {
        round(index * (len(records) - 1) / (count - 1)) for index in range(count)
    }
    return [records[index] for index in sorted(indexes)]


def sample_record(sample_class: str, item: dict[str, Any]) -> dict[str, Any]:
    run = item["run"]
    record = item["record"]
    source_quote = str(record.get("source_quote", ""))
    return {
        "sample_id": "",
        "sample_class": sample_class,
        "sample_kind": "record",
        "run_id": run["run_id"],
        "ticket_id": run["ticket_id"],
        "ticket_type": run["ticket_type"],
        "validation_status": run["validation_status"],
        "fatal_error_count": run["fatal_error_count"],
        "record_index": item["record_index"],
        "record_id": str(record.get("record_id", "")),
        "object_type": str(record.get("object_type", "")),
        "title": str(record.get("title", "")),
        "page_anchor": str(record.get("page_anchor", "")),
        "source_quote_sha256": sha256_text(source_quote),
        "source_quote_char_count": len(source_quote),
        "candidate_path": run["repaired_jsonl_path"],
        "validation_report_path": run["validation_report_path"],
        "ticket_path": run["ticket_path"],
        "record": record,
    }


def audit_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if entry["sample_kind"] == "run_defect":
        return audit_run_defect(entry)
    record = entry["record"]
    source_text = extract_source_excerpt(Path(entry["ticket_path"]))
    source_quote = str(record.get("source_quote", ""))
    source_assessment = assess_source_anchor(source_text, source_quote)
    source_anchor_verdict = source_assessment["source_anchor_verdict"]
    useful = is_useful_record(record)
    schema_valid = entry["validation_status"] == "valid"

    if schema_valid and source_assessment["support_level"] == "exact" and useful:
        audit_status = "accepted"
        defect_class = "none"
        functional_success_level = "A_accepted"
        repair_effort = "none"
        rationale = "Schema-valid candidate with an exact source quote in the bounded ticket excerpt and enough title/summary specificity for retrieval."
    elif useful and source_assessment["support_level"] in {"fragment", "fuzzy"}:
        audit_status = "repairable"
        defect_class = (
            "source_quote_contains_exact_anchor_plus_synthesis"
            if source_assessment["support_level"] == "fragment"
            else "source_quote_needs_human_anchor_repair"
        )
        functional_success_level = (
            "B_minor_repair"
            if schema_valid and source_assessment["support_level"] == "fragment"
            else "C_repairable"
        )
        repair_effort = (
            "minor_source_quote_repair"
            if schema_valid
            else "bounded_schema_and_source_quote_repair"
        )
        rationale = "Candidate appears source-backed and useful, but the source_quote is not a clean exact quote; it needs quote-anchor repair rather than rejection."
    elif source_assessment["support_level"] == "exact" and useful:
        audit_status = "repairable"
        defect_class = "schema_or_protocol_defect"
        functional_success_level = "C_repairable"
        repair_effort = "bounded_schema_repair"
        rationale = "Candidate appears source-backed, but deterministic validation already marked the run invalid."
    elif not useful:
        audit_status = "rejected"
        defect_class = "malformed_or_not_useful"
        functional_success_level = "F_protocol_failure"
        repair_effort = "not_repairable"
        rationale = "Candidate lacks enough title, summary, or source quote specificity for retrieval."
    else:
        audit_status = "rejected"
        defect_class = "unsupported_source_anchor"
        functional_success_level = "E_rejected"
        repair_effort = "not_repairable"
        rationale = "Candidate source_quote has no sufficient exact, fragment, or fuzzy support in the bounded ticket excerpt."

    return {
        "sample_id": entry["sample_id"],
        "sample_kind": "record",
        "sample_class": entry["sample_class"],
        "record_id": entry["record_id"],
        "run_id": entry["run_id"],
        "ticket_id": entry["ticket_id"],
        "ticket_type": entry["ticket_type"],
        "validation_status": entry["validation_status"],
        "object_type": entry["object_type"],
        "page_anchor": entry["page_anchor"],
        "source_quote_sha256": entry["source_quote_sha256"],
        "source_quote_char_count": entry["source_quote_char_count"],
        "source_anchor_verdict": source_anchor_verdict,
        "source_support_level": source_assessment["support_level"],
        "source_support_reason": source_assessment["reason"],
        "repair_effort": repair_effort,
        "functional_success_level": functional_success_level,
        "usefulness_verdict": "useful" if useful else "not_useful",
        "audit_status": audit_status,
        "defect_class": defect_class,
        "rationale": rationale,
    }


def audit_run_defect(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": entry["sample_id"],
        "sample_kind": "run_defect",
        "sample_class": entry["sample_class"],
        "run_id": entry["run_id"],
        "ticket_id": entry["ticket_id"],
        "ticket_type": entry["ticket_type"],
        "validation_status": entry["validation_status"],
        "fatal_error_count": entry["fatal_error_count"],
        "audit_status": "rejected",
        "defect_class": "zero_record_defect",
        "source_anchor_verdict": "not_applicable",
        "source_support_level": "none",
        "source_support_reason": "run emitted no repaired candidate record",
        "repair_effort": "rerun_or_prompt_repair",
        "functional_success_level": "F_protocol_failure",
        "usefulness_verdict": "not_useful",
        "rationale": "Worker completed but emitted no repaired candidate records for this ticket.",
    }


def build_sample_manifest(
    generated_utc: str, p90_summary: dict[str, Any], entries: list[dict[str, Any]]
) -> dict[str, Any]:
    sanitized = []
    for entry in entries:
        clean = {key: value for key, value in entry.items() if key != "record"}
        sanitized.append(clean)
    return {
        "schema_version": 1,
        "phase": "P91",
        "manifest_id": "p91_source_audit_sample_manifest",
        "generated_utc": generated_utc,
        "source_summary": "benchmarks/document_library/p90_full_document_candidate_packet_summary.json",
        "document_id": p90_summary["document_id"],
        "source_slice": p90_summary["source_slice"],
        "sample_shape": SAMPLE_SHAPE,
        "sample_count": len(entries),
        "sample_classes": dict(Counter(entry["sample_class"] for entry in entries)),
        "samples": sanitized,
        "public_safety": public_safety_flags(),
    }


def build_audit_packet(
    generated_utc: str, p90_summary: dict[str, Any], rows: list[dict[str, Any]]
) -> dict[str, Any]:
    record_rows = [row for row in rows if row["sample_kind"] == "record"]
    defect_rows = [row for row in rows if row["sample_kind"] == "run_defect"]
    return {
        "schema_version": 1,
        "phase": "P91",
        "packet_id": "p91_supervisor_source_audit_packet",
        "generated_utc": generated_utc,
        "document_id": p90_summary["document_id"],
        "source_slice": p90_summary["source_slice"],
        "source_summary": "benchmarks/document_library/p90_full_document_candidate_packet_summary.json",
        "supervisor_audit_method": "bounded source-quote containment plus field usefulness check against ignored P89 ticket excerpts",
        "audit_status_counts": dict(Counter(row["audit_status"] for row in rows)),
        "defect_class_counts": dict(Counter(row["defect_class"] for row in rows)),
        "functional_success_level_counts": dict(
            Counter(row["functional_success_level"] for row in rows)
        ),
        "repair_effort_counts": dict(Counter(row["repair_effort"] for row in rows)),
        "record_audit_count": len(record_rows),
        "run_defect_count": len(defect_rows),
        "accepted_record_count": sum(
            1 for row in record_rows if row["audit_status"] == "accepted"
        ),
        "repairable_record_count": sum(
            1 for row in record_rows if row["audit_status"] == "repairable"
        ),
        "rejected_record_count": sum(
            1 for row in record_rows if row["audit_status"] == "rejected"
        ),
        "needs_review_record_count": sum(
            1 for row in record_rows if row["audit_status"] == "needs_review"
        ),
        "audit_rows": rows,
        "accepted_record_scope_note": "Accepted counts apply only to this bounded P91 audit sample, not the full P90 packet.",
        "public_safety": public_safety_flags(),
    }


def build_reporting_draft(
    generated_utc: str, audit_packet: dict[str, Any]
) -> dict[str, Any]:
    accepted = audit_packet["accepted_record_count"]
    repairable = audit_packet["repairable_record_count"]
    rejected = audit_packet["rejected_record_count"]
    defects = audit_packet["run_defect_count"]
    return {
        "schema_version": 1,
        "phase": "P91",
        "draft_id": "p91_reporting_worker_draft_packet",
        "generated_utc": generated_utc,
        "authority": "non_authoritative_reporting_draft",
        "source_of_truth": "benchmarks/document_library/p91_supervisor_source_audit_packet.json",
        "summary": (
            "The bounded P91 audit sample found "
            f"{accepted} accepted records, {repairable} repairable records, "
            f"{rejected} rejected records, and {defects} run-level zero-record defects."
        ),
        "draft_recommendation": draft_recommendation(audit_packet),
        "quality_pattern": quality_pattern(audit_packet),
        "protocol_pattern": protocol_pattern(audit_packet),
        "public_safety": public_safety_flags(),
    }


def build_decision_packet(
    generated_utc: str,
    audit_packet: dict[str, Any],
    reporting_draft: dict[str, Any],
) -> dict[str, Any]:
    accepted = audit_packet["accepted_record_count"]
    repairable = audit_packet["repairable_record_count"]
    useful = accepted + repairable
    record_count = audit_packet["record_audit_count"]
    defect_counts = audit_packet["defect_class_counts"]
    protocol_defects = sum(
        count
        for defect, count in defect_counts.items()
        if defect in {"schema_or_protocol_defect", "zero_record_defect"}
    )
    if useful >= max(8, record_count // 2) and protocol_defects <= 6:
        decision = "scale_audit"
    elif accepted >= 4 and repairable >= 2:
        decision = "promote_seed"
    elif useful > 0:
        decision = "repair_protocol"
    else:
        decision = "stop"
    return {
        "schema_version": 1,
        "phase": "P91",
        "packet_id": "p91_source_audit_decision_packet",
        "generated_utc": generated_utc,
        "decision": decision,
        "quality_outcome": {
            "audited_record_count": record_count,
            "accepted_record_count": accepted,
            "repairable_record_count": repairable,
            "rejected_record_count": audit_packet["rejected_record_count"],
            "needs_review_record_count": audit_packet["needs_review_record_count"],
            "sample_useful_yield": round(useful / record_count, 3)
            if record_count
            else 0.0,
        },
        "protocol_outcome": {
            "run_defect_count": audit_packet["run_defect_count"],
            "defect_class_counts": defect_counts,
            "functional_success_level_counts": audit_packet[
                "functional_success_level_counts"
            ],
            "repair_effort_counts": audit_packet["repair_effort_counts"],
            "dominant_protocol_risk": dominant_protocol_risk(defect_counts),
        },
        "economics_governance_outcome": {
            "task_economics": "P90 produced source-backed audited sample records without a direct-supervisor extraction baseline.",
            "governance_overhead": "P91 required roadmap, changelog, issue, PR, and validation work that must remain separate from intrinsic task economics.",
            "next_cost_gate": "Do not scale full audit until protocol defects and accepted/repairable sample yield are reviewed.",
        },
        "reporting_worker_draft_path": "benchmarks/document_library/p91_reporting_worker_draft_packet.json",
        "supervisor_authority_path": "benchmarks/document_library/p91_supervisor_source_audit_packet.json",
        "accepted_record_scope_note": audit_packet["accepted_record_scope_note"],
        "public_safety": public_safety_flags(),
        "reporting_draft_summary": reporting_draft["summary"],
    }


def build_scoring_delta(
    generated_utc: str,
    audit_packet: dict[str, Any],
    decision_packet: dict[str, Any],
) -> dict[str, Any]:
    recalibrated = {
        "accepted_record_count": audit_packet["accepted_record_count"],
        "repairable_record_count": audit_packet["repairable_record_count"],
        "rejected_record_count": audit_packet["rejected_record_count"],
        "needs_review_record_count": audit_packet["needs_review_record_count"],
        "sample_useful_yield": decision_packet["quality_outcome"][
            "sample_useful_yield"
        ],
        "decision": decision_packet["decision"],
        "defect_class_counts": audit_packet["defect_class_counts"],
    }
    baseline = ORIGINAL_BINARY_SCORING_BASELINE
    return {
        "schema_version": 1,
        "phase": "P91",
        "report_id": "p91_source_quote_scoring_recalibration_delta",
        "generated_utc": generated_utc,
        "change_reason": "Exact source-quote containment was too blunt for tables and synthesized-but-source-backed quotes.",
        "original_binary_scoring": baseline,
        "recalibrated_scoring": recalibrated,
        "delta": {
            "accepted_record_count": recalibrated["accepted_record_count"]
            - baseline["accepted_record_count"],
            "repairable_record_count": recalibrated["repairable_record_count"]
            - baseline["repairable_record_count"],
            "rejected_record_count": recalibrated["rejected_record_count"]
            - baseline["rejected_record_count"],
            "sample_useful_yield": round(
                recalibrated["sample_useful_yield"] - baseline["sample_useful_yield"],
                3,
            ),
            "decision_changed": recalibrated["decision"] != baseline["decision"],
        },
        "functional_success_level_counts": audit_packet[
            "functional_success_level_counts"
        ],
        "repair_effort_counts": audit_packet["repair_effort_counts"],
        "public_safety": public_safety_flags(),
    }


def draft_recommendation(audit_packet: dict[str, Any]) -> str:
    accepted = audit_packet["accepted_record_count"]
    repairable = audit_packet["repairable_record_count"]
    protocol_defects = sum(
        count
        for defect, count in audit_packet["defect_class_counts"].items()
        if defect in {"schema_or_protocol_defect", "zero_record_defect"}
    )
    if accepted >= 4 and repairable >= 2:
        return "promote_seed_after_supervisor_review"
    if accepted + repairable and protocol_defects:
        return "repair_protocol_before_scale"
    if accepted >= 8:
        return "scale_audit_after_supervisor_review"
    if accepted + repairable:
        return "continue_bounded_audit"
    return "stop_or_switch_prompt"


def quality_pattern(audit_packet: dict[str, Any]) -> str:
    counts = audit_packet["audit_status_counts"]
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def protocol_pattern(audit_packet: dict[str, Any]) -> str:
    counts = audit_packet["defect_class_counts"]
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def dominant_protocol_risk(defect_counts: dict[str, int]) -> str:
    risks = {key: value for key, value in defect_counts.items() if key != "none"}
    if not risks:
        return "none"
    return max(risks.items(), key=lambda item: (item[1], item[0]))[0]


def extract_source_excerpt(ticket_path: Path) -> str:
    text = ticket_path.read_text(encoding="utf-8")
    marker = "## Source Excerpt"
    if marker not in text:
        return ""
    source = text.split(marker, 1)[1]
    fenced = re.search(r"```text\s*(.*?)\s*```", source, flags=re.S)
    if fenced:
        return fenced.group(1)
    return source


def assess_source_anchor(source_text: str, quote: str) -> dict[str, str]:
    normalized_source = normalize_text(source_text)
    normalized_quote = normalize_text(quote)
    if not normalized_quote:
        return {
            "source_anchor_verdict": "no_source_quote",
            "support_level": "none",
            "reason": "empty source_quote",
        }
    if normalized_quote in normalized_source:
        return {
            "source_anchor_verdict": "exact_source_quote",
            "support_level": "exact",
            "reason": "source_quote is an exact normalized substring of the bounded excerpt",
        }
    if quote_contains_source_line(source_text, quote):
        return {
            "source_anchor_verdict": "source_quote_contains_exact_fragment_plus_synthesis",
            "support_level": "fragment",
            "reason": "source_quote contains at least one exact source line plus synthesized or normalized material",
        }
    if token_support_ratio(source_text, quote) >= 0.72:
        return {
            "source_anchor_verdict": "source_quote_has_fuzzy_source_support",
            "support_level": "fuzzy",
            "reason": "source_quote terms are mostly present in the bounded excerpt but not as an exact quote",
        }
    return {
        "source_anchor_verdict": "source_quote_missing",
        "support_level": "none",
        "reason": "source_quote is not sufficiently supported by the bounded excerpt",
    }


def quote_contains_source_line(source_text: str, quote: str) -> bool:
    normalized_quote = normalize_text(quote)
    for line in source_text.splitlines():
        normalized_line = normalize_text(line)
        if len(normalized_line) >= 24 and normalized_line in normalized_quote:
            return True
    return False


def token_support_ratio(source_text: str, quote: str) -> float:
    quote_tokens = content_tokens(quote)
    if not quote_tokens:
        return 0.0
    source_tokens = set(content_tokens(source_text))
    supported = [token for token in quote_tokens if token in source_tokens]
    return len(supported) / len(quote_tokens)


def content_tokens(value: str) -> list[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "for",
        "in",
        "is",
        "of",
        "or",
        "the",
        "to",
    }
    return [
        token
        for token in re.findall(r"[a-z0-9.]+", value.lower())
        if len(token) > 1 and token not in stopwords
    ]


def contains_normalized(source_text: str, quote: str) -> bool:
    normalized_source = normalize_text(source_text)
    normalized_quote = normalize_text(quote)
    return bool(normalized_quote) and normalized_quote in normalized_source


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def is_useful_record(record: dict[str, Any]) -> bool:
    title = str(record.get("title", "")).strip()
    summary = str(record.get("summary", "")).strip()
    quote = str(record.get("source_quote", "")).strip()
    object_type = str(record.get("object_type", "")).strip()
    return bool(title and summary and quote and object_type) and len(summary) >= 20


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def public_safety_flags() -> dict[str, bool]:
    return {
        "raw_source_text_tracked": False,
        "raw_worker_output_tracked": False,
        "source_quotes_tracked": False,
        "provider_urls_or_headers_tracked": False,
        "personal_paths_tracked": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
