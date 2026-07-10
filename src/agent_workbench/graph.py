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
        from freshforge.validation import (
            has_error_diagnostics,
            validate_workflow_document,
        )
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
        agent_parameters = (
            parameters.get("agent_workbench") if isinstance(parameters, dict) else None
        )
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
            parameters.get("agent_workbench", {})
            if isinstance(parameters, dict)
            else {}
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


def render_graph_decisions_markdown(data: dict[str, Any]) -> str:
    """Render graph-node delegation recommendations."""
    from .decision import decide_task

    workflow = data.get("workflow", {})
    if not isinstance(workflow, dict):
        workflow = {}
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        nodes = []

    lines = [
        "# Graph Delegation Decision Report",
        "",
        "## Workflow",
        "",
        f"- id: `{workflow.get('id', '')}`",
        f"- name: {workflow.get('name', '')}",
        "",
        "## Node Recommendations",
        "",
    ]
    for node in nodes:
        if not isinstance(node, dict):
            continue
        decision_input = decision_input_from_node(node)
        result = decide_task(decision_input)
        parameters = node.get("parameters", {})
        agent_parameters = (
            parameters.get("agent_workbench", {})
            if isinstance(parameters, dict)
            else {}
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
                f"- recommendation: `{result.recommendation}`",
                f"- node_kind: `{agent_parameters.get('node_kind', '')}`",
                f"- needs: {format_list(needs)}",
                f"- role: `{decision_input.get('role', '')}`",
                f"- capability: `{decision_input.get('task_type', '')}`",
                f"- authority_level: `{decision_input.get('authority_level', '')}`",
                f"- suitability: `{result.suitability}`",
                f"- risk: `{result.risk}`",
                f"- expected_net_savings_usd: {result.economics.expected_net_savings_usd:.6f}",
                "",
                "#### Reasons",
                "",
            ]
        )
        lines.extend(f"- {reason}" for reason in result.reasons)
        if result.cautions:
            lines.extend(["", "#### Cautions", ""])
            lines.extend(f"- {caution}" for caution in result.cautions)
        lines.extend(["", "#### Supervisor Next Action", "", result.next_action, ""])
    return "\n".join(lines)


def decision_input_from_node(node: dict[str, Any]) -> dict[str, Any]:
    provenance = node.get("provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}
    parameters = node.get("parameters", {})
    agent_parameters = (
        parameters.get("agent_workbench", {}) if isinstance(parameters, dict) else {}
    )
    if not isinstance(agent_parameters, dict):
        agent_parameters = {}

    node_kind = str(agent_parameters.get("node_kind", "graph_node"))
    authority = str(provenance.get("authority_level", "L6"))
    decision_authority = authority_to_decision_level(authority)
    worker_node = node_kind.startswith("worker_") or authority in {"L0", "L1"}

    expected_verification = str(agent_parameters.get("evidence_reference", "")).strip()
    if not expected_verification:
        expected_verification = verification_reference_from_node(node)

    return {
        "task_id": str(node.get("id", "")),
        "title": str(node.get("name") or node.get("id", "")),
        "task_type": str(provenance.get("capability", node_kind)),
        "roadmap_level": "subtask" if worker_node else "task",
        "suitability": "high" if worker_node else "avoid",
        "risk": "low" if worker_node else "medium",
        "model": str(
            provenance.get("model_profile") or provenance.get("implementation", "")
        ),
        "model_profile_status": "observed",
        "authority_level": decision_authority,
        "expected_verification": expected_verification,
        "role": str(provenance.get("role", "")),
        "requires_tracked_mutation": node_kind == "supervisor_promotion",
        "requires_github_mutation": False,
        "requires_release_or_closeout": node_kind == "supervisor_promotion",
        "economics": default_node_economics(worker_node),
    }


def authority_to_decision_level(authority: str) -> str:
    if authority in {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}:
        return authority
    authority_map = {
        "deterministic": "L0",
        "worker-owned": "L1",
        "local-worker-owned": "L1",
        "supervisor-approved": "L4",
        "supervisor-owned": "L6",
        "coordinator-owned": "L6",
        "developer-owned": "L6",
    }
    return authority_map.get(authority, "L6")


def verification_reference_from_node(node: dict[str, Any]) -> str:
    artifacts = node.get("artifacts", [])
    if not isinstance(artifacts, list):
        return "graph node artifacts"
    references: list[str] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        artifact_id = str(artifact.get("artifact_id", "")).strip()
        path_or_reference = str(artifact.get("path_or_reference", "")).strip()
        if artifact_id and path_or_reference:
            references.append(f"{artifact_id}: {path_or_reference}")
        elif path_or_reference:
            references.append(path_or_reference)
    return "; ".join(references) or "graph node artifacts"


def default_node_economics(worker_node: bool) -> dict[str, float]:
    if not worker_node:
        return {}
    return {
        "direct_supervisor_input_tokens": 4000,
        "direct_supervisor_output_tokens": 1000,
        "delegated_supervisor_input_tokens": 900,
        "delegated_supervisor_output_tokens": 250,
        "worker_input_tokens": 4000,
        "worker_output_tokens": 1000,
        "cleanup_supervisor_input_tokens": 500,
        "cleanup_supervisor_output_tokens": 200,
        "supervisor_input_price_per_1m_usd": 2.0,
        "supervisor_output_price_per_1m_usd": 8.0,
        "worker_input_price_per_1m_usd": 0.0,
        "worker_output_price_per_1m_usd": 0.0,
        "failure_probability": 0.25,
    }


def format_list(values: list[Any]) -> str:
    if not values:
        return "`none`"
    return ", ".join(f"`{value}`" for value in values)
