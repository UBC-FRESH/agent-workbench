"""Materialize and validate the P92 whole-document supervisor pilot.

P92 tests a different ROI shape than the P89/P90 chunk battery: the paid
coordinator prepares one compact whole-document job for a delegated local
supervisor, then validates a compact report or bounce result. Raw source text
and live reports stay under ``runtime/``; tracked files contain only sanitized
manifests, contracts, gates, and economics assumptions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SELECTION = Path("benchmarks/document_library/p88_selected_corpus_slice.json")
DEFAULT_P90_SUMMARY = Path(
    "benchmarks/document_library/p90_full_document_candidate_packet_summary.json"
)
DEFAULT_P91_DECISION = Path(
    "benchmarks/document_library/p91_source_audit_decision_packet.json"
)
DEFAULT_RUNTIME_DIR = Path(
    "runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot"
)
DEFAULT_TRACKED_ROOT = Path("benchmarks/document_library")
DEFAULT_SUPERVISOR_ROLE = "document_metadata_extraction_supervisor"
DEFAULT_REPORT_PATH = (
    DEFAULT_RUNTIME_DIR / "reports" / "p92_tsa23_2012_23tsdp12_supervisor_report.json"
)
DEFAULT_MODEL = "document-metadata-extraction-supervisor"
DEFAULT_FINAL_MARKER = "P92_WHOLE_DOCUMENT_SUPERVISOR_REPORT_READY"

REQUIRED_REPORT_FIELDS = (
    "report_id",
    "document_id",
    "supervisor_role",
    "final_signal",
    "source_document_read",
    "output_quality",
    "candidate_record_count",
    "source_anchor_policy",
    "records",
    "gaps",
    "self_grade",
    "next_action",
)
ALLOWED_FINAL_SIGNALS = (
    "job_complete",
    "job_complete_with_caveats",
    "needs_coordinator_review",
    "job_failed",
)
ALLOWED_NEXT_ACTIONS = ("accept_seed", "repair", "bounce_redo", "stop")
ALLOWED_CONFIDENCE = ("high", "medium", "low")
MINIMUM_NONTRIVIAL_SOURCE_CHARS = 1_000
MINIMUM_EXPECTED_RECORDS = 20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or validate P92 whole-document supervisor pilot artifacts."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Agent Workbench checkout root. Defaults to the current directory.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    materialize = subparsers.add_parser(
        "materialize",
        help="Create the P92 whole-document supervisor ticket and tracked manifests.",
    )
    materialize.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    materialize.add_argument("--p90-summary", type=Path, default=DEFAULT_P90_SUMMARY)
    materialize.add_argument("--p91-decision", type=Path, default=DEFAULT_P91_DECISION)
    materialize.add_argument("--runtime-dir", type=Path, default=DEFAULT_RUNTIME_DIR)
    materialize.add_argument("--tracked-root", type=Path, default=DEFAULT_TRACKED_ROOT)
    materialize.add_argument("--supervisor-role", default=DEFAULT_SUPERVISOR_ROLE)
    materialize.add_argument("--supervisor-model", default=DEFAULT_MODEL)
    materialize.add_argument("--final-marker", default=DEFAULT_FINAL_MARKER)
    materialize.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Ignored runtime report path the delegated supervisor must write.",
    )
    materialize.add_argument("--force", action="store_true")

    validate = subparsers.add_parser(
        "validate-report",
        help="Validate a delegated supervisor report against the P92 contract.",
    )
    validate.add_argument("--input", type=Path, required=True)
    validate.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_TRACKED_ROOT
        / "p92_whole_document_supervisor_report_contract.json",
    )
    validate.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    if args.command == "materialize":
        materialize(args, project_root)
    elif args.command == "validate-report":
        validate_report_command(args, project_root)
    else:  # pragma: no cover - argparse enforces command choices.
        raise ValueError(f"unknown command: {args.command}")
    return 0


def materialize(args: argparse.Namespace, project_root: Path) -> None:
    selection_path = resolve_under_root(args.selection, project_root)
    p90_summary_path = resolve_under_root(args.p90_summary, project_root)
    p91_decision_path = resolve_under_root(args.p91_decision, project_root)
    runtime_dir = resolve_under_root(args.runtime_dir, project_root)
    tracked_root = resolve_under_root(args.tracked_root, project_root)
    report_path = resolve_under_root(args.report_path, project_root)

    selection = load_json(selection_path)
    p90_summary = load_json(p90_summary_path)
    p91_decision = load_json(p91_decision_path)
    chunks = verify_chunks(selection, project_root)
    generated_utc = now_utc()
    source_text = join_document_text(chunks)
    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    ticket_path = (
        runtime_dir
        / "tickets"
        / f"p92_{selection['document']['document_id']}_whole_document_supervisor.ticket.md"
    )
    bounce_ticket_path = (
        runtime_dir
        / "tickets"
        / f"p92_{selection['document']['document_id']}_bounce_redo.ticket.md"
    )
    runtime_index_path = runtime_dir / "p92_runtime_index.json"

    tracked_paths = tracked_output_paths(tracked_root)
    ensure_overwritable(
        [ticket_path, bounce_ticket_path, runtime_index_path, *tracked_paths],
        force=bool(args.force),
    )

    manifest = build_manifest(
        generated_utc=generated_utc,
        selection=selection,
        chunks=chunks,
        p90_summary=p90_summary,
        p91_decision=p91_decision,
        ticket_path=ticket_path,
        bounce_ticket_path=bounce_ticket_path,
        report_path=report_path,
        runtime_index_path=runtime_index_path,
        source_sha256=source_sha,
        supervisor_role=str(args.supervisor_role),
        supervisor_model=str(args.supervisor_model),
        final_marker=str(args.final_marker),
        project_root=project_root,
    )
    gate = build_gate(generated_utc, manifest, p90_summary, p91_decision)
    contract = build_report_contract(generated_utc, selection, manifest)
    roi = build_roi_estimate(generated_utc, selection, p90_summary, manifest)

    write_text(
        ticket_path,
        render_supervisor_ticket(
            manifest=manifest,
            contract=contract,
            source_text=source_text,
            project_root=project_root,
            final_marker=str(args.final_marker),
        ),
    )
    write_text(
        bounce_ticket_path,
        render_bounce_ticket(manifest=manifest, contract=contract),
    )
    write_json(runtime_index_path, build_runtime_index(manifest))
    write_json(
        tracked_root / "p92_whole_document_supervisor_pilot_manifest.json", manifest
    )
    write_json(tracked_root / "p92_whole_document_supervisor_gate.json", gate)
    write_json(
        tracked_root / "p92_whole_document_supervisor_report_contract.json", contract
    )
    write_json(tracked_root / "p92_whole_document_supervisor_roi_estimate.json", roi)
    print(
        "wrote "
        f"{repo_relative(tracked_root / 'p92_whole_document_supervisor_pilot_manifest.json', project_root)}"
    )
    print(f"wrote ignored ticket {repo_relative(ticket_path, project_root)}")


def validate_report_command(args: argparse.Namespace, project_root: Path) -> None:
    report_path = resolve_under_root(args.input, project_root)
    contract_path = resolve_under_root(args.contract, project_root)
    output_path = resolve_under_root(args.output, project_root)
    contract = load_json(contract_path)
    report = load_json(report_path)
    validation = validate_report(report, contract)
    write_json(output_path, validation)
    print(f"wrote {repo_relative(output_path, project_root)}")


def verify_chunks(
    selection: dict[str, Any], project_root: Path
) -> list[dict[str, Any]]:
    manifest_path = resolve_under_root(
        Path(str(selection["document"]["tracked_chunk_manifest"])), project_root
    )
    chunk_manifest = load_json(manifest_path)
    by_id = {str(chunk["chunk_id"]): chunk for chunk in chunk_manifest["chunks"]}
    verified = []
    for selected in selection["selected_scope"]["chunks"]:
        chunk_id = str(selected["chunk_id"])
        manifest_chunk = by_id[chunk_id]
        text_path = resolve_under_root(
            Path(str(manifest_chunk["runtime_text_path"])), project_root
        )
        text = text_path.read_text(encoding="utf-8-sig")
        actual_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        expected_sha = str(selected["text_sha256"])
        if actual_sha != expected_sha:
            raise ValueError(f"text hash mismatch for {chunk_id}")
        verified.append(
            {
                "chunk_id": chunk_id,
                "page_start": int(selected["page_start"]),
                "page_end": int(selected["page_end"]),
                "text_char_count": len(text),
                "text_sha256": actual_sha,
                "runtime_text_path": repo_relative(text_path, project_root),
                "text": text,
            }
        )
    return verified


def join_document_text(chunks: list[dict[str, Any]]) -> str:
    parts = []
    for chunk in chunks:
        parts.append(f"===== {chunk['chunk_id']} =====\n{chunk['text'].strip()}\n")
    return "\n".join(parts).strip() + "\n"


def build_manifest(
    *,
    generated_utc: str,
    selection: dict[str, Any],
    chunks: list[dict[str, Any]],
    p90_summary: dict[str, Any],
    p91_decision: dict[str, Any],
    ticket_path: Path,
    bounce_ticket_path: Path,
    report_path: Path,
    runtime_index_path: Path,
    source_sha256: str,
    supervisor_role: str,
    supervisor_model: str,
    final_marker: str,
    project_root: Path,
) -> dict[str, Any]:
    chunk_rows = [
        {
            "chunk_id": chunk["chunk_id"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "text_char_count": chunk["text_char_count"],
            "text_sha256": chunk["text_sha256"],
        }
        for chunk in chunks
    ]
    total_source_chars = sum(int(chunk["text_char_count"]) for chunk in chunks)
    return {
        "schema_version": 1,
        "phase": "P92",
        "pilot_id": "p92_whole_document_supervisor_tsa23_2012_23tsdp12",
        "generated_utc": generated_utc,
        "status": "materialized_not_live_run",
        "document_id": selection["document"]["document_id"],
        "document_title": selection["document"]["title"],
        "corpus_id": selection["corpus"]["corpus_id"],
        "source_sha256": selection["document"]["source_sha256"],
        "whole_document_runtime_text_sha256": source_sha256,
        "page_start": selection["selected_scope"]["page_start"],
        "page_end": selection["selected_scope"]["page_end"],
        "chunk_count": len(chunks),
        "total_source_char_count": total_source_chars,
        "chunks": chunk_rows,
        "delegated_supervisor": {
            "role": supervisor_role,
            "custom_agent": supervisor_model,
            "final_marker": final_marker,
            "tool_access": [
                "agent",
                "read",
                "search",
                "edit",
                "runCommands",
            ],
            "tool_policy": (
                "Full local tool access is allowed for source inspection, "
                "search, bounded validation, subagent audit, and writing the "
                "assigned runtime report. Tracked-file and GitHub mutation "
                "remain forbidden."
            ),
            "upfront_coordinator_shape": "single whole-document ticket",
            "report_path": repo_relative(report_path, project_root),
        },
        "runtime_artifacts": {
            "ticket_path": repo_relative(ticket_path, project_root),
            "bounce_ticket_path": repo_relative(bounce_ticket_path, project_root),
            "runtime_index_path": repo_relative(runtime_index_path, project_root),
        },
        "tracked_artifacts": {
            "manifest": "benchmarks/document_library/p92_whole_document_supervisor_pilot_manifest.json",
            "gate": "benchmarks/document_library/p92_whole_document_supervisor_gate.json",
            "report_contract": "benchmarks/document_library/p92_whole_document_supervisor_report_contract.json",
            "roi_estimate": "benchmarks/document_library/p92_whole_document_supervisor_roi_estimate.json",
            "graph_template": "templates/workbench_templates/document_library_whole_document_supervisor_graph.json",
        },
        "prior_evidence": {
            "p90_completed_runs": p90_summary["completed_run_count"],
            "p90_candidate_records": p90_summary["emitted_repaired_record_count"],
            "p90_valid_run_rate": round(
                p90_summary["valid_run_count"] / p90_summary["run_count"], 3
            ),
            "p91_decision": p91_decision["decision"],
            "p91_useful_sample_yield": useful_sample_yield(p91_decision),
        },
        "coordinator_boundary": [
            "select one document",
            "materialize one runtime ticket",
            "validate one returned report",
            "issue one compact bounce ticket only if minimum quality fails",
            "make final tracked decision after inspection",
        ],
        "public_safety": public_safety_block(),
    }


def build_gate(
    generated_utc: str,
    manifest: dict[str, Any],
    p90_summary: dict[str, Any],
    p91_decision: dict[str, Any],
) -> dict[str, Any]:
    total_source_chars = int(manifest["total_source_char_count"])
    expected_records = int(p90_summary["emitted_repaired_record_count"])
    gate_rows = [
        {
            "gate": "whole_document_scope_nontrivial",
            "status": "pass"
            if total_source_chars >= MINIMUM_NONTRIVIAL_SOURCE_CHARS
            else "fail",
            "evidence": {
                "total_source_char_count": total_source_chars,
                "minimum": MINIMUM_NONTRIVIAL_SOURCE_CHARS,
            },
        },
        {
            "gate": "prior_candidate_volume_nontrivial",
            "status": "pass"
            if expected_records >= MINIMUM_EXPECTED_RECORDS
            else "fail",
            "evidence": {
                "p90_candidate_records": expected_records,
                "minimum": MINIMUM_EXPECTED_RECORDS,
            },
        },
        {
            "gate": "source_audit_seed_promotable",
            "status": "pass" if p91_decision["decision"] == "promote_seed" else "fail",
            "evidence": {
                "p91_decision": p91_decision["decision"],
                "p91_useful_sample_yield": useful_sample_yield(p91_decision),
            },
        },
    ]
    return {
        "schema_version": 1,
        "phase": "P92",
        "generated_utc": generated_utc,
        "pilot_id": manifest["pilot_id"],
        "overall_gate": "pass"
        if all(row["status"] == "pass" for row in gate_rows)
        else "fail",
        "live_run_authorized_by_this_file": False,
        "gate_rows": gate_rows,
        "required_before_live_run": [
            "explicit maintainer approval for one whole-document delegated supervisor run",
            "supervisor-token start checkpoint before coordinator launch work",
            "supervisor-token end checkpoint after report validation and decision",
            "one named custom agent role and model lane",
            "full local supervisor tool access inside the report-only authority box",
            "hard stop after one initial run plus one compact bounce only if needed",
        ],
        "stop_rules": [
            "stop if delegated supervisor cannot read the whole document package",
            "stop if report JSON is missing or invalid after one bounce",
            "stop if candidate_record_count is zero for this nontrivial source",
            "stop if source_document_read is false",
            "stop if coordinator overhead exceeds the declared token budget",
        ],
        "public_safety": public_safety_block(),
    }


def build_report_contract(
    generated_utc: str, selection: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P92",
        "contract_id": "p92_whole_document_supervisor_report_contract",
        "generated_utc": generated_utc,
        "document_id": selection["document"]["document_id"],
        "supervisor_role": manifest["delegated_supervisor"]["role"],
        "required_fields": list(REQUIRED_REPORT_FIELDS),
        "allowed_final_signals": list(ALLOWED_FINAL_SIGNALS),
        "allowed_next_actions": list(ALLOWED_NEXT_ACTIONS),
        "allowed_confidence": list(ALLOWED_CONFIDENCE),
        "minimum_candidate_records": 1,
        "minimum_quality_bar": {
            "source_document_read": True,
            "records_must_be_list": True,
            "each_record_required_fields": [
                "record_id",
                "object_type",
                "title",
                "summary",
                "source_anchor",
                "confidence",
            ],
            "source_anchor_policy": (
                "Exact quotes are preferred, but table captions, page anchors, "
                "and clearly labeled synthesized table facts are repairable "
                "rather than automatic failures."
            ),
        },
        "bounce_policy": {
            "when": [
                "missing report JSON",
                "source_document_read is false",
                "candidate_record_count is zero",
                "records are mostly unsupported or unusable",
                "final_signal is job_failed without a compact gap report",
            ],
            "max_bounces": 1,
            "ticket": manifest["runtime_artifacts"]["bounce_ticket_path"],
        },
        "public_safety": public_safety_block(),
    }


def build_roi_estimate(
    generated_utc: str,
    selection: dict[str, Any],
    p90_summary: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    ticket_chars = int(manifest["total_source_char_count"]) + 5_000
    p90_records = int(p90_summary["emitted_repaired_record_count"])
    return {
        "schema_version": 1,
        "phase": "P92",
        "generated_utc": generated_utc,
        "document_id": selection["document"]["document_id"],
        "comparison": "whole_document_supervisor_vs_chunk_micro_management",
        "estimated_whole_document_ticket_tokens_c4": round(ticket_chars / 4),
        "source_tokens_c4": round(int(manifest["total_source_char_count"]) / 4),
        "p90_chunk_pipeline_minimum_coordinator_tokens_observed": 236_008,
        "p90_chunk_count": int(p90_summary["run_count"]),
        "p90_candidate_records": p90_records,
        "gross_local_worker_volume_token_equivalent_c4": 310_000,
        "roi_hypothesis": (
            "A single document-level delegated supervisor job should reduce "
            "paid coordinator micromanagement if the local supervisor returns "
            "a usable seed or a compact failure report after at most one bounce."
        ),
        "success_thresholds": {
            "coordinator_token_budget_target": "less than half the P90+P91 chunk-pipeline minimum",
            "minimum_candidate_records": 1,
            "preferred_candidate_records": "enough to cover title, structure, tables, assumptions, and named quantities",
            "must_separate": [
                "quality outcome",
                "protocol outcome",
                "economics outcome",
            ],
        },
        "known_risks": [
            "whole-document context may exceed the practical local supervisor window",
            "large reports may need deterministic pruning before paid coordinator review",
            "a no-tool supervisor may summarize too coarsely unless the custom role is explicit",
        ],
        "public_safety": public_safety_block(),
    }


def render_supervisor_ticket(
    *,
    manifest: dict[str, Any],
    contract: dict[str, Any],
    source_text: str,
    project_root: Path,
    final_marker: str,
) -> str:
    report_path = manifest["delegated_supervisor"]["report_path"]
    return f"""# P92 Whole-Document Document Metadata Extraction Supervisor Ticket

