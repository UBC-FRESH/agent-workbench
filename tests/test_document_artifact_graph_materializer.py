from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_graph_materializer_resolves_paths_from_project_root(tmp_path: Path) -> None:
    output_dir = tmp_path / "agent_jobs"
    source_summary = (
        "benchmarks/document_library/tsa23_tsr/"
        "p55_wave8_disagreement_verification_qwen36_summary.json"
    )
    command = [
        sys.executable,
        str(ROOT / "scripts" / "materialize_document_artifact_graph_job.py"),
        "--project-root",
        str(ROOT),
        "--output-dir",
        str(output_dir),
        "--job-id",
        "test_graph_document_audit",
        "--marker",
        "TEST_GRAPH_DOCUMENT_AUDIT",
        "--source-summary",
        source_summary,
    ]

    completed = subprocess.run(command, cwd=tmp_path, text=True, check=False)

    assert completed.returncode == 0
    ticket_path = output_dir / "test_graph_document_audit_ticket.md"
    manifest_path = output_dir / "test_graph_document_audit_manifest.json"
    assert ticket_path.exists()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["graph_id"] == "document_artifact_audit_supervisor_graph"
    assert manifest["source_summaries"] == [source_summary]
    assert manifest["audit_job_id"] == "test_graph_document_audit_audit"
    assert manifest["executable_node_ids"] == [
        "materialize_runtime_job",
        "subagent_artifact_audit",
        "write_supervisor_report",
        "validate_and_repair_report",
    ]
    assert (
        "materialize_document_artifact_audit.py"
        in manifest["exact_materializer_command"]
    )
    assert "--project-root" in manifest["exact_materializer_command"]
    assert source_summary in manifest["exact_materializer_command"]
    assert (
        "agent_workbench.cli authority validate" in manifest["exact_validation_command"]
    )
    assert "PYTHONPATH" in manifest["exact_validation_command"]
    assert (
        "verify_document_artifact_audit_report.py"
        in manifest["exact_document_audit_verifier_command"]
    )
    assert (
        "verify_document_artifact_graph_report.py"
        in manifest["exact_graph_report_verifier_command"]
    )
    assert (
        "repair_document_artifact_graph_reports.py"
        in manifest["exact_repair_helper_command"]
    )

    ticket = ticket_path.read_text(encoding="utf-8")
    assert "`materialize_runtime_job`" in ticket
    assert "`subagent_artifact_audit`" in ticket
    assert "`write_supervisor_report`" in ticket
    assert "`validate_and_repair_report`" in ticket
    assert "TEST_GRAPH_DOCUMENT_AUDIT done" in ticket
    assert "python -m agent_workbench.cli authority validate" in ticket
    assert "verify_document_artifact_audit_report.py" in ticket
    assert "verify_document_artifact_graph_report.py" in ticket
    assert "repair_document_artifact_graph_reports.py" in ticket
    assert "only authorized repair mechanism" in ticket
    assert "Materializer success is not completion" in ticket
    assert "audit-report validation alone" in ticket
    assert "This file is mandatory" in ticket
    assert "check that both runtime report files" in ticket
    assert "Do not delete or remove runtime files" in ticket
    assert "overwrite only" in ticket
    assert "Do not rerun the materializer command" in ticket
    assert "write a blocked graph report" in ticket
    assert '"subagent_result"' in ticket
    assert "accepted_after_supervisor_repair" in ticket
    assert "unavailable_supervisor_completed" in ticket


def test_pre_materialized_graph_ticket_hides_setup_from_action_list(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "agent_jobs"
    source_summary = (
        "benchmarks/document_library/tsa23_tsr/"
        "p55_wave8_disagreement_verification_qwen36_summary.json"
    )
    command = [
        sys.executable,
        str(ROOT / "scripts" / "materialize_document_artifact_graph_job.py"),
        "--project-root",
        str(ROOT),
        "--output-dir",
        str(output_dir),
        "--job-id",
        "test_graph_pre_materialized",
        "--marker",
        "TEST_GRAPH_PRE_MATERIALIZED",
        "--source-summary",
        source_summary,
        "--pre-materialize-audit-ticket",
    ]

    completed = subprocess.run(command, cwd=tmp_path, text=True, check=False)

    assert completed.returncode == 0
    ticket = (output_dir / "test_graph_pre_materialized_ticket.md").read_text(
        encoding="utf-8"
    )
    action_section = ticket.split("## Allowed Actions", 1)[1].split(
        "## First-Action Gate", 1
    )[0]
    execute_section = ticket.split(
        "Execute only these supervisor-owned and worker-owned nodes in order.", 1
    )[1].split("## Allowed Actions", 1)[0]
    assert "`materialize_runtime_job`" not in execute_section
    assert "Read the existing audit ticket first." in action_section
    assert "Do not run any materializer command" not in ticket
    assert "Materializer success is not completion" not in ticket
    assert "Do not rerun the materializer command" not in ticket
    assert "Coordinator setup node" in ticket
