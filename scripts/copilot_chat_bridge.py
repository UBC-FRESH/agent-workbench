"""Local Copilot Chat bridge v0 harness.

This script is intentionally repo-local tooling, not an installed package or
stable CLI. It launches a VS Code Copilot Chat worker ticket through stdin,
finds the persisted VS Code chat session by marker, and writes a supervisor
verification report from observed session evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote


DEFAULT_PROMPT = (
    "Execute the worker ticket provided on stdin exactly. "
    "Treat stdin as the authoritative ticket."
)


@dataclass
class SessionEvidence:
    session_path: Path | None = None
    transcript_path: Path | None = None
    resolved_model: str | None = None
    permission_levels: list[str] = field(default_factory=list)
    final_marker_present: bool = False
    completed: bool = False
    terminal_commands: list[str] = field(default_factory=list)
    file_paths: list[str] = field(default_factory=list)
    tool_names: list[str] = field(default_factory=list)
    raw_excerpt: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch and verify a Copilot Chat worker ticket."
    )
    parser.add_argument(
        "--ticket", required=True, help="Path to the worker ticket Markdown file."
    )
    parser.add_argument(
        "--marker", required=True, help="Unique marker expected in the session."
    )
    parser.add_argument(
        "--workspace-root", default=".", help="Repository root for the worker launch."
    )
    parser.add_argument(
        "--report", help="Supervisor report path. Defaults beside the ticket."
    )
    parser.add_argument(
        "--timeout-seconds", type=int, default=240, help="Session polling timeout."
    )
    parser.add_argument(
        "--poll-seconds", type=float, default=3.0, help="Polling interval."
    )
    parser.add_argument(
        "--code-command", default="code", help="VS Code command executable."
    )
    parser.add_argument(
        "--mode", default="agent", help="VS Code chat mode or custom agent identifier."
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="One-line prompt for code chat."
    )
    parser.add_argument(
        "--expected-model",
        help="Optional required resolved model id for benchmark runs.",
    )
    parser.add_argument(
        "--maximize",
        action="store_true",
        help="Maximize the VS Code chat pane on launch.",
    )
    parser.add_argument(
        "--skip-open-workspace",
        action="store_true",
        help="Do not open --workspace-root in VS Code before launching chat.",
    )
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Skip launch and only parse existing sessions.",
    )
    return parser.parse_args()


def appdata_workspace_storage() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError(
            "APPDATA is not set; VS Code workspace storage cannot be located."
        )
    return Path(appdata) / "Code" / "User" / "workspaceStorage"


def launch_code_chat(args: argparse.Namespace, ticket_text: str) -> None:
    code_command = resolve_code_command(args.code_command)
    workspace_root = str(Path(args.workspace_root).resolve())
    if not args.skip_open_workspace:
        workspace_completed = subprocess.run(
            [code_command, "--reuse-window", workspace_root],
            text=True,
            encoding="utf-8",
            check=False,
        )
        if workspace_completed.returncode != 0:
            raise RuntimeError(
                "code workspace open failed with exit code "
                f"{workspace_completed.returncode}"
            )
        time.sleep(2.0)
    command = [
        code_command,
        "chat",
        "--reuse-window",
        "--mode",
        args.mode,
        args.prompt,
        "-",
    ]
    if args.maximize:
        command.insert(3, "--maximize")
    completed = subprocess.run(
        command,
        input=ticket_text,
        text=True,
        encoding="utf-8",
        cwd=args.workspace_root,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"code chat failed with exit code {completed.returncode}")


def resolve_code_command(code_command: str) -> str:
    resolved = shutil.which(code_command)
    if resolved:
        return resolved
    if os.name == "nt" and code_command.lower() == "code":
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            candidate = (
                Path(local_appdata)
                / "Programs"
                / "Microsoft VS Code"
                / "bin"
                / "code.cmd"
            )
            if candidate.exists():
                return str(candidate)
    return code_command


def iter_candidate_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    patterns = [
        "*/chatSessions/*.jsonl",
        "*/GitHub.copilot-chat/transcripts/*.jsonl",
    ]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(root.glob(pattern))
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def find_session_files(
    marker: str, timeout: int, poll: float
) -> tuple[Path | None, Path | None]:
    storage_root = appdata_workspace_storage()
    deadline = time.time() + timeout
    session_path: Path | None = None
    transcript_path: Path | None = None
    while time.time() <= deadline:
        for path in iter_candidate_files(storage_root):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if marker not in text:
                continue
            normalized = str(path).replace("\\", "/")
            if "/chatSessions/" in normalized:
                session_path = path
            elif "/GitHub.copilot-chat/transcripts/" in normalized:
                transcript_path = path
        if session_path:
            text = session_path.read_text(encoding="utf-8", errors="replace")
            if '"modelState":{"value":1' in text or f"{marker} done" in text:
                return session_path, transcript_path
        time.sleep(poll)
    return session_path, transcript_path


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def load_evidence(
    marker: str, session_path: Path | None, transcript_path: Path | None
) -> SessionEvidence:
    evidence = SessionEvidence(
        session_path=session_path, transcript_path=transcript_path
    )
    if not session_path:
        return evidence
    text = session_path.read_text(encoding="utf-8", errors="replace")
    evidence.raw_excerpt = text[:2000]
    resolved = re.findall(r'"resolvedModel":"([^"]+)"', text)
    model_ids = re.findall(r'"modelId":"([^"]+)"', text)
    model_values = resolved or model_ids
    evidence.resolved_model = (
        normalize_model_id(model_values[-1]) if model_values else None
    )
    evidence.permission_levels = sorted(
        set(re.findall(r'"permissionLevel":"([^"]+)"', text))
    )
    evidence.completed = '"modelState":{"value":1' in text or f"{marker} done" in text
    evidence.final_marker_present = f"{marker} done" in text
    evidence.terminal_commands = re.findall(r'"original":"((?:\\.|[^"])*)"', text)
    evidence.file_paths = unique(extract_file_edit_paths(text))
    evidence.tool_names = unique(
        name
        for name in re.findall(r'"name":"([^"]+)"', text)
        if is_relevant_tool_name(name)
    )
    return evidence


def is_relevant_tool_name(name: str) -> bool:
    if name in {
        "read_file",
        "run_in_terminal",
        "create_file",
        "replace_string_in_file",
    }:
        return True
    lowered = name.lower()
    return "subagent" in lowered or lowered in {"agent", "agent/runsubagent"}


def unescape_json_text(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value.replace("\\\\", "\\")


def normalize_model_id(model_id: str) -> str:
    return model_id.removeprefix("ollama-models/Ollama/")


def extract_file_edit_paths(text: str) -> list[str]:
    paths: list[str] = []
    for name in ("create_file", "replace_string_in_file"):
        pattern = rf'"name":"{name}","arguments":"((?:\\.|[^"])*)"'
        for argument_blob in re.findall(pattern, text):
            decoded_blob = unescape_json_text(argument_blob)
            try:
                arguments = json.loads(decoded_blob)
            except json.JSONDecodeError:
                continue
            file_path = arguments.get("filePath")
            if isinstance(file_path, str):
                paths.append(file_path)
    return paths


def section_text(ticket: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)"
    match = re.search(pattern, ticket, flags=re.MULTILINE)
    return match.group(1) if match else ""


def extract_expected_commands(ticket: str) -> list[str]:
    commands: list[str] = []
    for heading in (
        "Required Commands",
        "Exact Materializer Command",
        "Graph Execution Requirements",
        "Required Graph Report",
    ):
        commands.extend(extract_fenced_commands(section_text(ticket, heading)))
    return unique(commands)


def extract_fenced_commands(section: str) -> list[str]:
    commands: list[str] = []
    for language, block in re.findall(r"```([A-Za-z0-9_-]*)\n([\s\S]*?)```", section):
        if language.casefold() not in {"", "powershell", "pwsh", "bash", "sh", "shell"}:
            continue
        for line in block.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
    return commands


def extract_allowed_files(ticket: str) -> list[str]:
    runtime_path_pattern = (
        r"`?(runtime[/\\](?:agent_jobs|document_library)[/\\][^`\s]+\.(?:md|json))`?"
    )
    read_paths = set(
        re.findall(runtime_path_pattern, section_text(ticket, "Required Reads"))
    )
    output_sections = "\n".join(
        section_text(ticket, heading)
        for heading in (
            "Required Output File",
            "Required Output Files",
            "Allowed Actions",
            "Workspace",
        )
    )
    output_paths = {
        path.replace("\\", "/")
        for path in re.findall(runtime_path_pattern, output_sections)
    }
    all_paths = re.findall(runtime_path_pattern, ticket)
    read_paths = {path.replace("\\", "/") for path in read_paths}
    all_paths = [path.replace("\\", "/") for path in all_paths]
    return unique(
        [path for path in all_paths if path in output_paths or path not in read_paths]
    )


def extract_required_json_fields(ticket: str) -> list[str]:
    fields_section = section_text(ticket, "Required Report JSON Fields")
    fields: list[str] = []
    for value in re.findall(r"`([^`]+)`", fields_section):
        stripped = value.strip()
        if stripped:
            fields.append(stripped)
    return unique(fields)


def json_field_present(data: object, dotted_path: str) -> bool:
    value = data
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return False
        value = value[part]
    return value not in (None, "")


def check_required_json_fields(
    workspace_root: Path,
    allowed_files: list[str],
    required_fields: list[str],
) -> list[str]:
    if not required_fields:
        return []
    report_paths = [path for path in allowed_files if path.endswith(".json")]
    if not report_paths:
        return [
            f"{field} (no allowed JSON report file found)" for field in required_fields
        ]
    report_path = workspace_root / report_paths[0]
    try:
        data = json.loads(report_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return [
            f"{field} (cannot read JSON report: {exc})" for field in required_fields
        ]
    return [field for field in required_fields if not json_field_present(data, field)]


def normalize_command(command: str) -> str:
    # Commands come from two surfaces:
    # - ticket Markdown, where PowerShell paths use literal backslashes; and
    # - VS Code JSON session text, where backslashes may already be escaped.
    #
    # Do not use ``unicode_escape`` here: Windows paths such as
    # ``runtime\agent_jobs`` contain ``\a``, which becomes a bell character and
    # causes false command mismatches.
    normalized = (
        command.replace("\\\\", "\\").replace('\\"', '"').replace("\\'", "'").strip()
    )
    normalized = re.sub(
        r"^(?:cd|Set-Location)\s+[A-Za-z]:\\[^\n;]+;\s*",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r'^\$env:PYTHONPATH\s*=\s*["\'][^"\']+["\'];\s*',
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(r'"([^"\s]+)"', r"\1", normalized)
    normalized = re.sub(r"'([^'\s]+)'", r"\1", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def normalize_command_for_comparison(command: str, workspace_root: Path) -> str:
    normalized = normalize_command(command)
    root_backslash = str(workspace_root.resolve()).rstrip("\\/")
    root_slash = root_backslash.replace("\\", "/")
    for root in (root_backslash, root_slash):
        normalized = re.sub(
            re.escape(root) + r"[/\\]",
            "",
            normalized,
            flags=re.IGNORECASE,
        )
    normalized = normalized.replace("/", "\\")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def command_matches(expected: str, observed: str) -> bool:
    if expected == observed:
        return True
    # VS Code/Copilot may choose repo-relative paths even when a ticket names an
    # absolute script path. After workspace-root stripping, those commands are
    # equivalent when the executable and full argument list match.
    return expected.casefold() == observed.casefold()


def is_benign_extra_command(command: str) -> bool:
    lowered = command.casefold()
    stripped = lowered.lstrip("() ")
    if not stripped.startswith("test-path ") and "test-path " not in stripped:
        return False
    return any(path in lowered for path in runtime_path_needles())


def is_repeatable_expected_command(command: str) -> bool:
    lowered = command.casefold()
    return (
        " authority validate " in lowered
        or "verify_document_artifact_audit_report.py" in lowered
        or "verify_document_artifact_graph_report.py" in lowered
    )


def compare_commands(
    expected_commands: list[str],
    observed_commands: list[str],
) -> tuple[list[str], list[str], list[str]]:
    missing: list[str] = []
    matched_observed_indices: set[int] = set()
    for expected in expected_commands:
        match_index = next(
            (
                index
                for index, observed in enumerate(observed_commands)
                if command_matches(expected, observed)
            ),
            None,
        )
        if match_index is None:
            if not is_optional_expected_command(expected):
                missing.append(expected)
        else:
            matched_observed_indices.add(match_index)

    extra: list[str] = []
    benign_extra: list[str] = []
    for index, observed in enumerate(observed_commands):
        if index in matched_observed_indices:
            continue
        if any(
            command_matches(expected, observed)
            and is_repeatable_expected_command(expected)
            for expected in expected_commands
        ):
            # Repeated validation commands are useful repair-loop evidence.
            # One-shot setup commands such as materializers remain deviations
            # when repeated.
            continue
        if is_benign_extra_command(observed):
            benign_extra.append(observed)
        else:
            extra.append(observed)
    return missing, extra, benign_extra


def is_optional_expected_command(command: str) -> bool:
    lowered = command.casefold()
    return "repair_document_artifact_graph_reports.py" in lowered


def is_allowed_report_write_command(command: str, allowed_files: list[str]) -> bool:
    lowered = command.casefold()
    if not (
        "set-content" in lowered
        or "[system.io.file]::writealltext" in lowered
        or (
            "python -c" in lowered
            and "json" in lowered
            and ("open(" in lowered or "json.load" in lowered or "json.dump" in lowered)
        )
    ):
        return False
    if not any(path in lowered for path in runtime_path_needles()):
        return False
    if has_forbidden_report_repair_command(lowered):
        return False
    normalized = command.replace("/", "\\").casefold()
    allowed_report_paths = {
        path.replace("/", "\\").casefold()
        for path in allowed_files
        if is_runtime_output_path(path) and path.endswith(".json")
    }
    return any(path in normalized for path in allowed_report_paths)


def has_forbidden_report_repair_command(lowered_command: str) -> bool:
    if any(
        term in lowered_command
        for term in (
            "remove-item",
            "git ",
            "gh ",
            "code chat",
            "invoke-webrequest",
            "curl ",
            "wget ",
        )
    ):
        return True
    return bool(re.search(r"(^|[;&|]\s*)(del|rm)\s+", lowered_command))


def classify_allowed_report_write_commands(
    extra_commands: list[str],
    allowed_files: list[str],
) -> tuple[list[str], list[str]]:
    remaining: list[str] = []
    benign: list[str] = []
    for command in extra_commands:
        if is_allowed_report_write_command(command, allowed_files):
            benign.append(command)
        else:
            remaining.append(command)
    return remaining, benign


def normalize_path(path: str, workspace_root: Path) -> str:
    cleaned = path.replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", cleaned):
        pass
    elif re.match(r"^[A-Za-z]%3A/", cleaned, flags=re.IGNORECASE):
        cleaned = unquote(cleaned)
    root = str(workspace_root.resolve()).replace("\\", "/")
    lowered = cleaned.lower()
    if lowered.startswith(root.lower() + "/"):
        return cleaned[len(root) + 1 :]
    return cleaned


def runtime_path_needles() -> tuple[str, ...]:
    return (
        "runtime\\agent_jobs\\",
        "runtime/agent_jobs/",
        "runtime\\document_library\\",
        "runtime/document_library/",
    )


def is_runtime_output_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith(("runtime/agent_jobs/", "runtime/document_library/"))


def model_matches(expected_model: str | None, observed_model: str | None) -> bool:
    if not expected_model:
        return True
    return (
        normalize_model_id(expected_model).casefold()
        == normalize_model_id(observed_model or "unknown").casefold()
    )


def build_report(
    marker: str,
    ticket_path: Path,
    report_path: Path,
    workspace_root: Path,
    ticket_text: str,
    evidence: SessionEvidence,
    expected_model: str | None = None,
) -> str:
    expected_commands = [
        normalize_command_for_comparison(command, workspace_root)
        for command in extract_expected_commands(ticket_text)
    ]
    observed_commands = [
        normalize_command_for_comparison(command, workspace_root)
        for command in evidence.terminal_commands
    ]
    allowed_files = extract_allowed_files(ticket_text)
    required_json_fields = extract_required_json_fields(ticket_text)
    observed_files = [
        normalize_path(path, workspace_root) for path in evidence.file_paths
    ]
    expected_file_set = set(allowed_files)
    observed_runtime_files = [
        path
        for path in observed_files
        if is_runtime_output_path(path) and path.endswith((".md", ".json"))
    ]
    missing_commands, extra_commands, benign_extra_commands = compare_commands(
        expected_commands,
        observed_commands,
    )
    extra_commands, report_write_commands = classify_allowed_report_write_commands(
        extra_commands,
        allowed_files,
    )
    benign_extra_commands.extend(report_write_commands)
    missing_files = [
        path
        for path in allowed_files
        if path not in observed_runtime_files and not (workspace_root / path).exists()
    ]
    extra_files = [
        path for path in observed_runtime_files if path not in expected_file_set
    ]
    missing_json_fields = check_required_json_fields(
        workspace_root,
        allowed_files,
        required_json_fields,
    )
    status = "accepted-candidate"
    deviations: list[str] = []
    if not evidence.session_path:
        deviations.append("No matching `chatSessions/*.jsonl` artifact was found.")
    if not evidence.completed:
        deviations.append("Matching session did not show completed model state.")
    if not evidence.final_marker_present:
        deviations.append("Final marker was not found in the session artifact.")
    if not model_matches(expected_model, evidence.resolved_model):
        deviations.append("Resolved model did not match expected model.")
    if missing_commands:
        deviations.append("Missing expected terminal commands.")
    if extra_commands:
        deviations.append("Observed extra terminal commands.")
    if missing_files:
        deviations.append("Missing expected output files.")
    if extra_files:
        deviations.append("Observed unexpected runtime Markdown files.")
    if missing_json_fields:
        deviations.append("Missing required JSON report fields.")
    if deviations:
        status = "needs-supervisor-review"

    lines = [
        "# Copilot Chat Bridge Supervisor Report",
        "",
        f"marker: {marker}",
        f"status: {status}",
        f"ticket: `{ticket_path.as_posix()}`",
        f"session_artifact: `{evidence.session_path}`"
        if evidence.session_path
        else "session_artifact: missing",
        f"transcript_artifact: `{evidence.transcript_path}`"
        if evidence.transcript_path
        else "transcript_artifact: missing",
        f"expected_model: {expected_model or 'unspecified'}",
        f"resolved_model: {evidence.resolved_model or 'unknown'}",
        f"model_match: {str(model_matches(expected_model, evidence.resolved_model)).lower()}",
        "permission_levels: "
        + (
            ", ".join(evidence.permission_levels)
            if evidence.permission_levels
            else "unknown"
        ),
        f"completed: {str(evidence.completed).lower()}",
        f"final_marker_present: {str(evidence.final_marker_present).lower()}",
        "",
        "## Expected Commands",
        "",
        *[f"- `{command}`" for command in expected_commands],
        "",
        "## Observed Commands",
        "",
        *[f"- `{command}`" for command in observed_commands],
        "",
        "## Benign Extra Commands",
        "",
        *[f"- `{command}`" for command in benign_extra_commands],
        "",
        "## Allowed Runtime Files",
        "",
        *[f"- `{path}`" for path in allowed_files],
        "",
        "## Observed Runtime Files",
        "",
        *[f"- `{path}`" for path in observed_runtime_files],
        "",
        "## Tool Names",
        "",
        *[f"- `{name}`" for name in evidence.tool_names],
        "",
        "## Required JSON Report Fields",
        "",
        *[f"- `{field}`" for field in required_json_fields],
        "",
        "## Deviations",
        "",
    ]
    if deviations:
        lines.extend(f"- {deviation}" for deviation in deviations)
        if missing_commands:
            lines.extend(
                f"  - missing command: `{command}`" for command in missing_commands
            )
        if extra_commands:
            lines.extend(
                f"  - extra command: `{command}`" for command in extra_commands
            )
        if missing_files:
            lines.extend(f"  - missing file: `{path}`" for path in missing_files)
        if extra_files:
            lines.extend(f"  - extra file: `{path}`" for path in extra_files)
        if missing_json_fields:
            lines.extend(
                f"  - missing JSON field: `{field}`" for field in missing_json_fields
            )
        if not model_matches(expected_model, evidence.resolved_model):
            lines.append(f"  - expected model: `{expected_model}`")
            lines.append(
                f"  - resolved model: `{evidence.resolved_model or 'unknown'}`"
            )
    else:
        lines.append("- none")
    lines.append("")
    report = "\n".join(lines)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report


def main() -> int:
    args = parse_args()
    workspace_root = Path(args.workspace_root).resolve()
    ticket_path = Path(args.ticket).resolve()
    if not ticket_path.exists():
        print(f"Ticket not found: {ticket_path}", file=sys.stderr)
        return 2
    report_path = (
        Path(args.report).resolve()
        if args.report
        else ticket_path.with_suffix(".supervisor.md")
    )
    ticket_text = ticket_path.read_text(encoding="utf-8-sig")
    if not args.no_launch:
        launch_code_chat(args, ticket_text)
    session_path, transcript_path = find_session_files(
        args.marker,
        timeout=args.timeout_seconds,
        poll=args.poll_seconds,
    )
    evidence = load_evidence(args.marker, session_path, transcript_path)
    report = build_report(
        marker=args.marker,
        ticket_path=ticket_path,
        report_path=report_path,
        workspace_root=workspace_root,
        ticket_text=ticket_text,
        evidence=evidence,
        expected_model=args.expected_model,
    )
    print(report)
    return 0 if evidence.session_path and evidence.completed else 1


if __name__ == "__main__":
    raise SystemExit(main())
