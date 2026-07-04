"""Policy tuning helpers built from pilot accounting records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .accounting import (
    AccountingCosts,
    calculate_costs,
    load_accounting_record,
    validate_accounting_record,
)


MIN_ML_RECORDS = 100
MIN_ML_PROJECTS = 3
MIN_ML_TASK_TYPES = 6


@dataclass(frozen=True)
class PolicyGroup:
    task_type: str
    model: str
    protocol: str
    records: int
    promising: int
    poor: int
    mixed: int
    insufficient: int
    accepted_claims: int
    rejected_claims: int
    needs_evidence_claims: int
    changed_decisions: int
    total_net_savings_usd: float

    @property
    def average_net_savings_usd(self) -> float:
        if self.records == 0:
            return 0.0
        return self.total_net_savings_usd / self.records

    @property
    def accepted_to_rejected_ratio(self) -> float:
        if self.rejected_claims == 0:
            return float(self.accepted_claims)
        return self.accepted_claims / self.rejected_claims


def tune_policy(paths: list[Path]) -> str:
    groups = collect_groups(paths)
    lines = [
        "# Delegation Policy Tuning Report",
        "",
        "This report applies transparent rules to sanitized pilot accounting",
        "records. It is a supervisor decision aid, not an automatic policy",
        "mutation.",
        "",
        "## Input Summary",
        "",
        f"- records: {sum(group.records for group in groups)}",
        f"- task_model_protocol_groups: {len(groups)}",
        "",
        "## Tuning Rules",
        "",
        "- Promote cautiously when records are mostly promising, net savings are",
        "  positive, and accepted claims exceed rejected claims.",
        "- Hold steady when evidence is mixed or sparse.",
        "- Lower trust when records are mostly poor, net savings are negative, or",
        "  rejected claims exceed accepted claims.",
        "- Bail out after two poor outcomes for the same task/model/protocol",
        "  group unless the supervisor rewrites the ticket or changes model.",
        "- Keep ML policy optimization disabled until the evidence volume and",
        "  diversity thresholds below are met.",
        "",
        "## Group Recommendations",
        "",
        "| Task Type | Model | Protocol | Records | Recommendation | Retry Limit | "
        "Bailout | Net USD | Rationale |",
        "| --- | --- | --- | ---: | --- | ---: | --- | ---: | --- |",
    ]
    for group in groups:
        recommendation, retry_limit, bailout, rationale = recommend_group(group)
        lines.append(
            "| {task_type} | `{model}` | `{protocol}` | {records} | `{recommendation}` | "
            "{retry_limit} | {bailout} | {net} | {rationale} |".format(
                task_type=group.task_type,
                model=group.model,
                protocol=group.protocol,
                records=group.records,
                recommendation=recommendation,
                retry_limit=retry_limit,
                bailout=bailout,
                net=f"{group.total_net_savings_usd:.6f}",
                rationale=rationale.replace("|", "\\|"),
            )
        )

    lines.extend(render_ml_boundary(groups))
    lines.append("")
    return "\n".join(lines)


def collect_groups(paths: list[Path]) -> list[PolicyGroup]:
    grouped: dict[tuple[str, str, str], list[tuple[dict[str, Any], AccountingCosts]]] = {}
    errors: list[str] = []
    for path in paths:
        try:
            data = load_accounting_record(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        result = validate_accounting_record(data)
        if not result.ok:
            errors.extend(f"{path}: {error}" for error in result.errors)
            continue
        key = (
            str(data.get("task_type", "")),
            str(data.get("model", "")),
            str(data.get("protocol", "")),
        )
        grouped.setdefault(key, []).append((data, calculate_costs(data)))

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"cannot tune policy from invalid accounting records:\n{joined}")

    return [build_group(key, values) for key, values in sorted(grouped.items())]


def build_group(
    key: tuple[str, str, str],
    values: list[tuple[dict[str, Any], AccountingCosts]],
) -> PolicyGroup:
    task_type, model, protocol = key
    classifications = {"promising": 0, "poor": 0, "mixed": 0, "insufficient-evidence": 0}
    accepted = 0
    rejected = 0
    needs = 0
    changed = 0
    net = 0.0
    for data, costs in values:
        outcome = data.get("outcome", {})
        classification = ""
        if isinstance(outcome, dict):
            classification = str(outcome.get("classification", ""))
        if classification not in classifications:
            classification = "insufficient-evidence"
        classifications[classification] += 1

        claims = data.get("claim_review", {})
        if isinstance(claims, dict):
            accepted += int(claims.get("accepted_claims", 0))
            rejected += int(claims.get("rejected_claims", 0))
            needs += int(claims.get("needs_evidence_claims", 0))
            if bool(claims.get("worker_changed_supervisor_decision", False)):
                changed += 1
        net += costs.net_savings_usd

    return PolicyGroup(
        task_type=task_type,
        model=model,
        protocol=protocol,
        records=len(values),
        promising=classifications["promising"],
        poor=classifications["poor"],
        mixed=classifications["mixed"],
        insufficient=classifications["insufficient-evidence"],
        accepted_claims=accepted,
        rejected_claims=rejected,
        needs_evidence_claims=needs,
        changed_decisions=changed,
        total_net_savings_usd=net,
    )


def recommend_group(group: PolicyGroup) -> tuple[str, int, str, str]:
    if group.records < 2:
        return (
            "hold",
            1,
            "collect at least one more record",
            "Evidence is too sparse for stable policy movement.",
        )
    if (
        group.promising > group.poor
        and group.total_net_savings_usd > 0
        and group.accepted_claims >= group.rejected_claims
    ):
        return (
            "maintain-or-promote",
            2,
            "bail after two poor repeats",
            "Positive net savings and claim balance support cautious delegation.",
        )
    if (
        group.poor >= group.promising
        and (group.total_net_savings_usd < 0 or group.rejected_claims > group.accepted_claims)
    ):
        return (
            "lower-trust",
            0,
            "do directly or change model/protocol",
            "Poor outcomes or negative economics dominate the pilot evidence.",
        )
    return (
        "hold",
        1,
        "split smaller if next record is poor",
        "Evidence is mixed; keep the current policy until more records exist.",
    )


def render_ml_boundary(groups: list[PolicyGroup]) -> list[str]:
    records = sum(group.records for group in groups)
    task_types = {group.task_type for group in groups}
    models = {group.model for group in groups}
    ready = (
        records >= MIN_ML_RECORDS
        and len(task_types) >= MIN_ML_TASK_TYPES
        and len(models) >= MIN_ML_PROJECTS
    )
    return [
        "",
        "## Future ML Boundary",
        "",
        f"- current_records: {records}",
        f"- minimum_records_before_ml: {MIN_ML_RECORDS}",
        f"- current_task_types: {len(task_types)}",
        f"- minimum_task_types_before_ml: {MIN_ML_TASK_TYPES}",
        f"- current_model_or_project_groups: {len(models)}",
        f"- minimum_model_or_project_groups_before_ml: {MIN_ML_PROJECTS}",
        f"- ml_optimizer_status: `{'eligible-for-design' if ready else 'premature'}`",
        "",
        "Rules-based tuning remains the active policy mechanism until the record",
        "set is large, varied, sanitized, and independently verifiable.",
    ]
