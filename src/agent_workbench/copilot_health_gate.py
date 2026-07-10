"""Controller/session health gates for SDK-owned Copilot runs."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .copilot_profile_runs import classify_controller_health, load_optional_json_object
from .copilot_sdk_bridge import (
    event_errors,
    load_sdk_event_jsonl,
    load_sdk_session_manifest,
    resolve_manifest_path,
    validate_sdk_session_manifest,
)


@dataclass(frozen=True)
class HealthGateRow:
    manifest_path: str
    run_id: str
    phase: str
    latest_status: str
    controller_health: str
    event_count: int
    status_summary_present: bool
    event_log_present: bool
    manifest_valid: bool
    validation_errors: tuple[str, ...]
    validation_warnings: tuple[str, ...]
    error_signatures: tuple[str, ...]
    decision: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class HealthGateReport:
    rows: tuple[HealthGateRow, ...]
    required_count: int | None
    go: bool
    decision: str
    reasons: tuple[str, ...]
    controller_health: dict[str, int]
    row_decisions: dict[str, int]
    repeated_error_signatures: dict[str, int]


def build_health_gate_report(
    manifest_paths: list[Path],
    *,
    required_count: int | None = None,
) -> HealthGateReport:
    rows = tuple(build_health_gate_row(path) for path in manifest_paths)
    signature_counts = count_row_error_signatures(rows)
    repeated = {
        signature: count
        for signature, count in sorted(signature_counts.items())
        if count > 1
    }
    reasons: list[str] = []
    if required_count is not None and len(rows) < required_count:
        reasons.append(f"manifest_count_below_required:{len(rows)}<{required_count}")
    if not rows:
        reasons.append("no_manifests")
    for row in rows:
        reasons.extend(f"{row.run_id}:{reason}" for reason in row.reasons)
    for signature, count in repeated.items():
        reasons.append(f"repeated_error_signature:{signature}:{count}")
    go = not reasons
    return HealthGateReport(
        rows=rows,
        required_count=required_count,
        go=go,
        decision="go" if go else "no-go",
        reasons=tuple(reasons),
        controller_health=dict(Counter(row.controller_health for row in rows)),
        row_decisions=dict(Counter(row.decision for row in rows)),
        repeated_error_signatures=repeated,
    )


def build_health_gate_row(manifest_path: Path) -> HealthGateRow:
    try:
        manifest = load_sdk_session_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return HealthGateRow(
            manifest_path=public_manifest_path(manifest_path),
            run_id=manifest_path.stem,
            phase="",
            latest_status="",
            controller_health="unknown",
            event_count=0,
            status_summary_present=False,
            event_log_present=False,
            manifest_valid=False,
            validation_errors=("manifest_unreadable",),
            validation_warnings=(),
            error_signatures=(),
            decision="block",
            reasons=("manifest_unreadable",),
        )

    validation = validate_sdk_session_manifest(
        manifest,
        manifest_path=manifest_path,
    )
    base = manifest_path.parent
    paths = manifest.get("paths", {})
    if not isinstance(paths, dict):
        paths = {}
    status_path = resolve_manifest_path(base, paths.get("status_summary", ""))
    event_log_path = resolve_manifest_path(base, paths.get("event_log", ""))
    status_summary = load_optional_json_object(status_path)
    events = load_sdk_event_jsonl(event_log_path) if event_log_path is not None else []
    latest_status = str(
        status_summary.get("latest_status")
        or manifest.get("state", {}).get("latest_status", "")
    )
    controller_health = classify_controller_health(latest_status, status_summary)
    signatures = normalize_error_signatures(
        list(status_summary.get("observed_errors", [])) + event_errors(events)
    )
    reasons = row_block_reasons(
        manifest_valid=validation.ok,
        validation_errors=validation.errors,
        status_summary_present=status_path is not None and status_path.exists(),
        event_log_present=event_log_path is not None and event_log_path.exists(),
        controller_health=controller_health,
        error_signatures=signatures,
    )
    return HealthGateRow(
        manifest_path=public_manifest_path(manifest_path),
        run_id=str(manifest.get("run_id", "")),
        phase=str(manifest.get("phase", "")),
        latest_status=latest_status,
        controller_health=controller_health,
        event_count=len(events),
        status_summary_present=status_path is not None and status_path.exists(),
        event_log_present=event_log_path is not None and event_log_path.exists(),
        manifest_valid=validation.ok,
        validation_errors=tuple(validation.errors),
        validation_warnings=tuple(validation.warnings),
        error_signatures=tuple(signatures),
        decision="go" if not reasons else "block",
        reasons=tuple(reasons),
    )


def row_block_reasons(
    *,
    manifest_valid: bool,
    validation_errors: list[str],
    status_summary_present: bool,
    event_log_present: bool,
    controller_health: str,
    error_signatures: tuple[str, ...],
) -> list[str]:
    reasons: list[str] = []
    if not manifest_valid:
        reasons.append("manifest_invalid")
    if validation_errors:
        reasons.append("manifest_validation_errors")
    if not status_summary_present:
        reasons.append("status_summary_missing")
    if not event_log_present:
        reasons.append("event_log_missing")
    if controller_health == "error":
        reasons.append("controller_error")
    elif controller_health != "healthy":
        reasons.append(f"controller_{controller_health or 'unknown'}")
    if error_signatures:
        reasons.append("controller_error_signature_present")
    return reasons


def normalize_error_signatures(errors: list[Any]) -> tuple[str, ...]:
    signatures = sorted(
        {
            signature
            for error in errors
            for signature in normalize_error_signature(error)
            if signature
        }
    )
    return tuple(signatures)


def normalize_error_signature(error: Any) -> tuple[str, ...]:
    if isinstance(error, dict):
        nested = error.get("error")
        if isinstance(nested, dict):
            code = nested.get("code")
            if code:
                return (sanitize_signature(str(code)),)
            message = nested.get("message")
            if message:
                return (message_signature(str(message)),)
        code = error.get("code")
        if code:
            return (sanitize_signature(str(code)),)
        message = error.get("message") or error.get("error_message")
        if message:
            return (message_signature(str(message)),)
        return ("dict_error",)
    text = str(error)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return (message_signature(text),)
    return normalize_error_signature(parsed)


def message_signature(message: str) -> str:
    lowered = message.lower()
    if "quota" in lowered:
        return "quota_exceeded"
    if "timeout" in lowered:
        return "timeout"
    if "524" in lowered:
        return "provider_524"
    return sanitize_signature(strip_request_ids(lowered))[:80] or "error"


def strip_request_ids(message: str) -> str:
    message = re.sub(r"\(request id:[^)]+\)", "", message, flags=re.IGNORECASE)
    return re.sub(r"\b[a-f0-9]{8,}\b", "", message, flags=re.IGNORECASE)


def sanitize_signature(value: str) -> str:
    signature = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return re.sub(r"_+", "_", signature)


def count_row_error_signatures(rows: tuple[HealthGateRow, ...]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(set(row.error_signatures))
    return dict(counts)


def health_gate_report_to_jsonable(report: HealthGateReport) -> dict[str, Any]:
    return {
        "valid": report.go,
        "decision": report.decision,
        "required_count": report.required_count,
        "manifest_count": len(report.rows),
        "reasons": list(report.reasons),
        "controller_health": report.controller_health,
        "row_decisions": report.row_decisions,
        "repeated_error_signatures": report.repeated_error_signatures,
        "rows": [
            {
                "manifest_path": row.manifest_path,
                "run_id": row.run_id,
                "phase": row.phase,
                "latest_status": row.latest_status,
                "controller_health": row.controller_health,
                "event_count": row.event_count,
                "status_summary_present": row.status_summary_present,
                "event_log_present": row.event_log_present,
                "manifest_valid": row.manifest_valid,
                "validation_error_count": len(row.validation_errors),
                "validation_warning_count": len(row.validation_warnings),
                "error_signatures": list(row.error_signatures),
                "decision": row.decision,
                "reasons": list(row.reasons),
            }
            for row in report.rows
        ],
    }


def render_health_gate_markdown(report: HealthGateReport) -> str:
    lines = [
        "# Copilot SDK Controller/Session Health Gate",
        "",
        f"- decision: `{report.decision}`",
        f"- valid: `{report.go}`",
        f"- manifest_count: {len(report.rows)}",
        f"- required_count: {report.required_count if report.required_count is not None else '(none)'}",
        "",
        "## Controller Health",
        "",
        markdown_count_table(report.controller_health),
        "",
        "## Row Decisions",
        "",
        markdown_count_table(report.row_decisions),
        "",
        "## Repeated Error Signatures",
        "",
        markdown_count_table(report.repeated_error_signatures),
        "",
        "## Reasons",
        "",
    ]
    if report.reasons:
        lines.extend(f"- `{reason}`" for reason in report.reasons)
    else:
        lines.append("- `(none)`")
    lines.extend(["", "## Rows", ""])
    lines.append(
        "| run_id | phase | status | controller_health | events | decision | signatures |"
    )
    lines.append("| --- | --- | --- | --- | ---: | --- | --- |")
    for row in report.rows:
        signatures = ", ".join(f"`{signature}`" for signature in row.error_signatures)
        lines.append(
            "| {run_id} | {phase} | {status} | {health} | {events} | {decision} | {signatures} |".format(
                run_id=escape_table(row.run_id),
                phase=escape_table(row.phase),
                status=escape_table(row.latest_status),
                health=escape_table(row.controller_health),
                events=row.event_count,
                decision=escape_table(row.decision),
                signatures=signatures or "(none)",
            )
        )
    lines.append("")
    return "\n".join(lines)


def markdown_count_table(counts: dict[str, int]) -> str:
    if not counts:
        return "| value | count |\n| --- | ---: |\n| (none) | 0 |"
    lines = ["| value | count |", "| --- | ---: |"]
    for key, count in sorted(counts.items()):
        lines.append(f"| `{escape_table(str(key))}` | {count} |")
    return "\n".join(lines)


def escape_table(value: str) -> str:
    return value.replace("|", "\\|")


def public_manifest_path(path: Path) -> str:
    if path.is_absolute():
        return path.name
    return path.as_posix()
