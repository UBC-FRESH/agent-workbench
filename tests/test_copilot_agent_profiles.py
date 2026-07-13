from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from agent_workbench.cli import (
    run_copilot_sdk_catalog_validate,
    run_copilot_sdk_profile_render,
    run_copilot_sdk_profile_validate,
)
from agent_workbench.copilot_agent_profiles import (
    STANDARD_AGENT_PROFILES,
    STANDARD_TASK_OVERLAYS,
    TASK_OVERLAY_HEADING,
    load_agent_profile_document,
    render_agent_profiles_markdown,
    render_profile_catalog_markdown,
    resolve_agent_profiles,
    validate_standard_profile_catalog,
)
from agent_workbench.copilot_sdk_tools import (
    AGENT_WORKBENCH_TOOL_NAMES,
    result_contract_payload,
    review_subject_payload,
    run_context_payload,
    validate_agent_workbench_tool_names,
    validate_result_payload,
    write_result_payload,
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


def test_agent_profile_normalizes_vscode_ollama_model_id(tmp_path: Path) -> None:
    profile_path = tmp_path / "worker.agent.md"
    write_profile(profile_path)
    text = profile_path.read_text(encoding="utf-8")
    profile_path.write_text(
        text.replace("model: qwen3.6", "model: ollama-models/qwen3.6"),
        encoding="utf-8",
    )

    manifest = manifest_with_profile(tmp_path, profile_path)
    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json"
    )

    assert resolved.ok, resolved.errors
    assert resolved.custom_agents[0]["model"] == "qwen3.6"


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


def test_named_standard_task_overlay_appends_to_selected_profile_only(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.agent.md"
    second = tmp_path / "second.agent.md"
    write_profile(first, name="first", body="First prompt.")
    write_profile(second, name="second", body="Second prompt.")
    manifest = manifest_with_profile(tmp_path, first)
    manifest["sdk"]["agent_profiles"]["source_paths"] = [str(first), str(second)]
    manifest["sdk"]["agent_profiles"]["selected"] = "second"
    manifest["sdk"]["agent_profiles"]["task_overlay"] = {
        "name": "documentation-expansion"
    }
    repo_root = Path(__file__).resolve().parents[1]

    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json", repo_root=repo_root
    )

    assert resolved.ok, resolved.errors
    assert resolved.task_overlay_names == ("documentation-expansion",)
    assert len(resolved.task_overlay_paths) == 1
    first_agent, second_agent = resolved.custom_agents
    assert TASK_OVERLAY_HEADING not in first_agent["prompt"]
    assert TASK_OVERLAY_HEADING in second_agent["prompt"]
    assert "Documentation Expansion Overlay" in second_agent["prompt"]
    assert "Documentation Expansion Overlay" not in second.read_text(encoding="utf-8")


def test_custom_tools_are_attached_to_selected_agent_only(tmp_path: Path) -> None:
    first = tmp_path / "first.agent.md"
    second = tmp_path / "second.agent.md"
    write_profile(first, name="first", body="First prompt.")
    write_profile(second, name="second", body="Second prompt.")
    manifest = manifest_with_profile(tmp_path, first)
    manifest["sdk"]["agent_profiles"]["source_paths"] = [str(first), str(second)]
    manifest["sdk"]["agent_profiles"]["selected"] = "second"
    manifest["sdk"]["agent_profiles"]["custom_tools"] = [
        "agent_workbench_run_context",
        "agent_workbench_review_subject",
        "agent_workbench_write_result",
    ]

    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json"
    )

    assert resolved.ok, resolved.errors
    first_agent, second_agent = resolved.custom_agents
    assert "agent_workbench_write_result" not in first_agent["tools"]
    assert "agent_workbench_run_context" in second_agent["tools"]
    assert "agent_workbench_review_subject" in second_agent["tools"]
    assert "agent_workbench_write_result" in second_agent["tools"]


