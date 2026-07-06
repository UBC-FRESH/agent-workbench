"""Materialize a graph-derived Copilot supervisor job ticket.

This script uses the tracked document-artifact audit workflow graph as the
source of node order and role boundaries, then emits an ignored runtime ticket
that asks the local Copilot supervisor to execute the graph-shaped job.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = SCRIPT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agent_workbench.graph import load_graph_document, validate_graph_document


DEFAULT_GRAPH_TEMPLATE = Path(
    "templates/workbench_templates/document_artifact_audit_supervisor_graph.json"
)
DEFAULT_OUTPUT_DIR = Path("runtime/agent_jobs")
DEFAULT_MATERIALIZER = Path("scripts/materialize_document_artifact_audit.py")
DEFAULT_AUDIT_VERIFIER = Path("scripts/verify_document_artifact_audit_report.py")
DEFAULT_GRAPH_VERIFIER = Path("scripts/verify_document_artifact_graph_report.py")
DEFAULT_REPAIR_HELPER = Path("scripts/repair_document_artifact_graph_reports.py")
DEFAULT_AUDITOR = "agent-workbench-result-auditor"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a graph-derived document-artifact audit supervisor job."
    )
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--marker", required=True)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Agent Workbench checkout root used to resolve repo-relative inputs.",
    )
    parser.add_argument("--phase", default="P57")
    parser.add_argument("--task-id", default="P57.4")
    parser.add_argument(
        "--title",
        default="Graph-derived document artifact audit supervisor job",
    )
    parser.add_argument(
        "--source-summary",
        action="append",
        required=True,
        help="Source summary JSON path. May be repeated.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--graph-template", type=Path, default=DEFAULT_GRAPH_TEMPLATE)
    parser.add_argument("--audit-materializer", type=Path, default=DEFAULT_MATERIALIZER)
    parser.add_argument("--audit-verifier", type=Path, default=DEFAULT_AUDIT_VERIFIER)
    parser.add_argument("--graph-verifier", type=Path, default=DEFAULT_GRAPH_VERIFIER)
    parser.add_argument("--repair-helper", type=Path, default=DEFAULT_REPAIR_HELPER)
    parser.add_argument("--auditor-subagent-name", default=DEFAULT_AUDITOR)
    parser.add_argument(
        "--pre-materialize-audit-ticket",
        action="store_true",
        help=(
            "Run the audit-ticket materializer before emitting the graph ticket, "
            "so Copilot starts at the supervisor/worker audit nodes."
        ),
    )
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


def quote_ps(value: str) -> str:
    escaped = value.replace("`", "``").replace('"', '`"')
    return f'"{escaped}"'


def shell_command(parts: list[str]) -> str:
    return " ".join(quote_ps(part) if needs_quotes(part) else part for part in parts)


def needs_quotes(value: str) -> bool:
    return any(char.isspace() for char in value) or any(
        char in value for char in ("(", ")", "[", "]", "{", "}", "&", ";")
    )


def validate_graph(path: Path) -> dict[str, Any]:
    data = load_graph_document(path)
    result = validate_graph_document(data, source_path=path, agent_metadata=True)
    if not result.ok:
        messages = "; ".join(
            f"{diagnostic.code}: {diagnostic.message}" for diagnostic in result.diagnostics
        )
        raise SystemExit(f"graph validation failed: {messages}")
    return data


def graph_node_ids(graph: dict[str, Any]) -> list[str]:
    nodes = graph.get("nodes", [])
    if not isinstance(nodes, list):
        raise SystemExit("graph nodes must be a list")
    ids: list[str] = []
    for node in nodes:
        if isinstance(node, dict) and str(node.get("id", "")).strip():
            ids.append(str(node["id"]))
    return ids


def executable_supervisor_node_ids(node_ids: list[str]) -> list[str]:
    coordinator_nodes = {"coordinator_job_ticket", "coordinator_review_packet"}
    return [node_id for node_id in node_ids if node_id not in coordinator_nodes]


def exact_materializer_command(
    *,
    project_root: Path,
    materializer: Path,
    output_dir: Path,
    job_id: str,
    marker: str,
    phase: str,
    task_id: str,
    title: str,
    source_summaries: list[Path],
    auditor_subagent_name: str,
) -> str:
    parts = [
        "python",
        str(materializer),
        "--project-root",
        str(project_root),
        "--output-dir",
        str(output_dir),
        "--job-id",
        job_id,
        "--marker",
        marker,
        "--phase",
        phase,
        "--task-id",
        task_id,
        "--title",
        title,
        "--auditor-subagent-name",
        auditor_subagent_name,
    ]
    for source_summary in source_summaries:
        parts.extend(["--source-summary", display_path(source_summary, project_root)])
    return shell_command(parts)


def exact_validation_command(*, project_root: Path, report_path: Path) -> str:
    report_display = display_path(report_path, project_root)
    return (
        f"$env:PYTHONPATH = {quote_ps(str(project_root / 'src'))}; "
        "python -m agent_workbench.cli authority validate --kind report "
        f"--input {quote_ps(report_display)}"
    )


def exact_document_audit_verifier_command(
    *,
    project_root: Path,
    verifier: Path,
    report_path: Path,
    source_summaries: list[Path],
) -> str:
    parts = [
        "python",
        str(verifier),
        "--project-root",
        str(project_root),
        "--report",
        display_path(report_path, project_root),
    ]
    for source_summary in source_summaries:
        parts.extend(["--source-summary", display_path(source_summary, project_root)])
    return shell_command(parts)


def exact_graph_report_verifier_command(
    *,
    project_root: Path,
    verifier: Path,
    graph_report_path: Path,
    audit_report_path: Path,
) -> str:
    parts = [
        "python",
        str(verifier),
        "--project-root",
        str(project_root),
        "--graph-report",
        display_path(graph_report_path, project_root),
        "--audit-report",
        display_path(audit_report_path, project_root),
    ]
    return shell_command(parts)


def exact_repair_helper_command(
    *,
    project_root: Path,
    repair_helper: Path,
    audit_report_path: Path,
    graph_report_path: Path,
    audit_job_id: str,
    graph_job_id: str,
    graph_id: str,
    source_summaries: list[Path],
) -> str:
    parts = [
        "python",
        str(repair_helper),
        "--project-root",
        str(project_root),
        "--audit-report",
        display_path(audit_report_path, project_root),
        "--graph-report",
        display_path(graph_report_path, project_root),
        "--audit-job-id",
        audit_job_id,
        "--graph-job-id",
        graph_job_id,
        "--graph-id",
        graph_id,
    ]
    for source_summary in source_summaries:
        parts.extend(["--source-summary", display_path(source_summary, project_root)])
    return shell_command(parts)


def source_list(paths: list[Path], project_root: Path) -> str:
    return "\n".join(f"- `{display_path(path, project_root)}`" for path in paths)


def node_list(ids: list[str]) -> str:
    return "\n".join(f"- `{node_id}`" for node_id in ids)


def materialize_ticket(
    *,
    job_id: str,
    marker: str,
    graph_id: str,
    graph_path: Path,
    node_ids: list[str],
    executable_node_ids: list[str],
    project_root: Path,
    source_summaries: list[Path],
    audit_job_id: str,
    audit_report_path: Path,
    graph_report_path: Path,
    audit_ticket_path: Path,
    exact_command: str,
    validation_command: str,
    document_audit_verifier_command: str,
    graph_report_verifier_command: str,
    repair_helper_command: str,
    pre_materialized_audit_ticket: bool,
) -> str:
    if pre_materialized_audit_ticket:
        required_reads_extra = f"- `{display_path(audit_ticket_path, project_root)}`\n"
        setup_action = (
            "- Read the existing audit ticket first.\n"
            "- Treat coordinator setup as already complete.\n"
            "- Execute only the supervisor-owned and worker-owned audit, report, "
            "validation, and repair actions.\n"
        )
        materializer_section = ""
        materialize_node_instruction = (
            "- Coordinator setup node: record `materialize_runtime_job` as "
            "`completed` in the graph report because the coordinator already "
            "completed setup. Do not take an action for this node.\n"
        )
        action_node_ids = [
            node_id
            for node_id in executable_node_ids
            if node_id != "materialize_runtime_job"
        ]
        pre_marker_warning = ""
        setup_recovery_rule = (
            "- If the existing audit ticket is missing or unusable, write a "
            "blocked graph report and stop.\n"
        )
        stop_intro = "The job is incomplete until both runtime reports below exist:"
    else:
        required_reads_extra = ""
        setup_action = (
            "- Run exactly the materializer command shown below once.\n"
            "- Read the generated audit ticket after the materializer command succeeds.\n"
        )
        materializer_section = f"""
