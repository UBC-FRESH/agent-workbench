from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from agent_workbench.copilot_sdk_bridge import (
    LiveCopilotSdkAdapter,
    SdkTurnConfig,
    load_sdk_session_manifest,
    monitor_sdk_session,
    run_sdk_turn,
    validate_sdk_session_manifest,
)


class FakeEvent:
    def __init__(self, event_type: str, data: dict[str, Any] | None = None):
        self.type = event_type
        self.data = data or {}


class FakeSession:
    def __init__(self, session_id: str, on_event: Any):
        self.session_id = session_id
        self.on_event = on_event
        self.sent_prompts: list[str] = []

    async def send(self, prompt: str) -> None:
        self.sent_prompts.append(prompt)
        self.on_event(FakeEvent("assistant.message", {"content": "working"}))
        self.on_event(FakeEvent("session.idle"))


class FakeAdapter:
    def __init__(self) -> None:
        self.created = False
        self.resumed = False
        self.stopped = False
        self.session: FakeSession | None = None

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        self.stopped = True

    async def create_session(
        self, manifest: dict[str, Any], on_event: Any
    ) -> FakeSession:
        self.created = True
        self.session = FakeSession("sdk-session-created", on_event)
        return self.session

    async def resume_session(
        self, manifest: dict[str, Any], on_event: Any
    ) -> FakeSession:
        self.resumed = True
        self.session = FakeSession(str(manifest["sdk"]["session_id"]), on_event)
        return self.session


def write_manifest_fixture(tmp_path: Path, *, session_id: str = "") -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    ticket = tmp_path / "ticket.md"
    ticket.write_text("Do exactly one SDK-owned task.\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "run_id": "p71-test-run",
        "phase": "P71",
        "governing_issue": 466,
        "child_issue": 468,
        "target_project": "femic",
        "target_task": "test SDK bridge",
        "workspace_root": "workspace",
        "sdk": {
            "provider": "github-copilot-sdk",
            "session_id": session_id,
            "resumable": True,
            "model": "",
            "permission_mode": "operator-configured",
            "mode": "empty",
            "base_directory": "runtime/copilot_sdk_home/p71-test-run",
            "available_tools": "default",
            "working_directory": "",
        },
        "paths": {
            "ticket": "ticket.md",
            "result": "result.md",
            "blocker": "blocker.md",
            "heartbeat": "run.heartbeat.jsonl",
            "event_log": "run.sdk_events.jsonl",
            "status_summary": "run.sdk_status.json",
            "nudge_log": "run.nudges.jsonl",
        },
        "control": {
            "stall_seconds": 1,
            "nonprogress_event_limit": 5,
            "max_nudges": 2,
            "max_retries": 1,
            "stop_condition": "result or blocker",
        },
        "state": {
            "latest_status": "created",
            "latest_event_at": "",
            "latest_nudge_at": "",
            "accepted_candidate": False,
        },
        "privacy": {
            "raw_events_local_only": True,
            "publish_sanitized_summary_only": True,
        },
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_validate_sdk_session_manifest_accepts_complete_manifest(
    tmp_path: Path,
) -> None:
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_sdk_session_manifest(manifest_path)

    result = validate_sdk_session_manifest(manifest, manifest_path=manifest_path)

    assert result.ok, result.errors


def test_validate_sdk_session_manifest_rejects_missing_ticket(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_sdk_session_manifest(manifest_path)
    manifest["paths"]["ticket"] = "missing.md"

    result = validate_sdk_session_manifest(manifest, manifest_path=manifest_path)

    assert not result.ok
    assert any("paths.ticket does not exist" in error for error in result.errors)


def test_run_sdk_turn_creates_session_and_writes_evidence(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path)
    adapter = FakeAdapter()

    summary = asyncio.run(
        run_sdk_turn(SdkTurnConfig(manifest_path=manifest_path), adapter)
    )

    assert adapter.created
    assert adapter.stopped
    assert summary["session_id"] == "sdk-session-created"
    assert summary["latest_status"] == "completion_candidate"
    assert (tmp_path / "run.sdk_events.jsonl").exists()
    status = json.loads((tmp_path / "run.sdk_status.json").read_text(encoding="utf-8"))
    assert status["event_count"] == 2
    manifest = load_sdk_session_manifest(manifest_path)
    assert manifest["sdk"]["session_id"] == "sdk-session-created"


def test_run_sdk_turn_resumes_session_and_records_nudge(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path, session_id="sdk-session-existing")
    adapter = FakeAdapter()

    summary = asyncio.run(
        run_sdk_turn(
            SdkTurnConfig(
                manifest_path=manifest_path,
                resume=True,
                nudge_text="You stalled. Continue the assigned task.",
            ),
            adapter,
        )
    )

    assert adapter.resumed
    assert summary["session_id"] == "sdk-session-existing"
    assert summary["latest_status"] == "completion_candidate"
    nudge_records = (tmp_path / "run.nudges.jsonl").read_text(encoding="utf-8")
    assert "You stalled" in nudge_records


def test_monitor_sdk_session_classifies_completion_candidate(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path, session_id="sdk-session-existing")
    events = [
        {
            "timestamp": "2026-07-07T00:00:00+00:00",
            "type": "assistant.message",
            "data": {},
        },
        {"timestamp": "2026-07-07T00:00:01+00:00", "type": "session.idle", "data": {}},
    ]
    (tmp_path / "run.sdk_events.jsonl").write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )

    summary = monitor_sdk_session(manifest_path)

    assert summary["latest_status"] == "completion_candidate"
    assert summary["recommended_coordinator_action"] == "verify-result-or-blocker"


def test_monitor_sdk_session_classifies_repeated_nonprogress(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path, session_id="sdk-session-existing")
    event = {
        "timestamp": "2026-07-07T00:00:00+00:00",
        "type": "assistant.message",
        "data": {"content": "still thinking"},
    }
    (tmp_path / "run.sdk_events.jsonl").write_text(
        "\n".join(json.dumps(event) for _ in range(5)) + "\n",
        encoding="utf-8",
    )

    summary = monitor_sdk_session(manifest_path)

    assert summary["latest_status"] == "nonprogress_stall"
    assert "Stop repeating status" in summary["recommended_nudge"]


def test_monitor_sdk_session_triggers_repeated_nudge_stop_rule(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path, session_id="sdk-session-existing")
    nudge = {"timestamp": "2026-07-07T00:00:00+00:00", "nudge_text": "continue"}
    (tmp_path / "run.nudges.jsonl").write_text(
        json.dumps(nudge) + "\n" + json.dumps(nudge) + "\n",
        encoding="utf-8",
    )

    summary = monitor_sdk_session(manifest_path)

    assert summary["stop_rule_triggered"]
    assert summary["recommended_coordinator_action"] == "stop-and-review"


def test_live_adapter_resolves_relative_working_directory(tmp_path: Path) -> None:
    adapter = LiveCopilotSdkAdapter()
    adapter.permission_handler = type(
        "PermissionHandler",
        (),
        {"approve_all": object()},
    )
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_sdk_session_manifest(manifest_path)
    manifest["sdk"]["working_directory"] = "."

    kwargs = adapter._session_kwargs(manifest)

    assert Path(str(kwargs["working_directory"])).is_absolute()
