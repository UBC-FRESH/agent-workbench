from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_verifier(
    graph_report: Path, audit_report: Path | None = None
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "verify_document_artifact_graph_report.py"),
        "--project-root",
        str(ROOT),
        "--graph-report",
        str(graph_report),
    ]
    if audit_report is not None:
        command.extend(["--audit-report", str(audit_report)])
    return subprocess.run(command, text=True, capture_output=True, check=False)


def write_audit_report(
    path: Path, status: str = "accepted_after_supervisor_repair"
) -> None:
    path.write_text(
        json.dumps(
            {
                "verification": {
                    "subagent_result_status": status,
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_graph_report(
    path: Path,
    *,
    status: str = "accepted_after_supervisor_repair",
    repair_required: bool = True,
) -> None:
    path.write_text(
        json.dumps(
            {
                "report_id": "test_graph_report",
                "graph_id": "document_artifact_audit_supervisor_graph",
                "audit_job_id": "test_audit",
                "supervisor_role": "supervisor",
                "final_signal": "job_complete_with_caveats",
                "completed_graph_nodes": [
                    {"node_id": "materialize_runtime_job", "status": "completed"},
                    {"node_id": "subagent_artifact_audit", "status": "completed"},
                    {"node_id": "write_supervisor_report", "status": "completed"},
                    {"node_id": "validate_and_repair_report", "status": "completed"},
                ],
                "audit_report_path": "runtime/agent_jobs/test_audit_report.json",
                "authority_validation": {
                    "attempted": True,
                    "passed_after_repair": True,
                    "error_excerpt": "",
                },
                "subagent_invocation_observed_by_supervisor": True,
                "subagent_result": {
                    "status": status,
                    "repair_required": repair_required,
                    "summary": "Subagent result required bounded supervisor repair.",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_graph_report_verifier_accepts_valid_report(tmp_path: Path) -> None:
    graph_report = tmp_path / "graph_report.json"
    audit_report = tmp_path / "audit_report.json"
    write_graph_report(graph_report)
    write_audit_report(audit_report)

    completed = run_verifier(graph_report, audit_report)

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_graph_report_verifier_rejects_missing_report_cleanly(tmp_path: Path) -> None:
    graph_report = tmp_path / "missing_graph_report.json"

    completed = run_verifier(graph_report)

    assert completed.returncode == 1
    assert "invalid document artifact graph report" in completed.stdout
    assert "missing JSON report" in completed.stdout
    assert "Traceback" not in completed.stdout
    assert "Traceback" not in completed.stderr


def test_graph_report_verifier_rejects_missing_subagent_result(tmp_path: Path) -> None:
    graph_report = tmp_path / "graph_report.json"
    write_graph_report(graph_report)
    data = json.loads(graph_report.read_text(encoding="utf-8"))
    del data["subagent_result"]
    graph_report.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed = run_verifier(graph_report)

    assert completed.returncode == 1
    assert "missing required field: subagent_result" in completed.stdout


def test_graph_report_verifier_rejects_mismatched_audit_status(tmp_path: Path) -> None:
    graph_report = tmp_path / "graph_report.json"
    audit_report = tmp_path / "audit_report.json"
    write_graph_report(graph_report, status="accepted_after_supervisor_repair")
    write_audit_report(audit_report, status="rejected_supervisor_replaced")

    completed = run_verifier(graph_report, audit_report)

    assert completed.returncode == 1
    assert (
        "must match audit_report.verification.subagent_result_status"
        in completed.stdout
    )


def test_graph_report_verifier_rejects_clean_status_with_repair_flag(
    tmp_path: Path,
) -> None:
    graph_report = tmp_path / "graph_report.json"
    write_graph_report(
        graph_report,
        status="accepted_without_repair",
        repair_required=True,
    )

    completed = run_verifier(graph_report)

    assert completed.returncode == 1
    assert "repair_required must be false" in completed.stdout