## Exact Materializer Command

```powershell
{exact_command}
```

If this command fails, write a blocked graph report to
`{display_path(graph_report_path, project_root)}` and stop.
"""
        materialize_node_instruction = (
            "- `materialize_runtime_job`: run the exact materializer command once.\n"
            "- After `materialize_runtime_job`, never run the materializer command "
            "again in this job.\n"
        )
        action_node_ids = executable_node_ids
        pre_marker_warning = "- Do not reply with the outer marker after materializer success alone.\n"
        setup_recovery_rule = (
            "- Do not rerun the materializer command for repair, confirmation, "
            "uncertainty,\n"
            "  or recovery. If the materializer command has already run once and the\n"
            "  generated audit ticket is missing or unusable, write a blocked graph "
            "report\n"
            "  and stop.\n"
        )
        stop_intro = (
            "Materializer success is not completion. The job is incomplete until both\n"
            "runtime reports below exist:"
        )

    return f"""# Graph-Derived Document Artifact Audit Supervisor Job

Marker: `{marker}`

Execute this ticket exactly. This is an Agent Workbench local-supervisor job
derived from the tracked FreshForge-compatible workflow graph `{graph_id}`.

## Required Reads

- `{display_path(graph_path, project_root)}`
{required_reads_extra.rstrip()}
{source_list(source_summaries, project_root)}

