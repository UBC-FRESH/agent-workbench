"""Artifact-first workflow step records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


ARTIFACT_KINDS = {"source", "generated", "promoted", "rejected"}
IMPLEMENTATION_TYPES = {"human", "local-worker", "paid-agent", "script", "ci", "workflow-tool"}

REQUIRED_FIELDS = (
    "workflow_id",
    "step_id",
    "title",
    "purpose",
    "input_artifacts",
    "transformation",
    "implementation",
    "output_artifacts",
    "verification",
    "token_accounting",
    "supervisor_decision",
)

ARTIFACT_REQUIRED_FIELDS = (
    "artifact_id",
    "kind",
    "path_or_reference",
    "provenance",
    "public_safety",
)


@dataclass(frozen=True)
class WorkflowValidation:
    ok: bool
    errors: list[str]


def load_workflow_step(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("workflow step record must be a JSON object")
    return data


def validate_workflow_step(data: dict[str, Any]) -> WorkflowValidation:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    for field in ("input_artifacts", "output_artifacts"):
        artifacts = data.get(field)
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(f"{field} must be a nonempty list")
            continue
        for index, artifact in enumerate(artifacts):
            errors.extend(validate_artifact(artifact, f"{field}[{index}]"))

    implementation = data.get("implementation")
    if not isinstance(implementation, dict):
        errors.append("implementation must be an object")
    else:
        implementation_type = str(implementation.get("type", ""))
        if implementation_type not in IMPLEMENTATION_TYPES:
            errors.append(
                "implementation.type must be one of "
                f"{sorted(IMPLEMENTATION_TYPES)}"
            )

    token_accounting = data.get("token_accounting")
    if not isinstance(token_accounting, dict):
        errors.append("token_accounting must be an object")
    else:
        for field, value in token_accounting.items():
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"token_accounting.{field} must be nonnegative number")

    for finding in find_private_values(data):
        errors.append(f"private-looking value detected: {finding}")

    return WorkflowValidation(ok=not errors, errors=errors)


def validate_artifact(value: Any, prefix: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{prefix} must be an object"]
    for field in ARTIFACT_REQUIRED_FIELDS:
        if field not in value:
            errors.append(f"{prefix}.{field} is required")
    kind = str(value.get("kind", ""))
    if kind not in ARTIFACT_KINDS:
        errors.append(f"{prefix}.kind must be one of {sorted(ARTIFACT_KINDS)}")
    decision = value.get("supervisor_decision")
    if kind in {"promoted", "rejected"} and not decision:
        errors.append(f"{prefix}.supervisor_decision is required for {kind} artifacts")
    return errors


def render_workflow_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Workflow Step Record",
        "",
        "## Metadata",
        "",
        f"- workflow_id: `{data.get('workflow_id', '')}`",
        f"- step_id: `{data.get('step_id', '')}`",
        f"- title: {data.get('title', '')}",
        f"- purpose: {data.get('purpose', '')}",
        "",
        "## Input Artifacts",
        "",
    ]
    lines.extend(render_artifacts(data.get("input_artifacts", [])))
    lines.extend(["", "## Transformation", ""])
    lines.append(str(data.get("transformation", "")))
    lines.extend(["", "## Implementation", ""])
    implementation = data.get("implementation", {})
    if isinstance(implementation, dict):
        for key, value in implementation.items():
            lines.append(f"- {key}: {format_value(value)}")

    lines.extend(["", "## Output Artifacts", ""])
    lines.extend(render_artifacts(data.get("output_artifacts", [])))
    lines.extend(["", "## Verification", ""])
    verification = data.get("verification", {})
    if isinstance(verification, dict):
        for key, value in verification.items():
            lines.append(f"- {key}: {format_value(value)}")

    lines.extend(["", "## Token Accounting", ""])
    token_accounting = data.get("token_accounting", {})
    if isinstance(token_accounting, dict):
        for key, value in token_accounting.items():
            lines.append(f"- {key}: {value}")

    lines.extend(["", "## Supervisor Decision", ""])
    decision = data.get("supervisor_decision", {})
    if isinstance(decision, dict):
        for key, value in decision.items():
            lines.append(f"- {key}: {format_value(value)}")
    lines.append("")
    return "\n".join(lines)


def render_artifacts(artifacts: Any) -> list[str]:
    lines: list[str] = []
    if not isinstance(artifacts, list):
        return ["- Invalid artifact list."]
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            lines.append("- Invalid artifact.")
            continue
        lines.append(f"### `{artifact.get('artifact_id', '')}`")
        lines.append("")
        for key in (
            "kind",
            "path_or_reference",
            "provenance",
            "public_safety",
            "verifier",
            "supervisor_decision",
        ):
            if key in artifact:
                lines.append(f"- {key}: {format_value(artifact.get(key))}")
        lines.append("")
    return lines


def format_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(f"`{item}`" for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
