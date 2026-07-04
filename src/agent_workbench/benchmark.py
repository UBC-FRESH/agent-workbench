"""Phase-scale A/B token economics benchmark records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values

LANE_IDS = {"direct_supervisor", "delegated_graph"}
LANE_STATUSES = {"planned", "running", "complete", "abandoned"}
REQUIRED_FIELDS = (
    "benchmark_id",
    "target",
    "start_state",
    "lanes",
    "token_accounting",
    "validation",
    "decision_rules",
)
TARGET_FIELDS = ("repo", "phase_id", "phase_title")
START_STATE_FIELDS = ("base_branch", "start_commit")
TOKEN_FIELDS = (
    "supervisor_input_tokens",
    "supervisor_output_tokens",
    "worker_input_tokens",
    "worker_output_tokens",
)
PRICE_FIELDS = (
    "supervisor_input_price_per_1m_usd",
    "supervisor_output_price_per_1m_usd",
    "worker_input_price_per_1m_usd",
    "worker_output_price_per_1m_usd",
)
FORBIDDEN_FIELDS = {
    "prompt",
    "prompts",
    "messages",
    "completion",
    "response",
    "raw_trace",
    "trace",
    "headers",
    "provider_url",
    "endpoint",
    "api_key",
}


@dataclass(frozen=True)
class BenchmarkValidation:
    ok: bool
    errors: list[str]


def load_benchmark_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("benchmark record must be a JSON object")
    return data


def validate_benchmark_record(data: dict[str, Any]) -> BenchmarkValidation:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    validate_required_mapping(data, "target", TARGET_FIELDS, errors)
    validate_required_mapping(data, "start_state", START_STATE_FIELDS, errors)

    lanes = data.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        errors.append("lanes must be a nonempty list")
    else:
        seen: set[str] = set()
        for index, lane in enumerate(lanes):
            validate_lane(lane, f"lanes[{index}]", seen, errors)
        missing = sorted(LANE_IDS - seen)
        if missing:
            errors.append(f"lanes missing required lane ids: {missing}")

    token_accounting = data.get("token_accounting")
    if not isinstance(token_accounting, dict):
        errors.append("token_accounting must be an object")
    else:
        for field in PRICE_FIELDS:
            value = number_or_none(token_accounting.get(field, 0))
            if value is None or value < 0:
                errors.append(f"token_accounting.{field} must be a nonnegative number")

    validation = data.get("validation")
    if not isinstance(validation, dict):
        errors.append("validation must be an object")
    elif not isinstance(validation.get("commands"), list) or not validation.get("commands"):
        errors.append("validation.commands must be a nonempty list")

    decision_rules = data.get("decision_rules")
    if not isinstance(decision_rules, list) or not decision_rules:
        errors.append("decision_rules must be a nonempty list")

    for finding in find_forbidden_keys(data):
        errors.append(f"forbidden raw-observability field detected: {finding}")
    for finding in find_private_values(data):
        errors.append(f"private-looking value detected: {finding}")

    return BenchmarkValidation(ok=not errors, errors=errors)


def validate_required_mapping(
    data: dict[str, Any],
    field_name: str,
    required_fields: tuple[str, ...],
    errors: list[str],
) -> None:
    value = data.get(field_name)
    if not isinstance(value, dict):
        errors.append(f"{field_name} must be an object")
        return
    for field in required_fields:
        if not str(value.get(field, "")).strip():
            errors.append(f"{field_name}.{field} is required")


def validate_lane(value: Any, prefix: str, seen: set[str], errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    lane_id = str(value.get("lane_id", "")).strip()
    if lane_id not in LANE_IDS:
        errors.append(f"{prefix}.lane_id must be one of {sorted(LANE_IDS)}")
    if lane_id in seen:
        errors.append(f"{prefix}.lane_id duplicates {lane_id}")
    seen.add(lane_id)
    status = str(value.get("status", "")).strip()
    if status not in LANE_STATUSES:
        errors.append(f"{prefix}.status must be one of {sorted(LANE_STATUSES)}")
    for field in ("branch", "worktree", "method", "rollback_plan"):
        if not str(value.get(field, "")).strip():
            errors.append(f"{prefix}.{field} is required")
    usage = value.get("usage", {})
    if usage is not None and not isinstance(usage, dict):
        errors.append(f"{prefix}.usage must be an object when provided")
    elif isinstance(usage, dict):
        for field in TOKEN_FIELDS:
            token_count = number_or_none(usage.get(field, 0))
            if token_count is None or token_count < 0:
                errors.append(f"{prefix}.usage.{field} must be a nonnegative number")


def render_benchmark_markdown(data: dict[str, Any]) -> str:
    target = data.get("target", {})
    start_state = data.get("start_state", {})
    token_accounting = data.get("token_accounting", {})
    validation = data.get("validation", {})
    if not isinstance(target, dict):
        target = {}
    if not isinstance(start_state, dict):
        start_state = {}
    if not isinstance(token_accounting, dict):
        token_accounting = {}
    if not isinstance(validation, dict):
        validation = {}

    lines = [
        "# Phase-Scale A/B Token Economics Benchmark",
        "",
        "## Benchmark",
        "",
        f"- benchmark_id: `{data.get('benchmark_id', '')}`",
        f"- target_repo: `{target.get('repo', '')}`",
        f"- phase_id: `{target.get('phase_id', '')}`",
        f"- phase_title: {target.get('phase_title', '')}",
        f"- base_branch: `{start_state.get('base_branch', '')}`",
        f"- start_commit: `{start_state.get('start_commit', '')}`",
        "",
        "## Lanes",
        "",
    ]
    for lane in data.get("lanes", []):
        if not isinstance(lane, dict):
            continue
        usage = lane.get("usage", {})
        if not isinstance(usage, dict):
            usage = {}
        costs = lane_costs(lane, token_accounting)
        lines.extend(
            [
                f"### `{lane.get('lane_id', '')}`",
                "",
                f"- status: `{lane.get('status', '')}`",
                f"- branch: `{lane.get('branch', '')}`",
                f"- worktree: `{lane.get('worktree', '')}`",
                f"- method: {lane.get('method', '')}",
                f"- rollback_plan: {lane.get('rollback_plan', '')}",
                f"- supervisor_input_tokens: {format_count(usage.get('supervisor_input_tokens', 0))}",
                f"- supervisor_output_tokens: {format_count(usage.get('supervisor_output_tokens', 0))}",
                f"- worker_input_tokens: {format_count(usage.get('worker_input_tokens', 0))}",
                f"- worker_output_tokens: {format_count(usage.get('worker_output_tokens', 0))}",
                f"- supervisor_cost_usd: {format_usd(costs['supervisor_cost_usd'])}",
                f"- worker_cost_usd: {format_usd(costs['worker_cost_usd'])}",
                f"- total_cost_usd: {format_usd(costs['total_cost_usd'])}",
                "",
            ]
        )

    direct = lane_by_id(data, "direct_supervisor")
    delegated = lane_by_id(data, "delegated_graph")
    if direct is not None and delegated is not None:
        direct_cost = lane_costs(direct, token_accounting)["total_cost_usd"]
        delegated_cost = lane_costs(delegated, token_accounting)["total_cost_usd"]
        lines.extend(
            [
                "## Economics Comparison",
                "",
                f"- direct_total_cost_usd: {format_usd(direct_cost)}",
                f"- delegated_total_cost_usd: {format_usd(delegated_cost)}",
                f"- delegated_net_savings_usd: {format_usd(direct_cost - delegated_cost)}",
                "",
            ]
        )

    lines.extend(["## Validation Commands", ""])
    for command in validation.get("commands", []):
        lines.append(f"- `{command}`")

    lines.extend(["", "## Decision Rules", ""])
    for rule in data.get("decision_rules", []):
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines)


def lane_by_id(data: dict[str, Any], lane_id: str) -> dict[str, Any] | None:
    lanes = data.get("lanes", [])
    if not isinstance(lanes, list):
        return None
    for lane in lanes:
        if isinstance(lane, dict) and lane.get("lane_id") == lane_id:
            return lane
    return None


def lane_costs(lane: dict[str, Any], token_accounting: dict[str, Any]) -> dict[str, float]:
    usage = lane.get("usage", {})
    if not isinstance(usage, dict):
        usage = {}
    supervisor_cost = cost_usd(
        usage.get("supervisor_input_tokens", 0),
        usage.get("supervisor_output_tokens", 0),
        token_accounting.get("supervisor_input_price_per_1m_usd", 0),
        token_accounting.get("supervisor_output_price_per_1m_usd", 0),
    )
    worker_cost = cost_usd(
        usage.get("worker_input_tokens", 0),
        usage.get("worker_output_tokens", 0),
        token_accounting.get("worker_input_price_per_1m_usd", 0),
        token_accounting.get("worker_output_price_per_1m_usd", 0),
    )
    return {
        "supervisor_cost_usd": supervisor_cost,
        "worker_cost_usd": worker_cost,
        "total_cost_usd": supervisor_cost + worker_cost,
    }


def find_forbidden_keys(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.lower() in FORBIDDEN_FIELDS:
                findings.append(child_path)
            findings.extend(find_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_forbidden_keys(child, f"{path}[{index}]"))
    return findings


def cost_usd(
    input_tokens: Any,
    output_tokens: Any,
    input_price_per_1m_usd: Any,
    output_price_per_1m_usd: Any,
) -> float:
    return (
        number(input_tokens) / 1_000_000 * number(input_price_per_1m_usd)
        + number(output_tokens) / 1_000_000 * number(output_price_per_1m_usd)
    )


def number(value: Any) -> float:
    parsed = number_or_none(value)
    return 0.0 if parsed is None else parsed


def number_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_usd(value: float) -> str:
    return f"{value:.6f}"


def format_count(value: Any) -> str:
    return f"{number(value):.0f}"
