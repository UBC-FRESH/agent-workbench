"""Build P55 TSA23 document-indexing chunks, tickets, and eval manifests.

Tracked outputs contain only sanitized metadata. Raw extracted page text and
worker tickets that include source text are written under ignored ``runtime/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader


DEFAULT_BENCHMARK_ROOT = Path("benchmarks/document_library/tsa23_tsr")
DEFAULT_RUNTIME_ROOT = Path("runtime/document_library/tsa23_tsr")
DEFAULT_REGISTRY = DEFAULT_BENCHMARK_ROOT / "corpus_registry.json"
DEFAULT_BATTERY = DEFAULT_BENCHMARK_ROOT / "p55_test_battery.json"
DEFAULT_MODEL_TIMEOUT_SECONDS = 1800
DEFAULT_WINDOW_PAGES = 8
DEFAULT_OVERLAP_PAGES = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract ignored TSA23 PDF chunks and generate no-tool worker "
            "tickets/eval manifests for the P55 indexing battery."
        )
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    parser.add_argument("--benchmark-root", type=Path, default=DEFAULT_BENCHMARK_ROOT)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--window-pages", type=int, default=DEFAULT_WINDOW_PAGES)
    parser.add_argument("--overlap-pages", type=int, default=DEFAULT_OVERLAP_PAGES)
    parser.add_argument(
        "--base-url-file",
        default="runtime/ollama_openai_base_url.txt",
        help="Ignored provider base URL file referenced by eval manifests.",
    )
    parser.add_argument(
        "--provider-headers-file",
        default="runtime/local_provider_headers.json",
        help="Ignored provider headers file referenced by eval manifests.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_MODEL_TIMEOUT_SECONDS,
        help="Per worker run timeout. Kept high because local model loads can dominate.",
    )
    parser.add_argument(
        "--max-ticket-chars",
        type=int,
        default=220_000,
        help="Hard cap on source text characters embedded in one worker ticket.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def repo_relative(path: Path) -> str:
    return path.as_posix()


def document_lookup(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(document["document_id"]): document for document in registry["documents"]}


def extract_document_chunks(
    *,
    document: dict[str, Any],
    runtime_root: Path,
    benchmark_root: Path,
    window_pages: int,
    overlap_pages: int,
) -> dict[str, Any]:
    document_id = str(document["document_id"])
    pdf_path = Path(str(document["materialization"]["runtime_pdf_cache_path"]))
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"materialized PDF not found for {document_id}: {pdf_path}. "
            "Run scripts/materialize_tsa23_tsr_corpus.py --materialize first."
        )

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    chunk_root = runtime_root / "chunks" / document_id
    chunks: list[dict[str, Any]] = []
    step = max(1, window_pages - overlap_pages)
    start_index = 0
    chunk_index = 1
    while start_index < page_count:
        end_index = min(start_index + window_pages, page_count)
        page_texts: list[str] = []
        empty_pages: list[int] = []
        for index in range(start_index, end_index):
            text = reader.pages[index].extract_text() or ""
            if not text.strip():
                empty_pages.append(index + 1)
            page_texts.append(f"\n\n[PDF page {index + 1}]\n{text.strip()}")
        chunk_text = "\n".join(page_texts).strip()
        chunk_id = f"{document_id}::pages_{start_index + 1:03d}_{end_index:03d}"
        chunk_path = chunk_root / f"{chunk_id.replace('::', '__')}.txt"
        write_text(chunk_path, chunk_text + "\n")
        chunks.append(
            {
                "chunk_id": chunk_id,
                "page_start": start_index + 1,
                "page_end": end_index,
                "pdf_page_count": page_count,
                "runtime_text_path": repo_relative(chunk_path),
                "text_sha256": sha256_text(chunk_text + "\n"),
                "text_char_count": len(chunk_text),
                "empty_pages": empty_pages,
            }
        )
        if end_index == page_count:
            break
        start_index += step
        chunk_index += 1

    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "corpus_id": document["corpus_id"],
        "document_id": document_id,
        "source_sha256": document["source_sha256"],
        "source_url": document["source_url"],
        "cycle_year": document["cycle_year"],
        "document_type": document["document_type"],
        "pdf_page_count": page_count,
        "window_pages": window_pages,
        "overlap_pages": overlap_pages,
        "chunk_count": len(chunks),
        "raw_text_policy": "Raw chunk text is ignored under runtime/.",
        "chunks": chunks,
    }
    manifest_path = benchmark_root / "chunk_manifests" / f"{document_id}.json"
    write_json(manifest_path, manifest)
    return manifest


def selected_chunks(manifest: dict[str, Any], page_windows: Any) -> list[dict[str, Any]]:
    if str(page_windows).lower() == "all":
        return list(manifest["chunks"])
    return list(manifest["chunks"][: int(page_windows)])


def build_ticket(
    *,
    record_type: str,
    document: dict[str, Any],
    chunk_manifest_path: Path,
    chunks: list[dict[str, Any]],
    max_ticket_chars: int,
) -> tuple[str, list[dict[str, Any]], bool]:
    included: list[dict[str, Any]] = []
    source_blocks: list[str] = []
    total_chars = 0
    truncated = False
    for chunk in chunks:
        text = Path(chunk["runtime_text_path"]).read_text(encoding="utf-8-sig")
        if total_chars + len(text) > max_ticket_chars and included:
            truncated = True
            break
        included.append(chunk)
        total_chars += len(text)
        source_blocks.append(
            "\n".join(
                [
                    "```text",
                    f"chunk_id: {chunk['chunk_id']}",
                    f"page_range: {chunk['page_start']}-{chunk['page_end']}",
                    f"text_sha256: {chunk['text_sha256']}",
                    "",
                    text.strip(),
                    "```",
                ]
            )
        )
        if total_chars >= max_ticket_chars:
            truncated = len(included) < len(chunks)
            break

    if not included:
        raise ValueError("ticket would contain zero chunks after max character cap")

    object_types = (
        "component_boundary, heading, appendix, table, figure, map, acronym, "
        "definition, cross_reference, other"
        if record_type == "structure"
        else "claim, assumption, constraint, policy_reference, model_input, "
        "numeric_value, scenario, sensitivity_test, decision_rationale, other"
    )
    ticket = f"""# P55 TSA23 Document Index Worker Ticket

