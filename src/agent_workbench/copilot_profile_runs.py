"""Profile-run evidence summaries for SDK-owned Copilot sessions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .copilot_agent_profiles import resolve_agent_profiles
from .copilot_sdk_bridge import (
    count_sdk_transcript_events,
    load_sdk_event_jsonl,
    load_sdk_session_manifest,
    resolve_manifest_path,
)


@dataclass(frozen=True)
class ProfileRunEvidence:
    run_id: str
    session_id: str
    phase: str
    selected_agent: str
    custom_tools: tuple[str, ...]
    task_overlays: tuple[str, ...]
    event_count: int
    assistant_messages: int
    user_messages: int
    tool_events: int
    permission_events: int
    custom_agent_events: int
    subagent_events: int
    agent_metadata_messages: int
    latest_status: str
    controller_health: str
    result_status: str
    result_path: str
    blocker_path: str
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def summarize_profile_run(manifest_path: Path) -> ProfileRunEvidence:
    manifest = load_sdk_session_manifest(manifest_path)
    base = manifest_path.parent
    resolved = resolve_agent_profiles(manifest, manifest_path=manifest_path)
    errors = list(resolved.errors)
    warnings = list(resolved.warnings)
    paths = manifest.get("paths", {})
    event_log = resolve_manifest_path(base, paths.get("event_log", ""))
    events = load_sdk_event_jsonl(event_log) if event_log is not None else []
    counts = count_sdk_transcript_events(events)
    status_summary = load_optional_json_object(
        resolve_manifest_path(base, paths.get("status_summary", ""))
    )
    result_path = resolve_manifest_path(base, paths.get("result", ""))
    blocker_path = resolve_manifest_path(base, paths.get("blocker", ""))
    result_status = first_existing_final_status(result_path, blocker_path)
    latest_status = str(
        status_summary.get("latest_status")
        or manifest.get("state", {}).get("latest_status", "")
    )
    controller_health = classify_controller_health(latest_status, status_summary)
    return ProfileRunEvidence(
        run_id=str(manifest.get("run_id", "")),
        session_id=str(manifest.get("sdk", {}).get("session_id", "")),
        phase=str(manifest.get("phase", "")),
        selected_agent=resolved.selected_agent,
        custom_tools=tuple(resolved.custom_tool_names),
        task_overlays=tuple(resolved.task_overlay_names),
        event_count=len(events),
        assistant_messages=int(counts["assistant_message_count"]),
        user_messages=int(counts["user_message_count"]),
        tool_events=int(counts["tool_event_count"]),
        permission_events=int(counts["permission_event_count"]),
        custom_agent_events=int(counts["custom_agent_event_count"]),
        subagent_events=int(counts["subagent_event_count"]),
        agent_metadata_messages=int(counts["agent_metadata_message_count"]),
        latest_status=latest_status,
        controller_health=controller_health,
        result_status=result_status,
        result_path=display_manifest_path(paths.get("result", "")),
        blocker_path=display_manifest_path(paths.get("blocker", "")),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def load_optional_json_object(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    return value if isinstance(value, dict) else {}


def first_existing_final_status(*paths: Path | None) -> str:
    for path in paths:
        if path is None or not path.exists():
            continue
        status = extract_final_status(path.read_text(encoding="utf-8-sig"))
        if status:
            return status
    return ""


def extract_final_status(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("final status:"):
            return line.split(":", 1)[1].strip()
    return ""


def classify_controller_health(
    latest_status: str,
    status_summary: dict[str, Any],
) -> str:
    observed_errors = status_summary.get("observed_errors", [])
    if observed_errors:
        return "error"
    if latest_status in {"completion_candidate", "monitoring"}:
        return "healthy"
    if latest_status in {"quiet_stall", "nonprogress_stall"}:
        return "stalled"
    if latest_status == "blocked":
        return "blocked"
    return "unknown"


def display_manifest_path(value: Any) -> str:
    return str(value) if isinstance(value, str) else ""


def render_profile_run_evidence_markdown(evidence: ProfileRunEvidence) -> str:
    lines = [
        "# Copilot SDK Profile Run Evidence",
        "",
        f"- valid: `{evidence.ok}`",
        f"- run_id: `{evidence.run_id}`",
        f"- session_id: `{evidence.session_id}`",
        f"- phase: `{evidence.phase}`",
        f"- selected_agent: `{evidence.selected_agent}`",
        f"- task_overlays: {render_tuple(evidence.task_overlays)}",
        f"- custom_tools: {render_tuple(evidence.custom_tools)}",
        f"- latest_status: `{evidence.latest_status}`",
        f"- controller_health: `{evidence.controller_health}`",
        f"- result_status: `{evidence.result_status}`",
        f"- result_path: `{evidence.result_path}`",
        f"- blocker_path: `{evidence.blocker_path}`",
        "",
        "## Conversation Shape",
        "",
        f"- event_count: {evidence.event_count}",
        f"- user_messages: {evidence.user_messages}",
        f"- assistant_messages: {evidence.assistant_messages}",
        f"- tool_events: {evidence.tool_events}",
        f"- permission_events: {evidence.permission_events}",
        f"- custom_agent_events: {evidence.custom_agent_events}",
        f"- subagent_events: {evidence.subagent_events}",
        f"- agent_metadata_messages: {evidence.agent_metadata_messages}",
        "",
    ]
    if evidence.errors:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in evidence.errors)
        lines.append("")
    if evidence.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in evidence.warnings)
        lines.append("")
    return "\n".join(lines)


def render_tuple(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "(none)"
