"""Heartbeat validation, stale-run summaries, and nudge suggestions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import find_private_values


REQUIRED_HEARTBEAT_FIELDS = (
    "timestamp",
    "checklist_item",
    "status",
    "action",
    "artifact_path",
    "command_summary",
    "next_intended_action",
)

ALLOWED_HEARTBEAT_STATUSES = (
    "thinking",
    "running_command",
    "tool_blocked",
    "no_progress",
    "completed",
    "blocked",
)

TERMINAL_STATUSES = ("completed", "blocked")


@dataclass(frozen=True)
class HeartbeatValidation:
    ok: bool
    errors: list[str]
    records: list[dict[str, Any]] = dataclass_field(default_factory=list)


def load_heartbeat_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(
                f"line {line_number}: heartbeat record must be a JSON object"
            )
        records.append(value)
    return records


def validate_heartbeat_records(records: list[dict[str, Any]]) -> HeartbeatValidation:
    errors: list[str] = []
    if not records:
        errors.append("heartbeat file contains no records")
    for index, record in enumerate(records, 1):
        for field in REQUIRED_HEARTBEAT_FIELDS:
            if field not in record:
                errors.append(f"record {index}: missing required field: {field}")
            elif not isinstance(record[field], str):
                errors.append(f"record {index}: {field} must be a string")
        status = record.get("status")
        if isinstance(status, str) and status not in ALLOWED_HEARTBEAT_STATUSES:
            errors.append(f"record {index}: invalid status: {status}")
        timestamp = record.get("timestamp")
        if isinstance(timestamp, str):
            try:
                parse_timestamp(timestamp)
            except ValueError as exc:
                errors.append(f"record {index}: invalid timestamp: {exc}")
        for finding in find_private_values(record):
            errors.append(f"record {index}: private-looking value detected: {finding}")
    return HeartbeatValidation(ok=not errors, errors=errors, records=records)


def summarize_heartbeat_records(
    records: list[dict[str, Any]],
    *,
    stale_after_seconds: int = 600,
    now: datetime | None = None,
) -> dict[str, Any]:
    validation = validate_heartbeat_records(records)
    now = now or datetime.now(timezone.utc)
    status_counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status", ""))
        status_counts[status] = status_counts.get(status, 0) + 1

    last_record = records[-1] if records else {}
    last_timestamp = None
    age_seconds = None
    is_stale = False
    if isinstance(last_record.get("timestamp"), str):
        last_timestamp = parse_timestamp(str(last_record["timestamp"]))
        age_seconds = max(0, int((now - last_timestamp).total_seconds()))
        is_stale = age_seconds > stale_after_seconds

    last_status = (
        str(last_record.get("status", "missing")) if last_record else "missing"
    )
    terminal = last_status in TERMINAL_STATUSES
    stalled = not terminal and (
        is_stale or last_status in ("no_progress", "tool_blocked") or not validation.ok
    )

    nudge_count = count_nudges(records)
    stall_count = int(status_counts.get("no_progress", 0)) + (1 if is_stale else 0)
    recommended_nudge_type = recommend_nudge_type(last_status, stalled)

    return {
        "record_count": len(records),
        "validation_ok": validation.ok,
        "validation_errors": validation.errors,
        "status_counts": status_counts,
        "last_status": last_status,
        "latest_status": last_status,
        "last_checklist_item": last_record.get("checklist_item", ""),
        "latest_checklist_item": last_record.get("checklist_item", ""),
        "last_action": last_record.get("action", ""),
        "latest_action": last_record.get("action", ""),
        "last_next_intended_action": last_record.get("next_intended_action", ""),
        "latest_next_intended_action": last_record.get("next_intended_action", ""),
        "last_artifact_path": last_record.get("artifact_path", ""),
        "latest_artifact_path": last_record.get("artifact_path", ""),
        "last_command_summary": last_record.get("command_summary", ""),
        "age_seconds": age_seconds,
        "stale_after_seconds": stale_after_seconds,
        "is_stale": is_stale,
        "stale": is_stale,
        "is_terminal": terminal,
        "stalled": stalled,
        "nudge_count": nudge_count,
        "stall_count": stall_count,
        "recommended_nudge_type": recommended_nudge_type,
        "stop_rule_triggered": nudge_count >= 2,
        "recommended_coordinator_action": recommend_action(last_status, stalled),
    }


def parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def recommend_action(last_status: str, stalled: bool) -> str:
    if last_status == "completed":
        return "review-result-and-archive"
    if last_status == "blocked":
        return "inspect-blocker"
    if last_status == "tool_blocked":
        return "send-write-blocker-nudge"
    if last_status == "no_progress":
        return "send-stop-summarizing-nudge"
    if stalled:
        return "inspect-filesystem-then-send-continue-nudge"
    return "wait"


def recommend_nudge_type(last_status: str, stalled: bool) -> str:
    if last_status == "completed":
        return "reconcile-checklist"
    if last_status in ("blocked", "tool_blocked"):
        return "write-blocker"
    if last_status == "no_progress" or stalled:
        return "stop-summarizing"
    if last_status == "thinking":
        return "continue-next-subtask"
    if last_status == "running_command":
        return "none"
    return "fix-shell-context"


def count_nudges(records: list[dict[str, Any]]) -> int:
    count = 0
    for record in records:
        nudge = record.get("nudge_type") or record.get("nudge")
        if isinstance(nudge, str) and nudge.strip():
            count += 1
    return count


def suggest_nudge(summary: dict[str, Any]) -> str:
    if summary.get("stop_rule_triggered"):
        return (
            "Stop this delegated lane and write the blocker file. The repeated-nudge "
            "stop rule has triggered; do not continue work until the coordinator "
            "reviews the heartbeat, result, blocker, archive, and token/cash ledger."
        )
    action = str(summary.get("recommended_coordinator_action", "wait"))
    checklist = str(summary.get("last_checklist_item", "the current checklist item"))
    next_action = str(
        summary.get("last_next_intended_action", "the next bounded action")
    )
    if action == "review-result-and-archive":
        return "No nudge needed. Review the result file and archive evidence."
    if action == "inspect-blocker":
        return "No nudge yet. Inspect the blocker file and decide repair, escalation, or abandon."
    if action == "send-write-blocker-nudge":
        return (
            "Write the blocker file now. Include the exact failed command, exact error text, "
            "current checklist item, and the next action you cannot complete."
        )
    if action == "send-stop-summarizing-nudge":
        return (
            "Stop summarizing progress. Continue the assigned child task from "
            f"`{checklist}` by doing exactly this next bounded action: {next_action}. "
            "If you cannot do that, write the blocker file."
        )
    if action == "inspect-filesystem-then-send-continue-nudge":
        return (
            "Continue the assigned child task only. Append a heartbeat record, then proceed "
            f"from `{checklist}` to the next bounded action: {next_action}. "
            "Do not summarize completion unless the result file is written."
        )
    return (
        "No nudge needed. Continue waiting for the next heartbeat or terminal result."
    )


def render_nudge(summary: dict[str, Any]) -> str:
    return (
        "# Delegated Run Nudge\n\n"
        f"- nudge_type: `{summary.get('recommended_nudge_type', '')}`\n"
        f"- latest_status: `{summary.get('latest_status', summary.get('last_status', ''))}`\n"
        "- latest_checklist_item: "
        f"`{summary.get('latest_checklist_item', summary.get('last_checklist_item', ''))}`\n"
        f"- stale: `{summary.get('stale', summary.get('is_stale', False))}`\n\n"
        "## Message\n\n"
        f"{suggest_nudge(summary)}\n"
    )


def render_heartbeat_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# Heartbeat Summary",
        "",
        f"- records: {summary.get('record_count', 0)}",
        f"- validation_ok: `{summary.get('validation_ok', False)}`",
        f"- last_status: `{summary.get('last_status', '')}`",
        f"- stale: `{summary.get('is_stale', False)}`",
        f"- stalled: `{summary.get('stalled', False)}`",
        f"- recommended_action: `{summary.get('recommended_coordinator_action', '')}`",
        "",
        "## Last Record",
        "",
        f"- checklist item: {summary.get('last_checklist_item', '')}",
        f"- action: {summary.get('last_action', '')}",
        f"- next intended action: {summary.get('last_next_intended_action', '')}",
        f"- artifact path: `{summary.get('last_artifact_path', '')}`",
        f"- command summary: `{summary.get('last_command_summary', '')}`",
        "",
        "## Nudge Suggestion",
        "",
        suggest_nudge(summary),
        "",
    ]
    errors = summary.get("validation_errors", [])
    if errors:
        lines.extend(["## Validation Errors", ""])
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    return "\n".join(lines)
