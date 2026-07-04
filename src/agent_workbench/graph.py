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


def load_graph_document(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("graph document must be a JSON object")
    return data


def validate_graph_document(data: dict[str, Any], *, source_path: Path | None = None) -> GraphValidation:
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
    return GraphValidation(
        ok=not has_error_diagnostics(diagnostics),
        workflow_id=spec.id if spec is not None else None,
        node_count=len(spec.nodes) if spec is not None else 0,
        diagnostics=converted,
    )


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
