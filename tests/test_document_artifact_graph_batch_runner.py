from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write_child_summary(path: Path, job_id: str, source_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "summary_id": f"{job_id}_summary",
                "job_id": job_id,
                "status": "accepted-candidate",
                "model": "qwen3.6:35b-a3b-bf16",
                "model_provenance": {
                    "observed_model": "qwen3.6:35b-a3b-bf16",
                },
                "source_count": source_count,
                "accepted_candidate": True,
                "subagent_tool_observed": True,
                "materializer_command_count": 0,
                "authority_validation_passed": True,
                "document_audit_verifier_passed": True,
                "document_graph_report_verifier_passed": True,
                "supervisor_report_score": 1.0,
                "audit_decision_breakdown": {
                    "needs_coordinator_review": source_count,
                },
                "subagent_outcome": {
                    "repair_required": False,
                },
            }
        ),
        encoding="utf-8",
    )


def test_batch_runner_summary_only_aggregates_child_summaries(
    tmp_path: Path,
) -> None:
    manifest = {
        "job_id": "batch",
        "marker": "BATCH",
        "phase": "P57",
        "task_id": "P57.5",
        "title": "Batch",
        "jobs": [
            {"job_id": "batch_split_01", "marker": "BATCH_SPLIT_01"},
            {"job_id": "batch_split_02", "marker": "BATCH_SPLIT_02"},
        ],
    }
    manifest_path = tmp_path / "batch_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    summary_dir = tmp_path / "summaries"
    write_child_summary(summary_dir / "batch_split_01_v1_internal_summary.json", "batch_split_01_v1", 5)
    write_child_summary(summary_dir / "batch_split_02_v1_internal_summary.json", "batch_split_02_v1", 4)
    token_record = tmp_path / "tokens.json"
    token_record.write_text(
        json.dumps(
            {
                "usage": {
                    "supervisor_input_tokens": 1000,
                    "supervisor_cached_input_tokens": 2000,
                    "supervisor_output_tokens": 100,
                    "supervisor_reasoning_output_tokens": 0,
                    "codex_total_token_delta": 3100,
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
    output = tmp_path / "summary.json"

    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_document_artifact_graph_batch.py"),
        "--project-root",
        str(tmp_path),
        "--batch-manifest",
        "batch_manifest.json",
        "--run-suffix",
        "v1",
        "--summary-dir",
        "summaries",
        "--summary-output",
        "summary.json",
        "--token-record",
        "tokens.json",
        "--summary-only",
    ]

    completed = subprocess.run(command, cwd=tmp_path, text=True, capture_output=True)

    assert completed.returncode == 0, completed.stderr
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["accepted_candidate"] is True
    assert summary["source_count"] == 9
    assert summary["child_run_count"] == 2
    assert summary["subagent_tool_observed_count"] == 2
    assert summary["audit_decision_breakdown"] == {"needs_coordinator_review": 9}
    assert summary["token_costs"]["estimated_paid_cost_usd"] == 0.0022
    assert summary["token_costs"]["measurement_boundary"] == "external_coordinator_span"


def test_batch_runner_dry_run_skips_existing_accepted_child(
    tmp_path: Path,
) -> None:
    manifest = {
        "job_id": "batch",
        "marker": "BATCH",
        "phase": "P57",
        "task_id": "P57.5",
        "title": "Batch",
        "jobs": [
            {
                "job_id": "batch_split_01",
                "marker": "BATCH_SPLIT_01",
                "source_summaries": ["source-a.json"],
            },
            {
                "job_id": "batch_split_02",
                "marker": "BATCH_SPLIT_02",
                "source_summaries": ["source-b.json"],
            },
        ],
    }
    manifest_path = tmp_path / "batch_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    summary_dir = tmp_path / "summaries"
    write_child_summary(summary_dir / "batch_split_01_v1_internal_summary.json", "batch_split_01_v1", 1)
    output = tmp_path / "summary.json"

    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_document_artifact_graph_batch.py"),
        "--project-root",
        str(tmp_path),
        "--batch-manifest",
        "batch_manifest.json",
        "--run-suffix",
        "v1",
        "--summary-dir",
        "summaries",
        "--summary-output",
        "summary.json",
        "--dry-run",
        "--skip-existing-accepted",
    ]

    completed = subprocess.run(command, cwd=tmp_path, text=True, capture_output=True)

    assert completed.returncode == 0, completed.stderr
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["child_run_results"][0]["skipped_existing_accepted"] is True
    assert "command" in summary["child_run_results"][1]
