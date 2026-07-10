"""Planning helpers for FoundryTK-style profile optimization experiments."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .copilot_profile_runs import ProfileRunEvidence, summarize_profile_run
from .evidence import find_private_values


EVALUATION_DIMENSIONS = (
    "reliability",
    "work_quality",
    "efficiency",
    "conversation_shape",
)


@dataclass(frozen=True)
class ProfileOptimizationPlan:
    runs: tuple[ProfileRunEvidence, ...]
    recommendation: str

    @property
    def ok(self) -> bool:
        return all(run.ok for run in self.runs)


@dataclass(frozen=True)
class ProfileEvaluationDataset:
    rows: tuple[dict[str, Any], ...]

    @property
    def ok(self) -> bool:
        return all(not row.get("errors") for row in self.rows)


@dataclass(frozen=True)
class ProfileEvaluationAggregate:
    rows: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class ProfileContractRepairPlan:
    summary: dict[str, Any]
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def build_profile_optimization_plan(
    manifest_paths: list[Path] | tuple[Path, ...],
    *,
    repo_root: Path | None = None,
) -> ProfileOptimizationPlan:
    runs = tuple(
        summarize_profile_run(path, repo_root=repo_root) for path in manifest_paths
    )
    return ProfileOptimizationPlan(
        runs=runs,
        recommendation=recommend_profile_optimization_next_step(runs),
    )


def recommend_profile_optimization_next_step(
    runs: tuple[ProfileRunEvidence, ...],
) -> str:
    if not runs:
        return (
            "Collect at least two comparable profile-run summaries before optimization."
        )
    if any(run.controller_health == "error" for run in runs):
        return (
            "Stabilize controller/session health before prompt or model optimization. "
            "FoundryTK-style evaluation should separate worker result quality from SDK "
            "or provider failure modes."
        )
    if any(not run.task_overlays for run in runs):
        return (
            "Run comparable tasks with named P73 overlays before optimizing profile "
            "instructions. Overlay selection is part of the treatment definition."
        )
    return (
        "Proceed to an external evaluation design: compare standard profile plus "
        "overlay variants on reliability, work quality, efficiency, and conversation "
        "shape before any model customization."
    )


def render_profile_optimization_plan_markdown(
    plan: ProfileOptimizationPlan,
) -> str:
    lines = [
        "# FoundryTK Profile Optimization Plan",
        "",
        f"- valid: `{plan.ok}`",
        f"- runs: {len(plan.runs)}",
        f"- dimensions: {', '.join(EVALUATION_DIMENSIONS)}",
        "- runtime_bridge_dependency: `none`",
        "- foundrytk_runtime_integration: `deferred`",
        f"- recommendation: {plan.recommendation}",
        "",
        "## Boundary",
        "",
        "P74 treats FoundryTK as an external evaluation and optimization lane. "
        "This plan does not add FoundryTK as a runtime dependency and does not "
        "change the Copilot SDK bridge.",
        "",
        "## Evaluation Dimensions",
        "",
        "- reliability: authority-boundary compliance, required artifacts, drift avoidance, clean stop behavior, and controller health.",
        "- work_quality: accepted result status, fewer coordinator repairs, stronger evidence, and better code or documentation output.",
        "- efficiency: useful work per event, assistant message, tool event, permission event, elapsed time, token, and GPU-watt when available.",
        "- conversation_shape: selected profile and overlay are explicit, compact transcript shows the expected roles, and subagent activity matches the task.",
        "",
        "## Runs",
        "",
    ]
    if not plan.runs:
        lines.extend(["No runs supplied.", ""])
        return "\n".join(lines)
    for run in plan.runs:
        lines.extend(
            [
                f"### {run.run_id or '(unknown run)'}",
                "",
                f"- selected_agent: `{run.selected_agent}`",
                f"- task_overlays: {render_values(run.task_overlays)}",
                f"- custom_tools: {render_values(run.custom_tools)}",
                f"- controller_health: `{run.controller_health}`",
                f"- latest_status: `{run.latest_status}`",
                f"- result_status: `{run.result_status}`",
                f"- event_count: {run.event_count}",
                f"- assistant_messages: {run.assistant_messages}",
                f"- tool_events: {run.tool_events}",
                f"- permission_events: {run.permission_events}",
                f"- custom_agent_events: {run.custom_agent_events}",
                f"- subagent_events: {run.subagent_events}",
                "",
            ]
        )
    lines.extend(
        [
            "## FoundryTK Candidate Roles",
            "",
            "- external evaluation guidance: use the run table to decide which profile/overlay pairs are comparable.",
            "- optional tool provider: expose evaluation lookup or trace-analysis tools only after local evidence schemas stabilize.",
            "- model-selection evidence source: compare profile/model pairs using the same task and overlay treatment.",
            "- trace/evaluation runner: evaluate reliability, work quality, efficiency, and conversation shape without becoming part of the SDK control path.",
            "",
        ]
    )
    return "\n".join(lines)


def render_values(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "(none)"


def build_profile_evaluation_dataset(
    manifest_paths: list[Path] | tuple[Path, ...],
    *,
    repo_root: Path | None = None,
) -> ProfileEvaluationDataset:
    runs = tuple(
        summarize_profile_run(path, repo_root=repo_root) for path in manifest_paths
    )
    return ProfileEvaluationDataset(rows=tuple(evaluation_row(run) for run in runs))


def evaluation_row(run: ProfileRunEvidence) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run.run_id,
        "phase": run.phase,
        "selected_agent": run.selected_agent,
        "task_overlays": list(run.task_overlays),
        "custom_tools": list(run.custom_tools),
        "latest_status": run.latest_status,
        "controller_health": run.controller_health,
        "result_status": run.result_status,
        "reliability": {
            "controller_health": run.controller_health,
            "has_required_result_status": bool(run.result_status),
            "custom_agent_events": run.custom_agent_events,
            "subagent_events": run.subagent_events,
        },
        "work_quality": {
            "result_status": run.result_status,
            "accepted_candidate": run.result_status == "accepted-candidate",
        },
        "efficiency": {
            "event_count": run.event_count,
            "assistant_messages": run.assistant_messages,
            "tool_events": run.tool_events,
            "permission_events": run.permission_events,
        },
        "conversation_shape": {
            "user_messages": run.user_messages,
            "assistant_messages": run.assistant_messages,
            "custom_agent_events": run.custom_agent_events,
            "subagent_events": run.subagent_events,
            "agent_metadata_messages": run.agent_metadata_messages,
        },
        "errors": list(run.errors),
        "warnings": list(run.warnings),
    }


def render_profile_evaluation_dataset_jsonl(
    dataset: ProfileEvaluationDataset,
) -> str:
    return "\n".join(json.dumps(row, sort_keys=True) for row in dataset.rows) + (
        "\n" if dataset.rows else ""
    )


def render_profile_evaluation_dataset_markdown(
    dataset: ProfileEvaluationDataset,
) -> str:
    lines = [
        "# Profile Evaluation Dataset Preview",
        "",
        f"- valid: `{dataset.ok}`",
        f"- rows: {len(dataset.rows)}",
        f"- dimensions: {', '.join(EVALUATION_DIMENSIONS)}",
        "- raw_transcripts_included: `False`",
        "- private_paths_included: `False`",
        "",
        "## Rows",
        "",
    ]
    if not dataset.rows:
        lines.extend(["No rows.", ""])
        return "\n".join(lines)
    for row in dataset.rows:
        lines.extend(
            [
                f"### {row.get('run_id') or '(unknown run)'}",
                "",
                f"- selected_agent: `{row.get('selected_agent', '')}`",
                f"- task_overlays: {render_list(row.get('task_overlays', []))}",
                f"- controller_health: `{row.get('controller_health', '')}`",
                f"- result_status: `{row.get('result_status', '')}`",
                f"- event_count: {row.get('efficiency', {}).get('event_count', 0)}",
                f"- assistant_messages: {row.get('efficiency', {}).get('assistant_messages', 0)}",
                f"- tool_events: {row.get('efficiency', {}).get('tool_events', 0)}",
                f"- permission_events: {row.get('efficiency', {}).get('permission_events', 0)}",
                f"- errors: {len(row.get('errors', []))}",
                f"- warnings: {len(row.get('warnings', []))}",
                "",
            ]
        )
    return "\n".join(lines)


def render_list(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "(none)"
    return ", ".join(str(value) for value in values)


def load_profile_evaluation_dataset_jsonl(path: Path) -> ProfileEvaluationDataset:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: dataset row must be an object")
        private_findings = find_private_values(row)
        if private_findings:
            raise ValueError(
                "{path}:{line}: private-looking value detected: {finding}".format(
                    path=path,
                    line=line_number,
                    finding=private_findings[0],
                )
            )
        rows.append(row)
    return ProfileEvaluationDataset(rows=tuple(rows))


def build_profile_evaluation_aggregate(
    dataset: ProfileEvaluationDataset,
) -> ProfileEvaluationAggregate:
    rows = dataset.rows
    errors = tuple(
        f"row {index}: {error}"
        for index, row in enumerate(rows, 1)
        for error in row.get("errors", [])
    )
    summary = {
        "schema_version": 1,
        "row_count": len(rows),
        "valid": not errors,
        "controller_health": counter_dict(
            row_value(row, "controller_health") for row in rows
        ),
        "result_status": counter_dict(row_value(row, "result_status") for row in rows),
        "selected_agent": counter_dict(
            row_value(row, "selected_agent") for row in rows
        ),
        "task_overlay": counter_dict(primary_overlay(row) for row in rows),
        "task_family": counter_dict(infer_task_family(row) for row in rows),
        "by_profile_result_status": nested_counter_dict(
            (row_value(row, "selected_agent"), row_value(row, "result_status"))
            for row in rows
        ),
        "by_overlay_result_status": nested_counter_dict(
            (primary_overlay(row), row_value(row, "result_status")) for row in rows
        ),
        "by_task_family_result_status": nested_counter_dict(
            (infer_task_family(row), row_value(row, "result_status")) for row in rows
        ),
        "treatment_cells": treatment_cells(rows),
        "conversation_shape": conversation_shape_summary(rows),
        "recommendation": recommend_next_lane(rows),
    }
    return ProfileEvaluationAggregate(rows=rows, summary=summary, errors=errors)


def render_profile_evaluation_aggregate_json(
    aggregate: ProfileEvaluationAggregate,
) -> str:
    payload = dict(aggregate.summary)
    payload["errors"] = list(aggregate.errors)
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_profile_evaluation_aggregate_markdown(
    aggregate: ProfileEvaluationAggregate,
) -> str:
    summary = aggregate.summary
    lines = [
        "# Profile Evaluation Aggregate Report",
        "",
        f"- valid: `{aggregate.ok}`",
        f"- rows: {summary['row_count']}",
        "- raw_transcripts_included: `False`",
        "- private_paths_included: `False`",
        f"- recommendation: {summary['recommendation']}",
        "",
        "## Top-Level Counts",
        "",
        "### Controller Health",
        "",
        markdown_count_table(summary["controller_health"]),
        "### Result Status",
        "",
        markdown_count_table(summary["result_status"]),
        "### Selected Profile",
        "",
        markdown_count_table(summary["selected_agent"]),
        "### Task Overlay",
        "",
        markdown_count_table(summary["task_overlay"]),
        "### Task Family",
        "",
        markdown_count_table(summary["task_family"]),
        "## Grouped Result Status",
        "",
        "### By Profile",
        "",
        markdown_nested_count_table(summary["by_profile_result_status"]),
        "### By Overlay",
        "",
        markdown_nested_count_table(summary["by_overlay_result_status"]),
        "### By Task Family",
        "",
        markdown_nested_count_table(summary["by_task_family_result_status"]),
        "## Treatment Cells",
        "",
        markdown_treatment_cell_table(summary["treatment_cells"]),
        "## Conversation Shape",
        "",
        markdown_conversation_shape_table(summary["conversation_shape"]),
        "",
    ]
    if aggregate.errors:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in aggregate.errors)
        lines.append("")
    return "\n".join(lines)


def load_profile_evaluation_aggregate_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: aggregate summary must be an object")
    private_findings = find_private_values(payload)
    private_findings.extend(find_private_keys(payload))
    if private_findings:
        raise ValueError(
            "{path}: private-looking value detected: {finding}".format(
                path=path,
                finding=private_findings[0],
            )
        )
    return payload


def find_private_keys(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = f"{path}.{key}"
            if find_private_values(str(key)):
                findings.append(key_path)
            findings.extend(find_private_keys(child, key_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_private_keys(child, f"{path}[{index}]"))
    return findings


def build_profile_contract_repair_plan(
    aggregate_summary: dict[str, Any],
) -> ProfileContractRepairPlan:
    errors = tuple(validate_aggregate_summary_shape(aggregate_summary))
    if errors:
        return ProfileContractRepairPlan(summary={}, errors=errors)
    weak_cells = ranked_weak_treatment_cells(
        aggregate_summary.get("treatment_cells", [])
    )
    task_family_targets = ranked_result_targets(
        aggregate_summary.get("by_task_family_result_status", {})
    )
    profile_targets = ranked_result_targets(
        aggregate_summary.get("by_profile_result_status", {})
    )
    summary = {
        "schema_version": 1,
        "source_schema_version": aggregate_summary.get("schema_version"),
        "row_count": aggregate_summary.get("row_count", 0),
        "controller_health": aggregate_summary.get("controller_health", {}),
        "result_status": aggregate_summary.get("result_status", {}),
        "weak_treatment_cells": weak_cells,
        "task_family_targets": task_family_targets,
        "profile_targets": profile_targets,
        "recommendation": recommend_contract_repair_next_step(
            aggregate_summary,
            weak_cells=weak_cells,
            task_family_targets=task_family_targets,
            profile_targets=profile_targets,
        ),
        "validation_boundary": (
            "After repair, rerun a matched replicated battery on repaired cells "
            "before model-lane expansion or FoundryTK runtime integration."
        ),
    }
    return ProfileContractRepairPlan(summary=summary)


def validate_aggregate_summary_shape(summary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(summary.get("row_count", 0), int):
        errors.append("row_count must be an integer")
    for key in (
        "controller_health",
        "result_status",
        "by_task_family_result_status",
        "by_profile_result_status",
    ):
        if not isinstance(summary.get(key, {}), dict):
            errors.append(f"{key} must be an object")
    if not isinstance(summary.get("treatment_cells", []), list):
        errors.append("treatment_cells must be a list")
    return errors


def ranked_weak_treatment_cells(cells: Any) -> list[dict[str, Any]]:
    if not isinstance(cells, list):
        return []
    weak_cells: list[dict[str, Any]] = []
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        statuses = cell.get("result_status", {})
        if not isinstance(statuses, dict):
            continue
        rows = int(cell.get("rows", 0)) if isinstance(cell.get("rows", 0), int) else 0
        accepted = int(statuses.get("accepted-candidate", 0))
        review = int(statuses.get("needs-supervisor-review", 0))
        blocked = int(statuses.get("blocked", 0))
        if rows <= 0 or (blocked == 0 and review == 0 and accepted >= rows):
            continue
        accepted_rate = round(accepted / rows, 3) if rows else 0.0
        repair_score = blocked * 3 + review + max(rows - accepted, 0)
        weak_cells.append(
            {
                "selected_agent": str(cell.get("selected_agent", "(missing)")),
                "task_overlay": str(cell.get("task_overlay", "(missing)")),
                "task_family": str(cell.get("task_family", "(missing)")),
                "rows": rows,
                "accepted_candidate": accepted,
                "needs_supervisor_review": review,
                "blocked": blocked,
                "accepted_rate": accepted_rate,
                "repair_score": repair_score,
                "repair_focus": repair_focus_for_counts(
                    blocked=blocked,
                    review=review,
                    accepted=accepted,
                    rows=rows,
                ),
            }
        )
    return sorted(
        weak_cells,
        key=lambda item: (
            -int(item["repair_score"]),
            -int(item["blocked"]),
            -int(item["needs_supervisor_review"]),
            float(item["accepted_rate"]),
            item["task_family"],
            item["selected_agent"],
            item["task_overlay"],
        ),
    )


def ranked_result_targets(groups: Any) -> list[dict[str, Any]]:
    if not isinstance(groups, dict):
        return []
    targets: list[dict[str, Any]] = []
    for name, statuses in groups.items():
        if not isinstance(statuses, dict):
            continue
        accepted = int(statuses.get("accepted-candidate", 0))
        review = int(statuses.get("needs-supervisor-review", 0))
        blocked = int(statuses.get("blocked", 0))
        rows = sum(int(value) for value in statuses.values() if isinstance(value, int))
        if rows <= 0 or (blocked == 0 and review == 0 and accepted >= rows):
            continue
        accepted_rate = round(accepted / rows, 3) if rows else 0.0
        repair_score = blocked * 3 + review + max(rows - accepted, 0)
        targets.append(
            {
                "name": str(name),
                "rows": rows,
                "accepted_candidate": accepted,
                "needs_supervisor_review": review,
                "blocked": blocked,
                "accepted_rate": accepted_rate,
                "repair_score": repair_score,
                "repair_focus": repair_focus_for_counts(
                    blocked=blocked,
                    review=review,
                    accepted=accepted,
                    rows=rows,
                ),
            }
        )
    return sorted(
        targets,
        key=lambda item: (
            -int(item["repair_score"]),
            -int(item["blocked"]),
            -int(item["needs_supervisor_review"]),
            float(item["accepted_rate"]),
            item["name"],
        ),
    )


def repair_focus_for_counts(
    *,
    blocked: int,
    review: int,
    accepted: int,
    rows: int,
) -> str:
    if blocked:
        return "repair blocker-producing contract ambiguity before rerun"
    if review > accepted:
        return "tighten evidence rubric and artifact references before rerun"
    if accepted < rows:
        return "reduce supervisor-review fallback before scale-up"
    return "monitor"


def recommend_contract_repair_next_step(
    aggregate_summary: dict[str, Any],
    *,
    weak_cells: list[dict[str, Any]],
    task_family_targets: list[dict[str, Any]],
    profile_targets: list[dict[str, Any]],
) -> str:
    if aggregate_summary.get("row_count", 0) == 0:
        return "Collect aggregate evidence before writing a contract repair plan."
    controller_health = aggregate_summary.get("controller_health", {})
    if isinstance(controller_health, dict) and any(
        status != "healthy" for status in controller_health
    ):
        return "Repair controller/session health before task/profile contract repair."
    top_task = task_family_targets[0]["name"] if task_family_targets else ""
    top_profile = profile_targets[0]["name"] if profile_targets else ""
    if top_task == "profile-evidence-review" and top_profile:
        return (
            "Repair profile-evidence-review fixtures and "
            f"{top_profile}-as-primary behavior before another live battery."
        )
    if weak_cells:
        first = weak_cells[0]
        return (
            "Repair the highest-scoring treatment cell before another live "
            "battery: {profile} / {overlay} / {task_family}.".format(
                profile=first["selected_agent"],
                overlay=first["task_overlay"],
                task_family=first["task_family"],
            )
        )
    return (
        "No weak contract cells detected; run another replicated battery or a "
        "verified model-lane block before broad claims."
    )


def render_profile_contract_repair_plan_json(
    plan: ProfileContractRepairPlan,
) -> str:
    payload = dict(plan.summary)
    payload["errors"] = list(plan.errors)
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_profile_contract_repair_plan_markdown(
    plan: ProfileContractRepairPlan,
) -> str:
    if plan.errors:
        lines = ["# Profile Contract Repair Plan", "", "- valid: `False`", ""]
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in plan.errors)
        lines.append("")
        return "\n".join(lines)
    summary = plan.summary
    lines = [
        "# Profile Contract Repair Plan",
        "",
        "- valid: `True`",
        f"- rows: {summary['row_count']}",
        "- raw_transcripts_included: `False`",
        "- private_paths_included: `False`",
        f"- recommendation: {summary['recommendation']}",
        "",
        "## Controller Health",
        "",
        markdown_count_table(summary["controller_health"]),
        "## Result Status",
        "",
        markdown_count_table(summary["result_status"]),
        "## Task Family Repair Targets",
        "",
        markdown_repair_target_table(summary["task_family_targets"]),
        "## Profile Repair Targets",
        "",
        markdown_repair_target_table(summary["profile_targets"]),
        "## Weak Treatment Cells",
        "",
        markdown_weak_cell_table(summary["weak_treatment_cells"]),
        "## Validation Boundary",
        "",
        summary["validation_boundary"],
        "",
    ]
    return "\n".join(lines)


def markdown_repair_target_table(targets: list[dict[str, Any]]) -> str:
    if not targets:
        return "No weak targets.\n"
    lines = [
        "| target | rows | accepted | review | blocked | accepted_rate | repair_score | focus |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for target in targets:
        lines.append(
            "| `{name}` | {rows} | {accepted} | {review} | {blocked} | {rate} | {score} | {focus} |".format(
                name=target["name"],
                rows=target["rows"],
                accepted=target["accepted_candidate"],
                review=target["needs_supervisor_review"],
                blocked=target["blocked"],
                rate=target["accepted_rate"],
                score=target["repair_score"],
                focus=target["repair_focus"],
            )
        )
    return "\n".join(lines) + "\n"


def markdown_weak_cell_table(cells: list[dict[str, Any]]) -> str:
    if not cells:
        return "No weak treatment cells.\n"
    lines = [
        "| profile | overlay | task_family | rows | accepted | review | blocked | accepted_rate | repair_score | focus |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for cell in cells:
        lines.append(
            "| `{profile}` | `{overlay}` | `{family}` | {rows} | {accepted} | {review} | {blocked} | {rate} | {score} | {focus} |".format(
                profile=cell["selected_agent"],
                overlay=cell["task_overlay"],
                family=cell["task_family"],
                rows=cell["rows"],
                accepted=cell["accepted_candidate"],
                review=cell["needs_supervisor_review"],
                blocked=cell["blocked"],
                rate=cell["accepted_rate"],
                score=cell["repair_score"],
                focus=cell["repair_focus"],
            )
        )
    return "\n".join(lines) + "\n"


def row_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key, "")
    return str(value) if value not in (None, "") else "(missing)"


def primary_overlay(row: dict[str, Any]) -> str:
    overlays = row.get("task_overlays", [])
    if isinstance(overlays, list) and overlays:
        return str(overlays[0])
    return "(none)"


def infer_task_family(row: dict[str, Any]) -> str:
    value = row.get("task_family", "")
    if isinstance(value, str) and value.strip():
        return value.strip()
    run_id = row_value(row, "run_id")
    parts = run_id.split("_")
    if len(parts) >= 2 and parts[1] in {"mca", "per"}:
        return {
            "mca": "manifest-contract-audit",
            "per": "profile-evidence-review",
        }[parts[1]]
    return "(unknown)"


def counter_dict(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def nested_counter_dict(pairs: Any) -> dict[str, dict[str, int]]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for outer, inner in pairs:
        counters[str(outer)][str(inner)] += 1
    return {
        outer: dict(sorted(counter.items()))
        for outer, counter in sorted(counters.items())
    }


def treatment_cells(rows: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    counters: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = (
            row_value(row, "selected_agent"),
            primary_overlay(row),
            infer_task_family(row),
        )
        counters[key][row_value(row, "result_status")] += 1
    cells: list[dict[str, Any]] = []
    for (profile, overlay, task_family), counts in sorted(counters.items()):
        cells.append(
            {
                "selected_agent": profile,
                "task_overlay": overlay,
                "task_family": task_family,
                "rows": sum(counts.values()),
                "result_status": dict(sorted(counts.items())),
            }
        )
    return cells


CONVERSATION_METRIC_PATHS = {
    "event_count": ("efficiency", "event_count"),
    "assistant_messages": ("efficiency", "assistant_messages"),
    "tool_events": ("efficiency", "tool_events"),
    "permission_events": ("efficiency", "permission_events"),
    "custom_agent_events": ("conversation_shape", "custom_agent_events"),
    "subagent_events": ("conversation_shape", "subagent_events"),
}


def conversation_shape_summary(
    rows: tuple[dict[str, Any], ...],
) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for metric, path in CONVERSATION_METRIC_PATHS.items():
        values = [numeric_nested_value(row, path) for row in rows]
        total = sum(values)
        count = len(values)
        summary[metric] = {
            "total": total,
            "average": round(total / count, 2) if count else 0.0,
        }
    return summary


def numeric_nested_value(row: dict[str, Any], path: tuple[str, str]) -> int:
    outer = row.get(path[0], {})
    if not isinstance(outer, dict):
        return 0
    value = outer.get(path[1], 0)
    return int(value) if isinstance(value, int | float) else 0


def recommend_next_lane(rows: tuple[dict[str, Any], ...]) -> str:
    if not rows:
        return "Collect profile evaluation dataset rows before choosing a lane."
    controller_counts = Counter(row_value(row, "controller_health") for row in rows)
    if any(status != "healthy" for status in controller_counts):
        return "Repair controller/session health before profile or model optimization."
    statuses = Counter(row_value(row, "result_status") for row in rows)
    accepted = statuses.get("accepted-candidate", 0)
    blocked = statuses.get("blocked", 0)
    accepted_rate = accepted / len(rows)
    if accepted_rate >= 0.95 and blocked == 0:
        return (
            "Treat the repaired profile-evidence-review contract as empirically "
            "stable enough for the next replicated comparison lane; audit any "
            "remaining needs-supervisor-review rows as targeted follow-up."
        )
    if accepted < len(rows):
        return (
            "Prioritize task/profile contract repair before another live battery, "
            "model-lane expansion, or FoundryTK runtime integration."
        )
    return (
        "Run another replicated battery or verified model-lane block before "
        "claiming profile or model superiority."
    )


def markdown_count_table(counts: dict[str, int]) -> str:
    if not counts:
        return "No rows.\n"
    lines = ["| value | rows |", "| --- | ---: |"]
    lines.extend(f"| `{key}` | {value} |" for key, value in counts.items())
    return "\n".join(lines) + "\n"


def markdown_nested_count_table(counts: dict[str, dict[str, int]]) -> str:
    if not counts:
        return "No rows.\n"
    lines = ["| group | value | rows |", "| --- | --- | ---: |"]
    for group, nested in counts.items():
        for value, count in nested.items():
            lines.append(f"| `{group}` | `{value}` | {count} |")
    return "\n".join(lines) + "\n"


def markdown_treatment_cell_table(cells: list[dict[str, Any]]) -> str:
    if not cells:
        return "No rows.\n"
    lines = [
        "| profile | overlay | task_family | rows | result_status |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for cell in cells:
        result_status = ", ".join(
            f"{status}: {count}" for status, count in cell["result_status"].items()
        )
        lines.append(
            "| `{profile}` | `{overlay}` | `{task_family}` | {rows} | {statuses} |".format(
                profile=cell["selected_agent"],
                overlay=cell["task_overlay"],
                task_family=cell["task_family"],
                rows=cell["rows"],
                statuses=result_status,
            )
        )
    return "\n".join(lines) + "\n"


def markdown_conversation_shape_table(
    metrics: dict[str, dict[str, float]],
) -> str:
    if not metrics:
        return "No rows.\n"
    lines = ["| metric | total | average |", "| --- | ---: | ---: |"]
    for metric, values in metrics.items():
        lines.append(f"| `{metric}` | {values['total']} | {values['average']} |")
    return "\n".join(lines) + "\n"
