"""Summarize the P92 whole-document supervisor live run.

Raw delegated-supervisor reports remain ignored runtime evidence. This helper
promotes only public-safe counts, verdicts, economics fields, and decision
metadata into a tracked P92 decision packet.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REPORT = Path(
    "runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/"
    "reports/p92_tsa23_2012_23tsdp12_supervisor_report.json"
)
DEFAULT_VALIDATION = Path(
    "runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/"
    "reports/p92_tsa23_2012_23tsdp12_supervisor_report.validation.json"
)
DEFAULT_BRIDGE_REPORT = Path(
    "runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/"
    "bridge/p92_bridge_report_r3.md"
)
DEFAULT_TOKEN_RECORD = Path(
    "runtime/supervisor_tokens/p92_whole_document_supervisor_live_r3/"
    "p92-whole-document-supervisor-live-r3.tokens.json"
)
DEFAULT_OUTPUT = Path(
    "benchmarks/document_library/p92_whole_document_supervisor_decision_packet.json"
)
P90_P91_MINIMUM_COORDINATOR_TOKENS = 236_008


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the tracked P92 whole-document supervisor decision packet."
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--bridge-report", type=Path, default=DEFAULT_BRIDGE_REPORT)
    parser.add_argument("--token-record", type=Path, default=DEFAULT_TOKEN_RECORD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = load_json(args.report)
    validation = load_json(args.validation)
    bridge_text = args.bridge_report.read_text(encoding="utf-8-sig")
    token_record = load_json(args.token_record)
    packet = build_packet(
        report,
        validation,
        bridge_text,
        token_record,
        evidence_paths={
            "report_path": args.report.as_posix(),
            "validation_path": args.validation.as_posix(),
            "bridge_report_path": args.bridge_report.as_posix(),
            "token_record_path": args.token_record.as_posix(),
        },
    )
    write_json(args.output, packet)
    print(f"wrote {args.output}")
    return 0


def build_packet(
    report: dict[str, Any],
    validation: dict[str, Any],
    bridge_text: str,
    token_record: dict[str, Any],
    *,
    evidence_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    records = report.get("records", [])
    if not isinstance(records, list):
        records = []
    confidence_counts = Counter(str(record.get("confidence", "")) for record in records)
    object_type_counts = Counter(
        str(record.get("object_type", "")) for record in records
    )
    bridge = parse_bridge_report(bridge_text)
    usage = token_record["usage"]
    evidence_paths = evidence_paths or {
        "report_path": DEFAULT_REPORT.as_posix(),
        "validation_path": DEFAULT_VALIDATION.as_posix(),
        "bridge_report_path": DEFAULT_BRIDGE_REPORT.as_posix(),
        "token_record_path": DEFAULT_TOKEN_RECORD.as_posix(),
    }
    total_delta = int(usage["codex_total_token_delta"])
    economics_decision = (
        "not_yet_proven"
        if total_delta >= P90_P91_MINIMUM_COORDINATOR_TOKENS
        else "promising"
    )
    return {
        "schema_version": 1,
        "phase": "P92",
        "packet_id": "p92_whole_document_supervisor_decision_packet",
        "generated_utc": now_utc(),
        "decision": "accept_seed_for_coordinator_audit",
        "decision_rationale": (
            "The full-tool delegated supervisor produced a deterministic-valid "
            "whole-document seed with no bridge deviations. Promote the seed to "
            "coordinator audit, but do not claim an economics win until launch "
            "and cached-context overhead are reduced."
        ),
        "quality_outcome": {
            "report_validation_status": validation["status"],
            "validation_fatal_error_count": validation["fatal_error_count"],
            "candidate_record_count": validation["candidate_record_count"],
            "source_document_read": bool(report.get("source_document_read")),
            "final_signal": report.get("final_signal"),
            "next_action": report.get("next_action"),
            "output_quality": report.get("output_quality"),
            "gap_count": len(report.get("gaps", [])),
            "confidence_counts": dict(sorted(confidence_counts.items())),
            "object_type_counts": dict(sorted(object_type_counts.items())),
        },
        "protocol_outcome": {
            "bridge_status": bridge["status"],
            "model_match": bridge["model_match"],
            "resolved_model": bridge["resolved_model"],
            "permission_levels": bridge["permission_levels"],
            "final_marker_present": bridge["final_marker_present"],
            "tool_names": bridge["tool_names"],
            "bridge_deviation_count": bridge["deviation_count"],
            "wrong_root_retry_required": True,
            "wrong_root_retry_note": (
                "The first live attempt produced a useful report in the wrong "
                "workspace root. The bridge was repaired to open Agent Workbench "
                "before launch; retry R3 accepted."
            ),
        },
        "economics_outcome": {
            "economics_decision": economics_decision,
            "token_record_scope": token_record["scope"],
            "supervisor_input_tokens": usage["supervisor_input_tokens"],
            "supervisor_cached_input_tokens": usage["supervisor_cached_input_tokens"],
            "supervisor_output_tokens": usage["supervisor_output_tokens"],
            "supervisor_reasoning_output_tokens": usage[
                "supervisor_reasoning_output_tokens"
            ],
            "codex_total_token_delta": total_delta,
            "p90_p91_minimum_coordinator_tokens_observed": (
                P90_P91_MINIMUM_COORDINATOR_TOKENS
            ),
            "cash_cost_usd": round(supervisor_cost_usd(token_record), 6),
            "economics_caveat": (
                "This accepted run proves a useful quality/protocol seed, but "
                "the measured coordinator token delta is still larger than the "
                "P90/P91 chunk-pipeline minimum because launch/retry/context "
                "overhead remains high."
            ),
        },
        "raw_evidence": {
            **evidence_paths,
            "raw_evidence_policy": "runtime paths are ignored and not promoted",
        },
        "public_safety": {
            "raw_source_text_tracked": False,
            "raw_worker_output_tracked": False,
            "source_quotes_tracked": False,
            "provider_urls_or_headers_tracked": False,
            "personal_paths_tracked": False,
        },
    }


def parse_bridge_report(text: str) -> dict[str, Any]:
    status = extract_scalar(text, "status")
    model_match = extract_scalar(text, "model_match") == "true"
    final_marker_present = extract_scalar(text, "final_marker_present") == "true"
    tool_names = extract_list_section(text, "Tool Names")
    deviations = extract_list_section(text, "Deviations")
    deviations = [] if deviations == ["none"] else deviations
    return {
        "status": status,
        "resolved_model": extract_scalar(text, "resolved_model"),
        "model_match": model_match,
        "permission_levels": extract_scalar(text, "permission_levels"),
        "final_marker_present": final_marker_present,
        "tool_names": tool_names,
        "deviation_count": len(deviations),
    }


def extract_scalar(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_list_section(text: str, heading: str) -> list[str]:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        return []
    values = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            values.append(stripped[2:].strip("`"))
    return values


def supervisor_cost_usd(token_record: dict[str, Any]) -> float:
    usage = token_record["usage"]
    prices = token_record["prices"]
    output_tokens = int(usage["supervisor_output_tokens"]) + int(
        usage["supervisor_reasoning_output_tokens"]
    )
    return (
        int(usage["supervisor_input_tokens"])
        * float(prices["supervisor_input_price_per_1m_usd"])
        / 1_000_000
        + int(usage["supervisor_cached_input_tokens"])
        * float(prices["supervisor_cached_input_price_per_1m_usd"])
        / 1_000_000
        + output_tokens
        * float(prices["supervisor_output_price_per_1m_usd"])
        / 1_000_000
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
