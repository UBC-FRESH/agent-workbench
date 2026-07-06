"""Archive VS Code Copilot Chat behavior traces for delegation runs."""

from __future__ import annotations

import json
import os
import shutil
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


DEFAULT_SNIPPET_CHARS = 240
DEFAULT_MAX_SNIPPETS = 20


@dataclass(frozen=True)
class CopilotArchiveConfig:
    workspace_root: Path
    output_dir: Path
    code_user_dir: Path | None = None
    run_id: str | None = None
    session_id: str | None = None
    prompt_marker: str | None = None
    max_snippet_chars: int = DEFAULT_SNIPPET_CHARS
    max_snippets: int = DEFAULT_MAX_SNIPPETS
    copy_raw: bool = True


@dataclass(frozen=True)
class CandidateSession:
    session_id: str
    chat_session_path: Path
    transcript_path: Path | None
    score: int
    last_write_time: float


def archive_copilot_session(config: CopilotArchiveConfig) -> dict[str, Any]:
    """Archive the best-matching Copilot session and return the manifest."""

    workspace_root = config.workspace_root.resolve()
    code_user_dir = config.code_user_dir or default_code_user_dir()
    workspace_storage = find_workspace_storage(workspace_root, code_user_dir)
    candidate = select_candidate_session(
        workspace_storage=workspace_storage,
        run_id=config.run_id,
        session_id=config.session_id,
        prompt_marker=config.prompt_marker,
    )
    if candidate is None:
        raise ValueError("no matching Copilot chat session found")

    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    copied_raw_files: list[str] = []

    raw_chat_name = f"chat_session_{candidate.session_id}.raw.jsonl"
    raw_chat_output = output_dir / raw_chat_name
    if config.copy_raw:
        shutil.copy2(candidate.chat_session_path, raw_chat_output)
        copied_raw_files.append(raw_chat_name)

    raw_transcript_output: Path | None = None
    if candidate.transcript_path is not None:
        raw_transcript_name = f"copilot_transcript_{candidate.session_id}.raw.jsonl"
        raw_transcript_output = output_dir / raw_transcript_name
        if config.copy_raw:
            shutil.copy2(candidate.transcript_path, raw_transcript_output)
            copied_raw_files.append(raw_transcript_name)

    transcript_source = candidate.transcript_path or candidate.chat_session_path
    manifest = build_manifest(
        session_id=candidate.session_id,
        chat_session_path=candidate.chat_session_path,
        transcript_path=transcript_source,
        copied_raw_files=copied_raw_files,
        workspace_root=workspace_root,
        workspace_storage=workspace_storage,
        run_id=config.run_id,
        prompt_marker=config.prompt_marker,
        max_snippet_chars=config.max_snippet_chars,
        max_snippets=config.max_snippets,
    )
    manifest_path = output_dir / f"{candidate.session_id}.copilot_archive_manifest.json"
    manifest["manifest_path"] = manifest_path.name
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def default_code_user_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "Code" / "User"
    return Path.home() / ".config" / "Code" / "User"


def find_workspace_storage(workspace_root: Path, code_user_dir: Path) -> Path:
    workspace_storage_root = code_user_dir / "workspaceStorage"
    if not workspace_storage_root.exists():
        raise ValueError(f"workspaceStorage not found: {workspace_storage_root}")

    matches: list[Path] = []
    for workspace_json in workspace_storage_root.glob("*/workspace.json"):
        try:
            data = json.loads(workspace_json.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        folder = data.get("folder")
        if not isinstance(folder, str):
            continue
        folder_path = uri_to_path(folder)
        if same_path(folder_path, workspace_root):
            matches.append(workspace_json.parent)

    if not matches:
        raise ValueError(f"no VS Code workspace storage matches {workspace_root}")
    return max(matches, key=lambda path: path.stat().st_mtime)


def uri_to_path(uri: str) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        return Path(uri)
    path = unquote(parsed.path)
    if os.name == "nt" and path.startswith("/") and len(path) >= 3 and path[2] == ":":
        path = path[1:]
    return Path(path)


def same_path(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return str(a).lower() == str(b).lower()


def select_candidate_session(
    workspace_storage: Path,
    run_id: str | None = None,
    session_id: str | None = None,
    prompt_marker: str | None = None,
) -> CandidateSession | None:
    chat_dir = workspace_storage / "chatSessions"
    transcript_dir = workspace_storage / "GitHub.copilot-chat" / "transcripts"
    if not chat_dir.exists():
        return None

    candidates: list[CandidateSession] = []
    for chat_path in chat_dir.glob("*.jsonl"):
        current_session_id = chat_path.stem
        if session_id and current_session_id != session_id:
            continue
        text = read_text_lossy(chat_path)
        score = 0
        if session_id and current_session_id == session_id:
            score += 1000
        if run_id and run_id in text:
            score += 100
        if prompt_marker and prompt_marker in text:
            score += 100
        if not any((session_id, run_id, prompt_marker)):
            score += 1
        transcript_path = transcript_dir / chat_path.name
        if transcript_path.exists():
            score += 5
        if score <= 0:
            continue
        candidates.append(
            CandidateSession(
                session_id=current_session_id,
                chat_session_path=chat_path,
                transcript_path=transcript_path if transcript_path.exists() else None,
                score=score,
                last_write_time=chat_path.stat().st_mtime,
            )
        )
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item.score, item.last_write_time))


