from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
import pytest

import agent_workbench.supervision_hook as supervision_hook
from agent_workbench.supervision_hook import (
    ASSIGNED_ROOT_ENV,
    RUN_ID_ENV,
    SUPERVISION_DIR_ENV,
    capture_from_environment,
    event_from_hook_payload,
    record_hook_invocation,
)
from agent_workbench.supervision import validate_events


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


@pytest.mark.parametrize("response", [
    {"exit_code": 2, "output": "secret output", "error": "secret error"},
    {"is_error": True, "output": "secret output"},
    {"status": "denied", "command": "secret command"},
])
def test_post_tool_failure_is_categorized_without_retaining_response(response, tmp_path: Path) -> None:
    value = event_from_hook_payload(
        {**payload(cwd=str(tmp_path)), "tool_response": response},
        run_id="p116-hook-probe", assigned_root=tmp_path, sequence=1,
    )
    assert value["kind"] == "tool_failed" and value["outcome"] == "failed"
    encoded = json.dumps(value)
    assert all(secret not in encoded for secret in ("secret output", "secret error", "secret command"))
    assert "tool_response" not in value


@pytest.mark.parametrize("payload_update", [
    {"exit_code": 17},
    {"tool_result": {"content": [{"type": "text", "text": "Exit code: 17"}]}},
    {"result": [{"text": "command done; Exit code: 17", "output": "secret"}]},
])
def test_post_tool_failure_shapes_are_categorical_and_redacted(payload_update, tmp_path: Path) -> None:
    value = event_from_hook_payload({**payload(cwd=str(tmp_path)), **payload_update}, run_id="run", assigned_root=tmp_path, sequence=1)
    assert value["kind"] == "tool_failed" and value["outcome"] == "failed"
    assert "Exit code" not in json.dumps(value) and "secret" not in json.dumps(value)


def test_zero_exit_code_does_not_fail(tmp_path: Path) -> None:
    value = event_from_hook_payload({**payload(cwd=str(tmp_path)), "tool_result": {"content": [{"text": "Exit code: 0"}]}}, run_id="run", assigned_root=tmp_path, sequence=1)
    assert value["kind"] == "tool_completed" and value["outcome"] == "succeeded"


def test_unknown_result_envelope_is_scanned_but_request_input_is_not(tmp_path: Path) -> None:
    envelope = {**payload(cwd=str(tmp_path)), "host_response": {"details": [{"text": "Exit code: 17", "output": "private"}]}}
    failed = event_from_hook_payload(envelope, run_id="run", assigned_root=tmp_path, sequence=1)
    assert failed["kind"] == "tool_failed" and "Exit code" not in json.dumps(failed)
    safe = {**payload(cwd=str(tmp_path)), "tool_input": {"text": "Exit code: 17", "command": "Exit code: 17"}}
    completed = event_from_hook_payload(safe, run_id="run", assigned_root=tmp_path, sequence=1)
    assert completed["kind"] == "tool_completed" and completed["outcome"] == "succeeded"


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


def test_inactive_activation_does_not_capture(tmp_path: Path, monkeypatch) -> None:
    supervision = tmp_path / "runtime" / "agent_jobs" / "run-inactive" / "supervision"
    supervision.mkdir(parents=True)
    (supervision / "activation.json").write_text(json.dumps({"active": False, "run_id": "run-inactive", "assigned_root": str(tmp_path), "supervision_dir": str(supervision)}))
    monkeypatch.chdir(tmp_path)
    assert capture_from_environment(payload(cwd=str(tmp_path))) is False
    assert not (supervision / "events.jsonl").exists()


def test_staged_activation_requires_exact_worker_session(tmp_path: Path, monkeypatch) -> None:
    supervision = tmp_path / "runtime" / "agent_jobs" / "run-active" / "supervision"
    supervision.mkdir(parents=True)
    (supervision / "activation.json").write_text(json.dumps({"active": True, "run_id": "run-active", "worker_session_id": "worker-exact", "assigned_root": str(tmp_path), "supervision_dir": str(supervision)}))
    monkeypatch.chdir(tmp_path)
    assert capture_from_environment(payload(cwd=str(tmp_path))) is False
    assert not (supervision / "events.jsonl").exists()
    assert capture_from_environment({**payload(cwd=str(tmp_path)), "session_id": "worker-exact"}) is True
    assert (supervision / "events.jsonl").exists()


