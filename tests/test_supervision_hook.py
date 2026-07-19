from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import agent_workbench.supervision_hook as supervision_hook
from agent_workbench.supervision_hook import (
    ASSIGNED_ROOT_ENV,
    RUN_ID_ENV,
    SUPERVISION_DIR_ENV,
    capture_from_environment,
    event_from_hook_payload,
)


WINDOWS_HOOK_COMMAND_BODY = (
    "& python (Join-Path (git rev-parse --show-toplevel) "
    "'scripts\\p116_capture_hook.py')"
)
EXPECTED_WINDOWS_HOOK_COMMAND = (
    'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
    + WINDOWS_HOOK_COMMAND_BODY
    + '"'
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


def test_capture_uses_staged_activation_manifest(tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "runtime" / "agent_jobs" / "run-1"
    supervision_dir = run_dir / "supervision"
    supervision_dir.mkdir(parents=True)
    (supervision_dir / "activation.json").write_text(json.dumps({
        "run_id": "run-1", "assigned_root": str(tmp_path),
        "supervision_dir": str(supervision_dir),
    }), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    for name in (RUN_ID_ENV, ASSIGNED_ROOT_ENV, SUPERVISION_DIR_ENV):
        monkeypatch.delenv(name, raising=False)

    assert capture_from_environment(payload(cwd=str(tmp_path)))
    event = json.loads((supervision_dir / "events.jsonl").read_text(encoding="utf-8"))
    assert event["run_id"] == "run-1"


def test_staged_activation_rejects_malformed_and_out_of_root(tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "runtime" / "agent_jobs" / "run-1" / "supervision"
    run_dir.mkdir(parents=True)
    activation = run_dir / "activation.json"
    monkeypatch.chdir(tmp_path)
    for name in (RUN_ID_ENV, ASSIGNED_ROOT_ENV, SUPERVISION_DIR_ENV):
        monkeypatch.delenv(name, raising=False)
    for value in ("not-json", {"run_id": "run-1", "assigned_root": str(tmp_path),
                                "supervision_dir": str(tmp_path.parent / "outside")}):
        activation.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        assert capture_from_environment(payload(cwd=str(tmp_path))) is False


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


def test_capture_refuses_output_directory_outside_assigned_root(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(RUN_ID_ENV, "p116-hook-probe")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path / "assigned"))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(tmp_path / "outside" / "supervision"))

    assert capture_from_environment(payload(cwd=str(tmp_path / "assigned"))) is False
    assert not (tmp_path / "outside" / "supervision" / "events.jsonl").exists()


def test_capture_records_bounded_local_error(tmp_path: Path, monkeypatch) -> None:
    supervision_dir = tmp_path / "supervision"
    monkeypatch.setenv(RUN_ID_ENV, "p116-hook-probe")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(supervision_dir))

    def fail_event(*args, **kwargs):
        raise ValueError("raw private failure details")

    monkeypatch.setattr(supervision_hook, "event_from_hook_payload", fail_event)
    assert capture_from_environment(payload(cwd=str(tmp_path)))
    event = json.loads((supervision_dir / "events.jsonl").read_text(encoding="utf-8"))
    assert event["kind"] == "tool_failed"
    assert event["stage"] == "hook"
    assert event["error_code"] == "capture_failure"
    assert event["run_id"] == "p116-hook-probe"
    assert "raw private failure details" not in json.dumps(event)
    assert set(event) <= {"schema_version", "sequence", "event_id", "timestamp", "kind", "stage", "outcome", "redaction_applied", "run_id", "hook_event", "tool_name", "root_match", "error_code"}


def test_configured_windows_hook_command_captures_event(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    configured_commands = [
        hook["command"]
        for matcher in config["hooks"].values()
        for entry in matcher
        for hook in entry["hooks"]
    ]
    assert configured_commands == [
        EXPECTED_WINDOWS_HOOK_COMMAND,
        EXPECTED_WINDOWS_HOOK_COMMAND,
    ]
    assert all(
        "commandWindows" not in hook
        for matcher in config["hooks"].values()
        for entry in matcher
        for hook in entry["hooks"]
    )
    env = os.environ | {
        RUN_ID_ENV: "p116-hook-subprocess",
        ASSIGNED_ROOT_ENV: str(tmp_path),
        SUPERVISION_DIR_ENV: str(tmp_path / "supervision"),
    }
    input_payload = json.dumps(payload(cwd=str(tmp_path), event="PreToolUse"))
    command = WINDOWS_HOOK_COMMAND_BODY

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
