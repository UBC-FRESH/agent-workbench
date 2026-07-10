"""Behavior analytics for sanitized Copilot archive manifests."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BEHAVIOR_OUTCOMES = (
    "smooth",
    "nudged-success",
    "noisy-success",
    "repair-needed",
    "blocked",
    "runaway",
)

REPEATED_SUMMARY_PATTERNS = (
    re.compile(r"successfully completed", re.IGNORECASE),
    re.compile(r"task has been completed", re.IGNORECASE),
    re.compile(r"ready for (review|merge)", re.IGNORECASE),
)

PREMATURE_COMPLETION_PATTERNS = (
    re.compile(r"\bcomplete\b", re.IGNORECASE),
    re.compile(r"\bsuccessfully\b", re.IGNORECASE),
)

SHELL_MISMATCH_PATTERNS = (
    re.compile(r"\bbash\b", re.IGNORECASE),
    re.compile(r"\bheredoc\b", re.IGNORECASE),
    re.compile(r"\bcat\s+>", re.IGNORECASE),
)


def load_archive_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("archive manifest must be a JSON object")
    return data


def load_behavior_input(path: Path) -> dict[str, Any]:
    return load_archive_manifest(path)


def analyze_archive_manifest(
    manifest: dict[str, Any],
    *,
    ticket_type: str = "unknown",
    task_size: str = "unknown",
    authority_level: str = "unknown",
) -> dict[str, Any]:
    user_snippets = string_list(manifest.get("user_message_snippets"))
    assistant_snippets = string_list(manifest.get("assistant_message_snippets"))
    tool_snippets = string_list(manifest.get("tool_request_snippets"))
    tool_statuses = manifest.get("tool_completion_statuses", {})
    if not isinstance(tool_statuses, dict):
        tool_statuses = {}

    keep_going_count = len(string_list(manifest.get("keep_going_user_messages")))
    stall_nudge_count = len(string_list(manifest.get("stall_nudge_user_messages")))
    nudge_count = keep_going_count + stall_nudge_count
    command_failure_count = count_status_failures(tool_statuses)
    repeated_summary_count = count_matching(
        assistant_snippets, REPEATED_SUMMARY_PATTERNS
    )
    shell_mismatch_count = count_matching(
        tool_snippets + assistant_snippets, SHELL_MISMATCH_PATTERNS
    )
    premature_completion_claim_count = count_premature_completion(
        assistant_snippets,
        user_snippets,
    )
    user_intervention_burden = max(0, int(manifest.get("user_message_count", 0)) - 1)
    coordinator_review_burden = (
        nudge_count
        + command_failure_count
        + shell_mismatch_count
        + repeated_summary_count
        + premature_completion_claim_count
    )
    runaway = repeated_summary_count >= 5 and nudge_count >= 1
    blocked = command_failure_count > 0 and not manifest.get("tool_request_count", 0)
    outcome = classify_behavior(
        nudge_count=nudge_count,
        command_failure_count=command_failure_count,
        repeated_summary_count=repeated_summary_count,
        premature_completion_claim_count=premature_completion_claim_count,
        runaway=runaway,
        blocked=blocked,
    )
    return {
        "schema_version": "p69.behavior.v1",
        "session_id": manifest.get("session_id", ""),
        "run_id": manifest.get("run_id", ""),
        "model_ids_detected": manifest.get("model_ids_detected", []),
        "permission_levels_detected": manifest.get("permission_levels_detected", []),
        "ticket_type": ticket_type,
        "task_size": task_size,
        "authority_level": authority_level,
        "stall_count": stall_nudge_count,
        "nudge_count": nudge_count,
        "tool_call_count": int(manifest.get("tool_request_count", 0)),
        "command_failure_count": command_failure_count,
        "shell_mismatch_count": shell_mismatch_count,
        "repeated_summary_count": repeated_summary_count,
        "premature_completion_claim_count": premature_completion_claim_count,
        "user_intervention_burden": user_intervention_burden,
        "coordinator_review_burden": coordinator_review_burden,
        "behavior_outcome": outcome,
        "policy_feedback": policy_feedback(outcome, coordinator_review_burden),
    }


def string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def count_status_failures(statuses: dict[object, object]) -> int:
    count = 0
    for key, value in statuses.items():
        status = str(key).lower()
        if status in ("failed", "failure", "error", "cancelled", "canceled"):
            try:
                count += int(value)
            except (TypeError, ValueError):
                count += 1
    return count


def count_matching(snippets: list[str], patterns: tuple[re.Pattern[str], ...]) -> int:
    return sum(
        1 for snippet in snippets for pattern in patterns if pattern.search(snippet)
    )


def count_premature_completion(
    assistant_snippets: list[str],
    user_snippets: list[str],
) -> int:
    if not any("keep going" in snippet.lower() for snippet in user_snippets):
        return 0
    return count_matching(assistant_snippets, PREMATURE_COMPLETION_PATTERNS)


def classify_behavior(
    *,
    nudge_count: int,
    command_failure_count: int,
    repeated_summary_count: int,
    premature_completion_claim_count: int,
    runaway: bool,
    blocked: bool,
) -> str:
    if runaway:
        return "runaway"
    if blocked:
        return "blocked"
    if command_failure_count or premature_completion_claim_count:
        return "repair-needed"
    if repeated_summary_count >= 2:
        return "noisy-success"
    if nudge_count:
        return "nudged-success"
    return "smooth"


def policy_feedback(outcome: str, burden: int) -> str:
    if outcome == "smooth":
        return "candidate for broader delegation after more archive samples"
    if outcome == "nudged-success":
        return "keep task-level ticketing and add heartbeat-triggered nudges"
    if outcome == "noisy-success":
        return "tighten final-response and no-summary-substitute clauses"
    if outcome == "repair-needed":
        return "issue bounded repair ticket before further scope expansion"
    if outcome == "blocked":
        return "escalate to coordinator before retry"
    if outcome == "runaway":
        return "stop lane and redesign ticket or model role"
    return f"review manually; coordinator burden={burden}"


def render_behavior_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Copilot Behavior Summary",
        "",
        f"- session_id: `{summary.get('session_id', '')}`",
        f"- run_id: `{summary.get('run_id', '')}`",
        f"- behavior_outcome: `{summary.get('behavior_outcome', '')}`",
        f"- ticket_type: `{summary.get('ticket_type', '')}`",
        f"- task_size: `{summary.get('task_size', '')}`",
        f"- authority_level: `{summary.get('authority_level', '')}`",
        "",
        "## Metrics",
        "",
        f"- stall_count: {summary.get('stall_count', 0)}",
        f"- nudge_count: {summary.get('nudge_count', 0)}",
        f"- tool_call_count: {summary.get('tool_call_count', 0)}",
        f"- command_failure_count: {summary.get('command_failure_count', 0)}",
        f"- shell_mismatch_count: {summary.get('shell_mismatch_count', 0)}",
        f"- repeated_summary_count: {summary.get('repeated_summary_count', 0)}",
        "- premature_completion_claim_count: "
        f"{summary.get('premature_completion_claim_count', 0)}",
        f"- user_intervention_burden: {summary.get('user_intervention_burden', 0)}",
        f"- coordinator_review_burden: {summary.get('coordinator_review_burden', 0)}",
        "",
        "## Policy Feedback",
        "",
        str(summary.get("policy_feedback", "")),
        "",
    ]
    return "\n".join(lines)


def synthesize_behavior_summaries(
    summaries: list[dict[str, Any]] | list[Path],
) -> dict[str, Any] | tuple[dict[str, Any], str]:
    if summaries and isinstance(summaries[0], Path):
        loaded: list[dict[str, Any]] = []
        for path in summaries:
            if not isinstance(path, Path):
                raise ValueError("mixed behavior synthesis inputs are not supported")
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict):
                raise ValueError(f"behavior summary must be a JSON object: {path}")
            loaded.append(data)
        synthesis = synthesize_behavior_summary_data(loaded)
        return synthesis, render_synthesis_markdown(synthesis)
    return synthesize_behavior_summary_data(summaries)  # type: ignore[arg-type]


def synthesize_behavior_summary_data(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    outcome_counts = Counter(
        str(item.get("behavior_outcome", "")) for item in summaries
    )
    model_counts: dict[str, int] = defaultdict(int)
    permission_counts: dict[str, int] = defaultdict(int)
    burden_total = 0
    for item in summaries:
        burden_total += int(item.get("coordinator_review_burden", 0))
        for model in item.get("model_ids_detected", []):
            model_counts[str(model)] += 1
        for permission in item.get("permission_levels_detected", []):
            permission_counts[str(permission)] += 1
    minimum_archive_count = 10
    return {
        "schema_version": "p69.behavior_synthesis.v1",
        "run_count": len(summaries),
        "outcome_counts": dict(outcome_counts),
        "model_counts": dict(sorted(model_counts.items())),
        "permission_counts": dict(sorted(permission_counts.items())),
        "coordinator_review_burden_total": burden_total,
        "coordinator_review_burden_mean": (
            burden_total / len(summaries) if summaries else 0
        ),
        "minimum_archive_count_before_tuning_defaults": minimum_archive_count,
        "policy_feedback": synthesis_policy_feedback(len(summaries), outcome_counts),
    }


def synthesis_policy_feedback(run_count: int, outcome_counts: Counter[str]) -> str:
    if run_count < 10:
        return "collect more archives before tuning default delegation policy"
    noisy = (
        outcome_counts.get("noisy-success", 0)
        + outcome_counts.get("repair-needed", 0)
        + outcome_counts.get("runaway", 0)
    )
    if noisy / run_count > 0.3:
        return "tighten tickets and controller stop rules before increasing delegation scope"
    return "sufficient sample for cautious policy tuning"


def render_synthesis_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Copilot Behavior Synthesis",
        "",
        f"- run_count: {summary.get('run_count', 0)}",
        "- coordinator_review_burden_total: "
        f"{summary.get('coordinator_review_burden_total', 0)}",
        "- coordinator_review_burden_mean: "
        f"{summary.get('coordinator_review_burden_mean', 0):.2f}",
        "- minimum_archive_count_before_tuning_defaults: "
        f"{summary.get('minimum_archive_count_before_tuning_defaults', 0)}",
        "",
        "## Outcome Counts",
        "",
    ]
    for outcome in BEHAVIOR_OUTCOMES:
        lines.append(
            f"- `{outcome}`: {summary.get('outcome_counts', {}).get(outcome, 0)}"
        )
    lines.extend(
        ["", "## Policy Feedback", "", str(summary.get("policy_feedback", "")), ""]
    )
    return "\n".join(lines)
