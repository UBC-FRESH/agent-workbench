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
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


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
    parser = argparse.ArgumentParser(description="Launch and verify a Copilot Chat worker ticket.")
    parser.add_argument("--ticket", required=True, help="Path to the worker ticket Markdown file.")
    parser.add_argument("--marker", required=True, help="Unique marker expected in the session.")
    parser.add_argument("--workspace-root", default=".", help="Repository root for the worker launch.")
    parser.add_argument("--report", help="Supervisor report path. Defaults beside the ticket.")
    parser.add_argument("--timeout-seconds", type=int, default=240, help="Session polling timeout.")
    parser.add_argument("--poll-seconds", type=float, default=3.0, help="Polling interval.")
    parser.add_argument("--code-command", default="code", help="VS Code command executable.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="One-line prompt for code chat.")
    parser.add_argument("--no-launch", action="store_true", help="Skip launch and only parse existing sessions.")
    return parser.parse_args()


def appdata_workspace_storage() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set; VS Code workspace storage cannot be located.")
    return Path(appdata) / "Code" / "User" / "workspaceStorage"


def launch_code_chat(args: argparse.Namespace, ticket_text: str) -> None:
    command = [
        args.code_command,
        "chat",
        "--reuse-window",
        "--maximize",
        "--mode",
        "agent",
        args.prompt,
        "-",
    ]
    completed = subprocess.run(
        command,
        input=ticket_text,
        text=True,
        cwd=args.workspace_root,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"code chat failed with exit code {completed.returncode}")


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


def find_session_files(marker: str, timeout: int, poll: float) -> tuple[Path | None, Path | None]:
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


def load_evidence(marker: str, session_path: Path | None, transcript_path: Path | None) -> SessionEvidence:
    evidence = SessionEvidence(session_path=session_path, transcript_path=transcript_path)
    if not session_path:
        return evidence
    text = session_path.read_text(encoding="utf-8", errors="replace")
    evidence.raw_excerpt = text[:2000]
    resolved = re.findall(r'"resolvedModel":"([^"]+)"', text)
    evidence.resolved_model = resolved[-1] if resolved else None
    evidence.permission_levels = sorted(set(re.findall(r'"permissionLevel":"([^"]+)"', text)))
    evidence.completed = '"modelState":{"value":1' in text or f"{marker} done" in text
    evidence.final_marker_present = f"{marker} done" in text
    evidence.terminal_commands = re.findall(r'"original":"((?:\\.|[^"])*)"', text)
    evidence.file_paths = unique(extract_file_edit_paths(text))
    evidence.tool_names = unique(
        name
        for name in re.findall(r'"name":"([^"]+)"', text)
        if name in {"read_file", "run_in_terminal", "create_file", "replace_string_in_file"}
    )
    return evidence


def unescape_json_text(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value.replace("\\\\", "\\")


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
    commands_section = section_text(ticket, "Required Commands")
    commands: list[str] = []
    for block in re.findall(r"```(?:\w+)?\n([\s\S]*?)```", commands_section):
        for line in block.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
    return commands


def extract_allowed_files(ticket: str) -> list[str]:
    read_paths = set(re.findall(r"`?(runtime/agent_jobs/[^`\s]+\.md)`?", section_text(ticket, "Required Reads")))
    all_paths = re.findall(r"`?(runtime/agent_jobs/[^`\s]+\.md)`?", ticket)
    return unique([path for path in all_paths if path not in read_paths])


def normalize_command(command: str) -> str:
    return command.encode("utf-8").decode("unicode_escape").strip()


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


def build_report(
    marker: str,
    ticket_path: Path,
    report_path: Path,
    workspace_root: Path,
    ticket_text: str,
    evidence: SessionEvidence,
) -> str:
    expected_commands = [normalize_command(command) for command in extract_expected_commands(ticket_text)]
    observed_commands = [normalize_command(command) for command in evidence.terminal_commands]
    allowed_files = extract_allowed_files(ticket_text)
    observed_files = [normalize_path(path, workspace_root) for path in evidence.file_paths]
    expected_file_set = set(allowed_files)
    observed_runtime_files = [
        path for path in observed_files if path.startswith("runtime/agent_jobs/") and path.endswith(".md")
    ]
    missing_commands = list((Counter(expected_commands) - Counter(observed_commands)).elements())
    extra_commands = list((Counter(observed_commands) - Counter(expected_commands)).elements())
    missing_files = [path for path in allowed_files if path not in observed_runtime_files and not (workspace_root / path).exists()]
    extra_files = [path for path in observed_runtime_files if path not in expected_file_set]
    status = "accepted-candidate"
    deviations: list[str] = []
    if not evidence.session_path:
        deviations.append("No matching `chatSessions/*.jsonl` artifact was found.")
    if not evidence.completed:
        deviations.append("Matching session did not show completed model state.")
    if not evidence.final_marker_present:
        deviations.append("Final marker was not found in the session artifact.")
    if missing_commands:
        deviations.append("Missing expected terminal commands.")
    if extra_commands:
        deviations.append("Observed extra terminal commands.")
    if missing_files:
        deviations.append("Missing expected output files.")
    if extra_files:
        deviations.append("Observed unexpected runtime Markdown files.")
    if deviations:
        status = "needs-supervisor-review"

    lines = [
        "# Copilot Chat Bridge Supervisor Report",
        "",
        f"marker: {marker}",
        f"status: {status}",
        f"ticket: `{ticket_path.as_posix()}`",
        f"session_artifact: `{evidence.session_path}`" if evidence.session_path else "session_artifact: missing",
        f"transcript_artifact: `{evidence.transcript_path}`" if evidence.transcript_path else "transcript_artifact: missing",
        f"resolved_model: {evidence.resolved_model or 'unknown'}",
        "permission_levels: " + (", ".join(evidence.permission_levels) if evidence.permission_levels else "unknown"),
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
        "## Deviations",
        "",
    ]
    if deviations:
        lines.extend(f"- {deviation}" for deviation in deviations)
        if missing_commands:
            lines.extend(f"  - missing command: `{command}`" for command in missing_commands)
        if extra_commands:
            lines.extend(f"  - extra command: `{command}`" for command in extra_commands)
        if missing_files:
            lines.extend(f"  - missing file: `{path}`" for path in missing_files)
        if extra_files:
            lines.extend(f"  - extra file: `{path}`" for path in extra_files)
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
    report_path = Path(args.report).resolve() if args.report else ticket_path.with_suffix(".supervisor.md")
    ticket_text = ticket_path.read_text(encoding="utf-8")
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
    )
    print(report)
    return 0 if evidence.session_path and evidence.completed else 1


if __name__ == "__main__":
    raise SystemExit(main())
