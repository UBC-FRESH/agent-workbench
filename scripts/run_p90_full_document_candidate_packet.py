"""Run the P90 full-document candidate extraction packet.

Raw model outputs and candidate JSONL stay under ``runtime/``. Tracked outputs
contain only sanitized counts, statuses, and repo-relative runtime inventories.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_p90_qwen36_comparison_batch import (
    extract_candidate_jsonl,
    load_json,
    read_probe_status,
    should_reuse_result,
    slug,
    write_json,
)


DEFAULT_TICKETS_DIR = Path(
    "runtime/document_library/tsa23_tsr/p89_document_indexing_recipe_v2/tickets"
)
DEFAULT_OUTPUT_DIR = Path(
    "runtime/document_library/tsa23_tsr/p90_full_document_candidate_packet"
)
DEFAULT_TRACKED_SUMMARY = Path(
    "benchmarks/document_library/p90_full_document_candidate_packet_summary.json"
)
DEFAULT_TRACKED_PACKET_MANIFEST = Path(
    "benchmarks/document_library/p90_full_document_candidate_packet_manifest.json"
)
DEFAULT_BASE_URL_FILE = Path("runtime/ollama_openai_base_url.txt")
DEFAULT_PROVIDER_HEADERS_FILE = Path("runtime/local_provider_headers.json")
DEFAULT_MODEL = "qwen3.6:35b-a3b-q8_0"
DEFAULT_MODEL_LABEL = "qwen36_q8"
TICKET_TYPES = ("structure", "content_metadata")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the P90 full-document candidate extraction packet."
    )
    parser.add_argument("--tickets-dir", type=Path, default=DEFAULT_TICKETS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--tracked-summary", type=Path, default=DEFAULT_TRACKED_SUMMARY)
    parser.add_argument(
        "--tracked-packet-manifest",
        type=Path,
        default=DEFAULT_TRACKED_PACKET_MANIFEST,
    )
    parser.add_argument("--base-url-file", type=Path, default=DEFAULT_BASE_URL_FILE)
    parser.add_argument(
        "--provider-headers-file",
        type=Path,
        default=DEFAULT_PROVIDER_HEADERS_FILE,
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--ticket-type",
        action="append",
        choices=TICKET_TYPES,
        default=None,
        help="Ticket type to run. May be repeated. Defaults to both types.",
    )
    parser.add_argument(
        "--max-tickets",
        type=int,
        default=None,
        help="Optional total ticket cap for shakedowns.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse raw result files only when their probe status is completed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_label = (
        DEFAULT_MODEL_LABEL if args.model == DEFAULT_MODEL else slug(args.model)
    )
    ticket_types = tuple(args.ticket_type or TICKET_TYPES)
    tickets = select_tickets(args.tickets_dir, ticket_types, args.max_tickets)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    runs: list[dict[str, Any]] = []
    for index, ticket in enumerate(tickets, start=1):
        run = run_or_reuse(args, ticket, model_label)
        runs.append(run)
        print(
            f"[{index}/{len(tickets)}] {run['ticket_type']} {run['ticket_id']} "
            f"probe={run['probe_status']} validation={run['validation_status']} "
            f"records={run['emitted_repaired_record_count']}"
        )

    summary = build_summary(runs, tickets, args.model, model_label)
    packet_manifest = build_packet_manifest(summary, runs, args.output_dir)
    write_json(args.output_dir / "p90_full_document_runtime_summary.json", summary)
    write_json(args.tracked_summary, summary)
    write_json(args.tracked_packet_manifest, packet_manifest)
    print(f"wrote {args.tracked_summary}")
    print(f"wrote {args.tracked_packet_manifest}")
    print(f"completed={summary['completed_run_count']} total={summary['run_count']}")
    return 0 if summary["blocked_run_count"] == 0 else 2


def select_tickets(
    tickets_dir: Path, ticket_types: tuple[str, ...], max_tickets: int | None
) -> list[Path]:
    tickets: list[Path] = []
    for ticket_type in ticket_types:
        selected = sorted(tickets_dir.glob(f"*_{ticket_type}.ticket.md"))
        if not selected:
            raise FileNotFoundError(f"no {ticket_type} tickets found in {tickets_dir}")
        tickets.extend(selected)
    tickets = sorted(tickets)
    if max_tickets is not None:
        tickets = tickets[:max_tickets]
    return tickets


def ticket_type_for(ticket: Path) -> str:
    name = ticket.name
    if name.endswith("_content_metadata.ticket.md"):
        return "content_metadata"
    if name.endswith("_structure.ticket.md"):
        return "structure"
    return "unknown"


def run_or_reuse(
    args: argparse.Namespace, ticket: Path, model_label: str
) -> dict[str, Any]:
    ticket_id = ticket.name.removesuffix(".ticket.md")
    ticket_type = ticket_type_for(ticket)
    run_id = f"{ticket_id}__{model_label}"
    result_path = args.output_dir / f"{run_id}.md"
    candidate_path = args.output_dir / f"{run_id}.candidate.jsonl"
    repaired_path = args.output_dir / f"{run_id}.repaired.jsonl"
    validation_path = args.output_dir / f"{run_id}.validation.json"

    if not should_reuse_result(args.resume, result_path):
        command = [
            sys.executable,
            "scripts/copilot_sdk_ollama_probe.py",
            "--model",
            args.model,
            "--base-url",
            args.base_url_file.read_text(encoding="utf-8").strip(),
            "--provider-headers-file",
            str(args.provider_headers_file),
            "--ticket",
            str(ticket),
            "--output",
            str(result_path),
            "--timeout-seconds",
            str(args.timeout_seconds),
            "--wire-api",
            "completions",
        ]
        completed = subprocess.run(command, check=False)
        probe_exit_code = completed.returncode
    else:
        probe_exit_code = 0

    extraction = extract_candidate_jsonl(result_path)
    candidate_path.write_text(extraction["jsonl"], encoding="utf-8")

    validate_command = [
        sys.executable,
        "scripts/build_p89_document_indexing_recipe_v2.py",
        "--project-root",
        ".",
        "validate-jsonl",
        "--input",
        str(candidate_path),
        "--output",
        str(validation_path),
        "--repaired-output",
        str(repaired_path),
    ]
    subprocess.run(validate_command, check=False)
    validation = load_json(validation_path)

    return {
        "run_id": run_id,
        "ticket_id": ticket_id,
        "ticket_type": ticket_type,
        "ticket_path": ticket.as_posix(),
        "model": args.model,
        "model_label": model_label,
        "probe_exit_code": probe_exit_code,
        "probe_status": read_probe_status(result_path),
        "raw_result_path": result_path.as_posix(),
        "candidate_jsonl_path": candidate_path.as_posix(),
        "repaired_jsonl_path": repaired_path.as_posix(),
        "validation_report_path": validation_path.as_posix(),
        "extraction_mode": extraction["mode"],
        "candidate_line_count": extraction["line_count"],
        "validation_status": validation.get("status"),
        "parseable_record_count": validation.get("parseable_record_count", 0),
        "emitted_repaired_record_count": validation.get(
            "emitted_repaired_record_count", 0
        ),
        "fatal_error_count": validation.get("fatal_error_count", 0),
        "repaired_line_count": validation.get("repaired_line_count", 0),
        "dropped_non_json_line_count": validation.get("dropped_non_json_line_count", 0),
        "error_kinds": sorted(
            {
                str(error.get("kind", "unknown"))
                for error in validation.get("errors", [])
                if isinstance(error, dict)
            }
        ),
    }


def build_summary(
    runs: list[dict[str, Any]], tickets: list[Path], model: str, model_label: str
) -> dict[str, Any]:
    by_type: dict[str, dict[str, Any]] = {}
    for ticket_type in TICKET_TYPES:
        type_runs = [run for run in runs if run["ticket_type"] == ticket_type]
        by_type[ticket_type] = summarize_runs(type_runs)

    blocked_run_count = sum(1 for run in runs if run["probe_status"] != "completed")
    valid_run_count = sum(1 for run in runs if run["validation_status"] == "valid")
    invalid_run_count = sum(1 for run in runs if run["validation_status"] != "valid")
    zero_record_runs = [
        {
            "run_id": run["run_id"],
            "ticket_id": run["ticket_id"],
            "ticket_type": run["ticket_type"],
            "validation_status": run["validation_status"],
            "fatal_error_count": run["fatal_error_count"],
        }
        for run in runs
        if int(run["emitted_repaired_record_count"]) == 0
    ]
    stop_decision = decide_stop(
        run_count=len(runs),
        blocked_run_count=blocked_run_count,
        valid_run_count=valid_run_count,
        by_type=by_type,
    )

    return {
        "schema_version": 1,
        "phase": "P90",
        "summary_id": "p90_full_document_candidate_packet",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "full_document_candidate_packet_built",
        "source_slice": "p88_tsa23_2012_data_package_full_document_pages_001_041",
        "document_id": "tsa23_2012_23tsdp12",
        "model": model,
        "model_label": model_label,
        "ticket_count": len(tickets),
        "run_count": len(runs),
        "completed_run_count": sum(
            1 for run in runs if run["probe_status"] == "completed"
        ),
        "blocked_run_count": blocked_run_count,
        "valid_run_count": valid_run_count,
        "invalid_run_count": invalid_run_count,
        "emitted_repaired_record_count": sum(
            int(run["emitted_repaired_record_count"]) for run in runs
        ),
        "parseable_record_count": sum(
            int(run["parseable_record_count"]) for run in runs
        ),
        "fatal_error_count": sum(int(run["fatal_error_count"]) for run in runs),
        "ticket_types": by_type,
        "extraction_modes": dict(Counter(str(run["extraction_mode"]) for run in runs)),
        "error_kinds": sorted(
            {kind for run in runs for kind in run.get("error_kinds", [])}
        ),
        "zero_repaired_record_runs": zero_record_runs,
        "stop_decision": stop_decision,
        "source_audit_recommendation": source_audit_recommendation(stop_decision),
        "runs": runs,
        "accepted_record_count": 0,
        "accepted_record_note": "No source audit has been performed; records are raw worker candidates only.",
        "public_safety": {
            "raw_source_text_tracked": False,
            "raw_worker_output_tracked": False,
            "source_quotes_tracked": False,
            "provider_urls_or_headers_tracked": False,
            "personal_paths_tracked": False,
        },
    }


def summarize_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "run_count": len(runs),
        "completed_run_count": sum(
            1 for run in runs if run["probe_status"] == "completed"
        ),
        "blocked_run_count": sum(
            1 for run in runs if run["probe_status"] != "completed"
        ),
        "valid_run_count": sum(
            1 for run in runs if run["validation_status"] == "valid"
        ),
        "invalid_run_count": sum(
            1 for run in runs if run["validation_status"] != "valid"
        ),
        "emitted_repaired_record_count": sum(
            int(run["emitted_repaired_record_count"]) for run in runs
        ),
        "parseable_record_count": sum(
            int(run["parseable_record_count"]) for run in runs
        ),
        "fatal_error_count": sum(int(run["fatal_error_count"]) for run in runs),
        "extraction_modes": dict(Counter(str(run["extraction_mode"]) for run in runs)),
        "error_kinds": sorted(
            {kind for run in runs for kind in run.get("error_kinds", [])}
        ),
        "zero_repaired_record_count": sum(
            1 for run in runs if int(run["emitted_repaired_record_count"]) == 0
        ),
    }


def decide_stop(
    *,
    run_count: int,
    blocked_run_count: int,
    valid_run_count: int,
    by_type: dict[str, dict[str, Any]],
) -> str:
    if blocked_run_count:
        return "provider_or_runtime_blocked"
    if run_count == 0:
        return "manual_review_needed"
    if any(summary["valid_run_count"] == 0 for summary in by_type.values()):
        return "repair_protocol_first"
    if valid_run_count / run_count < 0.5:
        return "repair_protocol_first"
    if any(
        summary["emitted_repaired_record_count"] == 0 for summary in by_type.values()
    ):
        return "manual_review_needed"
    return "ready_for_source_audit"


def source_audit_recommendation(stop_decision: str) -> dict[str, Any]:
    if stop_decision == "ready_for_source_audit":
        return {
            "status": "recommended",
            "sample_shape": "audit a bounded mixed sample from structure and content_metadata repaired JSONL outputs before accepting any record",
            "minimum_sample": {
                "structure_records": 10,
                "content_metadata_records": 10,
                "zero_record_or_invalid_runs": "inspect all zero-record or invalid runs",
            },
        }
    return {
        "status": "defer_acceptance",
        "sample_shape": "inspect protocol defects before source-audit acceptance",
    }


def build_packet_manifest(
    summary: dict[str, Any], runs: list[dict[str, Any]], output_dir: Path
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P90",
        "manifest_id": "p90_full_document_candidate_packet_manifest",
        "generated_utc": summary["generated_utc"],
        "document_id": summary["document_id"],
        "source_slice": summary["source_slice"],
        "runtime_packet_path": output_dir.as_posix(),
        "tracked_summary_path": DEFAULT_TRACKED_SUMMARY.as_posix(),
        "candidate_jsonl_paths": [run["candidate_jsonl_path"] for run in runs],
        "repaired_jsonl_paths": [run["repaired_jsonl_path"] for run in runs],
        "validation_report_paths": [run["validation_report_path"] for run in runs],
        "raw_result_paths": [run["raw_result_path"] for run in runs],
        "run_count": summary["run_count"],
        "completed_run_count": summary["completed_run_count"],
        "valid_run_count": summary["valid_run_count"],
        "emitted_repaired_record_count": summary["emitted_repaired_record_count"],
        "stop_decision": summary["stop_decision"],
        "source_audit_recommendation": summary["source_audit_recommendation"],
        "accepted_record_count": 0,
        "accepted_record_note": summary["accepted_record_note"],
        "public_safety": summary["public_safety"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