## Workflow Nodes

Full graph node sequence:

{node_list(node_ids)}

Execute only these supervisor-owned and worker-owned nodes in order.
Coordinator nodes are already materialized in this ticket and must not be
performed by you.

{node_list(action_node_ids)}

## Allowed Actions

{setup_action.rstrip()}
- Invoke the auditor subagent required by the generated audit ticket.
- Write exactly these runtime report files:
  - `{display_path(audit_report_path, project_root)}`
  - `{display_path(graph_report_path, project_root)}`
- Do not edit tracked files.
- Do not create commits, branches, GitHub issues, GitHub comments, or pull
  requests.
{pre_marker_warning.rstrip()}
- Do not reply with the outer marker after audit-report validation alone.
- Do not delete or remove runtime files. If repair is needed, overwrite only
  the assigned audit report or graph report path.
{setup_recovery_rule.rstrip()}

## First-Action Gate

The final marker is forbidden until real artifact work has happened.

- Your first substantive action must be to read the existing audit ticket and
  produce or repair the assigned audit report.
- If you cannot use tools, cannot create files, or decide the job is blocked,
  write the assigned graph report with `final_signal` set to `job_failed` or
  `needs_coordinator_review`; do not reply with the final marker by itself.
- A response containing only the final marker before the two assigned report
  files exist is a protocol failure, even if the marker text is exact.
{materializer_section}

## Graph Execution Requirements

{materialize_node_instruction.rstrip()}
- `subagent_artifact_audit`: follow the generated audit ticket and invoke the
  configured read-only auditor subagent.
- `write_supervisor_report`: write the generated audit report JSON.
- `validate_and_repair_report`: run this command after writing the audit report:

```powershell
{validation_command}
```

- Then run this document-artifact audit verifier command:

```powershell
{document_audit_verifier_command}
```

- If validation fails, repair only the generated audit report fields needed to
  pass validation by overwriting the assigned report file; do not delete the
  report file first. Then run the failed validation command one more time.
- For any audit-report or graph-report validation failure, use this exact
  overwrite-only repair helper command before rerunning validators:

```powershell
{repair_helper_command}
```

- Do not use ad hoc shell, PowerShell, Python, or delete/recreate commands for
  report repair. The repair helper is the only authorized repair mechanism.
- `Remove-Item`, `del`, `rm`, or any delete-then-recreate workflow is forbidden
  for assigned report repair. Overwrite the report in place.
- Validator failure is not a stop condition. It is a repair instruction. If
  authority validation reports missing `escalations`,
  `public_safety.raw_transcript_policy`, or a score problem, repair those
  fields before continuing.
- The audit report must preserve these top-level fields from the generated
  audit ticket output shape:
  - `escalations`
  - `public_safety.tracked_artifact`
  - `public_safety.raw_transcript_policy`
- `coordinator_review_packet`: do not create a tracked summary; instead write
  the compact graph report described below.

## Required Report JSON Fields

These fields are mandatory in the audit report before the final marker:

