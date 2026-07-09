"""Agent Workbench custom tools for Copilot SDK sessions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


AGENT_WORKBENCH_TOOL_NAMES = (
    "agent_workbench_run_context",
    "agent_workbench_result_contract",
    "agent_workbench_validate_result",
)


def validate_agent_workbench_tool_names(
    names: tuple[str, ...] | list[str],
) -> list[str]:
    allowed = set(AGENT_WORKBENCH_TOOL_NAMES)
    return [name for name in names if name not in allowed]


def build_agent_workbench_sdk_tools(
    names: tuple[str, ...] | list[str],
    *,
    manifest: dict[str, Any],
    manifest_path: Path | None = None,
) -> list[Any]:
    unknown = validate_agent_workbench_tool_names(names)
    if unknown:
        raise ValueError(f"unknown Agent Workbench SDK tool(s): {', '.join(unknown)}")
    if not names:
        return []

    from copilot import define_tool
    from pydantic import BaseModel, Field

    base = manifest_path.parent if manifest_path is not None else Path.cwd()

    class ValidateResultParams(BaseModel):
        path: str = Field(description="Result or blocker path to validate.")

    tool_by_name: dict[str, Any] = {
        "agent_workbench_run_context": define_tool(
            name="agent_workbench_run_context",
            description="Return public-safe Agent Workbench run context.",
            params_type=None,
            handler=lambda _params, _invocation: json.dumps(
                run_context_payload(manifest), sort_keys=True
            ),
        ),
        "agent_workbench_result_contract": define_tool(
            name="agent_workbench_result_contract",
            description="Return the required result and blocker contract for this run.",
            params_type=None,
            handler=lambda _params, _invocation: json.dumps(
                result_contract_payload(manifest), sort_keys=True
            ),
        ),
        "agent_workbench_validate_result": define_tool(
            name="agent_workbench_validate_result",
            description="Validate a result or blocker file against the manifest contract.",
            params_type=ValidateResultParams,
            handler=lambda params, _invocation: json.dumps(
                validate_result_payload(
                    manifest,
                    base=base,
                    requested_path=params.path,
                ),
                sort_keys=True,
            ),
        ),
    }
    return [tool_by_name[name] for name in names]


def run_context_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    paths = manifest.get("paths", {})
    control = manifest.get("control", {})
    return {
        "run_id": manifest.get("run_id", ""),
        "phase": manifest.get("phase", ""),
        "governing_issue": manifest.get("governing_issue", ""),
        "child_issue": manifest.get("child_issue", ""),
        "target_project": manifest.get("target_project", ""),
        "target_task": manifest.get("target_task", ""),
        "workspace_root": manifest.get("workspace_root", ""),
        "stop_condition": control.get("stop_condition", ""),
        "allowed_paths": {
            "ticket": paths.get("ticket", ""),
            "result": paths.get("result", ""),
            "blocker": paths.get("blocker", ""),
            "heartbeat": paths.get("heartbeat", ""),
        },
    }


def result_contract_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    paths = manifest.get("paths", {})
    return {
        "result_path": paths.get("result", ""),
        "blocker_path": paths.get("blocker", ""),
        "required_final_statuses": [
            "accepted-candidate",
            "blocked",
            "needs-supervisor-review",
        ],
        "required_result_sections": [
            "Final status",
            "Summary",
            "Files changed",
            "Validation",
            "Risks or follow-up",
        ],
        "required_blocker_sections": [
            "Final status",
            "Blocker",
            "Evidence",
            "Next required action",
        ],
    }


def validate_result_payload(
    manifest: dict[str, Any],
    *,
    base: Path,
    requested_path: str,
) -> dict[str, Any]:
    allowed = allowed_result_paths(manifest, base=base)
    candidate = resolve_result_path(requested_path, base=base)
    errors: list[str] = []
    if candidate not in allowed:
        errors.append("path is not the manifest result or blocker path")
    if not candidate.exists():
        errors.append("path does not exist")
        text = ""
    else:
        text = candidate.read_text(encoding="utf-8-sig")
    if text and "Final status:" not in text:
        errors.append("missing 'Final status:' line")
    if text and not any(
        status in text
        for status in ("accepted-candidate", "blocked", "needs-supervisor-review")
    ):
        errors.append("missing allowed final status value")
    return {
        "ok": not errors,
        "path": str(candidate),
        "errors": errors,
    }


def allowed_result_paths(manifest: dict[str, Any], *, base: Path) -> set[Path]:
    paths = manifest.get("paths", {})
    allowed: set[Path] = set()
    for key in ("result", "blocker"):
        value = paths.get(key)
        if isinstance(value, str) and value:
            allowed.add(resolve_result_path(value, base=base))
    return allowed


def resolve_result_path(path: str, *, base: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()