def test_unknown_standard_task_overlay_reports_available_names(tmp_path: Path) -> None:
    profile_path = tmp_path / "worker.agent.md"
    write_profile(profile_path)
    manifest = manifest_with_profile(tmp_path, profile_path)
    manifest["sdk"]["agent_profiles"]["task_overlay"] = {"name": "missing-overlay"}
    repo_root = Path(__file__).resolve().parents[1]

    resolved = resolve_agent_profiles(
        manifest, manifest_path=tmp_path / "manifest.json", repo_root=repo_root
    )

    assert not resolved.ok
    assert any("missing-overlay" in error for error in resolved.errors)
    assert any("repair-list-execution" in error for error in resolved.errors)
    assert "release-readiness-review" in STANDARD_TASK_OVERLAYS


def test_agent_workbench_tool_payloads_and_validation(tmp_path: Path) -> None:
    result = tmp_path / "result.md"
    result.write_text(
        "Final status: accepted-candidate\n\nSummary: done\n",
        encoding="utf-8",
    )
    subject = tmp_path / "profile_summaries" / "source.md"
    subject.parent.mkdir()
    subject.write_text(
        "# Copilot SDK Profile Run Evidence\n\n- controller_health: `healthy`\n",
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
        "paths": {
            "result": "result.md",
            "blocker": "blocker.md",
            "review_subject": "profile_summaries/source.md",
        },
        "control": {"stop_condition": "result or blocker"},
    }

    assert set(AGENT_WORKBENCH_TOOL_NAMES)
    assert validate_agent_workbench_tool_names(["missing_tool"]) == ["missing_tool"]
    context = run_context_payload(manifest)
    assert context["run_id"] == "p72-test-run"
    assert context["artifact_paths"]["result"] == "result.md"
    assert context["review_subject"]["read_tool"] == "agent_workbench_review_subject"
    contract = result_contract_payload(manifest)
    assert "accepted-candidate" in contract["required_final_statuses"]
    assert contract["review_subject_tool"] == "agent_workbench_review_subject"
    assert contract["write_tool"] == "agent_workbench_write_result"
    subject_payload = review_subject_payload(manifest, base=tmp_path)
    assert subject_payload["ok"], subject_payload["errors"]
    assert subject_payload["declared_path"] == "profile_summaries/source.md"
    assert subject_payload["kind"] == "profile-run-summary"
    assert subject_payload["resolved_path"] == "profile_summaries/source.md"
    assert "controller_health" in subject_payload["content"]
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


def test_review_subject_tool_rejects_missing_subject(tmp_path: Path) -> None:
    manifest = {
        "paths": {"review_subject": "profile_summaries/missing.md"},
    }

    payload = review_subject_payload(manifest, base=tmp_path)

    assert not payload["ok"]
    assert "review subject does not exist" in payload["errors"]


def test_review_subject_tool_rejects_current_run_output(tmp_path: Path) -> None:
    result = tmp_path / "result.md"
    result.write_text("Final status: accepted-candidate\n", encoding="utf-8")
    manifest = {
        "paths": {
            "result": "result.md",
            "blocker": "blocker.md",
            "review_subject": "result.md",
        },
    }

    payload = review_subject_payload(manifest, base=tmp_path)

    assert not payload["ok"]
    assert "review subject points at current-run output" in payload["errors"]


def test_review_subject_tool_rejects_private_path(tmp_path: Path) -> None:
    manifest = {
        "paths": {"review_subject": r"C:\Users\somebody\source.md"},
    }

    payload = review_subject_payload(manifest, base=tmp_path)

    assert not payload["ok"]
    assert "review subject path is private-looking" in payload["errors"]


def test_review_subject_tool_allows_runtime_sibling_subject(tmp_path: Path) -> None:
    manifest_base = tmp_path / "runtime" / "current" / "manifests"
    subject = tmp_path / "runtime" / "previous" / "profile_summaries" / "source.md"
    subject.parent.mkdir(parents=True)
    subject.write_text("controller_health: healthy\n", encoding="utf-8")
    manifest = {
        "paths": {"review_subject": "../../previous/profile_summaries/source.md"},
    }

    payload = review_subject_payload(manifest, base=manifest_base)

    assert payload["ok"], payload["errors"]
    assert payload["allowed_root"] == "runtime"
    assert payload["resolved_path"] == "source.md"


