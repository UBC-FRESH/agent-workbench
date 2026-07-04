"""Pilot accounting records for real-project delegation experiments."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


REQUIRED_FIELDS = (
    "pilot_id",
    "project",
    "task_id",
    "title",
    "task_type",
    "roadmap_level",
    "model",
    "protocol",
    "authority_level",
    "task_selection",
    "token_accounting",
    "claim_review",
    "verification",
    "outcome",
    "supervisor_assessment",
)

TOKEN_FIELDS = (
    "direct_supervisor_input_tokens",
    "direct_supervisor_output_tokens",
    "delegated_supervisor_input_tokens",
    "delegated_supervisor_output_tokens",
    "worker_input_tokens",
    "worker_output_tokens",
    "verification_supervisor_input_tokens",
    "verification_supervisor_output_tokens",
    "cleanup_supervisor_input_tokens",
    "cleanup_supervisor_output_tokens",
    "retry_supervisor_input_tokens",
    "retry_supervisor_output_tokens",
)

PRICE_FIELDS = (
    "supervisor_input_price_per_1m_usd",
    "supervisor_output_price_per_1m_usd",
    "worker_input_price_per_1m_usd",
    "worker_output_price_per_1m_usd",
)

CLAIM_FIELDS = (
    "accepted_claims",
    "rejected_claims",
    "needs_evidence_claims",
)

CLASSIFICATIONS = {
    "promising",
    "poor",
    "mixed",
    "insufficient-evidence",
}


@dataclass(frozen=True)
class AccountingCosts:
    direct_supervisor_cost_usd: float
    delegated_supervisor_cost_usd: float
    worker_cost_usd: float
    verification_supervisor_cost_usd: float
    cleanup_supervisor_cost_usd: float
    retry_supervisor_cost_usd: float
    delegated_total_cost_usd: float
    net_savings_usd: float


@dataclass(frozen=True)
class AccountingValidation:
    ok: bool
    errors: list[str]


def load_accounting_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("accounting record must be a JSON object")
    return data


def validate_accounting_record(data: dict[str, Any]) -> AccountingValidation:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    token_accounting = data.get("token_accounting")
    if not isinstance(token_accounting, dict):
        errors.append("token_accounting must be an object")
    else:
        for field in (*TOKEN_FIELDS, *PRICE_FIELDS):
            value = number_or_none(token_accounting.get(field, 0))
            if value is None or value < 0:
                errors.append(f"token_accounting.{field} must be a nonnegative number")

    claim_review = data.get("claim_review")
    if not isinstance(claim_review, dict):
        errors.append("claim_review must be an object")
    else:
        for field in CLAIM_FIELDS:
            value = integer_or_none(claim_review.get(field, 0))
            if value is None or value < 0:
                errors.append(f"claim_review.{field} must be a nonnegative integer")
        changed = claim_review.get("worker_changed_supervisor_decision", False)
        if not isinstance(changed, bool):
            errors.append("claim_review.worker_changed_supervisor_decision must be boolean")

    task_selection = data.get("task_selection")
    if not isinstance(task_selection, dict):
        errors.append("task_selection must be an object")
    else:
        if not task_selection.get("source"):
            errors.append("task_selection.source is required")
        if not task_selection.get("critical_path_position"):
            errors.append("task_selection.critical_path_position is required")

    verification = data.get("verification")
    if not isinstance(verification, dict):
        errors.append("verification must be an object")

    outcome = data.get("outcome")
    if not isinstance(outcome, dict):
        errors.append("outcome must be an object")
    else:
        classification = str(outcome.get("classification", "")).strip()
        if classification not in CLASSIFICATIONS:
            errors.append(f"outcome.classification must be one of {sorted(CLASSIFICATIONS)}")

    for finding in find_private_values(data):
        errors.append(f"private-looking value detected: {finding}")

    return AccountingValidation(ok=not errors, errors=errors)


def calculate_costs(data: dict[str, Any]) -> AccountingCosts:
    accounting = data.get("token_accounting", {})
    if not isinstance(accounting, dict):
        accounting = {}

    supervisor_input_price = number(accounting.get("supervisor_input_price_per_1m_usd", 0))
    supervisor_output_price = number(accounting.get("supervisor_output_price_per_1m_usd", 0))
    worker_input_price = number(accounting.get("worker_input_price_per_1m_usd", 0))
    worker_output_price = number(accounting.get("worker_output_price_per_1m_usd", 0))

    direct = token_cost(
        accounting,
        "direct_supervisor_input_tokens",
        "direct_supervisor_output_tokens",
        supervisor_input_price,
        supervisor_output_price,
    )
    delegated = token_cost(
        accounting,
        "delegated_supervisor_input_tokens",
        "delegated_supervisor_output_tokens",
        supervisor_input_price,
        supervisor_output_price,
    )
    worker = token_cost(
        accounting,
        "worker_input_tokens",
        "worker_output_tokens",
        worker_input_price,
        worker_output_price,
    )
    verification = token_cost(
        accounting,
        "verification_supervisor_input_tokens",
        "verification_supervisor_output_tokens",
        supervisor_input_price,
        supervisor_output_price,
    )
    cleanup = token_cost(
        accounting,
        "cleanup_supervisor_input_tokens",
        "cleanup_supervisor_output_tokens",
        supervisor_input_price,
        supervisor_output_price,
    )
    retry = token_cost(
        accounting,
        "retry_supervisor_input_tokens",
        "retry_supervisor_output_tokens",
        supervisor_input_price,
        supervisor_output_price,
    )
    delegated_total = delegated + worker + verification + cleanup + retry
    return AccountingCosts(
        direct_supervisor_cost_usd=direct,
        delegated_supervisor_cost_usd=delegated,
        worker_cost_usd=worker,
        verification_supervisor_cost_usd=verification,
        cleanup_supervisor_cost_usd=cleanup,
        retry_supervisor_cost_usd=retry,
        delegated_total_cost_usd=delegated_total,
        net_savings_usd=direct - delegated_total,
    )


def render_accounting_markdown(data: dict[str, Any]) -> str:
    costs = calculate_costs(data)
    claims = data.get("claim_review", {})
    outcome = data.get("outcome", {})
    selection = data.get("task_selection", {})
    verification = data.get("verification", {})
    assessment = data.get("supervisor_assessment", {})

    lines = [
        "# Pilot Accounting Record",
        "",
        "## Metadata",
        "",
        f"- pilot_id: `{data.get('pilot_id', '')}`",
        f"- project: `{data.get('project', '')}`",
        f"- task_id: `{data.get('task_id', '')}`",
        f"- title: {data.get('title', '')}",
        f"- task_type: `{data.get('task_type', '')}`",
        f"- roadmap_level: `{data.get('roadmap_level', '')}`",
        f"- model: `{data.get('model', '')}`",
        f"- protocol: `{data.get('protocol', '')}`",
        f"- authority_level: `{data.get('authority_level', '')}`",
        "",
        "## Selection",
        "",
    ]
    if isinstance(selection, dict):
        for key, value in selection.items():
            lines.append(f"- {key}: {format_value(value)}")

    lines.extend(
        [
            "",
            "## Claim Review",
            "",
            f"- accepted_claims: {claims.get('accepted_claims', 0)}",
            f"- rejected_claims: {claims.get('rejected_claims', 0)}",
            f"- needs_evidence_claims: {claims.get('needs_evidence_claims', 0)}",
            "- worker_changed_supervisor_decision: "
            f"{claims.get('worker_changed_supervisor_decision', False)}",
            "",
            "## Costs",
            "",
            f"- direct_supervisor_cost_usd: {format_usd(costs.direct_supervisor_cost_usd)}",
            f"- delegated_supervisor_cost_usd: {format_usd(costs.delegated_supervisor_cost_usd)}",
            f"- worker_cost_usd: {format_usd(costs.worker_cost_usd)}",
            "- verification_supervisor_cost_usd: "
            f"{format_usd(costs.verification_supervisor_cost_usd)}",
            f"- cleanup_supervisor_cost_usd: {format_usd(costs.cleanup_supervisor_cost_usd)}",
            f"- retry_supervisor_cost_usd: {format_usd(costs.retry_supervisor_cost_usd)}",
            f"- delegated_total_cost_usd: {format_usd(costs.delegated_total_cost_usd)}",
            f"- net_savings_usd: {format_usd(costs.net_savings_usd)}",
            "",
            "## Verification",
            "",
        ]
    )
    if isinstance(verification, dict):
        for key, value in verification.items():
            lines.append(f"- {key}: {format_value(value)}")

    lines.extend(
        [
            "",
            "## Outcome",
            "",
            f"- classification: `{outcome.get('classification', '')}`",
            f"- rationale: {outcome.get('rationale', '')}",
            "",
            "## Supervisor Assessment",
            "",
        ]
    )
    if isinstance(assessment, dict):
        for key, value in assessment.items():
            lines.append(f"- {key}: {format_value(value)}")
    lines.append("")
    return "\n".join(lines)


def synthesize_accounting_markdown(paths: list[Path]) -> str:
    records: list[tuple[Path, dict[str, Any], AccountingCosts]] = []
    errors: list[str] = []
    for path in paths:
        try:
            data = load_accounting_record(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        result = validate_accounting_record(data)
        if not result.ok:
            errors.extend(f"{path}: {error}" for error in result.errors)
            continue
        records.append((path, data, calculate_costs(data)))

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"cannot synthesize invalid accounting records:\n{joined}")

    total_direct = sum(costs.direct_supervisor_cost_usd for _path, _data, costs in records)
    total_delegated = sum(costs.delegated_total_cost_usd for _path, _data, costs in records)
    total_net = sum(costs.net_savings_usd for _path, _data, costs in records)
    promising = [item for item in records if classify_record(item[1], item[2]) == "promising"]
    poor = [item for item in records if classify_record(item[1], item[2]) == "poor"]

    lines = [
        "# Pilot Accounting Synthesis",
        "",
        "This synthesis uses sanitized pilot accounting records. It is a",
        "supervisor aid, not proof that worker claims are correct.",
        "",
        "## Summary",
        "",
        f"- records: {len(records)}",
        f"- total_direct_supervisor_cost_usd: {format_usd(total_direct)}",
        f"- total_delegated_cost_usd: {format_usd(total_delegated)}",
        f"- total_net_savings_usd: {format_usd(total_net)}",
        f"- promising_records: {len(promising)}",
        f"- poor_records: {len(poor)}",
        "",
        "## Record Table",
        "",
        "| Pilot | Project | Task Type | Model | Outcome | Net Savings USD | "
        "Accepted | Rejected | Needs Evidence |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for _path, data, costs in records:
        claims = data.get("claim_review", {})
        outcome = data.get("outcome", {})
        lines.append(
            "| {pilot} | {project} | {task_type} | `{model}` | `{outcome}` | "
            "{net} | {accepted} | {rejected} | {needs} |".format(
                pilot=data.get("pilot_id", ""),
                project=data.get("project", ""),
                task_type=data.get("task_type", ""),
                model=data.get("model", ""),
                outcome=outcome.get("classification", ""),
                net=format_usd(costs.net_savings_usd),
                accepted=claims.get("accepted_claims", 0),
                rejected=claims.get("rejected_claims", 0),
                needs=claims.get("needs_evidence_claims", 0),
            )
        )

    lines.extend(["", "## Delegation Classes", ""])
    lines.append(render_class_section("Promising", promising))
    lines.append(render_class_section("Poor", poor))
    if not promising or not poor:
        lines.extend(
            [
                "",
                "## Evidence Sufficiency",
                "",
                "The current pilot set does not yet contain both a promising and poor",
                "delegation class. Continue collecting varied task/model/protocol",
                "records before treating policy updates as stable.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def classify_record(data: dict[str, Any], costs: AccountingCosts) -> str:
    outcome = data.get("outcome", {})
    if isinstance(outcome, dict):
        classification = str(outcome.get("classification", "")).strip()
        if classification in {"promising", "poor"}:
            return classification
    claims = data.get("claim_review", {})
    accepted = number(claims.get("accepted_claims", 0)) if isinstance(claims, dict) else 0
    rejected = number(claims.get("rejected_claims", 0)) if isinstance(claims, dict) else 0
    if costs.net_savings_usd > 0 and accepted > rejected:
        return "promising"
    if costs.net_savings_usd < 0 or rejected > accepted:
        return "poor"
    return "insufficient-evidence"


def render_class_section(
    label: str,
    records: list[tuple[Path, dict[str, Any], AccountingCosts]],
) -> str:
    if not records:
        return f"### {label}\n\n- None identified."
    lines = [f"### {label}", ""]
    for _path, data, costs in records:
        lines.append(
            "- `{pilot}`: {task_type} with `{model}` ({net} USD net).".format(
                pilot=data.get("pilot_id", ""),
                task_type=data.get("task_type", ""),
                model=data.get("model", ""),
                net=format_usd(costs.net_savings_usd),
            )
        )
    return "\n".join(lines)


def token_cost(
    data: dict[str, Any],
    input_field: str,
    output_field: str,
    input_price_per_1m_usd: float,
    output_price_per_1m_usd: float,
) -> float:
    return (
        number(data.get(input_field, 0)) / 1_000_000 * input_price_per_1m_usd
        + number(data.get(output_field, 0)) / 1_000_000 * output_price_per_1m_usd
    )


def number(value: Any) -> float:
    parsed = number_or_none(value)
    return 0.0 if parsed is None else parsed


def number_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def integer_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    if float(value) != parsed:
        return None
    return parsed


def format_usd(value: float) -> str:
    return f"{value:.6f}"


def format_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(f"`{item}`" for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
