from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from agent_workbench.cli import run_foundrytk_profile_optimization_plan
from agent_workbench.foundry_profile_optimization import (
    build_profile_optimization_plan,
    render_profile_optimization_plan_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_profile(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "---",
                "name: worker",
                "description: Test worker.",
                "model: qwen3.6",
                "tools: ['read']",
                "---",
                "",
                "Do the work.",
            ]
        ),
        encoding="utf-8",
    )


def write_manifest(
    root: Path,
    *,
    run_id: str,
    controller_status: str = "completion_candidate",
    observed_errors: list[str] | None = None,
    overlay_name: str = "release-readiness-review",
) -> Path:
    root.mkdir()
    profile = root / "worker.agent.md"
    write_profile(profile)
    task_overlay: dict[str, str] | None = (
        {"name": overlay_name} if overlay_name else None
    )
    agent_profiles = {
        "source_paths": [str(profile)],
        "selected": "worker",
        "custom_tools": [],
    }
    if task_overlay is not None:
        agent_profiles["task_overlay"] = task_overlay
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "phase": "P74",
        "sdk": {
            "provider": "github-copilot-sdk",
            "session_id": f"{run_id}-session",
            "resumable": True,
            "mode": "empty",
            "permission_mode": "operator-configured",
            "agent_profiles": agent_profiles,
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
        "control": {"stop_condition": "result or blocker"},
        "state": {"latest_status": controller_status},
        "privacy": {"raw_events_local_only": True},
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (root / "run.sdk_events.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"type": "session.custom_agents_updated", "data": {}}),
                json.dumps({"type": "assistant.message", "data": {"content": "done"}}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "run.sdk_status.json").write_text(
        json.dumps(
            {
                "latest_status": controller_status,
                "observed_errors": observed_errors or [],
            }
        ),
        encoding="utf-8",
    )
    (root / "result.md").write_text(
        "Final status: accepted-candidate\n\nSummary: done.\n",
        encoding="utf-8",
    )
    return manifest_path


def test_profile_optimization_plan_requires_controller_stability(
    tmp_path: Path,
) -> None:
    manifest = write_manifest(
        tmp_path / "run",
        run_id="error-run",
        controller_status="blocked",
        observed_errors=["model.call_failure"],
    )

    plan = build_profile_optimization_plan([manifest], repo_root=REPO_ROOT)

    assert plan.ok
    assert "Stabilize controller/session health" in plan.recommendation


def test_profile_optimization_plan_requires_named_overlay(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path / "run", run_id="no-overlay", overlay_name="")

    plan = build_profile_optimization_plan([manifest], repo_root=REPO_ROOT)

    assert plan.ok
    assert "named P73 overlays" in plan.recommendation


def test_profile_optimization_plan_renders_public_safe_markdown(
    tmp_path: Path,
) -> None:
    manifest = write_manifest(tmp_path / "run", run_id="ready-run")

    plan = build_profile_optimization_plan([manifest], repo_root=REPO_ROOT)
    markdown = render_profile_optimization_plan_markdown(plan)

    assert plan.ok
    assert "Proceed to an external evaluation design" in plan.recommendation
    assert "# FoundryTK Profile Optimization Plan" in markdown
    assert "reliability" in markdown
    assert "conversation_shape" in markdown
    assert "Do the work." not in markdown


def test_foundrytk_profile_optimization_cli_writes_plan(
    tmp_path: Path, capsys: object
) -> None:
    manifest = write_manifest(tmp_path / "run", run_id="cli-run")
    output = tmp_path / "plan.md"

    exit_code = run_foundrytk_profile_optimization_plan(
        Namespace(manifest=[manifest], repo_root=REPO_ROOT, output=output)
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "runs=1 valid=True" in captured.out
    assert output.exists()
