from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from agent_workbench.cli import (
    run_foundrytk_profile_aggregate,
    run_foundrytk_profile_dataset,
    run_foundrytk_profile_optimization_plan,
)
from agent_workbench.foundry_profile_optimization import (
    build_profile_evaluation_aggregate,
    build_profile_evaluation_dataset,
    build_profile_optimization_plan,
    load_profile_evaluation_dataset_jsonl,
    render_profile_evaluation_aggregate_json,
    render_profile_evaluation_aggregate_markdown,
    render_profile_evaluation_dataset_jsonl,
    render_profile_evaluation_dataset_markdown,
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


def test_profile_evaluation_dataset_is_public_safe_jsonl(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path / "run", run_id="dataset-run")

    dataset = build_profile_evaluation_dataset([manifest], repo_root=REPO_ROOT)
    jsonl = render_profile_evaluation_dataset_jsonl(dataset)
    markdown = render_profile_evaluation_dataset_markdown(dataset)
    row = json.loads(jsonl)

    assert dataset.ok
    assert row["schema_version"] == 1
    assert row["run_id"] == "dataset-run"
    assert row["selected_agent"] == "worker"
    assert row["task_overlays"] == ["release-readiness-review"]
    assert row["reliability"]["controller_health"] == "healthy"
    assert row["work_quality"]["accepted_candidate"] is True
    assert row["efficiency"]["event_count"] == 2
    assert row["conversation_shape"]["assistant_messages"] == 1
    assert "# Profile Evaluation Dataset Preview" in markdown
    assert "Do the work." not in markdown


def test_foundrytk_profile_dataset_cli_writes_outputs(
    tmp_path: Path, capsys: object
) -> None:
    manifest = write_manifest(tmp_path / "run", run_id="dataset-cli-run")
    jsonl_output = tmp_path / "dataset.jsonl"
    markdown_output = tmp_path / "dataset.md"

    exit_code = run_foundrytk_profile_dataset(
        Namespace(
            manifest=[manifest],
            repo_root=REPO_ROOT,
            jsonl_output=jsonl_output,
            markdown_output=markdown_output,
        )
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "rows=1 valid=True" in captured.out
    assert jsonl_output.exists()
    assert markdown_output.exists()


def dataset_row(
    run_id: str,
    *,
    selected_agent: str,
    overlay: str,
    controller_health: str = "healthy",
    result_status: str = "accepted-candidate",
    event_count: int = 10,
    assistant_messages: int = 2,
    tool_events: int = 3,
    permission_events: int = 1,
    subagent_events: int = 0,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "phase": "P76",
        "selected_agent": selected_agent,
        "task_overlays": [overlay],
        "custom_tools": ["agent_workbench_write_result"],
        "latest_status": "completion_candidate",
        "controller_health": controller_health,
        "result_status": result_status,
        "reliability": {
            "controller_health": controller_health,
            "has_required_result_status": bool(result_status),
            "custom_agent_events": 1,
            "subagent_events": subagent_events,
        },
        "work_quality": {
            "result_status": result_status,
            "accepted_candidate": result_status == "accepted-candidate",
        },
        "efficiency": {
            "event_count": event_count,
            "assistant_messages": assistant_messages,
            "tool_events": tool_events,
            "permission_events": permission_events,
        },
        "conversation_shape": {
            "user_messages": 1,
            "assistant_messages": assistant_messages,
            "custom_agent_events": 1,
            "subagent_events": subagent_events,
            "agent_metadata_messages": 0,
        },
        "errors": [],
        "warnings": [],
    }


def write_dataset_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_profile_evaluation_aggregate_counts_grouped_cells(tmp_path: Path) -> None:
    rows = [
        dataset_row(
            "p75_mca_lsup_debug_r1",
            selected_agent="local-supervisor",
            overlay="existing-code-debugging",
            result_status="accepted-candidate",
            event_count=12,
        ),
        dataset_row(
            "p75_per_lsup_debug_r1",
            selected_agent="local-supervisor",
            overlay="existing-code-debugging",
            result_status="blocked",
            event_count=8,
            subagent_events=1,
        ),
        dataset_row(
            "p75_mca_raud_release_r1",
            selected_agent="result-auditor",
            overlay="release-readiness-review",
            result_status="needs-supervisor-review",
            event_count=10,
        ),
    ]
    dataset_path = tmp_path / "dataset.jsonl"
    write_dataset_jsonl(dataset_path, rows)

    dataset = load_profile_evaluation_dataset_jsonl(dataset_path)
    aggregate = build_profile_evaluation_aggregate(dataset)
    markdown = render_profile_evaluation_aggregate_markdown(aggregate)
    payload = json.loads(render_profile_evaluation_aggregate_json(aggregate))

    assert aggregate.ok
    assert payload["row_count"] == 3
    assert payload["controller_health"] == {"healthy": 3}
    assert payload["result_status"] == {
        "accepted-candidate": 1,
        "blocked": 1,
        "needs-supervisor-review": 1,
    }
    assert payload["task_family"] == {
        "manifest-contract-audit": 2,
        "profile-evidence-review": 1,
    }
    assert payload["by_profile_result_status"]["local-supervisor"] == {
        "accepted-candidate": 1,
        "blocked": 1,
    }
    assert payload["conversation_shape"]["event_count"]["total"] == 30
    assert payload["conversation_shape"]["event_count"]["average"] == 10
    assert "Prioritize task/profile contract repair" in payload["recommendation"]
    assert "# Profile Evaluation Aggregate Report" in markdown
    assert "raw_transcripts_included: `False`" in markdown
    assert "existing-code-debugging" in markdown


def test_profile_evaluation_aggregate_empty_dataset(tmp_path: Path) -> None:
    dataset_path = tmp_path / "empty.jsonl"
    dataset_path.write_text("", encoding="utf-8")

    aggregate = build_profile_evaluation_aggregate(
        load_profile_evaluation_dataset_jsonl(dataset_path)
    )

    assert aggregate.ok
    assert aggregate.summary["row_count"] == 0
    assert (
        "Collect profile evaluation dataset rows" in aggregate.summary["recommendation"]
    )


def test_profile_evaluation_aggregate_rejects_invalid_jsonl(tmp_path: Path) -> None:
    dataset_path = tmp_path / "bad.jsonl"
    dataset_path.write_text("{not json}\n", encoding="utf-8")

    try:
        load_profile_evaluation_dataset_jsonl(dataset_path)
    except ValueError as exc:
        assert "invalid JSON" in str(exc)
    else:
        raise AssertionError("expected invalid JSONL to fail")


def test_profile_evaluation_aggregate_rejects_private_values(tmp_path: Path) -> None:
    dataset_path = tmp_path / "private.jsonl"
    row = dataset_row(
        "p75_mca_lsup_debug_r1",
        selected_agent=r"C:\Users\somebody\agent",
        overlay="existing-code-debugging",
    )
    write_dataset_jsonl(dataset_path, [row])

    try:
        load_profile_evaluation_dataset_jsonl(dataset_path)
    except ValueError as exc:
        assert "private-looking value" in str(exc)
    else:
        raise AssertionError("expected private-looking dataset value to fail")


def test_foundrytk_profile_aggregate_cli_writes_outputs(
    tmp_path: Path, capsys: object
) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    json_output = tmp_path / "aggregate.json"
    markdown_output = tmp_path / "aggregate.md"
    write_dataset_jsonl(
        dataset_path,
        [
            dataset_row(
                "p75_mca_lsup_debug_r1",
                selected_agent="local-supervisor",
                overlay="existing-code-debugging",
            )
        ],
    )

    exit_code = run_foundrytk_profile_aggregate(
        Namespace(
            dataset=dataset_path,
            json_output=json_output,
            markdown_output=markdown_output,
        )
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "rows=1 valid=True" in captured.out
    assert json_output.exists()
    assert markdown_output.exists()