## Assigned Role

Use the `{manifest["delegated_supervisor"]["role"]}` protocol.

You are the delegated local supervisor. The paid coordinator has intentionally
not decomposed this document into tiny jobs. Your task is to read the whole
document text below, do a useful first-pass extraction, and write one compact
JSON report for coordinator validation.

## Workspace

- Project root: `{project_root.as_posix()}`
- Document ID: `{manifest["document_id"]}`
- Pages: `{manifest["page_start"]}-{manifest["page_end"]}`
- Report path to write: `{report_path}`
- Custom agent skin: `{manifest["delegated_supervisor"]["custom_agent"]}`

## Required Output File

- `{report_path}`

## Required Report JSON Fields

{required_field_bullets(contract)}

## Authority Boundary

- You have full local tool access for this bounded job: read, search,
  runCommands, edit, and auditor subagent use are allowed.
- You may write only the report path named above.
- Do not edit tracked files.
- Do not create commits, branches, GitHub issues, pull requests, or releases.
- Do not run broad repo-maintenance commands.
- Use tools to inspect/search the assigned source package and to validate the
  report shape when useful. Tool use is expected; do not treat this as a
  no-tool extraction task.
- If your active workspace root is not the project root above, do not write a
  report elsewhere. Return `needs_coordinator_review` and state that the
  workspace root is wrong.
