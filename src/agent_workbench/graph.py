"""FreshForge-backed graph validation helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class FreshForgeGraphUnavailable(RuntimeError):
    """Raised when the optional FreshForge graph dependency is unavailable."""


@dataclass(frozen=True)
class GraphDiagnostic:
    severity: str
    code: str
    message: str
    location: str | None = None


@dataclass(frozen=True)
class GraphValidation:
    ok: bool
    workflow_id: str | None
    node_count: int
    diagnostics: list[GraphDiagnostic]


REQUIRED_PROVENANCE_FIELDS = ("role", "capability", "authority_level", "implementation")
REQUIRED_AGENT_PARAMETERS = ("node_kind", "execution_boundary")
FORBIDDEN_NODE_FIELDS = {
    "role",
    "capability",
    "authority_level",
    "implementation",
    "token_accounting",
    "claim_review",
    "supervisor_decision",
}


def load_graph_document(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("graph document must be a JSON object")
    return data


def validate_graph_document(
    data: dict[str, Any],
    *,
    source_path: Path | None = None,
    agent_metadata: bool = False,
) -> GraphValidation:
    """Validate a FreshForge-compatible workflow graph without executing it."""
    try:
        from freshforge.records import DiagnosticSeverity
        from freshforge.validation import has_error_diagnostics, validate_workflow_document
    except ImportError as exc:
        raise FreshForgeGraphUnavailable(
            "FreshForge graph validation is optional. Install with "
            "`python -m pip install -e .[graph]` from the Agent Workbench checkout."
        ) from exc

    spec, diagnostics = validate_workflow_document(
        data,
        source_path=str(source_path) if source_path is not None else None,
    )
    converted = [
        GraphDiagnostic(
            severity=str(diagnostic.severity.value),
            code=diagnostic.code,
            message=diagnostic.message,
            location=diagnostic.location,
        )
        for diagnostic in diagnostics
    ]
    if agent_metadata:
        converted.extend(validate_agent_metadata(data))
    return GraphValidation(
        ok=not has_error_diagnostics(diagnostics)
        and not any(diagnostic.severity == "error" for diagnostic in converted),
        workflow_id=spec.id if spec is not None else None,
        node_count=len(spec.nodes) if spec is not None else 0,
        diagnostics=converted,
    )


def validate_agent_metadata(data: dict[str, Any]) -> list[GraphDiagnostic]:
    """Validate Agent Workbench metadata placement inside FreshForge fields."""
    diagnostics: list[GraphDiagnostic] = []
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        return diagnostics

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        location = f"nodes[{index}]"
        node_id = str(node.get("id", index))

        for field in sorted(FORBIDDEN_NODE_FIELDS):
            if field in node:
                diagnostics.append(
                    GraphDiagnostic(
                        severity="error",
                        code="agent_metadata.top_level_field",
                        message=(
                            f"Node '{node_id}' must store Agent Workbench "
                            f"metadata field '{field}' in parameters or provenance."
                        ),
                        location=f"{location}.{field}",
                    )
                )

        provenance = node.get("provenance")
        if not isinstance(provenance, dict):
            diagnostics.append(
                GraphDiagnostic(
                    severity="error",
                    code="agent_metadata.provenance.required",
                    message=f"Node '{node_id}' requires provenance metadata.",
                    location=f"{location}.provenance",
                )
            )
            provenance = {}
        for field in REQUIRED_PROVENANCE_FIELDS:
            if not str(provenance.get(field, "")).strip():
                diagnostics.append(
                    GraphDiagnostic(
                        severity="error",
                        code="agent_metadata.provenance.field_required",
                        message=f"Node '{node_id}' requires provenance.{field}.",
                        location=f"{location}.provenance.{field}",
                    )
                )

        parameters = node.get("parameters")
        agent_parameters = parameters.get("agent_workbench") if isinstance(parameters, dict) else None
        if not isinstance(agent_parameters, dict):
            diagnostics.append(
                GraphDiagnostic(
                    severity="error",
                    code="agent_metadata.parameters.required",
                    message=(
                        f"Node '{node_id}' requires parameters.agent_workbench "
                        "metadata."
                    ),
                    location=f"{location}.parameters.agent_workbench",
                )
            )
            agent_parameters = {}
        for field in REQUIRED_AGENT_PARAMETERS:
            if not str(agent_parameters.get(field, "")).strip():
                diagnostics.append(
                    GraphDiagnostic(
                        severity="error",
                        code="agent_metadata.parameters.field_required",
                        message=f"Node '{node_id}' requires parameters.agent_workbench.{field}.",
                        location=f"{location}.parameters.agent_workbench.{field}",
                    )
                )

    return diagnostics


def render_graph_validation(result: GraphValidation) -> str:
    lines = [
        "# Graph Validation",
        "",
        f"- ok: {str(result.ok).lower()}",
        f"- workflow_id: `{result.workflow_id or ''}`",
        f"- node_count: {result.node_count}",
        "",
        "## Diagnostics",
        "",
    ]
    if not result.diagnostics:
        lines.append("- none")
    for diagnostic in result.diagnostics:
        location = f" at `{diagnostic.location}`" if diagnostic.location else ""
        lines.append(
            f"- {diagnostic.severity}: `{diagnostic.code}`{location} - "
            f"{diagnostic.message}"
        )
    lines.append("")
    return "\n".join(lines)


def render_graph_markdown(data: dict[str, Any]) -> str:
    workflow = data.get("workflow", {})
    if not isinstance(workflow, dict):
        workflow = {}
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        nodes = []

    lines = [
        "# Agent Workbench Graph",
        "",
        "## Workflow",
        "",
        f"- id: `{workflow.get('id', '')}`",
        f"- name: {workflow.get('name', '')}",
        f"- description: {workflow.get('description', '')}",
        "",
        "## Nodes",
        "",
    ]
    for node in nodes:
        if not isinstance(node, dict):
            continue
        provenance = node.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {}
        parameters = node.get("parameters", {})
        agent_parameters = (
            parameters.get("agent_workbench", {}) if isinstance(parameters, dict) else {}
        )
        if not isinstance(agent_parameters, dict):
            agent_parameters = {}
        needs = node.get("needs", [])
        if not isinstance(needs, list):
            needs = []
        lines.extend(
            [
                f"### `{node.get('id', '')}`",
                "",
                f"- provider: `{node.get('provider', '')}`",
                f"- needs: {format_list(needs)}",
                f"- node_kind: `{agent_parameters.get('node_kind', '')}`",
                f"- role: `{provenance.get('role', '')}`",
                f"- capability: `{provenance.get('capability', '')}`",
                f"- authority_level: `{provenance.get('authority_level', '')}`",
                f"- implementation: {provenance.get('implementation', '')}",
                f"- execution_boundary: {agent_parameters.get('execution_boundary', '')}",
            ]
        )
        for key in (
            "evidence_reference",
            "claim_review",
            "supervisor_decision",
            "token_accounting",
        ):
            if key in agent_parameters:
                lines.append(f"- {key}: {agent_parameters[key]}")
        lines.extend(["", "#### Artifacts", ""])
        artifacts = node.get("artifacts", [])
        if not isinstance(artifacts, list) or not artifacts:
            lines.append("- none")
        else:
            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    continue
                lines.append(
                    f"- `{artifact.get('artifact_id', '')}` "
                    f"({artifact.get('kind', '')}): {artifact.get('path_or_reference', '')}"
                )
        lines.append("")
    return "\n".join(lines)


def format_list(values: list[Any]) -> str:
    if not values:
        return "`none`"
    return ", ".join(f"`{value}`" for value in values)
