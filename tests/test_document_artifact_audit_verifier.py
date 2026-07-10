from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    "benchmarks/document_library/tsa23_tsr/"
    "p55_wave8_disagreement_verification_qwen36_summary.json"
)


def run_verifier(report: Path, sources: list[str]) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "verify_document_artifact_audit_report.py"),
        "--project-root",
        str(ROOT),
        "--report",
        str(report),
    ]
    for source in sources:
        command.extend(["--source-summary", source])
    return subprocess.run(command, text=True, capture_output=True, check=False)


def valid_report(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "verification": {
                    "score": 1.0,
                    "all_decisions_consistent_with_gate": True,
                    "audit_items": [
                        {
                            "item_id": "source_summary_1",
                            "source_path": SOURCE,
                            "source_summary_id": "p55_wave8_disagreement_verification",
                            "source_document_id": "tsa23_2012_23ts13ra",
                            "source_gate_result": "wave8-quote-repair-needed",
                            "source_recommended_next_move": (
                                "Send only unresolved verifier fields to paid "
                                "supervisor audit: decision_rationale"
                            ),
                            "source_needs_supervisor_fields": 1,
                            "source_quote_over_limit_fields": 1,
                            "source_resolved_fields": 6,
                            "auditor_decision": "quote_repair_required",
                            "decision_consistent_with_gate": True,
                            "source_fact_copy_ok": True,
                        }
                    ],
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_document_artifact_verifier_accepts_valid_report(tmp_path: Path) -> None:
    report = tmp_path / "valid_report.json"
    valid_report(report)

    completed = run_verifier(report, [SOURCE])

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_document_artifact_verifier_rejects_missing_aggregate_decision(
    tmp_path: Path,
) -> None:
    report = tmp_path / "invalid_report.json"
    valid_report(report)
    data = json.loads(report.read_text(encoding="utf-8"))
    del data["verification"]["all_decisions_consistent_with_gate"]
    report.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed = run_verifier(report, [SOURCE])

    assert completed.returncode == 1
    assert "all_decisions_consistent_with_gate must be boolean" in completed.stdout


def test_document_artifact_verifier_prioritizes_quote_limit_failed(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "summary_id": "quote_limit_case",
                "document_id": "doc",
                "gate_result": "wave10-quote-limit-failed",
                "recommended_next_move": "Keep this field in supervisor lane.",
                "totals": {
                    "needs_supervisor_fields": 1,
                    "quote_over_limit_fields": 1,
                    "resolved_fields": 0,
                },
            }
        ),
        encoding="utf-8",
    )
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "verification": {
                    "score": 1.0,
                    "all_decisions_consistent_with_gate": True,
                    "audit_items": [
                        {
                            "item_id": "source_summary_1",
                            "source_path": source.as_posix(),
                            "source_summary_id": "quote_limit_case",
                            "source_document_id": "doc",
                            "source_gate_result": "wave10-quote-limit-failed",
                            "source_recommended_next_move": (
                                "Keep this field in supervisor lane."
                            ),
                            "source_needs_supervisor_fields": 1,
                            "source_quote_over_limit_fields": 1,
                            "source_resolved_fields": 0,
                            "auditor_decision": "quote_repair_required",
                            "decision_consistent_with_gate": True,
                            "source_fact_copy_ok": True,
                        }
                    ],
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    completed = run_verifier(report, [str(source)])

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_document_artifact_verifier_does_not_infer_paid_audit_from_generic_phrase(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "summary_id": "do_not_scale_case",
                "document_id": "doc",
                "gate_result": "do-not-scale-single-huge-ticket",
                "recommended_next_move": "Repair before supervisor audit.",
                "totals": {},
            }
        ),
        encoding="utf-8",
    )
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "verification": {
                    "score": 1.0,
                    "all_decisions_consistent_with_gate": True,
                    "audit_items": [
                        {
                            "item_id": "source_summary_1",
                            "source_path": source.as_posix(),
                            "source_summary_id": "do_not_scale_case",
                            "source_document_id": "doc",
                            "source_gate_result": "do-not-scale-single-huge-ticket",
                            "source_recommended_next_move": "Repair before supervisor audit.",
                            "source_needs_supervisor_fields": 0,
                            "source_quote_over_limit_fields": 0,
                            "source_resolved_fields": 0,
                            "auditor_decision": "paid_supervisor_audit_required",
                            "decision_consistent_with_gate": True,
                            "source_fact_copy_ok": True,
                        }
                    ],
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    completed = run_verifier(report, [str(source)])

    assert completed.returncode == 1
    assert "auditor_decision mismatch" in completed.stdout


def test_document_artifact_verifier_accepts_explicit_ready_to_scale_gate(
    tmp_path: Path,
) -> None:
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
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "verification": {
                    "score": 1.0,
                    "all_decisions_consistent_with_gate": True,
                    "audit_items": [
                        {
                            "item_id": "source_summary_1",
                            "source_path": source.as_posix(),
                            "source_summary_id": "ready_scale_case",
                            "source_document_id": "doc",
                            "source_gate_result": "ready-to-scale-after-clean-validation",
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
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    completed = run_verifier(report, [str(source)])

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_document_artifact_verifier_rejects_ready_to_scale_without_explicit_gate(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "summary_id": "generic_progress_case",
                "document_id": "doc",
                "gate_result": "x4-best-current-ticket-size",
                "recommended_next_move": "Continue with this candidate workflow.",
                "totals": {
                    "needs_supervisor_fields": 0,
                    "quote_over_limit_fields": 0,
                    "resolved_fields": 7,
                },
            }
        ),
        encoding="utf-8",
    )
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "verification": {
                    "score": 1.0,
                    "all_decisions_consistent_with_gate": True,
                    "audit_items": [
                        {
                            "item_id": "source_summary_1",
                            "source_path": source.as_posix(),
                            "source_summary_id": "generic_progress_case",
                            "source_document_id": "doc",
                            "source_gate_result": "x4-best-current-ticket-size",
                            "source_recommended_next_move": (
                                "Continue with this candidate workflow."
                            ),
                            "source_needs_supervisor_fields": 0,
                            "source_quote_over_limit_fields": 0,
                            "source_resolved_fields": 7,
                            "auditor_decision": "ready_to_scale",
                            "decision_consistent_with_gate": True,
                            "source_fact_copy_ok": True,
                        }
                    ],
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    completed = run_verifier(report, [str(source)])

    assert completed.returncode == 1
    assert (
        "expected 'needs_coordinator_review', observed 'ready_to_scale'"
        in completed.stdout
    )


def test_document_artifact_verifier_rejects_inconsistent_score(
    tmp_path: Path,
) -> None:
    report = tmp_path / "invalid_score_report.json"
    valid_report(report)
    data = json.loads(report.read_text(encoding="utf-8"))
    data["verification"]["score"] = 0.0
    report.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed = run_verifier(report, [SOURCE])

    assert completed.returncode == 1
    assert "verification.score should be 1.0" in completed.stdout
