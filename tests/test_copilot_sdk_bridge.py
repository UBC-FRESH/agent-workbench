from __future__ import annotations

import asyncio
import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from agent_workbench.cli import run_copilot_sdk_new_manifest
from agent_workbench.copilot_agent_profiles import resolve_agent_profiles
from agent_workbench.copilot_sdk_bridge import (
    LiveCopilotSdkAdapter,
    SdkTurnConfig,
    agent_profiles_event,
    load_sdk_session_manifest,
    monitor_sdk_session,
    render_sdk_compact_transcript_markdown,
    render_sdk_transcript_from_manifest,
    render_sdk_transcript_markdown,
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


def test_new_manifest_cli_generates_validator_accepted_manifest(
    tmp_path: Path, monkeypatch: Any
) -> None:
    monkeypatch.chdir(Path(__file__).parents[1])
    monkeypatch.setenv(
        "AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL", "https://ollama.example.test/v1"
    )
    ticket = tmp_path / "bootstrap_ticket.md"
    ticket.write_text("Implement the bounded bootstrap task.\n", encoding="utf-8")

    exit_code = run_copilot_sdk_new_manifest(
        Namespace(
            ticket=ticket,
            profile="agent-workbench-local-supervisor",
            run_id="p100-bootstrap",
            timeout_seconds=45,
            tool_mode="isolated",
            base_url=None,
            model="qwen3.6:35b-a3b-bf16",
        )
    )

    manifest_path = tmp_path / "p100-bootstrap_manifest.json"
    manifest = load_sdk_session_manifest(manifest_path)
    validation = validate_sdk_session_manifest(manifest, manifest_path=manifest_path)
    assert exit_code == 0
    assert validation.ok, validation.errors
    assert manifest["sdk"]["model"] == "qwen3.6:35b-a3b-bf16"
    assert manifest["sdk"]["provider_config"] == {
        "type": "openai",
        "base_url": "https://ollama.example.test/v1",
        "wire_api": "completions",
    }
    assert manifest["sdk"]["available_tools"] == "builtin-isolated"
    assert manifest["sdk"]["mode"] == "empty"
    assert manifest["sdk"]["excluded_builtin_agents"] == [
        "general-purpose",
        "explore",
        "task",
    ]
    assert manifest["control"]["stall_seconds"] == 45
    assert (
        manifest["sdk"]["agent_profiles"]["selected"]
        == "agent-workbench-local-supervisor"
    )
    assert manifest["sdk"]["agent_profiles"]["source_paths"] == [
        ".github/agents/agent-workbench-local-supervisor.agent.md",
        ".github/agents/qwen3-coder-strict-worker.agent.md",
        ".github/agents/qwen3-coder-next-strict-worker.agent.md",
        ".github/agents/agent-workbench-result-auditor.agent.md",
    ]
    assert manifest["sdk"]["agent_profiles"]["custom_tools"] == [
        "agent_workbench_run_context",
        "agent_workbench_result_contract",
        "agent_workbench_review_subject",
        "agent_workbench_write_result",
        "agent_workbench_validate_result",
    ]
    resolved = resolve_agent_profiles(manifest, manifest_path=manifest_path)
    assert resolved.ok, resolved.errors
    assert [agent["name"] for agent in resolved.custom_agents] == [
        "agent-workbench-local-supervisor",
        "qwen3-coder-strict-worker",
        "qwen3-coder-next-strict-worker",
        "agent-workbench-result-auditor",
    ]
    assert [agent["model"] for agent in resolved.custom_agents] == [
        "qwen3.6:35b-a3b-bf16",
        "qwen3.6:35b-a3b-bf16",
        "qwen3.6:35b-a3b-bf16",
        "qwen3.6:35b-a3b-bf16",
    ]
    adapter = LiveCopilotSdkAdapter()
    adapter.permission_handler = type(
        "PermissionHandler",
        (),
        {"approve_all": object()},
    )
    kwargs = adapter._session_kwargs(manifest)
    assert len(kwargs["tools"]) == 5
    assert "custom:agent_workbench_write_result" in kwargs["available_tools"]
    assert kwargs["excluded_builtin_agents"] == [
        "general-purpose",
        "explore",
        "task",
    ]


def test_new_manifest_cli_workspace_mode_enables_host_tools(
    tmp_path: Path, monkeypatch: Any
) -> None:
    repo_root = Path(__file__).parents[1]
    monkeypatch.chdir(repo_root)
    monkeypatch.setenv(
        "AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL", "https://ollama.example.test/v1"
    )
    ticket = tmp_path / "workspace_ticket.md"
    ticket.write_text("Run the implementation-authorized task.\n", encoding="utf-8")

    exit_code = run_copilot_sdk_new_manifest(
        Namespace(
            ticket=ticket,
            profile="agent-workbench-local-supervisor",
            run_id="workspace-tools",
            timeout_seconds=90,
            tool_mode="workspace",
        )
    )

    manifest = load_sdk_session_manifest(tmp_path / "workspace-tools_manifest.json")
    assert exit_code == 0
    assert manifest["sdk"]["mode"] == "copilot-cli"
    assert manifest["sdk"]["available_tools"] == "default"
    assert manifest["sdk"]["working_directory"] == str(repo_root.resolve())
    adapter = LiveCopilotSdkAdapter()
    adapter.permission_handler = type(
        "PermissionHandler",
        (),
        {"approve_all": object()},
    )
    kwargs = adapter._session_kwargs(manifest)
    assert "available_tools" not in kwargs
    assert kwargs["working_directory"] == str(repo_root.resolve())


def test_new_manifest_cli_accepts_generic_openai_overrides(
    tmp_path: Path, monkeypatch: Any
) -> None:
    monkeypatch.chdir(Path(__file__).parents[1])
    ticket = tmp_path / "vllm_ticket.md"
    ticket.write_text("Run the bounded vLLM task.\n", encoding="utf-8")

    exit_code = run_copilot_sdk_new_manifest(
        Namespace(
            ticket=ticket,
            profile="qwen3-coder-strict-worker",
            run_id="vllm-tools",
            timeout_seconds=60,
            tool_mode="workspace",
            base_url="https://vllm.example.test/v1",
            model="qwen3.6-27b-nvfp4",
        )
    )

    manifest = load_sdk_session_manifest(tmp_path / "vllm-tools_manifest.json")
    assert exit_code == 0
    assert manifest["sdk"]["model"] == "qwen3.6-27b-nvfp4"
    assert manifest["sdk"]["provider_config"] == {
        "type": "openai",
        "base_url": "https://vllm.example.test/v1",
        "wire_api": "completions",
    }
    resolved = resolve_agent_profiles(manifest, manifest_path=tmp_path / "vllm-tools_manifest.json")
    assert resolved.ok, resolved.errors
    assert [agent["model"] for agent in resolved.custom_agents] == [
        "qwen3.6-27b-nvfp4"
    ]


def test_live_adapter_injects_provider_headers_from_local_file(
    tmp_path: Path, monkeypatch: Any
) -> None:
    headers_path = tmp_path / "headers.json"
    headers_path.write_text(json.dumps({"X-Test-Header": "local-secret"}))
    monkeypatch.setenv("AGENT_WORKBENCH_PROVIDER_HEADERS_FILE", str(headers_path))
    adapter = LiveCopilotSdkAdapter()
    adapter.permission_handler = type(
        "PermissionHandler", (), {"approve_all": lambda *args: None}
    )()

    kwargs = adapter._session_kwargs(
        {
            "sdk": {
                "provider_config": {
                    "type": "openai",
                    "base_url": "https://example.test/v1",
                }
            }
        }
    )

    assert kwargs["provider"]["headers"] == {"X-Test-Header": "local-secret"}


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

    assert summary["repeated_nudge_signal"]
    assert summary["recommended_coordinator_action"] == "review-evidence-and-choose-next-action"


def test_render_sdk_transcript_omits_system_by_default(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path, session_id="sdk-session-existing")
    events = [
        {
            "timestamp": "2026-07-07T00:00:00+00:00",
            "type": "system.message",
            "data": {"content": "system prompt"},
        },
        {
            "timestamp": "2026-07-07T00:00:01+00:00",
            "type": "user.message",
            "data": {"content": "Do the assigned task."},
        },
        {
            "timestamp": "2026-07-07T00:00:02+00:00",
            "type": "assistant.message",
            "data": {"content": "I will inspect the worktree."},
        },
        {
            "timestamp": "2026-07-07T00:00:03+00:00",
            "type": "tool.execution_start",
            "data": {
                "tool_name": "powershell",
                "tool_call_id": "call-1",
                "arguments": {"command": "git status"},
            },
        },
        {
            "timestamp": "2026-07-07T00:00:04+00:00",
            "type": "tool.execution_complete",
            "data": {
                "tool_call_id": "call-1",
                "success": True,
                "result": {
                    "contents": [
                        {
                            "cwd": "workspace",
                            "exit_code": 0,
                            "output_preview": "clean",
                        }
                    ]
                },
            },
        },
    ]
    (tmp_path / "run.sdk_events.jsonl").write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )

    transcript, summary = render_sdk_transcript_from_manifest(manifest_path)

    assert summary.entry_count == 4
    assert summary.system_message_count == 1
    assert not summary.system_messages_included
    assert "system prompt" not in transcript
    assert "Coordinator -> Copilot worker" in transcript
    assert "I will inspect the worktree." in transcript
    assert "Tool start: powershell" in transcript
    assert "exit_code: 0" in transcript


