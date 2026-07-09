"""Planning helpers for FoundryTK-style profile optimization experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .copilot_profile_runs import ProfileRunEvidence, summarize_profile_run


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
    import json

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
