from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_graph_repair_helper_overwrites_reports_without_deleting(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "summary_id": "summary-1",
                "document_id": "doc-1",
                "gate_result": "quote-repair-needed",
                "recommended_next_move": "repair quotes",
                "totals": {
                    "needs_supervisor_fields": 2,
                    "quote_over_limit_fields": 1,
                    "resolved_fields": 3,
                },
            }
        ),
        encoding="utf-8",
    )
    audit_report = tmp_path / "audit.json"
    graph_report = tmp_path / "graph.json"
    audit_report.write_text(
        json.dumps({"verification": {"subagent_payload_excerpt": "ok"}}),
        encoding="utf-8",
    )
    graph_report.write_text("{}", encoding="utf-8")

    command = [
        sys.executable,
        str(ROOT / "scripts" / "repair_document_artifact_graph_reports.py"),
        "--project-root",
        str(tmp_path),
        "--audit-report",
        "audit.json",
        "--graph-report",
        "graph.json",
        "--audit-job-id",
        "job_audit",
        "--graph-job-id",
        "job",
        "--graph-id",
        "document_artifact_audit_supervisor_graph",
        "--source-summary",
        "source.json",
    ]

    completed = subprocess.run(command, cwd=tmp_path, text=True, capture_output=True)

    assert completed.returncode == 0, completed.stderr
    audit = json.loads(audit_report.read_text(encoding="utf-8"))
    graph = json.loads(graph_report.read_text(encoding="utf-8"))
    item = audit["verification"]["audit_items"][0]
    assert item["source_summary_id"] == "summary-1"
    assert item["auditor_decision"] == "quote_repair_required"
    assert item["decision_consistent_with_gate"] is True
    assert audit["verification"]["score"] == 1.0
    assert graph["subagent_result"]["status"] == audit["verification"][
        "subagent_result_status"
    ]
    assert graph["authority_validation"]["passed_after_repair"] is True