## Mission

Extract `{record_type}` metadata records from the supplied source chunks only.
Return JSONL only. Do not summarize the task in prose. Do not use tools,
commands, files, browsing, or GitHub. Stop after the JSONL records.

## Current State

- corpus_id: `{document['corpus_id']}`
- document_id: `{document['document_id']}`
- source_sha256: `{document['source_sha256']}`
- cycle_year: `{document['cycle_year']}`
- document_type: `{document['document_type']}`
- chunk_manifest: `{repo_relative(chunk_manifest_path)}`
- requested_record_type: `{record_type}`
- raw_text_tracked: `false`
- required_record_id_prefix: `{document['document_id']}::`

## Output Format

Return JSONL only. Each line must be one JSON object with these fields:

- `record_id`
- `corpus_id`
- `document_id`
- `source_sha256`
- `chunk_id`
- `page_anchor`
- `document_component`
- `section_path`
- `object_type`
- `title`
- `summary`
- `source_quote`
- `confidence`
- `worker_model`
- `review_status`

Set `review_status` to `raw_worker_candidate`.

Allowed `object_type` values for this ticket:

{object_types}

## Rules

- Use only the supplied source chunks.
- Preserve `document_id`, `source_sha256`, and `chunk_id` exactly.
- Every `record_id` must start with `{document['document_id']}::`.
- Every `record_id` must be unique within this response.
- `page_anchor` must be a string, such as `PDF page 12` or `PDF pages 12-14`.
- Include a short `source_quote` copied from the supplied chunks.
- Return bare JSONL only. Do not wrap the response in markdown fences.
- Do not invent pages, sections, titles, values, definitions, or citations.
- Prefer fewer, stronger records over many vague records.
- For each supplied chunk, extract at least one strong record when the chunk
  contains a section heading, table, figure, map, appendix, acronym,
  definition, cross-reference, assumption, or major claim.