- If the source is unreadable or too large to process, write a blocked report
  with `final_signal` set to `needs_coordinator_review` or `job_failed`.

## Minimum Useful Work

Produce a useful seed report, not a perfect production index.

Include:

- document-level metadata;
- major sections and table/caption inventory;
- named assumptions, constraints, scenarios, quantities, and model inputs;
- source anchors for records;
- confidence bins and gaps;
- a self-grade against the report contract;
- a `next_action` of `accept_seed`, `repair`, `bounce_redo`, or `stop`.

Source anchors may be exact quotes, table captions, page anchors, or clearly
labeled synthesized table facts. Do not fabricate facts. If you synthesize from
a table, say so in the record summary and use a table caption/page anchor.

## Report Contract

```json
{json.dumps(contract, indent=2)}
```

## Source Text

```text
{source_text}
```

## Final Chat Response

After the report file exists, respond with exactly:

`{final_marker} done`
"""


def render_bounce_ticket(manifest: dict[str, Any], contract: dict[str, Any]) -> str:
    return f"""# P92 Compact Bounce/Redo Ticket

This ticket is used only if the first whole-document supervisor report fails
the minimum quality bar.

## Previous Assignment

- Pilot ID: `{manifest["pilot_id"]}`
- Document ID: `{manifest["document_id"]}`
- Original report path: `{manifest["delegated_supervisor"]["report_path"]}`