def test_render_sdk_transcript_can_include_system_and_exclude_tools() -> None:
    manifest = {
        "run_id": "p71-test-run",
        "sdk": {"session_id": "sdk-session-existing"},
    }
    events = [
        {"timestamp": "t0", "type": "system.message", "data": {"content": "system"}},
        {"timestamp": "t1", "type": "user.message", "data": {"content": "prompt"}},
        {
            "timestamp": "t2",
            "type": "tool.execution_start",
            "data": {"tool_name": "powershell"},
        },
    ]

    transcript, summary = render_sdk_transcript_markdown(
        manifest,
        events,
        include_system=True,
        include_tools=False,
        max_text_chars=4000,
    )

    assert summary.entry_count == 2
    assert summary.system_messages_included
    assert not summary.tool_events_included
    assert "system" in transcript
    assert "prompt" in transcript
    assert "Tool start" not in transcript


def test_render_sdk_compact_transcript_collapses_full_payloads() -> None:
    manifest = {
        "run_id": "p71-test-run",
        "sdk": {"session_id": "sdk-session-existing"},
    }
    events = [
        {
            "timestamp": "t1",
            "type": "user.message",
            "data": {"content": "# Ticket\n\nDo the assigned task."},
        },
        {
            "timestamp": "t2",
            "type": "assistant.message",
            "data": {"content": "I will inspect the worktree."},
        },
        {
            "timestamp": "t3",
            "type": "tool.execution_start",
            "data": {
                "tool_name": "powershell",
                "tool_call_id": "call-1",
                "arguments": {"command": "git status"},
            },
        },
        {
            "timestamp": "t4",
            "type": "tool.execution_complete",
            "data": {
                "tool_call_id": "call-1",
                "success": True,
                "result": {
                    "contents": [
                        {
                            "cwd": "workspace",
                            "exit_code": 0,
                            "output_preview": "working tree clean",
                        }
                    ]
                },
            },
        },
    ]

    transcript, summary = render_sdk_compact_transcript_markdown(
        manifest,
        events,
        include_system=False,
        include_tools=True,
        max_text_chars=4000,
    )

    assert summary.entry_count == 4
    assert "# Copilot SDK Compact Transcript" in transcript
    assert "Ticket" in transcript
    assert "`git status`" in transcript
    assert "`success` - working tree clean" in transcript
    assert "<details>" in transcript
    assert (
        "<summary>Full tool.execution_complete event (call-1)</summary>" in transcript
    )


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


