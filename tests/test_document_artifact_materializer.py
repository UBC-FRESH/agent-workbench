from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agent_workbench.authority import validate_supervisor_job_contract


ROOT = Path(__file__).resolve().parents[1]


def test_materializer_resolves_paths_from_project_root(tmp_path: Path) -> None:
    output_dir = tmp_path / "agent_jobs"
    source_summary = (
        "benchmarks/document_library/tsa23_tsr/"
        "p55_wave8_disagreement_verification_qwen36_summary.json"
    )
    command = [
        sys.executable,
        str(ROOT / "scripts" / "materialize_document_artifact_audit.py"),
        "--project-root",
        str(ROOT),
        "--output-dir",
        str(output_dir),
        "--job-id",
        "test_document_audit",
        "--marker",
        "TEST_DOCUMENT_AUDIT",
        "--source-summary",
        source_summary,
    ]

    completed = subprocess.run(command, cwd=tmp_path, text=True, check=False)

    assert completed.returncode == 0
    contract_path = output_dir / "test_document_audit_contract.json"
    ticket_path = output_dir / "test_document_audit_ticket.md"
    report_path = output_dir / "test_document_audit_report.json"
    assert contract_path.exists()
    assert ticket_path.exists()
    assert report_path.parent == output_dir

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    result = validate_supervisor_job_contract(contract)
    assert result.ok, result.errors
    assert contract["inputs"][0]["path"] == source_summary
    assert contract["public_safety"]["tracked_artifact"] is False

    ticket = ticket_path.read_text(encoding="utf-8")
    assert f"`{source_summary}`" in ticket
    assert "parse-failed" in ticket
    assert "needs_coordinator_review" in ticket
    assert "gate_result` is blank, missing" in ticket
    assert '"source_gate_result": "wave8-quote-repair-needed"' in ticket
    assert '"source_resolved_fields": 6' in ticket
    assert "subagent_result_status" in ticket
    assert "accepted_after_supervisor_repair" in ticket
    assert "unavailable_supervisor_completed" in ticket
    assert "TEST_DOCUMENT_AUDIT done" in ticket
