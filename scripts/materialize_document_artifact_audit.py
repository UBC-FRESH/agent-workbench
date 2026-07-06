"""Materialize a runtime document-artifact audit contract and Copilot ticket.

This script turns the tracked strict document-artifact audit templates into a
runtime contract/ticket pair. Runtime files may name concrete source artifacts
and report paths; tracked templates remain public-safe placeholders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from string import Template
from typing import Any


DEFAULT_TEMPLATE = Path("templates/document_artifact_audit_supervisor_contract.json")
DEFAULT_OUTPUT_DIR = Path("runtime/agent_jobs")
DEFAULT_AUDITOR = "agent-workbench-result-auditor"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a document-artifact audit supervisor job."
    )
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--marker", required=True)
    parser.add_argument("--phase", default="P57")
    parser.add_argument("--task-id", default="P57.3")
    parser.add_argument("--title", default="Strict document artifact audit batch")
    parser.add_argument(
        "--source-summary",
        action="append",
        required=True,
        help="Source summary JSON path. May be repeated for a batch audit.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Project root used to resolve relative paths and render repo-relative ticket paths.",
    )
    parser.add_argument("--contract-template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--auditor-subagent-name", default=DEFAULT_AUDITOR)
    return parser.parse_args()


def resolve_under_root(path: Path, project_root: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root / path


def display_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_contract_template(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def materialize_contract(
    args: argparse.Namespace,
    project_root: Path,
    report_path: Path,
) -> dict[str, Any]:
    contract_template = resolve_under_root(args.contract_template, project_root)
    contract = load_contract_template(contract_template)
    source_paths = [
        resolve_under_root(Path(value), project_root) for value in args.source_summary
    ]
    contract["contract_id"] = args.job_id
    contract["workspace"] = {
        "root": ".",
        "root_policy": "repo_relative",
        "wrong_root_stop_rule": (
            "If the active workspace root is not the agent-workbench checkout, "
            "write a blocked report and stop."
        ),
    }
    contract["job"] = {
        "phase": args.phase,
        "task_id": args.task_id,
        "title": args.title,
        "goal": (
            "Audit document-indexing summary artifacts and preserve explicit "
            "source gate evidence in supervisor decisions."
        ),
        "supervisor_role": "supervisor",
    }
    contract["inputs"] = [
        {
            "artifact_id": f"source_summary_{index + 1}",
            "path": display_path(path, project_root),
            "role": "input",
        }
        for index, path in enumerate(source_paths)
    ]
    contract["outputs"] = [
        {
            "artifact_id": "supervisor_report",
            "path": display_path(report_path, project_root),
            "role": "report",
        }
    ]
    contract["verification"]["evidence_paths"] = [display_path(report_path, project_root)]
    contract["public_safety"]["tracked_artifact"] = False
    return contract


def source_list(paths: list[Path], project_root: Path) -> str:
    return "\n".join(f"- `{display_path(path, project_root)}`" for path in paths)


def load_source_fact(path: Path, project_root: Path, index: int) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    totals = data.get("totals", {})
    if not isinstance(totals, dict):
        totals = {}
    return {
        "item_id": f"source_summary_{index}",
        "source_path": display_path(path, project_root),
        "source_summary_id": str(data.get("summary_id", "")),
        "source_document_id": str(data.get("document_id", "")),
        "source_gate_result": str(data.get("gate_result", "")),
        "source_recommended_next_move": str(data.get("recommended_next_move", "")),
        "source_needs_supervisor_fields": int(
            totals.get("needs_supervisor_fields", 0) or 0
        ),
        "source_quote_over_limit_fields": int(
            totals.get("quote_over_limit_fields", 0) or 0
        ),
        "source_resolved_fields": int(totals.get("resolved_fields", 0) or 0),
    }


def source_fact_list(paths: list[Path], project_root: Path) -> list[dict[str, Any]]:
    return [
        load_source_fact(path, project_root, index)
        for index, path in enumerate(paths, start=1)
    ]


def source_facts_block(facts: list[dict[str, Any]]) -> str:
    return json.dumps(facts, indent=2)


def expected_items(paths: list[Path], project_root: Path) -> str:
    lines: list[str] = []
    facts = source_fact_list(paths, project_root)
    for index, fact in enumerate(facts, start=1):
        lines.extend(
            [
                "    {",
                f'      "item_id": {json.dumps(fact["item_id"])},',
                f'      "source_path": {json.dumps(fact["source_path"])},',
                f'      "source_summary_id": {json.dumps(fact["source_summary_id"])},',
                f'      "source_document_id": {json.dumps(fact["source_document_id"])},',
                f'      "source_gate_result": {json.dumps(fact["source_gate_result"])},',
                (
                    '      "source_recommended_next_move": '
                    f'{json.dumps(fact["source_recommended_next_move"])},'
                ),
                (
                    '      "source_needs_supervisor_fields": '
                    f'{fact["source_needs_supervisor_fields"]},'
                ),
                (
                    '      "source_quote_over_limit_fields": '
                    f'{fact["source_quote_over_limit_fields"]},'
                ),
                f'      "source_resolved_fields": {fact["source_resolved_fields"]},',
                '      "auditor_decision": "",',
                '      "decision_consistent_with_gate": false,',
                '      "source_fact_copy_ok": false',
                "    }",
            ]
        )
        if index < len(paths):
            lines[-1] += ","
    return "\n".join(lines)


def materialize_ticket(
    args: argparse.Namespace,
    project_root: Path,
    contract_path: Path,
    report_path: Path,
) -> str:
    paths = [resolve_under_root(Path(value), project_root) for value in args.source_summary]
    facts = source_fact_list(paths, project_root)
    template = Template(
        """# Strict Document Artifact Audit Batch