def test_review_subject_tool_rejects_runtime_escape(tmp_path: Path) -> None:
    manifest_base = tmp_path / "runtime" / "current" / "manifests"
    subject = tmp_path / "outside.md"
    subject.write_text("outside runtime\n", encoding="utf-8")
    manifest = {
        "paths": {"review_subject": "../../../outside.md"},
    }

    payload = review_subject_payload(manifest, base=manifest_base)

    assert not payload["ok"]
    assert "review subject is outside allowed root" in payload["errors"]


def test_review_subject_tool_returns_bounded_content(tmp_path: Path) -> None:
    subject = tmp_path / "profile_summaries" / "source.md"
    subject.parent.mkdir()
    subject.write_text("a" * 14000, encoding="utf-8")
    manifest = {
        "paths": {"review_subject": "profile_summaries/source.md"},
    }

    payload = review_subject_payload(manifest, base=tmp_path, max_chars=100)

    assert payload["ok"], payload["errors"]
    assert payload["content_chars"] == 100
    assert payload["truncated"] is True
    assert payload["content"] == "a" * 100


def test_agent_workbench_write_result_tool_is_path_constrained(tmp_path: Path) -> None:
    manifest = {
        "paths": {"result": "result.md", "blocker": "blocker.md"},
    }

    written = write_result_payload(
        manifest,
        base=tmp_path,
        requested_path="result.md",
        content="Final status: accepted-candidate\n\nSummary: done\n",
    )

    assert written["ok"]
    assert (tmp_path / "result.md").exists()

    blocked = write_result_payload(
        manifest,
        base=tmp_path,
        requested_path="other.md",
        content="Final status: accepted-candidate\n\nSummary: done\n",
    )

    assert not blocked["ok"]
    assert not (tmp_path / "other.md").exists()
    assert "path is not the manifest result or blocker path" in blocked["errors"]


def test_agent_workbench_write_result_rejects_invalid_content(tmp_path: Path) -> None:
    manifest = {
        "paths": {"result": "result.md", "blocker": "blocker.md"},
    }

    missing_status = write_result_payload(
        manifest,
        base=tmp_path,
        requested_path="result.md",
        content="Summary: done\n",
    )

    assert not missing_status["ok"]
    assert not (tmp_path / "result.md").exists()
    assert "missing 'Final status:' line" in missing_status["errors"]


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
    assert "task_overlays=" in captured.out
    assert output.exists()


def test_standard_profile_catalog_validation_is_public_safe() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    validation = validate_standard_profile_catalog(repo_root=repo_root)
    preview = render_profile_catalog_markdown(validation)

    assert validation.ok, validation.errors
    assert {entry.name for entry in validation.profiles} == set(STANDARD_AGENT_PROFILES)
    assert {name for name, _path, exists in validation.overlays if exists} == set(
        STANDARD_TASK_OVERLAYS
    )
    supervisor = next(
        entry
        for entry in validation.profiles
        if entry.name == "agent-workbench-local-supervisor"
    )
    assert supervisor.model
    assert "agent" in supervisor.tools
    assert "# Agent Workbench Profile Catalog Preview" in preview
    assert "prompt_chars:" in preview
    assert "Your authority is below" not in preview


def test_profile_catalog_cli_validate_writes_preview(
    tmp_path: Path, capsys: object
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output = tmp_path / "catalog_preview.md"

    exit_code = run_copilot_sdk_catalog_validate(
        Namespace(repo_root=repo_root, output=output)
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "profiles=4 overlays=7" in captured.out
    assert output.exists()
    assert "agent-workbench-result-auditor" in output.read_text(encoding="utf-8")


def test_result_auditor_profile_documents_primary_mode_contract() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    profile_path = repo_root / STANDARD_AGENT_PROFILES["agent-workbench-result-auditor"]

    document = load_agent_profile_document(profile_path)

    assert "When you are the selected primary profile" in document.prompt
    assert "agent_workbench_result_contract" in document.prompt
    assert "agent_workbench_write_result" in document.prompt
    assert "profile-evidence-review" in document.prompt
    assert "do not spawn subagents" in document.prompt
