"""Sanitized token/cost usage records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


SOURCE_TYPES = {
    "sdk-summary",
    "provider-usage",
    "observability-export",
    "manual-estimate",
}

REQUIRED_FIELDS = (
    "record_id",
    "source_type",
    "scope",
    "generated_utc",
    "usage",
    "prices",
    "public_safety",
)

USAGE_FIELDS = (
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
class TokenValidation:
    ok: bool
    errors: list[str]


@dataclass(frozen=True)
class TokenCosts:
    supervisor_cost_usd: float
    worker_cost_usd: float
    total_cost_usd: float


def load_token_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("token/cost record must be a JSON object")
    return data


def validate_token_record(data: dict[str, Any]) -> TokenValidation:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    source_type = str(data.get("source_type", ""))
    if source_type not in SOURCE_TYPES:
        errors.append(f"source_type must be one of {sorted(SOURCE_TYPES)}")

    usage = data.get("usage")
    if not isinstance(usage, dict):
        errors.append("usage must be an object")
    else:
        for field in USAGE_FIELDS:
            value = number_or_none(usage.get(field, 0))
            if value is None or value < 0:
                errors.append(f"usage.{field} must be a nonnegative number")

    prices = data.get("prices")
    if not isinstance(prices, dict):
        errors.append("prices must be an object")
    else:
        for field in PRICE_FIELDS:
            value = number_or_none(prices.get(field, 0))
            if value is None or value < 0:
                errors.append(f"prices.{field} must be a nonnegative number")

    public_safety = data.get("public_safety")
    if not isinstance(public_safety, dict):
        errors.append("public_safety must be an object")
    else:
        for field in (
            "raw_prompts_excluded",
            "raw_traces_excluded",
            "provider_urls_excluded",
            "headers_excluded",
            "personal_paths_excluded",
        ):
            if public_safety.get(field) is not True:
                errors.append(f"public_safety.{field} must be true")

    for finding in find_forbidden_keys(data):
        errors.append(f"forbidden raw-observability field detected: {finding}")
    for finding in find_private_values(data):
        errors.append(f"private-looking value detected: {finding}")

    return TokenValidation(ok=not errors, errors=errors)


def calculate_token_costs(data: dict[str, Any]) -> TokenCosts:
    usage = data.get("usage", {})
    prices = data.get("prices", {})
    if not isinstance(usage, dict):
        usage = {}
    if not isinstance(prices, dict):
        prices = {}
    supervisor_cost = cost_usd(
        usage.get("supervisor_input_tokens", 0),
        usage.get("supervisor_output_tokens", 0),
        prices.get("supervisor_input_price_per_1m_usd", 0),
        prices.get("supervisor_output_price_per_1m_usd", 0),
    )
    worker_cost = cost_usd(
        usage.get("worker_input_tokens", 0),
        usage.get("worker_output_tokens", 0),
        prices.get("worker_input_price_per_1m_usd", 0),
        prices.get("worker_output_price_per_1m_usd", 0),
    )
    return TokenCosts(
        supervisor_cost_usd=supervisor_cost,
        worker_cost_usd=worker_cost,
        total_cost_usd=supervisor_cost + worker_cost,
    )


def render_token_markdown(data: dict[str, Any]) -> str:
    costs = calculate_token_costs(data)
    lines = [
        "# Token Cost Record",
        "",
        "## Metadata",
        "",
        f"- record_id: `{data.get('record_id', '')}`",
        f"- source_type: `{data.get('source_type', '')}`",
        f"- generated_utc: `{data.get('generated_utc', '')}`",
        "",
        "## Scope",
        "",
    ]
    scope = data.get("scope", {})
    if isinstance(scope, dict):
        for key, value in scope.items():
            lines.append(f"- {key}: {format_value(value)}")

    lines.extend(["", "## Usage", ""])
    usage = data.get("usage", {})
    if isinstance(usage, dict):
        for key, value in usage.items():
            lines.append(f"- {key}: {value}")

    lines.extend(["", "## Prices", ""])
    prices = data.get("prices", {})
    if isinstance(prices, dict):
        for key, value in prices.items():
            lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Costs",
            "",
            f"- supervisor_cost_usd: {format_usd(costs.supervisor_cost_usd)}",
            f"- worker_cost_usd: {format_usd(costs.worker_cost_usd)}",
            f"- total_cost_usd: {format_usd(costs.total_cost_usd)}",
            "",
            "## Public Safety",
            "",
        ]
    )
    public_safety = data.get("public_safety", {})
    if isinstance(public_safety, dict):
        for key, value in public_safety.items():
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def synthesize_token_markdown(paths: list[Path]) -> str:
    records: list[tuple[Path, dict[str, Any], TokenCosts]] = []
    errors: list[str] = []
    for path in paths:
        try:
            data = load_token_record(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        result = validate_token_record(data)
        if not result.ok:
            errors.extend(f"{path}: {error}" for error in result.errors)
            continue
        records.append((path, data, calculate_token_costs(data)))

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"cannot synthesize invalid token records:\n{joined}")

    supervisor_cost = sum(costs.supervisor_cost_usd for _path, _data, costs in records)
    worker_cost = sum(costs.worker_cost_usd for _path, _data, costs in records)
    total_cost = sum(costs.total_cost_usd for _path, _data, costs in records)
    lines = [
        "# Token Cost Synthesis",
        "",
        "This report summarizes sanitized token/cost records. Raw prompts, traces,",
        "provider URLs, headers, and personal paths are excluded by contract.",
        "",
        "## Summary",
        "",
        f"- records: {len(records)}",
        f"- supervisor_cost_usd: {format_usd(supervisor_cost)}",
        f"- worker_cost_usd: {format_usd(worker_cost)}",
        f"- total_cost_usd: {format_usd(total_cost)}",
        "",
        "## Record Table",
        "",
        "| Record | Source Type | Project | Task | Supervisor USD | Worker USD | Total USD |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for _path, data, costs in records:
        scope = data.get("scope", {})
        if not isinstance(scope, dict):
            scope = {}
        lines.append(
            "| {record} | `{source}` | {project} | {task} | {supervisor} | "
            "{worker} | {total} |".format(
                record=data.get("record_id", ""),
                source=data.get("source_type", ""),
                project=scope.get("project", ""),
                task=scope.get("task_id", ""),
                supervisor=format_usd(costs.supervisor_cost_usd),
                worker=format_usd(costs.worker_cost_usd),
                total=format_usd(costs.total_cost_usd),
            )
        )
    lines.append("")
    return "\n".join(lines)


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


def format_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(f"`{item}`" for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
