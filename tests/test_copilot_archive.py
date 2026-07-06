from __future__ import annotations

import json
from pathlib import Path

from agent_workbench.copilot_archive import (
    CopilotArchiveConfig,
    archive_copilot_session,
    find_workspace_storage,
)


def test_copilot_archive_copies_raw_logs_and_writes_manifest(tmp_path: Path) -> None:
    workspace_root = tmp_path / "project"
    workspace_root.mkdir()
    code_user_dir = tmp_path / "Code" / "User"
    storage = code_user_dir / "workspaceStorage" / "workspace-a"
    chat_dir = storage / "chatSessions"
    transcript_dir = storage / "GitHub.copilot-chat" / "transcripts"
    chat_dir.mkdir(parents=True)
    transcript_dir.mkdir(parents=True)
    (storage / "workspace.json").write_text(
        json.dumps({"folder": workspace_root.resolve().as_uri()}),
        encoding="utf-8",
    )

    session_id = "session-123"
    chat_path = chat_dir / f"{session_id}.jsonl"
    chat_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "kind": 0,
                        "v": {
                            "customTitle": "P108 run",
                            "modelId": "ollama-models/Ollama/qwen3.6:35b-a3b-bf16",
                            "modeInfo": {"permissionLevel": "autopilot"},
                            "message": {"text": "P108_MARKER execute ticket"},
                        },
                    }
                ),
                json.dumps(
                    {
                        "kind": 1,
                        "v": {
                            "selectedModel": {
                                "identifier": (
                                    "ollama-models/Ollama/qwen3.6:35b-a3b-bf16"
                                )
                            },
                            "permissionLevel": "autopilot",
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    transcript_path = transcript_dir / f"{session_id}.jsonl"
    transcript_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "session.start",
                        "timestamp": "2026-07-06T00:00:00Z",
                        "data": {"sessionId": session_id},
                    }
                ),
                json.dumps(
                    {
                        "type": "user.message",
                        "timestamp": "2026-07-06T00:00:01Z",
                        "data": {"content": "P108_MARKER please keep going"},
                    }
                ),
                json.dumps(
                    {
                        "type": "assistant.message",
                        "timestamp": "2026-07-06T00:00:02Z",
                        "data": {
                            "content": "I will continue.",
                            "toolRequests": [
                                {
                                    "name": "run_in_terminal",
                                    "arguments": "{\"command\":\"git status\"}",
                                }
                            ],
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "tool.execution_complete",
                        "timestamp": "2026-07-06T00:00:03Z",
                        "data": {"status": "success"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "runtime" / "archive"
    manifest = archive_copilot_session(
        CopilotArchiveConfig(
            workspace_root=workspace_root,
            output_dir=output_dir,
            code_user_dir=code_user_dir,
            prompt_marker="P108_MARKER",
        )
    )

    assert manifest["session_id"] == session_id
    assert manifest["user_message_count"] == 1
    assert manifest["assistant_message_count_with_text"] == 1
    assert manifest["tool_request_count"] == 1
    assert manifest["event_counts"]["tool.execution_complete"] == 1
    assert manifest["tool_completion_statuses"]["success"] == 1
    assert manifest["permission_levels_detected"] == ["autopilot"]
    assert "ollama-models/Ollama/qwen3.6:35b-a3b-bf16" in manifest[
        "model_ids_detected"
    ]
    assert manifest["keep_going_user_messages"] == ["P108_MARKER please keep going"]
    assert (output_dir / f"chat_session_{session_id}.raw.jsonl").exists()
    assert (output_dir / f"copilot_transcript_{session_id}.raw.jsonl").exists()
    assert (output_dir / f"{session_id}.copilot_archive_manifest.json").exists()


def test_find_workspace_storage_fails_closed_without_match(tmp_path: Path) -> None:
    workspace_root = tmp_path / "project"
    workspace_root.mkdir()
    code_user_dir = tmp_path / "Code" / "User"
    storage = code_user_dir / "workspaceStorage" / "workspace-a"
    storage.mkdir(parents=True)
    (storage / "workspace.json").write_text(
        json.dumps({"folder": (tmp_path / "other").resolve().as_uri()}),
        encoding="utf-8",
    )

    try:
        find_workspace_storage(workspace_root, code_user_dir)
    except ValueError as exc:
        assert "no VS Code workspace storage matches" in str(exc)
    else:
        raise AssertionError("expected no-match workspace lookup to fail")
