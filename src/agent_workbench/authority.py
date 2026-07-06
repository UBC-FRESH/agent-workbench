"""Authority hierarchy, supervisor job contract, and report validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


AUTHORITY_ROLES = ("developer", "coordinator", "supervisor", "worker")
JOB_SIGNALS = {
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
WORKSPACE_ROOT_POLICIES = {
    "absolute_runtime_path",
    "repo_relative",
    "placeholder",
}
CONTRACT_REQUIRED_FIELDS = (
    "contract_id",
    "authority_model",
    "workspace",
    "job",
    "inputs",
    "outputs",
    "allowed_tools",
    "forbidden_actions",
    "stop_conditions",
    "success_criteria",
    "final_signals",
    "verification",
    "public_safety",
)
REPORT_REQUIRED_FIELDS = (
    "report_id",
    "contract_id",
    "supervisor_role",
    "final_signal",
    "completed_nodes",
    "artifacts",
    "verification",
    "escalations",
)


@dataclass(frozen=True)
class AuthorityValidation:
    ok: bool
    errors: list[str]


def load_authority_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("authority record must be a JSON object")
    return data


def validate_supervisor_job_contract(data: dict[str, Any]) -> AuthorityValidation:
    errors: list[str] = []
    for field in CONTRACT_REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    errors.extend(validate_authority_model(data.get("authority_model")))
    errors.extend(validate_workspace(data.get("workspace")))
    errors.extend(validate_job(data.get("job")))
    errors.extend(validate_artifact_list(data.get("inputs"), "inputs"))
    errors.extend(validate_artifact_list(data.get("outputs"), "outputs"))

    for field in (
        "allowed_tools",
        "forbidden_actions",
        "stop_conditions",
        "success_criteria",
    ):
        if not nonempty_string_list(data.get(field)):
            errors.append(f"{field} must be a nonempty list of strings")

    final_signals = data.get("final_signals")
    if not nonempty_string_list(final_signals):
        errors.append("final_signals must be a nonempty list of strings")
    else:
        unknown = sorted(set(final_signals) - JOB_SIGNALS)
        if unknown:
            errors.append(f"final_signals contains unknown signals: {unknown}")
        if not ({"job_complete", "needs_coordinator_review"} & set(final_signals)):
            errors.append(
                "final_signals should include job_complete or needs_coordinator_review"
            )

    verification = data.get("verification")
    if not isinstance(verification, dict):
        errors.append("verification must be an object")
    else:
        for field in ("required_checks", "evidence_paths", "scoring"):
            if not verification.get(field):
                errors.append(f"verification.{field} is required")

    errors.extend(validate_public_safety(data.get("public_safety"), data))
    return AuthorityValidation(ok=not errors, errors=errors)


def validate_supervisor_report(data: dict[str, Any]) -> AuthorityValidation:
    errors: list[str] = []
    for field in REPORT_REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    if str(data.get("supervisor_role", "")) != "supervisor":
        errors.append("supervisor_role must be supervisor")

    final_signal = str(data.get("final_signal", ""))
    if final_signal not in JOB_SIGNALS:
        errors.append(f"final_signal must be one of {sorted(JOB_SIGNALS)}")

    completed_nodes = data.get("completed_nodes")
    if not isinstance(completed_nodes, list):
        errors.append("completed_nodes must be a list")
    else:
        for index, node in enumerate(completed_nodes):
            if not isinstance(node, dict):
                errors.append(f"completed_nodes[{index}] must be an object")
                continue
            for field in ("node_id", "owner_role", "status"):
                if not node.get(field):
                    errors.append(f"completed_nodes[{index}].{field} is required")
            owner_role = str(node.get("owner_role", ""))
            if owner_role not in AUTHORITY_ROLES:
                errors.append(
                    f"completed_nodes[{index}].owner_role must be one of "
                    f"{list(AUTHORITY_ROLES)}"
                )

    errors.extend(validate_artifact_list(data.get("artifacts"), "artifacts"))

    verification = data.get("verification")
    if not isinstance(verification, dict):
        errors.append("verification must be an object")
    else:
        if "checks_run" not in verification:
            errors.append("verification.checks_run is required")
        if "score" not in verification:
            errors.append("verification.score is required")
        errors.extend(validate_subagent_payload_evidence(verification))

    escalations = data.get("escalations")
    if not isinstance(escalations, list):
        errors.append("escalations must be a list")

    public_safety = data.get("public_safety", {"tracked_artifact": False})
    errors.extend(validate_public_safety(public_safety, data))
    return AuthorityValidation(ok=not errors, errors=errors)


def validate_subagent_payload_evidence(verification: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    attempted = verification.get("subagent_invocation_attempted")
    if attempted is not True:
        return errors
    if not str(verification.get("subagent_name", "")).strip():
        errors.append("verification.subagent_name is required when subagent was attempted")
    if "subagent_invocation_observed_by_supervisor" not in verification:
        errors.append(
            "verification.subagent_invocation_observed_by_supervisor is required "
            "when subagent was attempted"
        )
    excerpt = str(verification.get("subagent_payload_excerpt", "")).strip()
    if not excerpt:
        errors.append(
            "verification.subagent_payload_excerpt is required when subagent was attempted"
        )
    elif len(excerpt) > 1000:
        errors.append("verification.subagent_payload_excerpt must be 1000 characters or fewer")
    result_status = str(verification.get("subagent_result_status", "")).strip()
    if result_status not in SUBAGENT_RESULT_STATUSES:
        errors.append(
            "verification.subagent_result_status must be one of "
            f"{sorted(SUBAGENT_RESULT_STATUSES)} when subagent was attempted"
        )
    repair_summary = str(verification.get("subagent_repair_summary", "")).strip()
    if result_status and result_status != "accepted_without_repair" and not repair_summary:
        errors.append(
            "verification.subagent_repair_summary is required when the subagent "
            "result was repaired, rejected, replaced, or unavailable"
        )
    return errors


def validate_authority_model(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["authority_model must be an object"]
    levels = value.get("levels")
    if not isinstance(levels, list):
        return ["authority_model.levels must be a list"]
    seen: set[str] = set()
    for index, level in enumerate(levels):
        if not isinstance(level, dict):
            errors.append(f"authority_model.levels[{index}] must be an object")
            continue
        role = str(level.get("role", ""))
        seen.add(role)
        if role not in AUTHORITY_ROLES:
            errors.append(
                f"authority_model.levels[{index}].role must be one of "
                f"{list(AUTHORITY_ROLES)}"
            )
        for field in ("authority", "responsibilities", "nondelegable_actions"):
            if not level.get(field):
                errors.append(f"authority_model.levels[{index}].{field} is required")
    missing = [role for role in AUTHORITY_ROLES if role not in seen]
    if missing:
        errors.append(f"authority_model.levels missing roles: {missing}")
    return errors


def validate_workspace(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["workspace must be an object"]
    errors: list[str] = []
    root = str(value.get("root", "")).strip()
    policy = str(value.get("root_policy", "")).strip()
    if not root:
        errors.append("workspace.root is required")
    if policy not in WORKSPACE_ROOT_POLICIES:
        errors.append(
            f"workspace.root_policy must be one of {sorted(WORKSPACE_ROOT_POLICIES)}"
        )
    if policy == "absolute_runtime_path" and ("${" in root or root.startswith(".")):
        errors.append("workspace.root must be absolute when root_policy is absolute_runtime_path")
    if not value.get("wrong_root_stop_rule"):
        errors.append("workspace.wrong_root_stop_rule is required")
    return errors


def validate_job(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["job must be an object"]
    errors: list[str] = []
    for field in ("phase", "task_id", "title", "goal", "supervisor_role"):
        if not value.get(field):
            errors.append(f"job.{field} is required")
    if str(value.get("supervisor_role", "")) != "supervisor":
        errors.append("job.supervisor_role must be supervisor")
    return errors


def validate_artifact_list(value: Any, field: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list) or not value:
        return [f"{field} must be a nonempty list"]
    for index, item in enumerate(value):
        prefix = f"{field}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for required in ("artifact_id", "path", "role"):
            if not item.get(required):
                errors.append(f"{prefix}.{required} is required")
        role = str(item.get("role", ""))
        if role not in {"input", "output", "evidence", "report"}:
            errors.append(f"{prefix}.role must be input, output, evidence, or report")
    return errors


def validate_public_safety(value: Any, record: dict[str, Any]) -> list[str]:
    if not isinstance(value, dict):
        return ["public_safety must be an object"]
    errors: list[str] = []
    tracked = bool(value.get("tracked_artifact", False))
    if "raw_transcript_policy" not in value:
        errors.append("public_safety.raw_transcript_policy is required")
    if tracked:
        for finding in find_private_values(record):
            errors.append(f"private-looking value detected: {finding}")
    return errors


def nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def render_supervisor_job_contract(data: dict[str, Any]) -> str:
    lines = [
        "# Supervisor Job Contract",
        "",
        f"- contract_id: `{data.get('contract_id', '')}`",
        f"- workspace_root: `{get_nested(data, 'workspace', 'root')}`",
        f"- workspace_root_policy: `{get_nested(data, 'workspace', 'root_policy')}`",
        f"- phase: `{get_nested(data, 'job', 'phase')}`",
        f"- task_id: `{get_nested(data, 'job', 'task_id')}`",
        f"- title: {get_nested(data, 'job', 'title')}",
        "",
        "## Authority Model",
        "",
    ]
    for level in data.get("authority_model", {}).get("levels", []):
        if not isinstance(level, dict):
            continue
        lines.extend(
            [
                f"### `{level.get('role', '')}`",
                "",
                f"- authority: {level.get('authority', '')}",
                f"- responsibilities: {format_list(level.get('responsibilities', []))}",
                "- nondelegable_actions: "
                f"{format_list(level.get('nondelegable_actions', []))}",
                "",
            ]
        )
    lines.extend(["## Inputs", ""])
    lines.extend(render_artifacts(data.get("inputs", [])))
    lines.extend(["", "## Outputs", ""])
    lines.extend(render_artifacts(data.get("outputs", [])))
    lines.extend(["", "## Allowed Tools", ""])
    lines.extend(f"- `{tool}`" for tool in data.get("allowed_tools", []))
    lines.extend(["", "## Forbidden Actions", ""])
    lines.extend(f"- {item}" for item in data.get("forbidden_actions", []))
    lines.extend(["", "## Stop Conditions", ""])
    lines.extend(f"- {item}" for item in data.get("stop_conditions", []))
    lines.extend(["", "## Success Criteria", ""])
    lines.extend(f"- {item}" for item in data.get("success_criteria", []))
    lines.extend(["", "## Final Signals", ""])
    lines.extend(f"- `{signal}`" for signal in data.get("final_signals", []))
    lines.append("")
    return "\n".join(lines)


def render_supervisor_report(data: dict[str, Any]) -> str:
    lines = [
        "# Supervisor Report",
        "",
        f"- report_id: `{data.get('report_id', '')}`",
        f"- contract_id: `{data.get('contract_id', '')}`",
        f"- final_signal: `{data.get('final_signal', '')}`",
        "",
        "## Completed Nodes",
        "",
    ]
    for node in data.get("completed_nodes", []):
        if not isinstance(node, dict):
            continue
        lines.append(
            "- `{node}` ({role}): `{status}`".format(
                node=node.get("node_id", ""),
                role=node.get("owner_role", ""),
                status=node.get("status", ""),
            )
        )
    lines.extend(["", "## Artifacts", ""])
    lines.extend(render_artifacts(data.get("artifacts", [])))
    lines.extend(["", "## Verification", ""])
    verification = data.get("verification", {})
    if isinstance(verification, dict):
        for key, value in verification.items():
            lines.append(f"- {key}: {format_value(value)}")
    lines.extend(["", "## Escalations", ""])
    escalations = data.get("escalations", [])
    if not escalations:
        lines.append("- none")
    else:
        for item in escalations:
            lines.append(f"- {format_value(item)}")
    lines.append("")
    return "\n".join(lines)


def render_artifacts(artifacts: Any) -> list[str]:
    if not isinstance(artifacts, list):
        return ["- invalid artifact list"]
    lines: list[str] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            lines.append("- invalid artifact")
            continue
        lines.append(
            "- `{artifact_id}` ({role}): `{path}`".format(
                artifact_id=artifact.get("artifact_id", ""),
                role=artifact.get("role", ""),
                path=artifact.get("path", ""),
            )
        )
    return lines


def get_nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return ""
        value = value.get(key, "")
    return value


def format_list(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    return ", ".join(f"`{item}`" for item in value)


def format_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(format_value(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