Marker: `$marker`

Execute this ticket exactly. This is a bounded Agent Workbench supervisor job.

## Required Reads

- `$contract_path`
$source_paths

## Allowed Actions

- Read the required files.
- Invoke the `$auditor_subagent_name` subagent once per source summary, or once
  with a compact batch payload if that is clearer.
- Write exactly one JSON report file: `$report_path`
- Do not edit tracked files.
- Do not create commits, branches, GitHub issues, GitHub comments, or pull
  requests.

## Auditor Payload

Use these deterministically pre-extracted source facts. Do not rewrite these
values from memory; copy them exactly into `verification.audit_items`.

```json
$source_facts
```

For each source summary, pass the auditor only these pre-extracted facts:

- `summary_id`
- `document_id`
- `gate_result`
- `recommended_next_move`
- `totals.needs_supervisor_fields`
- `totals.quote_over_limit_fields`
- `totals.resolved_fields`

Allowed `auditor_decision` values:

- `paid_supervisor_audit_required`
- `quote_repair_required`
- `ready_to_scale`
- `needs_coordinator_review`

Decision rules:

- If `gate_result` is blank, missing, or not part of the expected gate
  vocabulary, `auditor_decision` must be `needs_coordinator_review`.
- If `gate_result` is nonblank but does not contain one of the specific
  trigger strings below, `auditor_decision` must be
  `needs_coordinator_review`.
- If `gate_result` contains `quote-repair-needed` or `quote-limit-failed`,
  `auditor_decision` must be `quote_repair_required`.
- If `gate_result` contains `parse-failed`, `failed`, `blocked`, `unreadable`,
  or equivalent missing-evidence language, `auditor_decision` must be
  `needs_coordinator_review`.
- If `gate_result` contains `ready-for-supervisor-audit` or
  `recommended_next_move` says paid supervisor audit is required,
  `auditor_decision` must be `paid_supervisor_audit_required` unless a
  higher-priority repair or blocker gate applies.
- Use `ready_to_scale` only when `gate_result` explicitly contains
  `ready-to-scale`, `ready_to_scale`, or `ready-for-scale`.
- If a source artifact is unreadable, internally inconsistent, or the auditor
  payload contradicts these rules, set `final_signal` to
  `needs_coordinator_review`.

## Required Output File

Write this JSON object to `$report_path`:

```json
{
  "report_id": "$job_id_report",
  "contract_id": "$job_id",
  "supervisor_role": "supervisor",
  "final_signal": "job_complete_with_caveats",
  "completed_nodes": [
    {
      "node_id": "source_fact_extract",
      "owner_role": "supervisor",
      "status": "completed"
    },
    {
      "node_id": "artifact_audit",
      "owner_role": "worker",
      "status": "completed"
    },
    {
      "node_id": "decision_consistency_check",
      "owner_role": "supervisor",
      "status": "completed"
    }
  ],
  "artifacts": [
    {
      "artifact_id": "supervisor_report",
      "path": "$report_path",
      "role": "report"
    }
  ],
  "verification": {
    "checks_run": [
      "source artifacts read",
      "auditor subagent invoked",
      "decision consistency checked"
    ],
    "score": 0.0,
    "subagent_invocation_attempted": true,
    "subagent_name": "$auditor_subagent_name",
    "subagent_invocation_observed_by_supervisor": true,
    "subagent_payload_excerpt": "",
    "subagent_result_status": "accepted_after_supervisor_repair",
    "subagent_repair_summary": "",
    "audit_items": [
$expected_items
    ],
    "all_decisions_consistent_with_gate": false
  },
  "escalations": [],
  "public_safety": {
    "tracked_artifact": false,
    "raw_transcript_policy": "Runtime-only; do not copy raw transcripts into tracked files."
  }
}
```

Set `score` to `1.0` only if every source fact copy is correct, every
`auditor_decision` is valid, and every `decision_consistent_with_gate` is true.

## Required Report JSON Fields

- `verification.subagent_payload_excerpt`
- `verification.subagent_result_status`
- `verification.subagent_repair_summary` unless
  `subagent_result_status` is `accepted_without_repair`
- `verification.audit_items`
- `verification.all_decisions_consistent_with_gate`

Allowed `verification.subagent_result_status` values:

- `accepted_without_repair`: subagent result was used without supervisor
  correction.
- `accepted_after_supervisor_repair`: subagent result was useful but required
  supervisor repair before validation passed.
- `rejected_supervisor_replaced`: subagent result was unusable and the
  supervisor replaced it.
- `unavailable_supervisor_completed`: subagent could not be used and the
  supervisor completed the bounded report directly.

## Stop Condition

After the JSON report file exists, reply exactly:

`$marker done`
"""
    )
    return template.substitute(
        marker=args.marker,
        contract_path=display_path(contract_path, project_root),
        source_paths=source_list(paths, project_root),
        source_facts=source_facts_block(facts),
        report_path=display_path(report_path, project_root),
        auditor_subagent_name=args.auditor_subagent_name,
        job_id=args.job_id,
        job_id_report=f"{args.job_id}_report",
        expected_items=expected_items(paths, project_root),
    )


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_dir = resolve_under_root(args.output_dir, project_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    contract_path = output_dir / f"{args.job_id}_contract.json"
    ticket_path = output_dir / f"{args.job_id}_ticket.md"
    report_path = output_dir / f"{args.job_id}_report.json"
    contract = materialize_contract(args, project_root, report_path)
    contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    ticket_path.write_text(
        materialize_ticket(args, project_root, contract_path, report_path),
        encoding="utf-8",
    )
    print(f"contract: {contract_path}")
    print(f"ticket: {ticket_path}")
    print(f"report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
