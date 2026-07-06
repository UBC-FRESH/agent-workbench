"""Verify a document-artifact graph supervisor report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FINAL_SIGNALS = {
    "job_complete",
    "job_complete_with_caveats",
    "needs_coordinator_review",
    "needs_developer_decision",
    "job_failed",
    "job_aborted",
    "job_partially_complete",
}
SUBAGENT_RESULT_STATUSES = {
    "accepted_without_repair",
    "accepted_after_supervisor_repair",
    "rejected_supervisor_replaced",
    "unavailable_supervisor_completed",
}
REQUIRED_NODE_IDS = {
    "materialize_runtime_job",
    "subagent_artifact_audit",
    "write_supervisor_report",
    "validate_and_repair_report",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify document-artifact graph supervisor report structure."
    )
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--graph-report", type=Path, required=True)
    parser.add_argument("--audit-report", type=Path)
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


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing JSON report: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def verify_graph_report(
    report: dict[str, Any],
    *,
    audit_report: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    for field in (
        "report_id",
        "graph_id",
        "audit_job_id",
        "supervisor_role",
        "final_signal",
        "completed_graph_nodes",
        "audit_report_path",
        "authority_validation",
        "subagent_invocation_observed_by_supervisor",
        "subagent_result",
    ):
        if field not in report:
            errors.append(f"missing required field: {field}")

    if report.get("supervisor_role") != "supervisor":
        errors.append("supervisor_role must be supervisor")

    final_signal = str(report.get("final_signal", ""))
    if final_signal not in FINAL_SIGNALS:
        errors.append(f"final_signal must be one of {sorted(FINAL_SIGNALS)}")

    errors.extend(verify_completed_nodes(report.get("completed_graph_nodes")))
    errors.extend(verify_authority_validation(report.get("authority_validation")))
    errors.extend(verify_subagent_result(report.get("subagent_result"), audit_report))

    if report.get("subagent_invocation_observed_by_supervisor") is not True:
        errors.append("subagent_invocation_observed_by_supervisor must be true")

    return errors


def verify_completed_nodes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return ["completed_graph_nodes must be a list"]
    errors: list[str] = []
    observed: dict[str, Any] = {}
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"completed_graph_nodes[{index}] must be an object")
            continue
        node_id = str(item.get("node_id", ""))
        observed[node_id] = item
        if item.get("status") != "completed":
            errors.append(f"completed_graph_nodes[{index}].status must be completed")
    missing = sorted(REQUIRED_NODE_IDS - set(observed))
    if missing:
        errors.append(f"completed_graph_nodes missing required nodes: {missing}")
    return errors


def verify_authority_validation(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["authority_validation must be an object"]
    errors: list[str] = []
    if value.get("attempted") is not True:
        errors.append("authority_validation.attempted must be true")
    if not isinstance(value.get("passed_after_repair"), bool):
        errors.append("authority_validation.passed_after_repair must be boolean")
    error_excerpt = value.get("error_excerpt", "")
    if not isinstance(error_excerpt, str):
        errors.append("authority_validation.error_excerpt must be a string")
    elif len(error_excerpt) > 500:
        errors.append("authority_validation.error_excerpt must be 500 characters or fewer")
    return errors


def verify_subagent_result(
    value: Any,
    audit_report: dict[str, Any] | None,
) -> list[str]:
    if not isinstance(value, dict):
        return ["subagent_result must be an object"]
    errors: list[str] = []
    status = str(value.get("status", ""))
    if status not in SUBAGENT_RESULT_STATUSES:
        errors.append(
            f"subagent_result.status must be one of {sorted(SUBAGENT_RESULT_STATUSES)}"
        )
    repair_required = value.get("repair_required")
    if not isinstance(repair_required, bool):
        errors.append("subagent_result.repair_required must be boolean")
    elif status == "accepted_without_repair" and repair_required:
        errors.append(
            "subagent_result.repair_required must be false for accepted_without_repair"
        )
    elif status and status != "accepted_without_repair" and not repair_required:
        errors.append(
            "subagent_result.repair_required must be true unless accepted_without_repair"
        )
    summary = str(value.get("summary", "")).strip()
    if not summary:
        errors.append("subagent_result.summary is required")
    elif len(summary) > 1000:
        errors.append("subagent_result.summary must be 1000 characters or fewer")

    if audit_report is not None:
        verification = audit_report.get("verification")
        if not isinstance(verification, dict):
            errors.append("audit_report.verification must be an object")
        else:
            audit_status = str(verification.get("subagent_result_status", ""))
            if audit_status and status != audit_status:
                errors.append(
                    "subagent_result.status must match "
                    "audit_report.verification.subagent_result_status"
                )
    return errors


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    graph_report_path = resolve_under_root(args.graph_report, project_root)
    try:
        graph_report = load_json(graph_report_path)
        audit_report = None
        if args.audit_report is not None:
            audit_report = load_json(resolve_under_root(args.audit_report, project_root))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"invalid document artifact graph report: {exc}")
        return 1
    errors = verify_graph_report(graph_report, audit_report=audit_report)
    if errors:
        print("invalid document artifact graph report")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "valid document artifact graph report: "
        f"{display_path(graph_report_path, project_root)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
