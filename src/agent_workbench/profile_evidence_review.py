"""Contracts for profile-evidence-review SDK task fixtures."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


PROFILE_EVIDENCE_REVIEW_TASK = "profile-evidence-review"
CURRENT_RUN_OUTPUT_KEYS = {
    "result",
    "blocker",
    "heartbeat",
    "event_log",
    "status_summary",
    "nudge_log",
    "profile_summary",
    "compact_transcript",
}
RESULT_STATUSES = (
    "accepted-candidate",
    "rejected-candidate",
    "blocked",
    "needs-supervisor-review",
)


@dataclass(frozen=True)
class ProfileEvidenceReviewContract:
    run_id: str
    task_family: str
    selected_agent: str
    task_overlay: str
    review_subject_path: str
    review_subject_kind: str
    result_path: str
    blocker_path: str
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def build_profile_evidence_review_contract(
    manifest: dict[str, Any],
    *,
    manifest_path: Path | None = None,
    require_existing_subject: bool = True,
) -> ProfileEvidenceReviewContract:
    base = manifest_path.parent if manifest_path is not None else Path.cwd()
    paths = manifest.get("paths", {}) if isinstance(manifest.get("paths"), dict) else {}
    errors: list[str] = []
    warnings: list[str] = []
    task_family = manifest_task_family(manifest)
    if task_family != PROFILE_EVIDENCE_REVIEW_TASK:
        errors.append(
            "manifest is not a profile-evidence-review task "
            f"(found {task_family or '(missing)'})"
        )
    review_subject_path = manifest_review_subject_path(manifest)
    review_subject_kind = manifest_review_subject_kind(manifest, review_subject_path)
    if not review_subject_path:
        errors.append(
            "profile-evidence-review requires a pre-existing review subject path"
        )
    else:
        private_findings = find_private_values(
            {"review_subject_path": review_subject_path}
        )
        if private_findings:
            errors.append(
                f"private-looking review subject path detected: {private_findings[0]}"
            )
        subject = resolve_manifest_relative_path(review_subject_path, base=base)
        for key in CURRENT_RUN_OUTPUT_KEYS:
            value = paths.get(key)
            if isinstance(value, str) and value:
                current_output = resolve_manifest_relative_path(value, base=base)
                if subject == current_output:
                    errors.append(
                        "review subject must be pre-existing and separate from "
                        f"current-run {key} path"
                    )
        if require_existing_subject and not subject.exists():
            errors.append(f"review subject does not exist: {review_subject_path}")
        if not review_subject_kind:
            warnings.append("review subject kind was inferred as public-safe-artifact")
    return ProfileEvidenceReviewContract(
        run_id=str(manifest.get("run_id", "")),
        task_family=task_family,
        selected_agent=manifest_selected_agent(manifest),
        task_overlay=manifest_task_overlay(manifest),
        review_subject_path=review_subject_path,
        review_subject_kind=review_subject_kind,
        result_path=str(paths.get("result", "")),
        blocker_path=str(paths.get("blocker", "")),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def manifest_task_family(manifest: dict[str, Any]) -> str:
    experiment = manifest.get("experiment", {})
    if isinstance(experiment, dict):
        task_family = experiment.get("task_family")
        if isinstance(task_family, str) and task_family.strip():
            return task_family.strip()
    target_task = manifest.get("target_task")
    return target_task.strip() if isinstance(target_task, str) else ""


def manifest_selected_agent(manifest: dict[str, Any]) -> str:
    sdk = manifest.get("sdk", {})
    if not isinstance(sdk, dict):
        return ""
    agent_profiles = sdk.get("agent_profiles", {})
    if not isinstance(agent_profiles, dict):
        return ""
    selected = agent_profiles.get("selected", "")
    return selected.strip() if isinstance(selected, str) else ""


def manifest_task_overlay(manifest: dict[str, Any]) -> str:
    sdk = manifest.get("sdk", {})
    if not isinstance(sdk, dict):
        return ""
    agent_profiles = sdk.get("agent_profiles", {})
    if not isinstance(agent_profiles, dict):
        return ""
    overlay = agent_profiles.get("task_overlay", {})
    if not isinstance(overlay, dict):
        return ""
    name = overlay.get("name", "")
    return name.strip() if isinstance(name, str) else ""


def manifest_review_subject_path(manifest: dict[str, Any]) -> str:
    profile_review = manifest.get("profile_evidence_review", {})
    if isinstance(profile_review, dict):
        value = profile_review.get("review_subject_path")
        if isinstance(value, str) and value.strip():
            return value.strip()
    paths = manifest.get("paths", {})
    if isinstance(paths, dict):
        value = paths.get("review_subject")
        if isinstance(value, str) and value.strip():
            return value.strip()
    experiment = manifest.get("experiment", {})
    if isinstance(experiment, dict):
        value = experiment.get("review_subject_path")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def manifest_review_subject_kind(
    manifest: dict[str, Any],
    review_subject_path: str,
) -> str:
    profile_review = manifest.get("profile_evidence_review", {})
    if isinstance(profile_review, dict):
        value = profile_review.get("review_subject_kind")
        if isinstance(value, str) and value.strip():
            return value.strip()
    experiment = manifest.get("experiment", {})
    if isinstance(experiment, dict):
        value = experiment.get("review_subject_kind")
        if isinstance(value, str) and value.strip():
            return value.strip()
    lowered = review_subject_path.lower()
    if "profile_summaries" in lowered or "profile-summary" in lowered:
        return "profile-run-summary"
    if "compact" in lowered or "transcript" in lowered:
        return "compact-transcript"
    return "public-safe-artifact" if review_subject_path else ""


def resolve_manifest_relative_path(path: str, *, base: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()


def render_profile_evidence_review_contract_json(
    contract: ProfileEvidenceReviewContract,
) -> str:
    return (
        json.dumps(
            {
                "schema_version": 1,
                "valid": contract.ok,
                "run_id": contract.run_id,
                "task_family": contract.task_family,
                "selected_agent": contract.selected_agent,
                "task_overlay": contract.task_overlay,
                "review_subject_path": contract.review_subject_path,
                "review_subject_kind": contract.review_subject_kind,
                "result_path": contract.result_path,
                "blocker_path": contract.blocker_path,
                "errors": list(contract.errors),
                "warnings": list(contract.warnings),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def render_profile_evidence_review_ticket(
    contract: ProfileEvidenceReviewContract,
) -> str:
    lines = [
        f"# Profile Evidence Review Ticket: {contract.run_id or '(unknown run)'}",
        "",
        "Final status: pending",
        "",
        "## Treatment Cell",
        "",
        f"- profile: {contract.selected_agent or '(missing)'}",
        f"- overlay: {contract.task_overlay or '(missing)'}",
        f"- task_family: {contract.task_family or '(missing)'}",
        "",
        "## Review Subject",
        "",
        f"- review_subject_path: {contract.review_subject_path or '(missing)'}",
        f"- review_subject_kind: {contract.review_subject_kind or '(missing)'}",
        "- review_subject_timing: pre-existing artifact declared before this run starts",
        "",
        "## Current Run Outputs",
        "",
        f"- result: {contract.result_path or '(missing)'}",
        f"- blocker: {contract.blocker_path or '(missing)'}",
        "",
        "## Task",
        "",
        "Review the declared pre-existing review subject. Do not treat profile "
        "summaries, compact transcripts, event logs, status summaries, result "
        "files, or blocker files generated by this same run as input evidence.",
        "",
        "Use `agent_workbench_run_context` and `agent_workbench_result_contract` "
        "when those tools are available. Write exactly one result or blocker "
        "artifact with `agent_workbench_write_result` when that tool is available.",
        "",
        "## Scoring Rubric",
        "",
        "- controller_health: classify the reviewed run as healthy, degraded, blocked, or unknown from the subject artifact.",
        "- result_validity: classify whether the reviewed run's result status was accepted-candidate, rejected-candidate, blocked, needs-supervisor-review, or missing.",
        "- evidence_sufficiency: accepted only when the subject cites enough public-safe evidence to support both controller_health and result_validity.",
        "- evidence_gap: use needs-supervisor-review when the subject is readable but insufficient; use blocked only when the declared subject cannot be inspected or the contract cannot be followed.",
        "",
        "## Required Output",
        "",
        "The written Markdown must start with exactly one of:",
        "",
    ]
    lines.extend(f"- Final status: {status}" for status in RESULT_STATUSES)
    lines.extend(
        [
            "",
            "Use `accepted-candidate` only when the declared review subject is "
            "present, readable, public-safe, and sufficient for the scoring "
            "rubric. Include concise evidence bullets. Do not include raw private "
            "transcript text, credentials, provider endpoints, or personal "
            "absolute paths.",
            "",
        ]
    )
    if contract.errors:
        lines.extend(["## Contract Errors", ""])
        lines.extend(f"- {error}" for error in contract.errors)
        lines.append("")
    if contract.warnings:
        lines.extend(["## Contract Warnings", ""])
        lines.extend(f"- {warning}" for warning in contract.warnings)
        lines.append("")
    return "\n".join(lines)
