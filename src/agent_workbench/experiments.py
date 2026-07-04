"""Sanitized delegation experiment observation records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


REQUIRED_FIELDS = (
    "record_id",
    "schema_version",
    "generated_utc",
    "experiment",
    "task",
    "model",
    "protocol",
    "outcome",
    "economics",
    "links",
    "public_safety",
)

EXPERIMENT_FIELDS = ("experiment_id", "series_id", "project", "phase")
TASK_FIELDS = ("task_id", "task_family", "scale_factor")
MODEL_FIELDS = ("model_id", "provider", "cash_cost_per_token_usd")
OUTCOME_FIELDS = ("status", "records_produced", "accepted_records", "repairable_records")
ECONOMICS_FIELDS = (
    "worker_input_tokens",
    "worker_output_tokens",
    "worker_cost_usd",
    "supervisor_cost_usd",
    "direct_baseline_cost_usd",
    "net_savings_usd",
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
class ExperimentValidation:
    ok: bool
    errors: list[str]


def load_experiment_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("experiment record must be a JSON object")
    return data


def validate_experiment_record(data: dict[str, Any]) -> ExperimentValidation:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    validate_mapping(data, "experiment", EXPERIMENT_FIELDS, errors)
    validate_mapping(data, "task", TASK_FIELDS, errors)
    validate_mapping(data, "model", MODEL_FIELDS, errors)
    validate_mapping(data, "outcome", OUTCOME_FIELDS, errors)
    validate_mapping(data, "economics", ECONOMICS_FIELDS, errors)

    task = data.get("task", {})
    if isinstance(task, dict):
        for field in ("scale_factor", "input_pages", "input_words", "input_characters"):
            if field in task:
                validate_nonnegative_number(task, field, f"task.{field}", errors)

    model = data.get("model", {})
    if isinstance(model, dict):
        validate_nonnegative_number(
            model,
            "cash_cost_per_token_usd",
            "model.cash_cost_per_token_usd",
            errors,
        )

    outcome = data.get("outcome", {})
    if isinstance(outcome, dict):
        for field in (
            "records_produced",
            "accepted_records",
            "repairable_records",
            "rejected_records",
            "needs_review_records",
        ):
            if field in outcome:
                validate_nonnegative_number(outcome, field, f"outcome.{field}", errors)

    economics = data.get("economics", {})
    if isinstance(economics, dict):
        for field in ECONOMICS_FIELDS:
            validate_number(economics, field, f"economics.{field}", errors)

    public_safety = data.get("public_safety")
    if not isinstance(public_safety, dict):
        errors.append("public_safety must be an object")
    else:
        for field in (
            "raw_inputs_excluded",
            "raw_outputs_excluded",
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

    return ExperimentValidation(ok=not errors, errors=errors)


def render_experiment_markdown(data: dict[str, Any]) -> str:
    experiment = safe_mapping(data.get("experiment"))
    task = safe_mapping(data.get("task"))
    model = safe_mapping(data.get("model"))
    protocol = safe_mapping(data.get("protocol"))
    outcome = safe_mapping(data.get("outcome"))
    economics = safe_mapping(data.get("economics"))
    links = safe_mapping(data.get("links"))

    lines = [
        "# Delegation Experiment Observation",
        "",
        f"- record_id: `{data.get('record_id', '')}`",
        f"- generated_utc: `{data.get('generated_utc', '')}`",
        f"- experiment_id: `{experiment.get('experiment_id', '')}`",
        f"- series_id: `{experiment.get('series_id', '')}`",
        f"- project: `{experiment.get('project', '')}`",
        f"- phase: `{experiment.get('phase', '')}`",
        "",
        "## Task",
        "",
        f"- task_id: `{task.get('task_id', '')}`",
        f"- task_family: `{task.get('task_family', '')}`",
        f"- scale_factor: {task.get('scale_factor', '')}",
        f"- input_pages: {task.get('input_pages', '')}",
        f"- input_words: {task.get('input_words', '')}",
        f"- input_characters: {task.get('input_characters', '')}",
        "",
        "## Model And Protocol",
        "",
        f"- model_id: `{model.get('model_id', '')}`",
        f"- provider: `{model.get('provider', '')}`",
        f"- authority_level: `{protocol.get('authority_level', '')}`",
        f"- timeout_seconds: {protocol.get('timeout_seconds', '')}",
        f"- audit_strategy: `{protocol.get('audit_strategy', '')}`",
        "",
        "## Outcome",
        "",
        f"- status: `{outcome.get('status', '')}`",
        f"- records_produced: {outcome.get('records_produced', 0)}",
        f"- accepted_records: {outcome.get('accepted_records', 0)}",
        f"- repairable_records: {outcome.get('repairable_records', 0)}",
        f"- rejected_records: {outcome.get('rejected_records', 0)}",
        f"- needs_review_records: {outcome.get('needs_review_records', 0)}",
        "",
        "## Economics",
        "",
        f"- worker_input_tokens: {economics.get('worker_input_tokens', 0)}",
        f"- worker_output_tokens: {economics.get('worker_output_tokens', 0)}",
        f"- worker_cost_usd: {format_float(economics.get('worker_cost_usd', 0))}",
        f"- supervisor_cost_usd: {format_float(economics.get('supervisor_cost_usd', 0))}",
        f"- direct_baseline_cost_usd: {format_float(economics.get('direct_baseline_cost_usd', 0))}",
        f"- net_savings_usd: {format_float(economics.get('net_savings_usd', 0))}",
        f"- benefit_cost_ratio: {format_float(benefit_cost_ratio(economics))}",
        "",
        "## Links",
        "",
    ]
    for key, value in links.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def synthesize_experiment_markdown(paths: list[Path]) -> str:
    records: list[tuple[Path, dict[str, Any]]] = []
    errors: list[str] = []
    for path in paths:
        try:
            data = load_experiment_record(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        validation = validate_experiment_record(data)
        if not validation.ok:
            errors.extend(f"{path}: {error}" for error in validation.errors)
            continue
        records.append((path, data))

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"cannot synthesize invalid experiment records:\n{joined}")

    lines = [
        "# Delegation Experiment Synthesis",
        "",
        "This report summarizes sanitized delegation experiment observations.",
        "Raw inputs, outputs, traces, provider URLs, headers, and personal paths",
        "are excluded by contract.",
        "",
        "## Summary",
        "",
        f"- records: {len(records)}",
        "",
        "## Observation Table",
        "",
        "| Record | Series | Task | Scale | Model | Status | Worker In | Worker Out | Supervisor USD | Direct USD | Net USD | BCR |",
        "| --- | --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _path, data in records:
        experiment = safe_mapping(data.get("experiment"))
        task = safe_mapping(data.get("task"))
        model = safe_mapping(data.get("model"))
        outcome = safe_mapping(data.get("outcome"))
        economics = safe_mapping(data.get("economics"))
        lines.append(
            "| {record} | {series} | {task_id} | {scale} | {model} | {status} | "
            "{worker_in} | {worker_out} | {supervisor} | {direct} | {net} | {bcr} |".format(
                record=data.get("record_id", ""),
                series=experiment.get("series_id", ""),
                task_id=task.get("task_id", ""),
                scale=task.get("scale_factor", ""),
                model=model.get("model_id", ""),
                status=outcome.get("status", ""),
                worker_in=int_number(economics.get("worker_input_tokens", 0)),
                worker_out=int_number(economics.get("worker_output_tokens", 0)),
                supervisor=format_float(economics.get("supervisor_cost_usd", 0)),
                direct=format_float(economics.get("direct_baseline_cost_usd", 0)),
                net=format_float(economics.get("net_savings_usd", 0)),
                bcr=format_float(benefit_cost_ratio(economics)),
            )
        )
    lines.append("")
    return "\n".join(lines)


def validate_mapping(
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
        if field not in value:
            errors.append(f"{field_name}.{field} is required")


def validate_nonnegative_number(
    data: dict[str, Any],
    field: str,
    label: str,
    errors: list[str],
) -> None:
    value = number_or_none(data.get(field))
    if value is None or value < 0:
        errors.append(f"{label} must be a nonnegative number")


def validate_number(data: dict[str, Any], field: str, label: str, errors: list[str]) -> None:
    if number_or_none(data.get(field)) is None:
        errors.append(f"{label} must be a number")


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


def safe_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def benefit_cost_ratio(economics: dict[str, Any]) -> float:
    direct = number(economics.get("direct_baseline_cost_usd", 0))
    delegated = number(economics.get("supervisor_cost_usd", 0)) + number(
        economics.get("worker_cost_usd", 0)
    )
    if delegated <= 0:
        return 0.0
    return direct / delegated


def number(value: Any) -> float:
    parsed = number_or_none(value)
    return 0.0 if parsed is None else parsed


def number_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def int_number(value: Any) -> int:
    return int(number(value))


def format_float(value: Any) -> str:
    return f"{number(value):.6f}"