## Redo Instructions

The coordinator must fill in the concrete failure notes before launch:

1. Failed grade cause: `<one sentence>`
2. Missing or weak areas: `<3-6 bullets>`
3. Minimum repair target: `<specific records/sections/gaps>`

Do not restart the whole coordination ritual. Reuse the same document context
where available, fix only the failed quality dimensions, and write the same
report path.

## Minimum Bar

- `source_document_read` must be `true`.
- `candidate_record_count` must be greater than zero.
- `records` must be a list of source-anchored candidate records.
- `next_action` must be one of: {", ".join(contract["allowed_next_actions"])}.
- If the job still cannot be completed, return a compact gap report rather
  than an empty or ceremonial result.
"""


def required_field_bullets(contract: dict[str, Any]) -> str:
    return "\n".join(f"- `{field}`" for field in contract["required_fields"])


def build_runtime_index(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P92",
        "pilot_id": manifest["pilot_id"],
        "ticket_path": manifest["runtime_artifacts"]["ticket_path"],
        "bounce_ticket_path": manifest["runtime_artifacts"]["bounce_ticket_path"],
        "report_path": manifest["delegated_supervisor"]["report_path"],
        "raw_text_policy": "Runtime ticket contains full source text and remains ignored.",
    }


def validate_report(report: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    errors = []
    for field in contract["required_fields"]:
        if field not in report:
            errors.append({"kind": "missing_required_field", "field": field})
    if report.get("document_id") != contract["document_id"]:
        errors.append({"kind": "wrong_document_id", "field": "document_id"})
    if report.get("supervisor_role") != contract["supervisor_role"]:
        errors.append({"kind": "wrong_supervisor_role", "field": "supervisor_role"})
    if report.get("final_signal") not in contract["allowed_final_signals"]:
        errors.append({"kind": "invalid_final_signal", "field": "final_signal"})
    if report.get("next_action") not in contract["allowed_next_actions"]:
        errors.append({"kind": "invalid_next_action", "field": "next_action"})
    if report.get("source_document_read") is not True:
        errors.append({"kind": "source_not_read", "field": "source_document_read"})
    records = report.get("records")
    if not isinstance(records, list):
        errors.append({"kind": "records_not_list", "field": "records"})
        records = []
    reported_count = report.get("candidate_record_count")
    if not isinstance(reported_count, int):
        errors.append(
            {
                "kind": "invalid_candidate_record_count",
                "field": "candidate_record_count",
            }
        )
    elif reported_count != len(records):
        errors.append(
            {"kind": "candidate_count_mismatch", "field": "candidate_record_count"}
        )
    if len(records) < int(contract["minimum_candidate_records"]):
        errors.append({"kind": "zero_or_too_few_records", "field": "records"})
    required_record_fields = contract["minimum_quality_bar"][
        "each_record_required_fields"
    ]
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append({"kind": "record_not_object", "record_index": index})
            continue
        for field in required_record_fields:
            if not record.get(field):
                errors.append(
                    {
                        "kind": "record_missing_required_field",
                        "record_index": index,
                        "field": field,
                    }
                )
        if record.get("confidence") not in contract["allowed_confidence"]:
            errors.append(
                {
                    "kind": "invalid_record_confidence",
                    "record_index": index,
                    "field": "confidence",
                }
            )
    return {
        "schema_version": 1,
        "phase": "P92",
        "status": "valid" if not errors else "invalid",
        "fatal_error_count": len(errors),
        "candidate_record_count": len(records),
        "errors": errors,
        "decision_hint": decision_hint(errors, report),
    }


def decision_hint(errors: list[dict[str, Any]], report: dict[str, Any]) -> str:
    if not errors and report.get("next_action") == "accept_seed":
        return "coordinator_audit_seed"
    if not errors and report.get("next_action") == "repair":
        return "coordinator_review_repair_request"
    if any(
        error["kind"] in {"source_not_read", "zero_or_too_few_records"}
        for error in errors
    ):
        return "bounce_or_stop"
    if errors:
        return "repair_or_bounce"
    return "coordinator_review"


def tracked_output_paths(tracked_root: Path) -> list[Path]:
    return [
        tracked_root / "p92_whole_document_supervisor_pilot_manifest.json",
        tracked_root / "p92_whole_document_supervisor_gate.json",
        tracked_root / "p92_whole_document_supervisor_report_contract.json",
        tracked_root / "p92_whole_document_supervisor_roi_estimate.json",
    ]


def public_safety_block() -> dict[str, bool]:
    return {
        "raw_source_text_tracked": False,
        "raw_worker_output_tracked": False,
        "source_quotes_tracked": False,
        "provider_urls_or_headers_tracked": False,
        "personal_paths_tracked": False,
    }


def useful_sample_yield(p91_decision: dict[str, Any]) -> float:
    quality = p91_decision.get("quality_outcome")
    if isinstance(quality, dict) and "sample_useful_yield" in quality:
        return float(quality["sample_useful_yield"])
    return float(p91_decision["sample_useful_yield"])


def ensure_overwritable(paths: list[Path], *, force: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not force:
        joined = ", ".join(str(path) for path in existing[:5])
        raise FileExistsError(
            f"refusing to overwrite existing generated files: {joined}"
        )


def resolve_under_root(path: Path, project_root: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def repo_relative(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