def test_live_adapter_passes_custom_agent_kwargs(tmp_path: Path) -> None:
    profile_path = tmp_path / "worker.agent.md"
    profile_path.write_text(
        "\n".join(
            [
                "---",
                "name: worker",
                "description: Worker profile.",
                "model: qwen3.6",
                "tools: ['read', 'agent_workbench_run_context']",
                "---",
                "",
                "Do the assigned work.",
            ]
        ),
        encoding="utf-8",
    )
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_sdk_session_manifest(manifest_path)
    manifest["_manifest_path"] = str(manifest_path)
    manifest["sdk"]["available_tools"] = ["read"]
    manifest["sdk"]["agent_profiles"] = {
        "source_paths": [str(profile_path)],
        "selected": "worker",
        "default_agent": {"excluded_tools": ["terminal"]},
        "custom_agents_local_only": True,
        "include_sub_agent_streaming_events": True,
        "custom_tools": ["agent_workbench_run_context"],
        "task_overlay": {"text": "Use the result contract tool before finishing."},
    }
    adapter = LiveCopilotSdkAdapter()
    adapter.permission_handler = type(
        "PermissionHandler",
        (),
        {"approve_all": object()},
    )

    kwargs = adapter._session_kwargs(manifest)

    assert kwargs["agent"] == "worker"
    assert kwargs["default_agent"] == {"excluded_tools": ["terminal"]}
    assert kwargs["custom_agents_local_only"] is True
    assert kwargs["include_sub_agent_streaming_events"] is True
    assert kwargs["custom_agents"][0]["name"] == "worker"
    assert "Use the result contract tool" in kwargs["custom_agents"][0]["prompt"]
    assert len(kwargs["tools"]) == 1
    assert "agent_workbench_run_context" in kwargs["available_tools"]