def test_capture_is_inert_without_explicit_run_environment(tmp_path: Path, monkeypatch) -> None:
    for name in (RUN_ID_ENV, ASSIGNED_ROOT_ENV, SUPERVISION_DIR_ENV):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)

    assert capture_from_environment(payload(cwd=str(Path.cwd()))) is False
    assert not (tmp_path / "invocation_receipt.json").exists()


def test_capture_uses_staged_activation_manifest(tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "runtime" / "agent_jobs" / "run-1"
    supervision_dir = run_dir / "supervision"
    supervision_dir.mkdir(parents=True)
    (supervision_dir / "activation.json").write_text(json.dumps({
    "active": True,
        "run_id": "run-1", "worker_session_id": "worker-019f77d9", "assigned_root": str(tmp_path),
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


def test_stale_activation_manifests_do_not_suppress_active_manifest(tmp_path: Path, monkeypatch) -> None:
    jobs_dir = tmp_path / "runtime" / "agent_jobs"
    stale_dir = jobs_dir / "old-run" / "supervision"
    active_dir = jobs_dir / "active-run" / "supervision"
    stale_dir.mkdir(parents=True)
    active_dir.mkdir(parents=True)
    stale_dir.joinpath("activation.json").write_text(json.dumps({
        "run_id": "old-run", "assigned_root": str(tmp_path),
        "supervision_dir": str(stale_dir),
    }), encoding="utf-8")
    active_dir.joinpath("activation.json").write_text(json.dumps({
        "active": True, "run_id": "active-run", "worker_session_id": "worker-019f77d9", "assigned_root": str(tmp_path),
        "supervision_dir": str(active_dir),
    }), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    for name in (RUN_ID_ENV, ASSIGNED_ROOT_ENV, SUPERVISION_DIR_ENV):
        monkeypatch.delenv(name, raising=False)

    assert capture_from_environment(payload(cwd=str(tmp_path)))
    event = json.loads(active_dir.joinpath("events.jsonl").read_text(encoding="utf-8"))
    assert event["run_id"] == "active-run"
    assert not stale_dir.joinpath("events.jsonl").exists()


def test_multiple_active_activation_manifests_fail_closed(tmp_path: Path, monkeypatch) -> None:
    jobs_dir = tmp_path / "runtime" / "agent_jobs"
    for run_id in ("active-one", "active-two"):
        supervision_dir = jobs_dir / run_id / "supervision"
        supervision_dir.mkdir(parents=True)
        supervision_dir.joinpath("activation.json").write_text(json.dumps({
            "active": True, "run_id": run_id, "worker_session_id": "worker-019f77d9", "assigned_root": str(tmp_path),
            "supervision_dir": str(supervision_dir),
        }), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    for name in (RUN_ID_ENV, ASSIGNED_ROOT_ENV, SUPERVISION_DIR_ENV):
        monkeypatch.delenv(name, raising=False)

    assert capture_from_environment(payload(cwd=str(tmp_path))) is False


def test_active_staged_manifest_overrides_inherited_environment(tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "runtime" / "agent_jobs" / "active-run"
    supervision_dir = run_dir / "supervision"
    supervision_dir.mkdir(parents=True)
    supervision_dir.joinpath("activation.json").write_text(json.dumps({
        "active": True, "run_id": "active-run", "worker_session_id": "worker-019f77d9", "assigned_root": str(tmp_path),
        "supervision_dir": str(supervision_dir),
    }), encoding="utf-8")
    inherited_dir = tmp_path / "old-run-supervision"
    monkeypatch.setenv(RUN_ID_ENV, "old-run")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(inherited_dir))
    monkeypatch.chdir(tmp_path)

    assert capture_from_environment(payload(cwd=str(tmp_path)))
    event = json.loads(supervision_dir.joinpath("events.jsonl").read_text(encoding="utf-8"))
    assert event["run_id"] == "active-run"
    assert not inherited_dir.joinpath("events.jsonl").exists()


def test_multiple_active_manifests_do_not_fall_back_to_environment(tmp_path: Path, monkeypatch) -> None:
    jobs_dir = tmp_path / "runtime" / "agent_jobs"
    for run_id in ("active-one", "active-two"):
        supervision_dir = jobs_dir / run_id / "supervision"
        supervision_dir.mkdir(parents=True)
        supervision_dir.joinpath("activation.json").write_text(json.dumps({
            "active": True, "run_id": run_id, "worker_session_id": "worker-019f77d9", "assigned_root": str(tmp_path),
            "supervision_dir": str(supervision_dir),
        }), encoding="utf-8")
    inherited_dir = tmp_path / "old-run-supervision"
    monkeypatch.setenv(RUN_ID_ENV, "old-run")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(inherited_dir))
    monkeypatch.chdir(tmp_path)

    assert capture_from_environment(payload(cwd=str(tmp_path))) is False
    assert not inherited_dir.joinpath("events.jsonl").exists()


def test_capture_appends_sanitized_ordered_events(tmp_path: Path, monkeypatch) -> None:
    supervision_dir = tmp_path / "supervision"
    monkeypatch.chdir(tmp_path)
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


def test_capture_drops_next_event_at_total_payload_bound(tmp_path: Path, monkeypatch) -> None:
    supervision_dir = tmp_path / "supervision"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(RUN_ID_ENV, "p116-hook-probe")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(supervision_dir))

    while True:
        assert capture_from_environment(payload(cwd=str(tmp_path)))
        events = [
            json.loads(line)
            for line in (supervision_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        if len(events) > 1 and not capture_from_environment(payload(cwd=str(tmp_path))):
            break
        receipt = json.loads((supervision_dir / "invocation_receipt.json").read_text(encoding="utf-8"))
        if receipt["status"] == "event_dropped":
            break

    retained = [
        json.loads(line)
        for line in (supervision_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert json.loads((supervision_dir / "invocation_receipt.json").read_text(encoding="utf-8"))["status"] == "event_dropped"
    assert validate_events(retained, assigned_root=tmp_path).ok
    assert len(retained) == len(events)


def test_capture_refuses_output_directory_outside_assigned_root(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(RUN_ID_ENV, "p116-hook-probe")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path / "assigned"))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(tmp_path / "outside" / "supervision"))

    assert capture_from_environment(payload(cwd=str(tmp_path / "assigned"))) is False
    assert not (tmp_path / "outside" / "supervision" / "events.jsonl").exists()


def test_capture_records_bounded_local_error(tmp_path: Path, monkeypatch) -> None:
    supervision_dir = tmp_path / "supervision"
    monkeypatch.chdir(tmp_path)
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


def test_invocation_receipt_distinguishes_invoked_from_event_written(tmp_path: Path, monkeypatch) -> None:
    supervision_dir = tmp_path / "supervision"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(RUN_ID_ENV, "p116-hook-probe")
    monkeypatch.setenv(ASSIGNED_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(SUPERVISION_DIR_ENV, str(supervision_dir))

    assert record_hook_invocation()
    receipt = json.loads((supervision_dir / "invocation_receipt.json").read_text())
    assert receipt == {"receipt_version": 1, "status": "invoked"}
    assert capture_from_environment(payload(cwd=str(tmp_path)))
    receipt = json.loads((supervision_dir / "invocation_receipt.json").read_text())
    assert receipt["status"] == "event_written"
    assert set(receipt) == {"receipt_version", "status"}


def test_entrypoint_records_payload_rejected_and_remains_sanitized(tmp_path: Path) -> None:
    env = os.environ | {
        RUN_ID_ENV: "p116-hook-receipt",
        ASSIGNED_ROOT_ENV: str(tmp_path),
        SUPERVISION_DIR_ENV: str(tmp_path / "supervision"),
    }
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        ["python", str(root / "scripts" / "p116_capture_hook.py")],
        cwd=tmp_path, input="[\"raw command\"]", text=True, capture_output=True, env=env, check=False,
    )
    assert completed.returncode == 0
    receipt = json.loads((tmp_path / "supervision" / "invocation_receipt.json").read_text())
    assert receipt == {"receipt_version": 1, "status": "payload_rejected"}
    assert "raw command" not in json.dumps(receipt)


def test_configured_windows_hook_command_captures_event(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    if "hooks" not in config:
        pytest.skip("workspace hooks are not staged")
    configured_commands = [
        hook["command"]
        for matcher in config["hooks"].values()
        for entry in matcher
        for hook in entry["hooks"]
    ]
    assert len(configured_commands) == 2
    assert all("p116_capture_hook.py" in command for command in configured_commands)
    assert [
        entry["matcher"]
        for matcher in config["hooks"].values()
        for entry in matcher
    ] == ["^Bash$", "^Bash$"]
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
    command = f"& python '{root / 'scripts' / 'p116_capture_hook.py'}'"

    completed = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=tmp_path,
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
