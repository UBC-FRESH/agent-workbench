"""Role, capability, and implementation records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


ROLE_TYPES = {"reviewer", "programmer", "analyst", "editor", "supervisor"}
IMPLEMENTATION_TYPES = {"human", "local-worker", "paid-agent", "script", "workflow-tool"}
AUTHORITY_LEVELS = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "supervisor-owned"}

REQUIRED_FIELDS = ("role", "capability", "implementations", "selection_policy")


@dataclass(frozen=True)
class RoleValidation:
    ok: bool
    errors: list[str]


def load_role_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("role/capability record must be a JSON object")
    return data


def validate_role_record(data: dict[str, Any]) -> RoleValidation:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    role = data.get("role")
    if not isinstance(role, dict):
        errors.append("role must be an object")
    else:
        role_type = str(role.get("type", ""))
        if role_type not in ROLE_TYPES:
            errors.append(f"role.type must be one of {sorted(ROLE_TYPES)}")
        for field in ("id", "scope", "responsibility", "allowed_artifacts"):
            if not role.get(field):
                errors.append(f"role.{field} is required")

    capability = data.get("capability")
    if not isinstance(capability, dict):
        errors.append("capability must be an object")
    else:
        for field in ("id", "description", "task_types", "inputs", "outputs"):
            if not capability.get(field):
                errors.append(f"capability.{field} is required")
        authority = str(capability.get("maximum_authority_level", ""))
        if authority not in AUTHORITY_LEVELS:
            errors.append(
                "capability.maximum_authority_level must be one of "
                f"{sorted(AUTHORITY_LEVELS)}"
            )

    implementations = data.get("implementations")
    if not isinstance(implementations, list) or not implementations:
        errors.append("implementations must be a nonempty list")
    else:
        for index, implementation in enumerate(implementations):
            errors.extend(validate_implementation(implementation, index))

    selection = data.get("selection_policy")
    if not isinstance(selection, dict):
        errors.append("selection_policy must be an object")
    elif not selection.get("model_swap_rule"):
        errors.append("selection_policy.model_swap_rule is required")

    for finding in find_private_values(data):
        errors.append(f"private-looking value detected: {finding}")

    return RoleValidation(ok=not errors, errors=errors)


def validate_implementation(value: Any, index: int) -> list[str]:
    prefix = f"implementations[{index}]"
    if not isinstance(value, dict):
        return [f"{prefix} must be an object"]
    errors: list[str] = []
    implementation_type = str(value.get("type", ""))
    if implementation_type not in IMPLEMENTATION_TYPES:
        errors.append(f"{prefix}.type must be one of {sorted(IMPLEMENTATION_TYPES)}")
    authority = str(value.get("authority_level", ""))
    if authority not in AUTHORITY_LEVELS:
        errors.append(f"{prefix}.authority_level must be one of {sorted(AUTHORITY_LEVELS)}")
    for field in ("id", "name", "fit_notes"):
        if not value.get(field):
            errors.append(f"{prefix}.{field} is required")
    return errors


def render_role_markdown(data: dict[str, Any]) -> str:
    role = data.get("role", {})
    capability = data.get("capability", {})
    selection = data.get("selection_policy", {})
    lines = [
        "# Role Capability Implementation Record",
        "",
        "## Role",
        "",
    ]
    if isinstance(role, dict):
        for key, value in role.items():
            lines.append(f"- {key}: {format_value(value)}")

    lines.extend(["", "## Capability", ""])
    if isinstance(capability, dict):
        for key, value in capability.items():
            lines.append(f"- {key}: {format_value(value)}")

    lines.extend(["", "## Implementations", ""])
    implementations = data.get("implementations", [])
    if isinstance(implementations, list):
        for implementation in implementations:
            if not isinstance(implementation, dict):
                continue
            lines.append(f"### `{implementation.get('id', '')}`")
            lines.append("")
            for key, value in implementation.items():
                lines.append(f"- {key}: {format_value(value)}")
            lines.append("")

    lines.extend(["## Selection Policy", ""])
    if isinstance(selection, dict):
        for key, value in selection.items():
            lines.append(f"- {key}: {format_value(value)}")
    lines.append("")
    return "\n".join(lines)


def format_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(f"`{item}`" for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
