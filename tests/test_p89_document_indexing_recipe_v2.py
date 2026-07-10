from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_p89_document_indexing_recipe_v2.py"


def test_p89_materializer_generates_sanitized_full_document_specs(
    tmp_path: Path,
) -> None:
    source_text = (
        "[PDF page 1]\n"
        "1. INTRODUCTION\n"
        "Synthetic fixture introduces a technical document.\n\n"
        "[PDF page 2]\n"
        "2. ASSUMPTIONS\n"
        "The base case includes current management assumptions.\n"
    )
    selection = build_selection(tmp_path, source_text)
    command = [
        sys.executable,
        str(SCRIPT),
        "--project-root",
        str(tmp_path),
        "materialize",
        "--selection",
        str(selection),
        "--force",
    ]

    completed = subprocess.run(command, cwd=tmp_path, text=True, check=False)

    assert completed.returncode == 0
    tracked_root = tmp_path / "benchmarks" / "document_library"
    manifest = json.loads(
        (tracked_root / "p89_recipe_v2_materialization_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    summary = json.loads(
        (tracked_root / "p89_dry_run_materialization_summary.json").read_text(
            encoding="utf-8"
        )
    )
    enum = json.loads(
        (tracked_root / "p89_chunk_id_enum.json").read_text(encoding="utf-8")
    )

    assert manifest["chunk_manifest"] == (
        "benchmarks/document_library/tsa23_tsr/chunk_manifests/tsa23_2012_23tsdp12.json"
    )
    assert manifest["source_slice"] == "test_full_document"
    assert manifest["ticket_count"] == 4
    assert manifest["live_execution_allowed"] is False
    assert summary["section_count"] == 2
    assert summary["ticket_count"] == 4
    assert len(enum["allowed_chunk_ids"]) == 1

    manifest_text = json.dumps(manifest)
    assert "Synthetic fixture introduces" not in manifest_text
    ticket_paths = sorted(
        (tmp_path / "runtime" / "document_library" / "tsa23_tsr")
        .joinpath("p89_document_indexing_recipe_v2", "tickets")
        .glob("*.ticket.md")
    )
    assert len(ticket_paths) == 4
    ticket_text = ticket_paths[0].read_text(encoding="utf-8")
    assert "Synthetic fixture introduces" in ticket_text
    assert "not authorization to contact a live model" in ticket_text


def test_p89_validator_repairs_fences_and_trailing_commas(tmp_path: Path) -> None:
    contract_path = write_contract(tmp_path)
    candidate_path = tmp_path / "runtime" / "candidate.jsonl"
    candidate_path.parent.mkdir(parents=True)
    candidate_path.write_text(
        "\n".join(
            [
                "Here is the result:",
                "```json",
                json.dumps(valid_record()) + ",",
                "```",
            ]
        ),
        encoding="utf-8",
    )
    report_path = tmp_path / "runtime" / "report.json"
    repaired_path = tmp_path / "runtime" / "repaired.jsonl"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(tmp_path),
            "validate-jsonl",
            "--input",
            str(candidate_path),
            "--contract",
            str(contract_path),
            "--output",
            str(report_path),
            "--repaired-output",
            str(repaired_path),
        ],
        cwd=tmp_path,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    repaired_records = [
        json.loads(line)
        for line in repaired_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert report["status"] == "valid"
    assert report["parseable_record_count"] == 1
    assert report["repaired_line_count"] == 4
    assert report["dropped_non_json_line_count"] == 1
    assert repaired_records == [valid_record()]


def test_p89_validator_rejects_unknown_chunk_id(tmp_path: Path) -> None:
    contract_path = write_contract(tmp_path)
    candidate_path = tmp_path / "runtime" / "candidate.jsonl"
    candidate_path.parent.mkdir(parents=True)
    record = valid_record()
    record["chunk_id"] = "tsa23_2012_23tsdp12::pages_999"
    candidate_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    report_path = tmp_path / "runtime" / "report.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(tmp_path),
            "validate-jsonl",
            "--input",
            str(candidate_path),
            "--contract",
            str(contract_path),
            "--output",
            str(report_path),
        ],
        cwd=tmp_path,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "invalid"
    assert report["fatal_error_count"] == 1
    assert report["errors"][0]["kind"] == "unknown_chunk_id"


def build_selection(tmp_path: Path, source_text: str) -> Path:
    source_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    chunk_runtime_path = (
        tmp_path
        / "runtime"
        / "document_library"
        / "tsa23_tsr"
        / "chunks"
        / "tsa23_2012_23tsdp12"
        / "tsa23_2012_23tsdp12__pages_001_002.txt"
    )
    chunk_runtime_path.parent.mkdir(parents=True)
    chunk_runtime_path.write_text(source_text, encoding="utf-8")
    chunk_manifest_path = (
        tmp_path
        / "benchmarks"
        / "document_library"
        / "tsa23_tsr"
        / "chunk_manifests"
        / "tsa23_2012_23tsdp12.json"
    )
    chunk_manifest_path.parent.mkdir(parents=True)
    runtime_rel = chunk_runtime_path.relative_to(tmp_path).as_posix()
    chunk = {
        "chunk_id": "tsa23_2012_23tsdp12::pages_001_002",
        "empty_pages": [],
        "page_end": 2,
        "page_start": 1,
        "runtime_text_path": runtime_rel,
        "text_char_count": len(source_text),
        "text_sha256": source_hash,
    }
    chunk_manifest_path.write_text(
        json.dumps({"schema_version": 1, "chunks": [chunk]}, indent=2) + "\n",
        encoding="utf-8",
    )
    selection_path = tmp_path / "benchmarks" / "document_library" / "selection.json"
    selection_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "phase": "P88",
                "slice_id": "test_full_document",
                "corpus": {"corpus_id": "bc_tsr_tsa23_public_1995_present"},
                "document": {
                    "document_id": "tsa23_2012_23tsdp12",
                    "source_sha256": "source-sha",
                    "tracked_chunk_manifest": (
                        "benchmarks/document_library/tsa23_tsr/chunk_manifests/"
                        "tsa23_2012_23tsdp12.json"
                    ),
                },
                "selected_scope": {
                    "chunk_ids": [chunk["chunk_id"]],
                    "chunks": [chunk],
                },
                "stop_rules": ["stop on test rule"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return selection_path


def write_contract(tmp_path: Path) -> Path:
    contract_path = tmp_path / "benchmarks" / "document_library" / "contract.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        json.dumps(
            {
                "allowed_chunk_ids": [
                    "tsa23_2012_23tsdp12::pages_001_002",
                ],
                "allowed_object_types": ["heading", "claim"],
                "required_fields": list(valid_record()),
                "required_review_status": "raw_worker_candidate",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return contract_path


def valid_record() -> dict[str, object]:
    return {
        "record_id": "tsa23_2012_23tsdp12::record_001",
        "corpus_id": "bc_tsr_tsa23_public_1995_present",
        "document_id": "tsa23_2012_23tsdp12",
        "source_sha256": "source-sha",
        "chunk_id": "tsa23_2012_23tsdp12::pages_001_002",
        "page_anchor": "PDF page 1",
        "document_component": "introduction",
        "section_path": "1. Introduction",
        "object_type": "heading",
        "title": "Introduction",
        "summary": "The document introduction starts here.",
        "source_quote": "1. INTRODUCTION",
        "confidence": 0.9,
        "worker_model": "configured-local-document-worker",
        "review_status": "raw_worker_candidate",
    }
