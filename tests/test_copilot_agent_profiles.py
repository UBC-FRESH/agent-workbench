from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from agent_workbench.cli import (
    run_copilot_sdk_profile_render,
    run_copilot_sdk_profile_validate,
)
from agent_workbench.copilot_agent_profiles import (
    TASK_OVERLAY_HEADING,
    render_agent_profiles_markdown,
    resolve_agent_profiles,
)
from agent_workbench.copilot_sdk_tools import (
    AGENT_WORKBENCH_TOOL_NAMES,
    result_contract_payload,
    run_context_payload,
    validate_agent_workbench_tool_names,
    validate_result_payload,
)


def write_profile(
    path: Path, *, name: str = "worker", body: str = "Do the work."
) -> None:
    path.write_text(
        "\n".join(
            [
                "---",
                f"name: {name}",
                "description: Test worker.",
                "model: qwen3.6",
                "tools:",
                "  - read",
                "  - agent_workbench_run_context",
                "agents:",
                "  - auditor",
                "---",
                "",
                body,
            ]
        ),
        encoding="utf-8",
    )


def manifest_with_profile(tmp_path: Path, profile_path: Path) -> dict[str, object]:
    return {
        "_manifest_path": str(tmp_path / "manifest.json"),
        "run_id": "p72-test-run",
        "phase": "P72",
        "governing_issue": 473,
        "child_issue": 474,
        "target_project": "agent-workbench",
        "target_task": "profile tests",
        "workspace_root": ".",
        "sdk": {
            "provider": "github-copilot-sdk",
            "session_id": "",
            "resumable": True,
            "model": "",
            "permission_mode": "operator-configured",
            "mode": "empty",
            "base_directory": "runtime/copilot_sdk_home/p72-test-run",
            "agent_profiles": {
                "source_paths": [str(profile_path)],
                "selected": "worker",
                "default_agent": {"excluded_tools": ["terminal"], "ignored": True},
                "custom_agents_local_only": True,
                "include_sub_agent_streaming_events": True,
                "custom_tools": ["agent_workbench_run_context"],
                "task_overlay": {"text": "Repair only the listed defects."},
            },
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
        "state": {},
        "privacy": {"raw_events_local_only": True},
    }


def test_resolve_agent_profiles_parses_frontmatter_and_overlay(tmp_path: Path) -> None:
    profile_path = tmp_path / "worker.agent.md"
    write_profile(profile_path)
    manifest = manifest_with_profile(tmp_path, profile_path)

    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json"
    )

    assert resolved.ok, resolved.errors
    assert resolved.selected_agent == "worker"
    assert resolved.default_agent == {"excluded_tools": ["terminal"]}
    assert resolved.custom_agents_local_only
    assert resolved.include_sub_agent_streaming_events
    assert resolved.custom_tool_names == ("agent_workbench_run_context",)
    agent = resolved.custom_agents[0]
    assert agent["name"] == "worker"
    assert agent["display_name"] if "display_name" in agent else True
    assert TASK_OVERLAY_HEADING in agent["prompt"]
    assert "Repair only the listed defects." in agent["prompt"]
    assert resolved.unsupported_fields["worker"] == ("agents",)
    assert any("ignored is not passed" in warning for warning in resolved.warnings)


def test_resolve_agent_profiles_rejects_missing_name_or_empty_body(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "bad.agent.md"
    profile_path.write_text(
        "---\ndescription: Missing name.\n---\n\n",
        encoding="utf-8",
    )
    manifest = manifest_with_profile(tmp_path, profile_path)
    manifest["sdk"]["agent_profiles"]["selected"] = "missing"

    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json"
    )

    assert not resolved.ok
    assert any("missing name" in error for error in resolved.errors)
    assert any("does not match" in error for error in resolved.errors)


def test_resolve_agent_profiles_requires_custom_tool_registration(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "worker.agent.md"
    write_profile(profile_path)
    manifest = manifest_with_profile(tmp_path, profile_path)
    manifest["sdk"]["agent_profiles"]["custom_tools"] = []

    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json"
    )

    assert not resolved.ok
    assert any("unregistered custom tool" in error for error in resolved.errors)


def test_render_agent_profiles_markdown_is_public_safe_preview(tmp_path: Path) -> None:
    profile_path = tmp_path / "worker.agent.md"
    write_profile(profile_path)
    manifest = manifest_with_profile(tmp_path, profile_path)
    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json"
    )

    preview = render_agent_profiles_markdown(resolved)

    assert "# Copilot SDK Agent Profile Preview" in preview
    assert "worker" in preview
    assert "prompt_chars:" in preview
    assert "Repair only the listed defects." not in preview


def test_agent_workbench_tool_payloads_and_validation(tmp_path: Path) -> None:
    result = tmp_path / "result.md"
    result.write_text(
        "Final status: accepted-candidate\n\nSummary: done\n",
        encoding="utf-8",
    )
    manifest = {
        "run_id": "p72-test-run",
        "phase": "P72",
        "governing_issue": 473,
        "child_issue": 477,
        "target_project": "agent-workbench",
        "target_task": "tool tests",
        "workspace_root": ".",
        "paths": {"result": "result.md", "blocker": "blocker.md"},
        "control": {"stop_condition": "result or blocker"},
    }

    assert set(AGENT_WORKBENCH_TOOL_NAMES)
    assert validate_agent_workbench_tool_names(["missing_tool"]) == ["missing_tool"]
    context = run_context_payload(manifest)
    assert context["run_id"] == "p72-test-run"
    contract = result_contract_payload(manifest)
    assert "accepted-candidate" in contract["required_final_statuses"]
    validation = validate_result_payload(
        manifest,
        base=tmp_path,
        requested_path="result.md",
    )
    assert validation == {"ok": True, "path": str(result.resolve()), "errors": []}

    blocked = validate_result_payload(
        manifest,
        base=tmp_path,
        requested_path="other.md",
    )
    assert not blocked["ok"]
    assert "path is not the manifest result or blocker path" in blocked["errors"]


def test_profile_preview_can_be_serialized_to_manifest_sidecar(tmp_path: Path) -> None:
    profile_path = tmp_path / "worker.agent.md"
    write_profile(profile_path)
    manifest = manifest_with_profile(tmp_path, profile_path)
    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json"
    )

    payload = {
        "agents": resolved.custom_agents,
        "selected": resolved.selected_agent,
        "custom_tools": resolved.custom_tool_names,
    }

    assert json.loads(json.dumps(payload))["selected"] == "worker"


def test_profile_cli_validate_and_render(tmp_path: Path, capsys: object) -> None:
    profile_path = tmp_path / "worker.agent.md"
    write_profile(profile_path)
    manifest = manifest_with_profile(tmp_path, profile_path)
    manifest_path = tmp_path / "manifest.json"
    manifest.pop("_manifest_path")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    output = tmp_path / "profile_preview.md"

    validate_code = run_copilot_sdk_profile_validate(Namespace(manifest=manifest_path))
    render_code = run_copilot_sdk_profile_render(
        Namespace(manifest=manifest_path, output=output)
    )

    captured = capsys.readouterr()
    assert validate_code == 0
    assert render_code == 0
    assert "profiles=1 selected=worker" in captured.out
    assert output.exists()