- `verification.subagent_payload_excerpt`
- `verification.subagent_result_status`
- `verification.audit_items`
- `verification.all_decisions_consistent_with_gate`
- `escalations`
- `public_safety.raw_transcript_policy`

## Required Graph Report

This file is mandatory. It is not an optional summary. The job is a protocol
failure if `{display_path(graph_report_path, project_root)}` does not exist
before the final marker response.

Write this JSON object to `{display_path(graph_report_path, project_root)}`:

```json
{{
  "report_id": "{job_id}_graph_report",
  "graph_id": "{graph_id}",
  "audit_job_id": "{audit_job_id}",
  "supervisor_role": "supervisor",
  "final_signal": "job_complete_with_caveats",
  "completed_graph_nodes": [
    {{
      "node_id": "materialize_runtime_job",
      "status": "completed"
    }},
    {{
      "node_id": "subagent_artifact_audit",
      "status": "completed"
    }},
    {{
      "node_id": "write_supervisor_report",
      "status": "completed"
    }},
    {{
      "node_id": "validate_and_repair_report",
      "status": "completed"
    }}
  ],
  "audit_report_path": "{display_path(audit_report_path, project_root)}",
  "authority_validation": {{
    "attempted": true,
    "passed_after_repair": false,
    "error_excerpt": ""
  }},
  "subagent_invocation_observed_by_supervisor": true,
  "subagent_result": {{
    "status": "accepted_after_supervisor_repair",
    "repair_required": true,
    "summary": "Set status to accepted_without_repair, accepted_after_supervisor_repair, rejected_supervisor_replaced, or unavailable_supervisor_completed."
  }},
  "notes": []
}}
```

Keep `error_excerpt` under 500 characters. Do not paste raw transcript text.

After writing the graph report, run this graph-report verifier command:

```powershell
{graph_report_verifier_command}
```

If graph-report verification fails, repair only the assigned graph report file
by overwriting it in place. Do not delete the report file first. Then run the
graph-report verifier command one more time.

## Stop Condition

{stop_intro}

- `{display_path(audit_report_path, project_root)}`
- `{display_path(graph_report_path, project_root)}`

Before replying with the outer marker, check that both runtime report files
exist. If either file is missing, create or overwrite the missing assigned
report file first.

After both runtime reports exist, reply exactly:

`{marker} done`
"""


def materialize_manifest(
    *,
    job_id: str,
    marker: str,
    graph: dict[str, Any],
    graph_path: Path,
    node_ids: list[str],
    executable_node_ids: list[str],
    project_root: Path,
    source_summaries: list[Path],
    ticket_path: Path,
    audit_job_id: str,
    audit_report_path: Path,
    graph_report_path: Path,
    audit_ticket_path: Path,
    exact_command: str,
    validation_command: str,
    document_audit_verifier_command: str,
    graph_report_verifier_command: str,
    repair_helper_command: str,
    pre_materialized_audit_ticket: bool,
) -> dict[str, Any]:
    workflow = graph.get("workflow", {})
    if not isinstance(workflow, dict):
        workflow = {}
    return {
        "job_id": job_id,
        "marker": marker,
        "graph_id": workflow.get("id", ""),
        "graph_template": display_path(graph_path, project_root),
        "node_ids": node_ids,
        "executable_node_ids": executable_node_ids,
        "source_summaries": [
            display_path(path, project_root) for path in source_summaries
        ],
        "ticket_path": display_path(ticket_path, project_root),
        "audit_job_id": audit_job_id,
        "audit_ticket_path": display_path(audit_ticket_path, project_root),
        "audit_report_path": display_path(audit_report_path, project_root),
        "graph_report_path": display_path(graph_report_path, project_root),
        "pre_materialized_audit_ticket": pre_materialized_audit_ticket,
        "exact_materializer_command": exact_command,
        "exact_validation_command": validation_command,
        "exact_document_audit_verifier_command": document_audit_verifier_command,
        "exact_graph_report_verifier_command": graph_report_verifier_command,
        "exact_repair_helper_command": repair_helper_command,
        "runtime_only": True,
    }


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_dir = resolve_under_root(args.output_dir, project_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    graph_path = resolve_under_root(args.graph_template, project_root)
    graph = validate_graph(graph_path)
    workflow = graph.get("workflow", {})
    if not isinstance(workflow, dict):
        workflow = {}
    graph_id = str(workflow.get("id", "")).strip()
    if not graph_id:
        raise SystemExit("graph workflow.id is required")
    nodes = graph_node_ids(graph)
    executable_nodes = executable_supervisor_node_ids(nodes)

    materializer = resolve_under_root(args.audit_materializer, project_root)
    verifier = resolve_under_root(args.audit_verifier, project_root)
    graph_verifier = resolve_under_root(args.graph_verifier, project_root)
    repair_helper = resolve_under_root(args.repair_helper, project_root)
    source_summaries = [
        resolve_under_root(Path(value), project_root) for value in args.source_summary
    ]
    audit_job_id = f"{args.job_id}_audit"
    audit_marker = f"{args.marker}_AUDIT"
    ticket_path = output_dir / f"{args.job_id}_ticket.md"
    manifest_path = output_dir / f"{args.job_id}_manifest.json"
    audit_report_path = output_dir / f"{audit_job_id}_report.json"
    audit_ticket_path = output_dir / f"{audit_job_id}_ticket.md"
    graph_report_path = output_dir / f"{args.job_id}_graph_report.json"

    exact_command = exact_materializer_command(
        project_root=project_root,
        materializer=materializer,
        output_dir=output_dir,
        job_id=audit_job_id,
        marker=audit_marker,
        phase=args.phase,
        task_id=args.task_id,
        title=args.title,
        source_summaries=source_summaries,
        auditor_subagent_name=args.auditor_subagent_name,
    )
    validation_command = exact_validation_command(
        project_root=project_root,
        report_path=audit_report_path,
    )
    document_audit_verifier_command = exact_document_audit_verifier_command(
        project_root=project_root,
        verifier=verifier,
        report_path=audit_report_path,
        source_summaries=source_summaries,
    )
    graph_report_verifier_command = exact_graph_report_verifier_command(
        project_root=project_root,
        verifier=graph_verifier,
        graph_report_path=graph_report_path,
        audit_report_path=audit_report_path,
    )
    repair_helper_command = exact_repair_helper_command(
        project_root=project_root,
        repair_helper=repair_helper,
        audit_report_path=audit_report_path,
        graph_report_path=graph_report_path,
        audit_job_id=audit_job_id,
        graph_job_id=args.job_id,
        graph_id=graph_id,
        source_summaries=source_summaries,
    )
    if args.pre_materialize_audit_ticket:
        completed = subprocess.run(
            exact_command,
            cwd=project_root,
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit(
                "audit-ticket pre-materialization failed with exit code "
                f"{completed.returncode}\nstdout: {completed.stdout}\nstderr: "
                f"{completed.stderr}"
            )

    ticket = materialize_ticket(
        job_id=args.job_id,
        marker=args.marker,
        graph_id=graph_id,
        graph_path=graph_path,
        node_ids=nodes,
        executable_node_ids=executable_nodes,
        project_root=project_root,
        source_summaries=source_summaries,
        audit_job_id=audit_job_id,
        audit_report_path=audit_report_path,
        graph_report_path=graph_report_path,
        audit_ticket_path=audit_ticket_path,
        exact_command=exact_command,
        validation_command=validation_command,
        document_audit_verifier_command=document_audit_verifier_command,
        graph_report_verifier_command=graph_report_verifier_command,
        repair_helper_command=repair_helper_command,
        pre_materialized_audit_ticket=args.pre_materialize_audit_ticket,
    )
    ticket_path.write_text(ticket, encoding="utf-8")

    manifest = materialize_manifest(
        job_id=args.job_id,
        marker=args.marker,
        graph=graph,
        graph_path=graph_path,
        node_ids=nodes,
        executable_node_ids=executable_nodes,
        project_root=project_root,
        source_summaries=source_summaries,
        ticket_path=ticket_path,
        audit_job_id=audit_job_id,
        audit_report_path=audit_report_path,
        graph_report_path=graph_report_path,
        audit_ticket_path=audit_ticket_path,
        exact_command=exact_command,
        validation_command=validation_command,
        document_audit_verifier_command=document_audit_verifier_command,
        graph_report_verifier_command=graph_report_verifier_command,
        repair_helper_command=repair_helper_command,
        pre_materialized_audit_ticket=args.pre_materialize_audit_ticket,
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"ticket: {ticket_path}")
    print(f"manifest: {manifest_path}")
    print(f"audit_report: {audit_report_path}")
    print(f"graph_report: {graph_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