def build_manifest(
    session_id: str,
    chat_session_path: Path,
    transcript_path: Path,
    copied_raw_files: list[str],
    workspace_root: Path,
    workspace_storage: Path,
    run_id: str | None,
    prompt_marker: str | None,
    max_snippet_chars: int,
    max_snippets: int,
) -> dict[str, Any]:
    transcript_summary = summarize_transcript(
        transcript_path,
        max_snippet_chars=max_snippet_chars,
        max_snippets=max_snippets,
    )
    session_summary = summarize_chat_session(chat_session_path)
    return {
        "archive_schema_version": 1,
        "archive_id": f"copilot_session_{session_id}",
        "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "run_id": run_id or "",
        "prompt_marker": prompt_marker or "",
        "workspace_root_name": workspace_root.name,
        "workspace_storage_id": workspace_storage.name,
        "session_id": session_id,
        "raw_files": copied_raw_files,
        "source_files": {
            "chat_session_file": chat_session_path.name,
            "transcript_file": transcript_path.name,
            "source_paths_recorded": False,
        },
        **transcript_summary,
        **session_summary,
        "public_safety": {
            "raw_archive_is_runtime_only": True,
            "manifest_contains_only_snippets": True,
            "source_paths_recorded": False,
            "not_for_tracked_commit_without_sanitization": True,
        },
    }


def summarize_transcript(
    path: Path,
    max_snippet_chars: int = DEFAULT_SNIPPET_CHARS,
    max_snippets: int = DEFAULT_MAX_SNIPPETS,
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    first_timestamp = ""
    last_timestamp = ""
    user_messages: list[str] = []
    assistant_messages: list[str] = []
    tool_requests: list[dict[str, str]] = []
    tool_names: Counter[str] = Counter()
    completion_statuses: Counter[str] = Counter()

    for record in iter_jsonl(path):
        event_type = str(record.get("type", "unknown"))
        counts[event_type] += 1
        timestamp = record.get("timestamp")
        if isinstance(timestamp, str):
            first_timestamp = first_timestamp or timestamp
            last_timestamp = timestamp
        data = record.get("data")
        if not isinstance(data, dict):
            continue
        if event_type == "user.message":
            content = data.get("content")
            if isinstance(content, str):
                user_messages.append(snippet(content, max_snippet_chars))
        elif event_type == "assistant.message":
            content = data.get("content")
            if isinstance(content, str) and content.strip():
                assistant_messages.append(snippet(content, max_snippet_chars))
            for request in data.get("toolRequests") or []:
                if not isinstance(request, dict):
                    continue
                name = str(request.get("name", ""))
                tool_names[name] += 1
                tool_requests.append(
                    {
                        "name": name,
                        "arguments_snippet": snippet(
                            str(request.get("arguments", "")),
                            max_snippet_chars,
                        ),
                    }
                )
        elif event_type == "tool.execution_complete":
            status = extract_tool_completion_status(data)
            completion_statuses[status] += 1

    return {
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "event_counts": dict(sorted(counts.items())),
        "user_message_count": len(user_messages),
        "assistant_message_count_with_text": len(assistant_messages),
        "tool_request_count": len(tool_requests),
        "tool_names": dict(sorted(tool_names.items())),
        "tool_completion_statuses": dict(sorted(completion_statuses.items())),
        "keep_going_user_messages": [
            message for message in user_messages if "keep going" in message.lower()
        ],
        "stall_nudge_user_messages": [
            message for message in user_messages if "stall" in message.lower()
        ],
        "user_message_snippets": user_messages[:max_snippets],
        "assistant_message_snippets": assistant_messages[:max_snippets],
        "tool_request_snippets": tool_requests[:max_snippets],
    }


def summarize_chat_session(path: Path) -> dict[str, Any]:
    model_ids: set[str] = set()
    permission_levels: set[str] = set()
    session_titles: set[str] = set()

    for record in iter_jsonl(path):
        for key, value in walk_json(record):
            if key in {"modelId", "identifier"} and isinstance(value, str):
                if "ollama" in value.lower() or ":" in value:
                    model_ids.add(value)
            elif key == "permissionLevel" and isinstance(value, str):
                permission_levels.add(value)
            elif key == "customTitle" and isinstance(value, str):
                session_titles.add(value)

    return {
        "model_ids_detected": sorted(model_ids),
        "permission_levels_detected": sorted(permission_levels),
        "session_titles_detected": sorted(session_titles),
    }


def walk_json(value: Any) -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.append((str(key), child))
            found.extend(walk_json(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(walk_json(child))
    return found


def extract_tool_completion_status(data: dict[str, Any]) -> str:
    for key in ("status", "outcome", "result"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    if data.get("error"):
        return "error"
    return "unknown"


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in read_text_lossy(path).splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def read_text_lossy(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def snippet(value: str, max_chars: int) -> str:
    compact = " ".join(value.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max(max_chars - 1, 0)] + "…"
