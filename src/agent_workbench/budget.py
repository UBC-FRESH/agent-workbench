"""Paid-supervisor budget declaration validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


REQUIRED_FIELDS = (
    "budget_id",
    "project",
    "phase",
    "experiment_question",
    "max_paid_cost_usd",
    "max_attempts",
    "checkpoint_spans",
    "stop_condition",
    "maintainer_checkpoint",
    "summary_status",
    "public_safety",
)
SUMMARY_STATUS_FIELDS = (
    "budget_declared",
    "budget_exceeded",
    "attempt_count",
    "stop_rule_triggered",
    "maintainer_checkpoint_required",
)
SPAN_OWNERS = {"coordinator", "local_supervisor", "paid_supervisor", "worker"}


@dataclass(frozen=True)
class BudgetValidation:
    ok: bool
    errors: list[str]


def load_budget_declaration(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("budget declaration must be a JSON object")
    return data


def validate_budget_declaration(data: dict[str, Any]) -> BudgetValidation:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")
    for field in ("budget_id", "project", "phase", "experiment_question"):
        if not nonempty_string(data.get(field)):
            errors.append(f"{field} must be a nonempty string")
    if not nonnegative_number(data.get("max_paid_cost_usd")):
        errors.append("max_paid_cost_usd must be a nonnegative number")
    if not positive_integer(data.get("max_attempts")):
        errors.append("max_attempts must be a positive integer")
    errors.extend(validate_checkpoint_spans(data.get("checkpoint_spans")))
    errors.extend(
        validate_stop_condition(data.get("stop_condition"), data.get("max_attempts"))
    )
    errors.extend(validate_maintainer_checkpoint(data.get("maintainer_checkpoint")))
    errors.extend(
        validate_summary_status(data.get("summary_status"), data.get("max_attempts"))
    )
    errors.extend(validate_public_safety(data.get("public_safety"), data))
    return BudgetValidation(ok=not errors, errors=errors)


def validate_checkpoint_spans(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["checkpoint_spans must be a nonempty list"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        prefix = f"checkpoint_spans[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        span_id = item.get("span_id")
        if not isinstance(span_id, str) or not span_id.strip():
            errors.append(f"{prefix}.span_id must be a nonempty string")
        elif span_id in seen:
            errors.append(f"{prefix}.span_id is duplicated: {span_id}")
        else:
            seen.add(span_id)
        if item.get("owner") not in SPAN_OWNERS:
            errors.append(f"{prefix}.owner must be one of {sorted(SPAN_OWNERS)}")
        if not nonempty_string(item.get("description")):
            errors.append(f"{prefix}.description must be a nonempty string")
        if not isinstance(item.get("required"), bool):
            errors.append(f"{prefix}.required must be boolean")
    return errors


def validate_stop_condition(value: Any, max_attempts: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["stop_condition must be an object"]
    errors: list[str] = []
    if not nonempty_string(value.get("description")):
        errors.append("stop_condition.description must be a nonempty string")
    stop_after = value.get("stop_after_attempts")
    if not positive_integer(stop_after):
        errors.append("stop_condition.stop_after_attempts must be a positive integer")
    elif positive_integer(max_attempts) and stop_after > max_attempts:
        errors.append("stop_condition.stop_after_attempts cannot exceed max_attempts")
    for field in ("stop_on_budget_exceeded", "stop_on_repeated_failure"):
        if field in value and not isinstance(value.get(field), bool):
            errors.append(f"stop_condition.{field} must be boolean")
    return errors


def validate_maintainer_checkpoint(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["maintainer_checkpoint must be an object"]
    errors: list[str] = []
    if not isinstance(value.get("required"), bool):
        errors.append("maintainer_checkpoint.required must be boolean")
    if not nonempty_string(value.get("trigger")):
        errors.append("maintainer_checkpoint.trigger must be a nonempty string")
    if not nonempty_string(value.get("decision_surface")):
        errors.append(
            "maintainer_checkpoint.decision_surface must be a nonempty string"
        )
    return errors


def validate_summary_status(value: Any, max_attempts: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["summary_status must be an object"]
    errors: list[str] = []
    for field in SUMMARY_STATUS_FIELDS:
        if field not in value:
            errors.append(f"summary_status.{field} is required")
    for field in (
        "budget_declared",
        "budget_exceeded",
        "stop_rule_triggered",
        "maintainer_checkpoint_required",
    ):
        if field in value and not isinstance(value.get(field), bool):
            errors.append(f"summary_status.{field} must be boolean")
    attempt_count = value.get("attempt_count")
    if not nonnegative_integer(attempt_count):
        errors.append("summary_status.attempt_count must be a nonnegative integer")
    elif positive_integer(max_attempts) and attempt_count > max_attempts:
        errors.append("summary_status.attempt_count cannot exceed max_attempts")
    if value.get("budget_declared") is not True:
        errors.append("summary_status.budget_declared must be true")
    if (
        value.get("budget_exceeded") is True
        and value.get("stop_rule_triggered") is not True
    ):
        errors.append("budget_exceeded=true requires stop_rule_triggered=true")
    return errors


def validate_public_safety(value: Any, record: dict[str, Any]) -> list[str]:
    if not isinstance(value, dict):
        return ["public_safety must be an object"]
    errors: list[str] = []
    if not isinstance(value.get("tracked_artifact"), bool):
        errors.append("public_safety.tracked_artifact must be boolean")
    for field in (
        "contains_private_paths",
        "contains_provider_details",
        "contains_raw_prompts",
    ):
        if not isinstance(value.get(field), bool):
            errors.append(f"public_safety.{field} must be boolean")
        elif value.get(field):
            errors.append(f"public_safety.{field} must be false for budget records")
    if value.get("tracked_artifact") is True:
        private_values = find_private_values(record)
        if private_values:
            errors.append(
                "tracked budget declaration contains private-looking value(s): "
                + ", ".join(private_values[:3])
            )
    return errors


def render_budget_validation(data: dict[str, Any], result: BudgetValidation) -> str:
    summary = data.get("summary_status", {})
    if not isinstance(summary, dict):
        summary = {}
    lines = [
        "# Supervisor Budget Validation",
        "",
        f"- status: `{'ok' if result.ok else 'failed'}`",
        f"- budget_id: `{data.get('budget_id', '')}`",
        f"- project: `{data.get('project', '')}`",
        f"- phase: `{data.get('phase', '')}`",
        f"- max_paid_cost_usd: `{data.get('max_paid_cost_usd', '')}`",
        f"- max_attempts: `{data.get('max_attempts', '')}`",
        f"- budget_declared: `{summary.get('budget_declared', '')}`",
        f"- budget_exceeded: `{summary.get('budget_exceeded', '')}`",
        f"- attempt_count: `{summary.get('attempt_count', '')}`",
        f"- stop_rule_triggered: `{summary.get('stop_rule_triggered', '')}`",
        (
            "- maintainer_checkpoint_required: "
            f"`{summary.get('maintainer_checkpoint_required', '')}`"
        ),
    ]
    if result.errors:
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in result.errors)
    return "\n".join(lines) + "\n"


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonnegative_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0
    )


def positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def nonnegative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0