def test_live_adapter_adds_custom_tools_to_builtin_isolated_filter(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "worker.agent.md"
    profile_path.write_text(
        "\n".join(
            [
                "---",
                "name: worker",
                "description: Worker profile.",
                "model: qwen3.6",
                "tools: ['read']",
                "---",
                "",
                "Do the assigned work.",
            ]
        ),
        encoding="utf-8",
    )
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_sdk_session_manifest(manifest_path)
    manifest["_manifest_path"] = str(manifest_path)
    manifest["sdk"]["available_tools"] = "builtin-isolated"
    manifest["sdk"]["agent_profiles"] = {
        "source_paths": [str(profile_path)],
        "selected": "worker",
        "custom_tools": [
            "agent_workbench_run_context",
            "agent_workbench_write_result",
        ],
    }
    adapter = LiveCopilotSdkAdapter()
    adapter.permission_handler = type(
        "PermissionHandler",
        (),
        {"approve_all": object()},
    )

    kwargs = adapter._session_kwargs(manifest)

    available = list(kwargs["available_tools"])
    assert "custom:agent_workbench_run_context" in available
    assert "custom:agent_workbench_write_result" in available


def test_agent_profiles_event_records_manifest_resolved_profiles(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "worker.agent.md"
    profile_path.write_text(
        "\n".join(
            [
                "---",
                "name: worker",
                "description: Worker profile.",
                "model: qwen3.6",
                "tools: ['read', 'agent_workbench_run_context']",
                "---",
                "",
                "Do the assigned work.",
            ]
        ),
        encoding="utf-8",
    )
    manifest_path = write_manifest_fixture(tmp_path)
    manifest = load_sdk_session_manifest(manifest_path)
    manifest["_manifest_path"] = str(manifest_path)
    manifest["sdk"]["agent_profiles"] = {
        "source_paths": [str(profile_path)],
        "selected": "worker",
        "custom_tools": ["agent_workbench_run_context"],
        "task_overlay": {"name": "release-readiness-review"},
    }

    event = agent_profiles_event(manifest)

    assert event is not None
    assert event["type"] == "session.custom_agents_updated"
    assert event["data"]["emitted_by"] == "agent-workbench"
    assert event["data"]["selected_agent"] == "worker"
    assert event["data"]["custom_agents"][0]["name"] == "worker"
    assert event["data"]["custom_tools"] == ["agent_workbench_run_context"]
    assert event["data"]["task_overlay_names"] == ["release-readiness-review"]
    assert len(event["data"]["task_overlay_paths"]) == 1


class FakeRawSdkSession:
    id = "sdk-session-existing"

    def __init__(self) -> None:
        self.handlers: list[Any] = []

    def on(self, handler: Any) -> None:
        self.handlers.append(handler)


class FakeSdkClient:
    def __init__(self) -> None:
        self.resume_kwargs: dict[str, Any] = {}

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def resume_session(self, session_id: str, **kwargs: Any) -> FakeRawSdkSession:
        self.resume_kwargs = {"session_id": session_id, **kwargs}
        return FakeRawSdkSession()


def test_live_adapter_resume_passes_session_kwargs(tmp_path: Path) -> None:
    manifest_path = write_manifest_fixture(tmp_path, session_id="sdk-session-existing")
    manifest = load_sdk_session_manifest(manifest_path)
    manifest["sdk"]["model"] = "qwen3.6"
    adapter = LiveCopilotSdkAdapter()
    adapter.client = FakeSdkClient()
    adapter.permission_handler = type(
        "PermissionHandler",
        (),
        {"approve_all": object()},
    )

    session = asyncio.run(adapter.resume_session(manifest, lambda _event: None))

    assert session.session_id == "sdk-session-existing"
    assert adapter.client.resume_kwargs["session_id"] == "sdk-session-existing"
    assert adapter.client.resume_kwargs["model"] == "qwen3.6"


def test_transcript_counts_custom_agent_and_subagent_events() -> None:
    manifest = {
        "run_id": "p72-test-run",
        "sdk": {"session_id": "sdk-session-existing"},
    }
    events = [
        {
            "timestamp": "t1",
            "type": "session.custom_agents_updated",
            "data": {"custom_agents": [{"name": "worker"}]},
        },
        {
            "timestamp": "t2",
            "type": "assistant.message",
            "data": {"content": "working", "agent_name": "worker"},
        },
        {
            "timestamp": "t3",
            "type": "subagent.started",
            "data": {"content": "auditor started", "subagent_name": "auditor"},
        },
    ]

    transcript, summary = render_sdk_compact_transcript_markdown(
        manifest,
        events,
        include_system=False,
        include_tools=True,
        max_text_chars=4000,
    )

    assert summary.custom_agent_event_count == 1
    assert summary.subagent_event_count == 1
    assert summary.agent_metadata_message_count == 1
    assert "Custom agents updated" in transcript
    assert "Copilot worker (worker)" in transcript
    assert "Subagent event (auditor)" in transcript
