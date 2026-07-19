from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from agent_workbench.supervision_hook import (
    ASSIGNED_ROOT_ENV,
    RUN_ID_ENV,
    SUPERVISION_DIR_ENV,
    capture_from_environment,
    event_from_hook_payload,
)


def payload(*, cwd: str, event: str = "PostToolUse") -> dict[str, object]:
    return {
        "session_id": "worker-019f77d9",
        "turn_id": "turn-019f77d9",
        "cwd": cwd,
        "hook_event_name": event,
        "tool_name": "Bash",
        "tool_input": {"command": "never persist this"},
        "tool_response": {"output": "never persist this either"},
    }


def test_event_redacts_hook_tool_input_and_output(tmp_path: Path) -> None:
    value = event_from_hook_payload(
        payload(cwd=str(tmp_path)),
        run_id="p116-hook-probe",
        assigned_root=tmp_path,
        sequence=1,
    )

    assert value["kind"] == "tool_completed"
    assert value["outcome"] == "succeeded"
    assert value["root_match"] is True
    assert "tool_input" not in value
    assert "tool_response" not in value
    assert "command" not in json.dumps(value)


def test_event_marks_wrong_session_root(tmp_path: Path) -> None:
    value = event_from_hook_payload(
        payload(cwd=str(tmp_path / "wrong"), event="PreToolUse"),
        run_id="p116-hook-probe",
        assigned_root=tmp_path,
        sequence=1,
    )

    assert value["kind"] == "workspace_mismatch"
    assert value["outcome"] == "failed"
    assert value["root_match"] is False


def test_capture_is_inert_without_explicit_run_environment(monkeypatch) -> None:
    for name in (RUN_ID_ENV, ASSIGNED_ROOT_ENV, SUPERVISION_DIR_ENV):
        monkeypatch.delenv(name, raising=False)

    assert capture_from_environment(payload(cwd=str(Path.cwd()))) is False


def test_capture_appends_sanitized_ordered_events(tmp_path: Path, monkeypatch) -> None:
    supervision_dir = tmp_path / "supervision"
    monkeypatch.setenv(RUN_ID_ENV, "p116-hook-probe")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(supervision_dir))

    assert capture_from_environment(payload(cwd=str(tmp_path), event="PreToolUse"))
    assert capture_from_environment(payload(cwd=str(tmp_path), event="PostToolUse"))

    events = [
        json.loads(line)
        for line in (supervision_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [event["sequence"] for event in events] == [1, 2]
    assert [event["kind"] for event in events] == ["tool_started", "tool_completed"]
    assert "tool_input" not in events[0]


def test_configured_windows_hook_command_captures_event(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    env = os.environ | {
        RUN_ID_ENV: "p116-hook-subprocess",
        ASSIGNED_ROOT_ENV: str(root),
        SUPERVISION_DIR_ENV: str(tmp_path / "supervision"),
    }
    input_payload = json.dumps(payload(cwd=str(root), event="PreToolUse"))
    command = (
        "& python (Join-Path (git rev-parse --show-toplevel) "
        "'scripts\\p116_capture_hook.py')"
    )

    completed = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=root,
        input=input_payload,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    events = [
        json.loads(line)
        for line in (tmp_path / "supervision" / "events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(events) == 1
    assert events[0]["kind"] == "tool_started"
    assert events[0]["root_match"] is True
