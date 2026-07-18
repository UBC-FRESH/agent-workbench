"""Copilot child-task run manifest validation and review packet rendering."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values
from .heartbeat import load_heartbeat_jsonl, summarize_heartbeat_records


REQUIRED_RUN_FIELDS = (
    "run_id",
    "ticket_path",
    "child_issue",
    "expected_model",
    "permission_mode",
    "heartbeat_path",
    "result_path",
    "blocker_path",
    "archive_manifest_path",
    "token_ledger_path",
    "workspace_root",
)

RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{15,}$")


@dataclass(frozen=True)
class ControllerValidation:
    ok: bool
    errors: list[str]
    warnings: list[str]


def load_run_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("controller run manifest must be a JSON object")
    return data


def load_task_run_manifest(path: Path) -> dict[str, Any]:
    return load_run_manifest(path)


def validate_run_manifest(
    manifest: dict[str, Any],
    *,
    manifest_path: Path | None = None,
    require_existing_ticket: bool = True,
) -> ControllerValidation:
    errors: list[str] = []
    warnings: list[str] = []
    for field in REQUIRED_RUN_FIELDS:
        if field not in manifest:
            errors.append(f"missing required field: {field}")
        elif not isinstance(manifest[field], str):
            errors.append(f"{field} must be a string")

    run_id = str(manifest.get("run_id", ""))
    if run_id and not RUN_ID_PATTERN.match(run_id):
        errors.append("run_id must be at least 16 safe characters")

    workspace_root = Path(str(manifest.get("workspace_root", "")))
    if str(workspace_root) and not workspace_root.exists():
        errors.append(f"workspace_root does not exist: {workspace_root}")

    expected_model = str(manifest.get("expected_model", ""))
    if expected_model and "ollama" not in expected_model.lower():
        warnings.append(
            "expected_model does not explicitly identify the Ollama provider"
        )

    permission_mode = str(manifest.get("permission_mode", ""))
    if permission_mode not in ("autopilot", "bypass approvals", "default approvals"):
        errors.append(f"invalid permission_mode: {permission_mode}")

    if manifest.get("economics_claim") is True and not manifest.get(
        "budget_record_path"
    ):
        errors.append("economics_claim=true requires budget_record_path")

    base = manifest_path.parent if manifest_path is not None else Path(".")
    ticket_path = resolve_path(base, manifest.get("ticket_path"))
    if require_existing_ticket and ticket_path is not None and not ticket_path.exists():
        errors.append(f"ticket_path does not exist: {ticket_path}")

    if not str(manifest.get("prompt_marker", "")).strip():
        warnings.append("prompt_marker is empty; archive matching may be ambiguous")

    public_scan_manifest = dict(manifest)
    public_scan_manifest.pop("workspace_root", None)
    for finding in find_private_values(public_scan_manifest):
        errors.append(f"private-looking value detected: {finding}")

    return ControllerValidation(ok=not errors, errors=errors, warnings=warnings)


def validate_task_run_manifest(
    manifest: dict[str, Any],
    *,
    manifest_path: Path | None = None,
    require_existing_ticket: bool = True,
) -> ControllerValidation:
    return validate_run_manifest(
        manifest,
        manifest_path=manifest_path,
        require_existing_ticket=require_existing_ticket,
    )


def resolve_path(base: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return base / path


def build_launch_prompt(
    manifest: dict[str, Any],
    ticket_text: str | None = None,
    *,
    manifest_path: Path | None = None,
) -> str:
    if ticket_text is None:
        if manifest_path is None:
            raise ValueError("ticket_text or manifest_path is required")
        ticket_path = resolve_path(manifest_path.parent, manifest["ticket_path"])
        if ticket_path is None:
            raise ValueError("ticket_path is required")
        ticket_text = ticket_path.read_text(encoding="utf-8-sig")
    run_id = str(manifest.get("run_id", ""))
    expected_model = str(manifest.get("expected_model", ""))
    permission_mode = str(manifest.get("permission_mode", ""))
    result_path = str(manifest.get("result_path", ""))
    blocker_path = str(manifest.get("blocker_path", ""))
    heartbeat_path = str(manifest.get("heartbeat_path", ""))
    archive_path = str(manifest.get("archive_manifest_path", ""))
    return "\n".join(
        [
            f"Run id: {run_id}",
            "Execute the child-task ticket below exactly.",
            "",
            "Execution contract:",
            f"- Expected model evidence: `{expected_model}`.",
            f"- Expected permission mode: `{permission_mode}`.",
            f"- Write result file: `{result_path}`.",
            f"- Write blocker file if blocked: `{blocker_path}`.",
            f"- Append heartbeat records: `{heartbeat_path}`.",
            f"- Coordinator archive manifest target: `{archive_path}`.",
            "- Do not maximize or rearrange the VS Code UI.",
            "- Do not complete sibling tasks, parent closeout, PR merge, or issue closure.",
            "- Do not substitute a prose summary for files, commands, checks, or artifacts.",
            "",
            "Ticket:",
            "",
            ticket_text.strip(),
            "",
            "Stop when the assigned child task is complete or blocked.",
        ]
    )


def render_launch_command(manifest: dict[str, Any], prompt_path: Path) -> str:
    workspace_root = str(manifest.get("workspace_root", "."))
    return (
        "code chat --reuse-window --mode agent "
        f"--add-file {prompt_path.as_posix()} {workspace_root}"
    )


def generate_prompt_file(manifest_path: Path, output: Path) -> dict[str, Any]:
    manifest = load_run_manifest(manifest_path)
    validation = validate_run_manifest(manifest, manifest_path=manifest_path)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))
    ticket_path = resolve_path(manifest_path.parent, manifest["ticket_path"])
    if ticket_path is None:
        raise ValueError("ticket_path is required")
    ticket_text = ticket_path.read_text(encoding="utf-8-sig")
    prompt = build_launch_prompt(manifest, ticket_text)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(prompt + "\n", encoding="utf-8")
    return {
        "prompt_path": str(output),
        "launch_command": render_launch_command(manifest, output),
        "warnings": validation.warnings,
    }


def render_review_packet(
    manifest_or_path: dict[str, Any] | Path,
    output: Path | None = None,
    *,
    heartbeat_summary: dict[str, object] | None = None,
    archive_manifest: dict[str, object] | None = None,
    task_result: dict[str, object] | None = None,
) -> tuple[dict[str, Any], str] | dict[str, Any]:
    if isinstance(manifest_or_path, dict):
        packet = render_review_packet_from_data(
            manifest_or_path,
            heartbeat_summary=heartbeat_summary,
            archive_manifest=archive_manifest,
            task_result=task_result,
        )
        return packet, render_review_markdown(packet)
    if output is None:
        raise ValueError("output is required when rendering from a manifest path")
    packet = render_review_packet_from_path(manifest_or_path, output)
    return packet


def render_review_packet_from_path(manifest_path: Path, output: Path) -> dict[str, Any]:
    manifest = load_run_manifest(manifest_path)
    validation = validate_run_manifest(
        manifest,
        manifest_path=manifest_path,
        require_existing_ticket=False,
    )
    base = manifest_path.parent
    heartbeat_summary = read_heartbeat_summary(base, manifest)
    result_text = read_optional_text(base, manifest.get("result_path"))
    blocker_text = read_optional_text(base, manifest.get("blocker_path"))
    archive = read_optional_json(base, manifest.get("archive_manifest_path"))
    decision = recommend_decision(
        validation, heartbeat_summary, result_text, blocker_text, archive
    )
    packet = {
        "run_id": manifest.get("run_id", ""),
        "child_issue": manifest.get("child_issue", ""),
        "validation_ok": validation.ok,
        "validation_errors": validation.errors,
        "validation_warnings": validation.warnings,
        "heartbeat_summary": heartbeat_summary,
        "result_present": bool(result_text),
        "blocker_present": bool(blocker_text),
        "archive_present": bool(archive),
        "archive_metrics": archive_metrics(archive),
        "recommended_decision": decision,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_review_markdown(packet), encoding="utf-8")
    return packet


def render_review_packet_from_data(
    manifest: dict[str, Any],
    *,
    heartbeat_summary: dict[str, object] | None = None,
    archive_manifest: dict[str, object] | None = None,
    task_result: dict[str, object] | None = None,
) -> dict[str, Any]:
    validation = validate_run_manifest(manifest, require_existing_ticket=False)
    heartbeat = dict(heartbeat_summary or {})
    archive = dict(archive_manifest or {})
    result_text = json.dumps(task_result) if task_result else ""
    blocker_text = ""
    decision = recommend_decision(
        validation, heartbeat, result_text, blocker_text, archive
    )
    return {
        "run_id": manifest.get("run_id", ""),
        "child_issue": manifest.get("child_issue", ""),
        "validation_ok": validation.ok,
        "validation_errors": validation.errors,
        "validation_warnings": validation.warnings,
        "heartbeat_summary": heartbeat,
        "result_present": bool(task_result),
        "blocker_present": False,
        "archive_present": bool(archive),
        "archive_metrics": archive_metrics(archive),
        "recommended_decision": decision,
    }


def read_heartbeat_summary(base: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    heartbeat_path = resolve_path(base, manifest.get("heartbeat_path"))
    if heartbeat_path is None or not heartbeat_path.exists():
        return {
            "present": False,
            "validation_ok": False,
            "validation_errors": ["missing heartbeat"],
        }
    records = load_heartbeat_jsonl(heartbeat_path)
    summary = summarize_heartbeat_records(records)
    summary["present"] = True
    return summary


def read_optional_text(base: Path, value: object) -> str:
    path = resolve_path(base, value)
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig")


def read_optional_json(base: Path, value: object) -> dict[str, Any]:
    path = resolve_path(base, value)
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"archive manifest must be a JSON object: {path}")
    return data


def archive_metrics(archive: dict[str, Any]) -> dict[str, Any]:
    if not archive:
        return {}
    return {
        "session_id": archive.get("session_id", ""),
        "model_ids_detected": archive.get("model_ids_detected", []),
        "permission_levels_detected": archive.get("permission_levels_detected", []),
        "user_message_count": archive.get("user_message_count", 0),
        "assistant_message_count": archive.get("assistant_message_count_with_text", 0),
        "tool_request_count": archive.get("tool_request_count", 0),
        "keep_going_count": len(archive.get("keep_going_user_messages", [])),
        "stall_nudge_count": len(archive.get("stall_nudge_user_messages", [])),
    }


def recommend_decision(
    validation: ControllerValidation,
    heartbeat_summary: dict[str, Any],
    result_text: str,
    blocker_text: str,
    archive: dict[str, Any],
) -> str:
    if not validation.ok:
        return "reject"
    if blocker_text:
        return "escalate"
    if not result_text:
        return "repair"
    if not heartbeat_summary.get("validation_ok"):
        return "repair"
    if not archive:
        return "repair"
    if heartbeat_summary.get("repeated_nudge_signal"):
        return "review"
    return "accept"


def render_review_markdown(packet: dict[str, Any]) -> str:
    archive = packet.get("archive_metrics", {})
    heartbeat = packet.get("heartbeat_summary", {})
    lines = [
        "# Copilot Task Review Packet",
        "",
        f"- run_id: `{packet.get('run_id', '')}`",
        f"- child_issue: `{packet.get('child_issue', '')}`",
        f"- validation_ok: `{packet.get('validation_ok', False)}`",
        f"- result_present: `{packet.get('result_present', False)}`",
        f"- blocker_present: `{packet.get('blocker_present', False)}`",
        f"- archive_present: `{packet.get('archive_present', False)}`",
        f"- recommended_decision: `{packet.get('recommended_decision', '')}`",
        "",
        "## Heartbeat",
        "",
        f"- present: `{heartbeat.get('present', False)}`",
        f"- last_status: `{heartbeat.get('last_status', '')}`",
        f"- stale: `{heartbeat.get('is_stale', False)}`",
        f"- stalled: `{heartbeat.get('stalled', False)}`",
        f"- nudge_count: {heartbeat.get('nudge_count', 0)}",
        f"- stall_count: {heartbeat.get('stall_count', 0)}",
        "",
        "## Archive Metrics",
        "",
        f"- session_id: `{archive.get('session_id', '')}`",
        f"- user_message_count: {archive.get('user_message_count', 0)}",
        f"- assistant_message_count: {archive.get('assistant_message_count', 0)}",
        f"- tool_request_count: {archive.get('tool_request_count', 0)}",
        f"- keep_going_count: {archive.get('keep_going_count', 0)}",
        f"- stall_nudge_count: {archive.get('stall_nudge_count', 0)}",
        "",
    ]
    errors = packet.get("validation_errors", [])
    if errors:
        lines.extend(["## Validation Errors", ""])
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    return "\n".join(lines)
