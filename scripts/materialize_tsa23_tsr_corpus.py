"""Resolve and optionally materialize the TSA 23 TSR mini-corpus through FEMIC.

The tracked outputs from this script are sanitized metadata only. Downloaded
PDFs, extraction chunks, prompts, and worker outputs belong under ``runtime/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TSA_CODE = "23"
DEFAULT_MIN_YEAR = 1995
DEFAULT_CORPUS_ID = "bc_tsr_tsa23_public_1995_present"
DEFAULT_BENCHMARK_ROOT = Path("benchmarks/document_library/tsa23_tsr")
DEFAULT_RUNTIME_ROOT = Path("runtime/document_library/tsa23_tsr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a reproducible Agent Workbench registry for all public TSA 23 "
            "TSR PDF documents from FEMIC metadata, with optional FEMIC-backed "
            "PDF materialization."
        )
    )
    parser.add_argument(
        "--femic-root",
        type=Path,
        default=Path("../femic"),
        help="Adjacent FEMIC checkout containing metadata/tsr and the femic CLI.",
    )
    parser.add_argument(
        "--femic-python",
        type=Path,
        default=None,
        help=(
            "Python executable to run 'python -m femic'. Defaults to FEMIC's "
            ".venv Python when present, otherwise the current Python."
        ),
    )
    parser.add_argument("--tsa-code", default=DEFAULT_TSA_CODE)
    parser.add_argument("--min-year", type=int, default=DEFAULT_MIN_YEAR)
    parser.add_argument("--corpus-id", default=DEFAULT_CORPUS_ID)
    parser.add_argument(
        "--benchmark-root",
        type=Path,
        default=DEFAULT_BENCHMARK_ROOT,
        help="Tracked sanitized output directory.",
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=DEFAULT_RUNTIME_ROOT,
        help="Ignored runtime directory for materialized PDFs and raw chunks.",
    )
    parser.add_argument(
        "--refresh-index",
        action="store_true",
        help="Run 'python -m femic tsr index' before reading FEMIC metadata.",
    )
    parser.add_argument(
        "--materialize",
        action="store_true",
        help="Run 'python -m femic tsr fetch --tsa <code>' into runtime-root/corpus.",
    )
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def femic_python(femic_root: Path, override: Path | None) -> Path:
    if override is not None:
        return resolve(override)
    windows_venv = femic_root / ".venv" / "Scripts" / "python.exe"
    posix_venv = femic_root / ".venv" / "bin" / "python"
    if windows_venv.exists():
        return windows_venv
    if posix_venv.exists():
        return posix_venv
    return Path(sys.executable)


def run_femic(command: list[str], *, femic_root: Path, python_exe: Path) -> None:
    subprocess.run(
        [str(python_exe), "-m", "femic", *command],
        cwd=femic_root,
        check=True,
    )


def load_documents(documents_path: Path) -> list[dict[str, Any]]:
    raw = json.loads(documents_path.read_text(encoding="utf-8"))
    documents = raw.get("documents")
    if not isinstance(documents, list):
        raise ValueError(f"Expected documents list in {documents_path}")
    return documents


def normalized_doc_id(document: dict[str, Any]) -> str:
    stem = str(document["file_name"]).rsplit(".", 1)[0].lower()
    return f"tsa23_{int(document['cycle_year'])}_{stem}"


def relative_pdf_cache_path(document: dict[str, Any]) -> str:
    return (
        "runtime/document_library/tsa23_tsr/corpus/"
        f"tsa/{document['tsa_id']}/{document['relative_path']}"
    )


def local_pdf_path(runtime_root: Path, document: dict[str, Any]) -> Path:
    return (
        runtime_root
        / "corpus"
        / "tsa"
        / str(document["tsa_id"])
        / str(document["relative_path"])
    )


def sha256_if_present(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_documents(
    documents: list[dict[str, Any]], *, tsa_code: str, min_year: int
) -> list[dict[str, Any]]:
    selected = []
    for document in documents:
        if str(document.get("tsa_code")) != str(tsa_code):
            continue
        if str(document.get("file_extension", "")).lower() != "pdf":
            continue
        if int(document.get("cycle_year") or 0) < min_year:
            continue
        selected.append(document)
    return sorted(
        selected,
        key=lambda item: (
            int(item.get("cycle_year") or 0),
            str(item.get("document_type", "")),
            str(item.get("relative_path", "")),
        ),
    )


def registry_record(
    document: dict[str, Any], *, corpus_id: str, runtime_root: Path
) -> dict[str, Any]:
    document_id = normalized_doc_id(document)
    pdf_path = local_pdf_path(runtime_root, document)
    return {
        "schema_version": 1,
        "document_id": document_id,
        "corpus_id": corpus_id,
        "title": document.get("title", ""),
        "document_type": document.get("document_type", ""),
        "jurisdiction": "British Columbia",
        "management_unit": {
            "type": "TSA",
            "code": document.get("tsa_code", ""),
            "name": document.get("tsa_name", ""),
        },
        "cycle_label": document.get("cycle_label", ""),
        "cycle_year": document.get("cycle_year"),
        "source_url": document.get("url", ""),
        "source_provenance": (
            "FEMIC TSR registry generated from public BC Ministry of Forests "
            "Timber Supply Review document listings."
        ),
        "source_sha256": sha256_if_present(pdf_path),
        "byte_size": document.get("size_bytes", 0),
        "language": "en",
        "public_access": {
            "is_public": True,
            "license_or_terms": "Public BC Ministry of Forests web document.",
            "redistribution_notes": (
                "Agent Workbench tracks metadata only; raw PDFs remain ignored "
                "runtime material or FEMIC-managed source data."
            ),
        },
        "femic_source": {
            "metadata_file": "metadata/tsr/tsa_documents.json",
            "tsa_id": document.get("tsa_id", ""),
            "relative_path": document.get("relative_path", ""),
            "file_name": document.get("file_name", ""),
            "listed_modified_raw": document.get("listed_modified_raw", ""),
        },
        "materialization": {
            "runtime_pdf_cache_path": relative_pdf_cache_path(document),
            "materialized_at_generation": bool(pdf_path.exists()),
        },
        "extraction": {
            "status": "not_started",
            "tool": "target-project PDF text extractor, to be selected before worker runs",
            "runtime_chunk_root": f"runtime/document_library/tsa23_tsr/chunks/{document_id}",
            "tracked_chunk_manifest": (
                f"benchmarks/document_library/tsa23_tsr/chunk_manifests/"
                f"{document_id}.json"
            ),
            "text_extraction_notes": "Raw extracted text must remain ignored.",
        },
        "indexing": {
            "structure_pass_status": "not_started",
            "content_metadata_status": "not_started",
            "self_audit_status": "not_started",
            "repair_status": "not_started",
            "supervisor_audit_status": "not_started",
            "promoted_index_status": "not_started",
        },
        "public_safety": {
            "raw_document_tracked": False,
            "raw_text_tracked": False,
            "raw_worker_outputs_tracked": False,
            "provider_urls_tracked": False,
            "provider_headers_tracked": False,
            "personal_paths_tracked": False,
        },
    }


def pilot_documents(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preferred_names = {"23ts95ra.pdf", "23ts06ra.pdf", "23ts13ra.pdf"}
    preferred = [
        record
        for record in records
        if record["femic_source"]["file_name"].lower() in preferred_names
    ]
    if len(preferred) >= 2:
        return preferred
    return records[: min(3, len(records))]


def chunk_manifest_scaffold(
    *, corpus_id: str, selected_records: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "corpus_id": corpus_id,
        "status": "planned_no_raw_text_tracked",
        "raw_text_policy": "Raw extracted page/chunk text stays under runtime/.",
        "default_chunking_plan": {
            "unit": "page_window",
            "window_pages": 24,
            "overlap_pages": 2,
            "ticket_size_sequence": ["x2", "x4", "x8", "x16"],
        },
        "document_scaffolds": [
            {
                "document_id": record["document_id"],
                "cycle_year": record["cycle_year"],
                "document_type": record["document_type"],
                "tracked_chunk_manifest": record["extraction"]["tracked_chunk_manifest"],
                "runtime_chunk_root": record["extraction"]["runtime_chunk_root"],
                "planned_worker_passes": [
                    "structure",
                    "content_metadata",
                    "local_self_audit",
                    "delegated_repair_iteration",
                    "supervisor_audit_calibration",
                ],
                "required_record_id_prefix": f"{record['document_id']}::",
            }
            for record in selected_records
        ],
    }


def audit_calibration_scaffold(
    *, corpus_id: str, selected_records: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "corpus_id": corpus_id,
        "status": "planned",
        "calibration_goal": (
            "Test whether MP11-derived chunk size, record schema, and bailout "
            "rules generalize across older and newer TSA 23 public TSR documents."
        ),
        "supervisor_token_accounting": "required",
        "sample_design": {
            "document_count": len(selected_records),
            "per_document_candidate_sample": 20,
            "strata": [
                "cycle_year",
                "document_type",
                "structure_records",
                "content_metadata_records",
                "repair_candidates",
            ],
        },
        "tracked_metrics": [
            "worker_input_tokens",
            "worker_output_tokens",
            "parseable_record_count",
            "record_id_preservation_rate",
            "accepted_rate",
            "repairable_rate",
            "rejected_rate",
            "supervisor_audit_cost_usd",
            "supervisor_cost_per_accepted_or_repairable_record",
        ],
        "bailout_checks": [
            "zero primary identifier preservation",
            "known calibration repairables missed",
            "malformed JSONL above threshold",
            "uncontrolled tool-call behavior in a no-tool lane",
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = Path.cwd()
    femic_root = resolve(args.femic_root)
    benchmark_root = repo_root / args.benchmark_root
    runtime_root = repo_root / args.runtime_root
    python_exe = femic_python(femic_root, args.femic_python)
    documents_path = femic_root / "metadata" / "tsr" / "tsa_documents.json"

    if args.refresh_index:
        run_femic(["tsr", "index"], femic_root=femic_root, python_exe=python_exe)

    if args.materialize:
        run_femic(
            [
                "tsr",
                "fetch",
                "--documents-path",
                str(documents_path),
                "--tsa",
                str(args.tsa_code),
                "--corpus-root",
                str(runtime_root / "corpus"),
                "--manifest-path",
                str(runtime_root / "femic_fetch_manifest.json"),
            ],
            femic_root=femic_root,
            python_exe=python_exe,
        )

    selected = select_documents(
        load_documents(documents_path),
        tsa_code=args.tsa_code,
        min_year=args.min_year,
    )
    if not selected:
        raise SystemExit(
            f"No PDF documents found for TSA {args.tsa_code} from {args.min_year} onward."
        )

    records = [
        registry_record(document, corpus_id=args.corpus_id, runtime_root=runtime_root)
        for document in selected
    ]
    pilot_records = pilot_documents(records)
    counts = Counter(str(record["cycle_year"]) for record in records)
    type_counts = Counter(record["document_type"] for record in records)

    registry = {
        "schema_version": 1,
        "corpus_id": args.corpus_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "selection": {
            "tsa_code": str(args.tsa_code),
            "management_unit": "100 Mile House TSA",
            "min_cycle_year": args.min_year,
            "document_kind": "public TSR PDFs",
            "source_metadata": "FEMIC metadata/tsr/tsa_documents.json",
        },
        "counts": {
            "documents": len(records),
            "by_cycle_year": dict(sorted(counts.items())),
            "by_document_type": dict(sorted(type_counts.items())),
        },
        "reproducibility": {
            "script": "scripts/materialize_tsa23_tsr_corpus.py",
            "dry_run_command": (
                "python scripts/materialize_tsa23_tsr_corpus.py "
                "--femic-root ../femic"
            ),
            "materialize_command": (
                "python scripts/materialize_tsa23_tsr_corpus.py "
                "--femic-root ../femic --materialize"
            ),
            "runtime_policy": "PDFs, raw text, prompts, and worker outputs stay under runtime/.",
        },
        "documents": records,
        "pilot_documents": [record["document_id"] for record in pilot_records],
    }
    write_json(benchmark_root / "corpus_registry.json", registry)
    write_json(
        benchmark_root / "chunk_manifest_scaffold.json",
        chunk_manifest_scaffold(corpus_id=args.corpus_id, selected_records=pilot_records),
    )
    write_json(
        benchmark_root / "audit_calibration_scaffold.json",
        audit_calibration_scaffold(corpus_id=args.corpus_id, selected_records=pilot_records),
    )

    print(
        f"Registered {len(records)} TSA {args.tsa_code} public TSR PDFs in "
        f"{benchmark_root.as_posix()}"
    )
    print("Pilot documents:")
    for record in pilot_records:
        print(f"- {record['document_id']} ({record['cycle_year']}, {record['document_type']})")


if __name__ == "__main__":
    main()