- If a chunk has no useful metadata, output no records for that chunk.

## Source Chunks

{chr(10).join(source_blocks)}
"""
    return ticket, included, truncated


def manifest_payload(
    *,
    evaluation_id: str,
    ticket_path: Path,
    output_dir: Path,
    models: list[str],
    repeats: int,
    timeout_seconds: int,
    base_url_file: str,
    provider_headers_file: str,
) -> dict[str, Any]:
    return {
        "evaluation_id": evaluation_id,
        "ticket": repo_relative(ticket_path),
        "expected_marker": "",
        "required_sections": [],
        "forbidden_phrases": [
            "I cannot",
            "I can't",
            "would do",
            "would have",
            "ready for",
            "completed successfully",
        ],
        "allow_unexpected_sections": True,
        "allow_preamble": False,
        "require_patch": False,
        "allowed_patch_files": [],
        "models": models,
        "repeats": repeats,
        "timeout_seconds": timeout_seconds,
        "output_dir": repo_relative(output_dir),
        "probe_script": "scripts/copilot_sdk_ollama_probe.py",
        "python_executable": "",
        "base_url": "",
        "base_url_file": base_url_file,
        "provider_headers_file": provider_headers_file,
        "wire_api": "completions",
        "mode": "empty",
        "base_directory": repo_relative(output_dir.parent / "copilot_sdk_home"),
        "sdk_source": "",
    }


def build_eval_packets(
    *,
    battery: dict[str, Any],
    registry: dict[str, Any],
    chunk_manifests: dict[str, dict[str, Any]],
    benchmark_root: Path,
    runtime_root: Path,
    base_url_file: str,
    provider_headers_file: str,
    timeout_seconds: int,
    max_ticket_chars: int,
) -> dict[str, Any]:
    documents = document_lookup(registry)
    ticket_shapes = {shape["shape_id"]: shape for shape in battery["ticket_shapes"]}
    models = {item["model"]: item for item in battery["models"]}
    packets: list[dict[str, Any]] = []

    def add_packet(
        *,
        wave_id: str,
        document_id: str,
        shape_id: str,
        model_names: list[str],
        repeats: int = 1,
    ) -> None:
        shape = ticket_shapes[shape_id]
        document = documents[document_id]
        chunk_manifest = chunk_manifests[document_id]
        page_windows = shape["page_windows"]
        chunks = selected_chunks(chunk_manifest, page_windows)
        chunk_manifest_path = benchmark_root / "chunk_manifests" / f"{document_id}.json"
        packet_id = f"{wave_id}__{document_id}__{shape_id}__{'-'.join(slug(m) for m in model_names)}"
        ticket_path = runtime_root / "p55" / "tickets" / f"{packet_id}.ticket.md"
        ticket, included, truncated = build_ticket(
            record_type=str(shape["record_type"]),
            document=document,
            chunk_manifest_path=chunk_manifest_path,
            chunks=chunks,
            max_ticket_chars=max_ticket_chars,
        )
        write_text(ticket_path, ticket)
        manifest_path = runtime_root / "p55" / "manifests" / f"{packet_id}.manifest.json"
        output_dir = runtime_root / "p55" / "eval" / packet_id
        write_json(
            manifest_path,
            manifest_payload(
                evaluation_id=packet_id,
                ticket_path=ticket_path,
                output_dir=output_dir,
                models=model_names,
                repeats=repeats,
                timeout_seconds=timeout_seconds,
                base_url_file=base_url_file,
                provider_headers_file=provider_headers_file,
            ),
        )
        packets.append(
            {
                "packet_id": packet_id,
                "wave_id": wave_id,
                "document_id": document_id,
                "shape_id": shape_id,
                "record_type": shape["record_type"],
                "models": model_names,
                "repeats": repeats,
                "ticket_path": repo_relative(ticket_path),
                "manifest_path": repo_relative(manifest_path),
                "output_dir": repo_relative(output_dir),
                "included_chunk_count": len(included),
                "requested_page_windows": page_windows,
                "requested_chunk_count": len(chunk_manifest["chunks"])
                if str(page_windows).lower() == "all"
                else int(page_windows),
                "ticket_text_truncated_by_char_cap": truncated,
                "ticket_char_count": len(ticket),
                "source_text_char_count": sum(int(chunk["text_char_count"]) for chunk in included),
            }
        )

    pilot_docs = [item["document_id"] for item in battery["documents"]]
    primary_model = "qwen3-coder-next:latest"
    for document_id in pilot_docs:
        add_packet(
            wave_id="wave1_single_model_smoke",
            document_id=document_id,
            shape_id="structure_x2",
            model_names=[primary_model],
        )
    for document_id in pilot_docs:
        add_packet(
            wave_id="wave1_full_document_smoke",
            document_id=document_id,
            shape_id="structure_full",
            model_names=[primary_model],
        )

    comparison_doc = str(
        battery.get("primary_comparison_document_id")
        or battery["documents"][-1]["document_id"]
    )
    add_packet(
        wave_id="wave2_model_ab",
        document_id=comparison_doc,
        shape_id="structure_x4",
        model_names=[
            "qwen3-coder:latest",
            "qwen3-coder-next:latest",
            "gpt-oss:120b",
        ],
    )

    for shape_id in ["structure_x2", "structure_x4", "structure_x8"]:
        add_packet(
            wave_id="wave3_size_scale",
            document_id=comparison_doc,
            shape_id=shape_id,
            model_names=[primary_model],
        )

    add_packet(
        wave_id="wave4_repeatability",
        document_id=comparison_doc,
        shape_id="structure_x4",
        model_names=[primary_model],
        repeats=3,
    )
    add_packet(
        wave_id="wave5_content_metadata_probe",
        document_id=comparison_doc,
        shape_id="content_x4",
        model_names=[primary_model],
    )

    return {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "battery_id": battery["battery_id"],
        "corpus_id": registry["corpus_id"],
        "packets": packets,
        "raw_ticket_policy": "Tickets contain source text and remain ignored under runtime/.",
        "model_catalog": list(models),
    }


def main() -> None:
    args = parse_args()
    registry = load_json(args.registry)
    battery = load_json(args.battery)
    documents = document_lookup(registry)
    chunk_manifests: dict[str, dict[str, Any]] = {}
    for item in battery["documents"]:
        document_id = str(item["document_id"])
        chunk_manifests[document_id] = extract_document_chunks(
            document=documents[document_id],
            runtime_root=args.runtime_root,
            benchmark_root=args.benchmark_root,
            window_pages=args.window_pages,
            overlap_pages=args.overlap_pages,
        )

    eval_index = build_eval_packets(
        battery=battery,
        registry=registry,
        chunk_manifests=chunk_manifests,
        benchmark_root=args.benchmark_root,
        runtime_root=args.runtime_root,
        base_url_file=args.base_url_file,
        provider_headers_file=args.provider_headers_file,
        timeout_seconds=args.timeout_seconds,
        max_ticket_chars=args.max_ticket_chars,
    )
    write_json(args.benchmark_root / "p55_eval_packet_index.json", eval_index)
    print(f"wrote chunk manifests for {len(chunk_manifests)} documents")
    print(f"wrote {len(eval_index['packets'])} eval packets")
    for packet in eval_index["packets"]:
        print(f"- {packet['packet_id']}: {packet['included_chunk_count']} chunks")


if __name__ == "__main__":
    main()
