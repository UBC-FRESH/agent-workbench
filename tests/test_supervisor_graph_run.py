from __future__ import annotations

import json
from types import SimpleNamespace
from pathlib import Path

from agent_workbench.cli import (
    run_supervisor_document_audit_graph,
    run_supervisor_document_audit_graph_summary,
)
from agent_workbench.supervisor_graph_run import (
    DocumentAuditGraphRunConfig,
    build_run_plan,
    run_checked,
    summarize_document_audit_graph_run,
    summarize_existing_document_audit_graph,
)


ROOT = Path(__file__).resolve().parents[1]


def test_document_audit_graph_live_run_requires_budget_record(capsys) -> None:
    args = SimpleNamespace(dry_run=False, budget_record=None)

    exit_code = run_supervisor_document_audit_graph(args)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "--budget-record is required" in captured.err


def test_document_audit_graph_summary_requires_budget_record(capsys) -> None:
    args = SimpleNamespace(budget_record=None)

    exit_code = run_supervisor_document_audit_graph_summary(args)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "--budget-record is required" in captured.err


def test_document_audit_graph_run_plan_uses_bridge_without_maximize(
    tmp_path: Path,
) -> None:
    config = DocumentAuditGraphRunConfig(
        project_root=tmp_path,
        repo_root=tmp_path,
        job_id="p57_example",
        marker="P57_EXAMPLE",
        phase="P57",
        task_id="P57.4",
        title="Example graph run",
        source_summaries=(Path("benchmarks/source_a.json"),),
        output_dir=Path("runtime/agent_jobs"),
        summary_output=Path("benchmarks/summary.json"),
        token_dir=Path("runtime/supervisor_tokens/p57_example"),
        expected_model="qwen3.6:35b-a3b-bf16",
        bridge_prompt="Execute the full graph ticket to completion.",
        dry_run=True,
    )

    plan = build_run_plan(config)

    bridge_command = plan["commands"]["bridge"]
    assert "--maximize" not in bridge_command
    assert "--expected-model" in bridge_command
    assert "qwen3.6:35b-a3b-bf16" in bridge_command
    assert "--prompt" in bridge_command
    assert "Execute the full graph ticket to completion." in bridge_command
    assert "--workspace-root" in bridge_command
    assert str(tmp_path.resolve()) in bridge_command
    assert plan["paths"]["ticket"] == "runtime/agent_jobs/p57_example_ticket.md"
    assert plan["paths"]["summary_output"] == "benchmarks/summary.json"
    assert plan["runtime_only"]["raw_transcripts_excluded"] is True


def test_document_audit_graph_plan_can_pre_materialize_audit_ticket(
    tmp_path: Path,
) -> None:
    config = DocumentAuditGraphRunConfig(
        project_root=tmp_path,
        repo_root=tmp_path,
        job_id="p57_pre_materialized",
        marker="P57_PRE_MATERIALIZED",
        phase="P57",
        task_id="P57.5",
        title="Pre-materialized graph run",
        source_summaries=(Path("benchmarks/source_a.json"),),
        output_dir=Path("runtime/agent_jobs"),
        summary_output=Path("benchmarks/summary.json"),
        token_dir=Path("runtime/supervisor_tokens/p57_pre_materialized"),
        pre_materialize_audit_ticket=True,
        dry_run=True,
    )

    plan = build_run_plan(config)

    assert "--pre-materialize-audit-ticket" in plan["commands"]["materialize"]
    assert plan["pre_materialized_audit_ticket"] is True
    assert "--pre-materialize-audit-ticket" not in plan["commands"]["bridge"]


def test_run_checked_quiet_captures_failure_output(tmp_path: Path) -> None:
    script = tmp_path / "fail.py"
    script.write_text(
        "import sys\nprint('short stdout')\nprint('short stderr', file=sys.stderr)\nsys.exit(3)\n",
        encoding="utf-8",
    )

    try:
        run_checked(["python", str(script)], tmp_path, quiet=True)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("run_checked should have raised RuntimeError")

    assert "exit code 3" in message
    assert "short stdout" in message
    assert "short stderr" in message


