from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_p92_whole_document_supervisor_pilot.py"


def test_p92_materializer_writes_single_whole_document_ticket(
    tmp_path: Path,
) -> None:
    selection_path = build_selection(tmp_path)
    p90_path = write_p90_summary(tmp_path)
    p91_path = write_p91_decision(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(tmp_path),
            "materialize",
            "--selection",
            str(selection_path),
            "--p90-summary",
            str(p90_path),
            "--p91-decision",
            str(p91_path),
            "--force",
        ],
        cwd=tmp_path,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    tracked_root = tmp_path / "benchmarks" / "document_library"
    manifest = json.loads(
        (tracked_root / "p92_whole_document_supervisor_pilot_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    gate = json.loads(
        (tracked_root / "p92_whole_document_supervisor_gate.json").read_text(
            encoding="utf-8"
        )
    )
    contract = json.loads(
        (tracked_root / "p92_whole_document_supervisor_report_contract.json").read_text(
            encoding="utf-8"
        )
    )
    roi = json.loads(
        (tracked_root / "p92_whole_document_supervisor_roi_estimate.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["status"] == "materialized_not_live_run"
    assert manifest["chunk_count"] == 2
    assert manifest["total_source_char_count"] > 1_000
    assert manifest["delegated_supervisor"]["role"] == (
        "document_metadata_extraction_supervisor"
    )
    assert manifest["delegated_supervisor"]["custom_agent"] == (
        "document-metadata-extraction-supervisor"
    )
    assert "runCommands" in manifest["delegated_supervisor"]["tool_access"]
    assert gate["overall_gate"] == "pass"
    assert gate["live_run_authorized_by_this_file"] is False
    assert contract["minimum_quality_bar"]["source_document_read"] is True
    assert roi["comparison"] == "whole_document_supervisor_vs_chunk_micro_management"

    manifest_text = json.dumps(manifest)
    assert "Synthetic section text" not in manifest_text
    ticket_path = tmp_path / manifest["runtime_artifacts"]["ticket_path"]
    ticket_text = ticket_path.read_text(encoding="utf-8")
    assert "Synthetic section text" in ticket_text
    assert "paid coordinator has intentionally" in ticket_text
    assert "P92_WHOLE_DOCUMENT_SUPERVISOR_REPORT_READY" in ticket_text


def test_p92_report_validator_accepts_useful_seed(tmp_path: Path) -> None:
    contract_path = write_contract(tmp_path)
    report_path = tmp_path / "runtime" / "report.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(json.dumps(valid_report()), encoding="utf-8")
    validation_path = tmp_path / "runtime" / "validation.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(tmp_path),
            "validate-report",
            "--input",
            str(report_path),
            "--contract",
            str(contract_path),
            "--output",
            str(validation_path),
        ],
        cwd=tmp_path,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    assert validation["status"] == "valid"
    assert validation["candidate_record_count"] == 1
    assert validation["decision_hint"] == "coordinator_audit_seed"


def test_p92_report_validator_bounces_zero_record_report(tmp_path: Path) -> None:
    contract_path = write_contract(tmp_path)
    report = valid_report()
    report["records"] = []
    report["candidate_record_count"] = 0
    report_path = tmp_path / "runtime" / "report.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text(json.dumps(report), encoding="utf-8")
    validation_path = tmp_path / "runtime" / "validation.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(tmp_path),
            "validate-report",
            "--input",
            str(report_path),
            "--contract",
            str(contract_path),
            "--output",
            str(validation_path),
        ],
        cwd=tmp_path,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    assert validation["status"] == "invalid"
    assert validation["decision_hint"] == "bounce_or_stop"
    assert {error["kind"] for error in validation["errors"]} == {
        "zero_or_too_few_records"
    }


def build_selection(tmp_path: Path) -> Path:
    chunks = []
    for index in range(1, 3):
        source_text = (
            f"[PDF page {index}]\n"
            f"{index}. Synthetic section text for a public technical document.\n"
            "This fixture includes assumptions, table references, and model inputs. "
            * 20
        )
        source_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        text_path = (
            tmp_path
            / "runtime"
            / "document_library"
            / "tsa23_tsr"
            / "chunks"
            / f"chunk_{index}.txt"
        )
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(source_text, encoding="utf-8")
        chunks.append(
            {
                "chunk_id": f"test_doc::pages_{index:03}_{index:03}",
                "page_start": index,
                "page_end": index,
                "text_char_count": len(source_text),
                "text_sha256": source_hash,
                "runtime_text_path": text_path.relative_to(tmp_path).as_posix(),
            }
        )

    chunk_manifest_path = (
        tmp_path
        / "benchmarks"
        / "document_library"
        / "tsa23_tsr"
        / "chunk_manifests"
        / "test_doc.json"
    )
    chunk_manifest_path.parent.mkdir(parents=True)
    chunk_manifest_path.write_text(
        json.dumps({"schema_version": 1, "chunks": chunks}, indent=2) + "\n",
        encoding="utf-8",
    )
    selection_path = tmp_path / "benchmarks" / "document_library" / "selection.json"
    selection_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "phase": "P88",
                "slice_id": "test_whole_document",
                "corpus": {"corpus_id": "test_corpus"},
                "document": {
                    "document_id": "test_doc",
                    "title": "Test document",
                    "source_sha256": "source-sha",
                    "tracked_chunk_manifest": (
                        "benchmarks/document_library/tsa23_tsr/chunk_manifests/"
                        "test_doc.json"
                    ),
                },
                "selected_scope": {
                    "page_start": 1,
                    "page_end": 2,
                    "chunks": chunks,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return selection_path


def write_p90_summary(tmp_path: Path) -> Path:
    path = tmp_path / "benchmarks" / "document_library" / "p90.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "run_count": 4,
                "completed_run_count": 4,
                "valid_run_count": 3,
                "emitted_repaired_record_count": 40,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def write_p91_decision(tmp_path: Path) -> Path:
    path = tmp_path / "benchmarks" / "document_library" / "p91.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "decision": "promote_seed",
                "sample_useful_yield": 0.938,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def write_contract(tmp_path: Path) -> Path:
    path = tmp_path / "benchmarks" / "document_library" / "contract.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "document_id": "test_doc",
                "supervisor_role": "document_metadata_extraction_supervisor",
                "required_fields": [
                    "report_id",
                    "document_id",
                    "supervisor_role",
                    "final_signal",
                    "source_document_read",
                    "output_quality",
                    "candidate_record_count",
                    "source_anchor_policy",
                    "records",
                    "gaps",
                    "self_grade",
                    "next_action",
                ],
                "allowed_final_signals": [
                    "job_complete",
                    "job_complete_with_caveats",
                    "needs_coordinator_review",
                    "job_failed",
                ],
                "allowed_next_actions": [
                    "accept_seed",
                    "repair",
                    "bounce_redo",
                    "stop",
                ],
                "allowed_confidence": ["high", "medium", "low"],
                "minimum_candidate_records": 1,
                "minimum_quality_bar": {
                    "each_record_required_fields": [
                        "record_id",
                        "object_type",
                        "title",
                        "summary",
                        "source_anchor",
                        "confidence",
                    ]
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def valid_report() -> dict[str, object]:
    return {
        "report_id": "test_report",
        "document_id": "test_doc",
        "supervisor_role": "document_metadata_extraction_supervisor",
        "final_signal": "job_complete_with_caveats",
        "source_document_read": True,
        "output_quality": {
            "quality_validated_candidate": True,
            "protocol_accepted_candidate": True,
            "economics_usable": False,
        },
        "candidate_record_count": 1,
        "source_anchor_policy": "caption/page anchors used for tables",
        "records": [
            {
                "record_id": "test_doc::record_001",
                "object_type": "heading",
                "title": "Synthetic section",
                "summary": "The document contains a synthetic section.",
                "source_anchor": "PDF page 1",
                "confidence": "high",
            }
        ],
        "gaps": [],
        "self_grade": {"summary": "Useful seed with caveats."},
        "next_action": "accept_seed",
    }