def test_document_audit_graph_summary_extracts_cost_and_quality(
    tmp_path: Path,
) -> None:
    bridge_report = tmp_path / "bridge.md"
    bridge_report.write_text(
        """# Copilot Chat Bridge Supervisor Report

marker: P57_EXAMPLE
status: accepted-candidate
expected_model: qwen3.6:35b-a3b-bf16
resolved_model: qwen3.6:35b-a3b-bf16
model_match: true
permission_levels: autopilot
completed: true
final_marker_present: true

## Observed Commands

- `python scripts\\materialize_document_artifact_audit.py`

## Tool Names

- `runSubagent`
""",
        encoding="utf-8",
    )
    audit_report = tmp_path / "audit.json"
    audit_report.write_text(
        json.dumps(
            {
                "verification": {
                    "score": 1.0,
                    "all_decisions_consistent_with_gate": True,
                    "subagent_result_status": "accepted_after_supervisor_repair",
                    "audit_items": [
                        {"auditor_decision": "needs_coordinator_review"},
                        {"auditor_decision": "quote_repair_required"},
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    graph_report = tmp_path / "graph.json"
    graph_report.write_text(
        json.dumps(
            {
                "graph_id": "document_artifact_audit_supervisor_graph",
                "subagent_result": {
                    "status": "accepted_after_supervisor_repair",
                    "repair_required": True,
                    "summary": "Supervisor repaired worker output.",
                },
            }
        ),
        encoding="utf-8",
    )
    token_record = tmp_path / "tokens.json"
    token_record.write_text(
        json.dumps(
            {
                "usage": {
                    "supervisor_input_tokens": 1000,
                    "supervisor_cached_input_tokens": 2000,
                    "supervisor_output_tokens": 100,
                    "supervisor_reasoning_output_tokens": 50,
                    "codex_total_token_delta": 3150,
                },
                "prices": {
                    "supervisor_input_price_per_1m_usd": 1.0,
                    "supervisor_cached_input_price_per_1m_usd": 0.1,
                    "supervisor_output_price_per_1m_usd": 10.0,
                },
            }
        ),
        encoding="utf-8",
    )
    plan = {"source_summaries": ["source_a.json", "source_b.json"]}

    summary = summarize_document_audit_graph_run(
        job_id="p57_example",
        phase="P57",
        task_id="P57.4",
        plan=plan,
        bridge_report=bridge_report,
        audit_report=audit_report,
        graph_report=graph_report,
        token_record=token_record,
    )

    assert summary["accepted_candidate"] is True, summary["validation_results"]
    assert summary["quality_validated_candidate"] is True
    assert summary["protocol_accepted_candidate"] is True
    assert summary["economics_usable"] is True
    assert summary["final_decision"] == "accepted_economics_evidence"
    assert summary["rejection_reasons"] == []
    assert summary["model"] == "qwen3.6:35b-a3b-bf16"
    assert summary["model_provenance"] == {
        "expected_model": "qwen3.6:35b-a3b-bf16",
        "observed_model": "qwen3.6:35b-a3b-bf16",
        "authoritative_model": "qwen3.6:35b-a3b-bf16",
        "source": "copilot_chat_bridge_report",
        "match_status": "matched",
        "self_reported_model": "",
        "self_report_status": "not_applicable",
    }
    assert summary["subagent_tool_observed"] is True
    assert summary["materializer_command_count"] == 1
    assert summary["supervisor_report_score"] == 1.0
    assert summary["audit_decision_breakdown"] == {
        "needs_coordinator_review": 1,
        "quote_repair_required": 1,
    }
    assert summary["token_costs"]["estimated_paid_cost_usd"] == 0.0027
    assert summary["token_costs"]["estimated_paid_cost_per_source_artifact_usd"] == 0.00135
    assert summary["token_costs"]["economics_usable"] is True


def test_document_audit_graph_summary_marks_failed_zero_token_span_unusable(
    tmp_path: Path,
) -> None:
    bridge_report = tmp_path / "bridge.md"
    bridge_report.write_text(
        """# Copilot Chat Bridge Supervisor Report

status: needs-supervisor-review
resolved_model: qwen3.6:35b-a3b-bf16
permission_levels: autopilot
final_marker_present: true

## Observed Commands

- `python scripts\\materialize_document_artifact_audit.py`

## Tool Names

- `runSubagent`
""",
        encoding="utf-8",
    )
    audit_report = tmp_path / "audit.json"
    audit_report.write_text(
        json.dumps(
            {
                "verification": {
                    "score": 1.0,
                    "subagent_result_status": "accepted_after_supervisor_repair",
                    "audit_items": [],
                }
            }
        ),
        encoding="utf-8",
    )
    graph_report = tmp_path / "missing_graph.json"
    token_record = tmp_path / "tokens.json"
    token_record.write_text(
        json.dumps(
            {
                "usage": {
                    "supervisor_input_tokens": 0,
                    "supervisor_cached_input_tokens": 0,
                    "supervisor_output_tokens": 0,
                    "supervisor_reasoning_output_tokens": 0,
                    "codex_total_token_delta": 0,
                },
                "prices": {},
            }
        ),
        encoding="utf-8",
    )

    summary = summarize_document_audit_graph_run(
        job_id="p57_failed",
        phase="P57",
        task_id="P57.5",
        plan={"source_summaries": ["source_a.json"]},
        bridge_report=bridge_report,
        audit_report=audit_report,
        graph_report=graph_report,
        token_record=token_record,
        validation_results={
            "authority_validation": {
                "returncode": 1,
                "stderr": "failed at "
                + "C:"
                + r"\Users\example\Projects\agent-workbench\script.py",
            }
        },
        failure="authority_validation failed",
    )

    assert summary["accepted_candidate"] is False
    assert summary["quality_validated_candidate"] is False
    assert summary["protocol_accepted_candidate"] is False
    assert summary["economics_usable"] is False
    assert summary["final_decision"] == "rejected"
    assert "authority_validation failed" in summary["rejection_reasons"]
    assert summary["failure"] == "authority_validation failed"
    assert summary["token_costs"]["economics_usable"] is False
    assert "not usable" in summary["token_costs"]["not_usable_reason"]
    assert "C:\\Users" not in summary["validation_results"]["authority_validation"]["stderr"]


def test_document_audit_graph_model_mismatch_is_protocol_rejection(
    tmp_path: Path,
) -> None:
    bridge_report = tmp_path / "bridge.md"
    bridge_report.write_text(
        """# Copilot Chat Bridge Supervisor Report

status: accepted-candidate
expected_model: qwen3.6:35b-a3b-bf16
resolved_model: qwen3-coder:latest
model_match: false
permission_levels: autopilot
final_marker_present: true
""",
        encoding="utf-8",
    )
    token_record = tmp_path / "tokens.json"
    token_record.write_text(
        json.dumps(
            {
                "usage": {
                    "supervisor_input_tokens": 100,
                    "supervisor_cached_input_tokens": 0,
                    "supervisor_output_tokens": 10,
                    "supervisor_reasoning_output_tokens": 0,
                    "codex_total_token_delta": 110,
                },
                "prices": {
                    "supervisor_input_price_per_1m_usd": 1.0,
                    "supervisor_cached_input_price_per_1m_usd": 0.1,
                    "supervisor_output_price_per_1m_usd": 10.0,
                },
            }
        ),
        encoding="utf-8",
    )

    summary = summarize_document_audit_graph_run(
        job_id="p57_model_mismatch",
        phase="P57",
        task_id="P57.5",
        plan={"source_summaries": ["source_a.json"]},
        bridge_report=bridge_report,
        audit_report=tmp_path / "audit.json",
        graph_report=tmp_path / "graph.json",
        token_record=token_record,
    )

    assert summary["accepted_candidate"] is False
    assert summary["quality_validated_candidate"] is True
    assert summary["protocol_accepted_candidate"] is False
    assert summary["economics_usable"] is False
    assert summary["final_decision"] == "quality_valid_protocol_rejected"
    assert "model_provenance_mismatch" in summary["rejection_reasons"]


def test_summarize_existing_document_audit_graph_uses_external_token_record(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "runtime" / "agent_jobs"
    output_dir.mkdir(parents=True)
    token_dir = tmp_path / "runtime" / "supervisor_tokens" / "external"
    token_dir.mkdir(parents=True)
    job_id = "p57_external"
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "summary_id": "ready_scale_case",
                "document_id": "doc",
                "gate_result": "ready-to-scale-after-clean-validation",
                "recommended_next_move": "Scale this packet size to the next wave.",
                "totals": {
                    "needs_supervisor_fields": 0,
                    "quote_over_limit_fields": 0,
                    "resolved_fields": 7,
                },
            }
        ),
        encoding="utf-8",
    )
    (output_dir / f"{job_id}_bridge_report.md").write_text(
        """# Copilot Chat Bridge Supervisor Report

marker: P57_EXTERNAL
status: accepted-candidate
resolved_model: qwen3.6:35b-a3b-bf16
permission_levels: autopilot
completed: true
final_marker_present: true

## Observed Commands

- `python scripts\\materialize_document_artifact_audit.py`

## Tool Names

- `runSubagent`
""",
        encoding="utf-8",
    )
    (output_dir / f"{job_id}_audit_report.json").write_text(
        json.dumps(
            {
                "report_id": f"{job_id}_report",
                "contract_id": job_id,
                "supervisor_role": "supervisor",
                "final_signal": "job_complete_with_caveats",
                "completed_nodes": [
                    {
                        "node_id": "source_fact_extract",
                        "owner_role": "supervisor",
                        "status": "completed",
                    },
                    {
                        "node_id": "artifact_audit",
                        "owner_role": "worker",
                        "status": "completed",
                    },
                ],
                "artifacts": [
                    {
                        "artifact_id": "supervisor_report",
                        "path": f"runtime/agent_jobs/{job_id}_audit_report.json",
                        "role": "report",
                    }
                ],
                "verification": {
                    "checks_run": ["source artifacts read"],
                    "score": 1.0,
                    "subagent_invocation_attempted": True,
                    "subagent_name": "agent-workbench-result-auditor",
                    "subagent_invocation_observed_by_supervisor": True,
                    "subagent_payload_excerpt": "Audited one ready-scale source summary.",
                    "subagent_result_status": "accepted_without_repair",
                    "subagent_repair_summary": "",
                    "audit_items": [
                        {
                            "item_id": "source_summary_1",
                            "source_path": "source.json",
                            "source_summary_id": "ready_scale_case",
                            "source_document_id": "doc",
                            "source_gate_result": (
                                "ready-to-scale-after-clean-validation"
                            ),
                            "source_recommended_next_move": (
                                "Scale this packet size to the next wave."
                            ),
                            "source_needs_supervisor_fields": 0,
                            "source_quote_over_limit_fields": 0,
                            "source_resolved_fields": 7,
                            "auditor_decision": "ready_to_scale",
                            "decision_consistent_with_gate": True,
                            "source_fact_copy_ok": True,
                        }
                    ],
                    "all_decisions_consistent_with_gate": True,
                },
                "escalations": [],
                "public_safety": {
                    "tracked_artifact": False,
                    "raw_transcript_policy": (
                        "Runtime-only; do not copy raw transcripts into tracked files."
                    ),
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / f"{job_id}_graph_report.json").write_text(
        json.dumps(
            {
                "report_id": f"{job_id}_graph_report",
                "graph_id": "document_artifact_audit_supervisor_graph",
                "audit_job_id": job_id,
                "supervisor_role": "supervisor",
                "final_signal": "job_complete_with_caveats",
                "completed_graph_nodes": [
                    {"node_id": "materialize_runtime_job", "status": "completed"},
                    {"node_id": "subagent_artifact_audit", "status": "completed"},
                    {"node_id": "write_supervisor_report", "status": "completed"},
                    {"node_id": "validate_and_repair_report", "status": "completed"},
                ],
                "audit_report_path": f"runtime/agent_jobs/{job_id}_audit_report.json",
                "authority_validation": {
                    "attempted": True,
                    "passed_after_repair": True,
                    "error_excerpt": "",
                },
                "subagent_invocation_observed_by_supervisor": True,
                "subagent_result": {
                    "status": "accepted_without_repair",
                    "repair_required": False,
                    "summary": "Subagent output was accepted without repair.",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    external_token_record = token_dir / "external.tokens.json"
    external_token_record.write_text(
        json.dumps(
            {
                "usage": {
                    "supervisor_input_tokens": 1000,
                    "supervisor_cached_input_tokens": 0,
                    "supervisor_output_tokens": 100,
                    "supervisor_reasoning_output_tokens": 0,
                    "codex_total_token_delta": 1100,
                },
                "prices": {
                    "supervisor_input_price_per_1m_usd": 1.0,
                    "supervisor_cached_input_price_per_1m_usd": 0.1,
                    "supervisor_output_price_per_1m_usd": 10.0,
                },
            }
        ),
        encoding="utf-8",
    )
    config = DocumentAuditGraphRunConfig(
        project_root=tmp_path,
        repo_root=ROOT,
        job_id=job_id,
        marker="P57_EXTERNAL",
        phase="P57",
        task_id="P57.5",
        title="External checkpoint summary",
        source_summaries=(Path("source.json"),),
        output_dir=Path("runtime/agent_jobs"),
        summary_output=Path("benchmarks/summary.json"),
        token_dir=Path("runtime/supervisor_tokens/internal"),
    )

    summary = summarize_existing_document_audit_graph(
        config,
        token_record=external_token_record,
    )

    assert summary["accepted_candidate"] is True, summary["validation_results"]
    assert summary["quality_validated_candidate"] is True
    assert summary["protocol_accepted_candidate"] is True
    assert summary["economics_usable"] is True
    assert summary["final_decision"] == "accepted_economics_evidence"
    assert summary["authority_validation_passed"] is True
    assert summary["document_audit_verifier_passed"] is True
    assert summary["document_graph_report_verifier_passed"] is True
    assert summary["token_costs"]["economics_usable"] is True
    assert summary["token_costs"]["measurement_boundary"] == "external_coordinator_span"
    assert summary["token_costs"]["estimated_paid_cost_usd"] == 0.002
