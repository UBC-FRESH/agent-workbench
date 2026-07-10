"""Materialize the P89 document-indexing recipe v2 dry-run packet.

P89 is deliberately non-live. This helper reads the P88 selected corpus slice,
verifies ignored runtime text chunks, splits them into smaller section-level
ticket specs, writes raw-text worker tickets under ``runtime/``, and writes
sanitized tracked manifests/contracts under ``benchmarks/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SELECTION = Path("benchmarks/document_library/p88_selected_corpus_slice.json")
DEFAULT_TRACKED_ROOT = Path("benchmarks/document_library")
DEFAULT_RUNTIME_DIR = Path(
    "runtime/document_library/tsa23_tsr/p89_document_indexing_recipe_v2"
)
DEFAULT_MODEL_PLACEHOLDER = "configured-local-document-worker"
REQUIRED_FIELDS = (
    "record_id",
    "corpus_id",
    "document_id",
    "source_sha256",
    "chunk_id",
    "page_anchor",
    "document_component",
    "section_path",
    "object_type",
    "title",
    "summary",
    "source_quote",
    "confidence",
    "worker_model",
    "review_status",
)
ALLOWED_OBJECT_TYPES = (
    "component_boundary",
    "heading",
    "appendix",
    "table",
    "figure",
    "map",
    "acronym",
    "definition",
    "cross_reference",
    "section_summary",
    "claim",
    "assumption",
    "constraint",
    "policy_reference",
    "model_input",
    "numeric_value",
    "scenario",
    "sensitivity_test",
    "decision_rationale",
    "other",
)


@dataclass(frozen=True)
class ChunkText:
    chunk_id: str
    page_start: int
    page_end: int
    text_sha256: str
    text_char_count: int
    runtime_text_path: str
    text: str


@dataclass(frozen=True)
class SectionSpec:
    section_id: str
    chunk_id: str
    page_start: int
    page_end: int
    section_index: int
    section_title: str
    text: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or validate P89 document-indexing recipe v2 artifacts."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Agent Workbench checkout root. Defaults to the current directory.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    materialize = subparsers.add_parser(
        "materialize",
        help="Generate P89 dry-run tickets, manifests, and validation contracts.",
    )
    materialize.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    materialize.add_argument(
        "--tracked-output-root", type=Path, default=DEFAULT_TRACKED_ROOT
    )
    materialize.add_argument("--output-dir", type=Path, default=DEFAULT_RUNTIME_DIR)
    materialize.add_argument("--model-placeholder", default=DEFAULT_MODEL_PLACEHOLDER)
    materialize.add_argument(
        "--force",
        action="store_true",
        help="Overwrite generated runtime and tracked P89 outputs.",
    )

    validate = subparsers.add_parser(
        "validate-jsonl",
        help="Validate and mechanically repair a candidate JSONL file.",
    )
    validate.add_argument("--input", type=Path, required=True)
    validate.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_TRACKED_ROOT / "p89_jsonl_validation_contract.json",
    )
    validate.add_argument("--output", type=Path, required=True)
    validate.add_argument("--repaired-output", type=Path, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_root = args.project_root.resolve()
    if args.command == "materialize":
        materialize(args, project_root)
    elif args.command == "validate-jsonl":
        validate_jsonl_command(args, project_root)
    else:  # pragma: no cover - argparse prevents this branch.
        raise ValueError(f"unknown command: {args.command}")
    return 0


def materialize(args: argparse.Namespace, project_root: Path) -> None:
    selection_path = resolve_under_root(args.selection, project_root)
    tracked_root = resolve_under_root(args.tracked_output_root, project_root)
    output_dir = resolve_under_root(args.output_dir, project_root)

    selection = load_json(selection_path)
    chunk_manifest_path = resolve_under_root(
        Path(selection["document"]["tracked_chunk_manifest"]), project_root
    )
    chunk_manifest = load_json(chunk_manifest_path)
    chunks = verify_selected_chunks(selection, chunk_manifest, project_root)
    sections = split_sections(chunks)
    ticket_specs = build_ticket_specs(
        selection=selection,
        sections=sections,
        output_dir=output_dir,
        project_root=project_root,
    )
    if bool(args.force):
        clean_generated_runtime_files(output_dir)

    runtime_paths = [
        output_dir / "tickets" / f"{spec['ticket_id']}.ticket.md"
        for spec in ticket_specs
    ]
    runtime_paths.extend(
        output_dir / "validation_inputs" / f"{spec['ticket_id']}.candidate.jsonl"
        for spec in ticket_specs
    )
    runtime_paths.append(output_dir / "p89_runtime_index.json")
    tracked_paths = [
        tracked_root / "p89_recipe_v2_materialization_manifest.json",
        tracked_root / "p89_chunk_id_enum.json",
        tracked_root / "p89_jsonl_validation_contract.json",
        tracked_root / "p89_validation_input_manifest.json",
        tracked_root / "p89_dry_run_materialization_summary.json",
    ]
    ensure_overwritable(runtime_paths + tracked_paths, force=bool(args.force))

    write_runtime_tickets(
        selection=selection,
        sections=sections,
        ticket_specs=ticket_specs,
        output_dir=output_dir,
        model_placeholder=str(args.model_placeholder),
        project_root=project_root,
    )
    write_runtime_validation_inputs(ticket_specs, output_dir)
    write_json(output_dir / "p89_runtime_index.json", runtime_index(ticket_specs))

    chunk_enum = chunk_id_enum(selection, chunks)
    validation_contract = jsonl_validation_contract(selection, chunk_enum)
    validation_input_manifest = build_validation_input_manifest(ticket_specs)
    materialization_manifest = build_materialization_manifest(
        selection=selection,
        chunk_manifest_path=chunk_manifest_path,
        ticket_specs=ticket_specs,
        project_root=project_root,
    )
    summary = build_summary(selection, chunks, sections, ticket_specs)

    write_json(tracked_root / "p89_chunk_id_enum.json", chunk_enum)
    write_json(tracked_root / "p89_jsonl_validation_contract.json", validation_contract)
    write_json(
        tracked_root / "p89_validation_input_manifest.json",
        validation_input_manifest,
    )
    write_json(
        tracked_root / "p89_recipe_v2_materialization_manifest.json",
        materialization_manifest,
    )
    write_json(tracked_root / "p89_dry_run_materialization_summary.json", summary)

    print(
        f"wrote {repo_relative(tracked_root / 'p89_chunk_id_enum.json', project_root)}"
    )
    print(
        "wrote "
        f"{repo_relative(tracked_root / 'p89_jsonl_validation_contract.json', project_root)}"
    )
    print(
        "wrote "
        f"{repo_relative(tracked_root / 'p89_recipe_v2_materialization_manifest.json', project_root)}"
    )
    print(f"wrote {len(ticket_specs)} ignored runtime ticket specs")


def verify_selected_chunks(
    selection: dict[str, Any],
    chunk_manifest: dict[str, Any],
    project_root: Path,
) -> list[ChunkText]:
    manifest_by_id = {
        str(chunk["chunk_id"]): chunk for chunk in chunk_manifest["chunks"]
    }
    verified: list[ChunkText] = []
    for selected in selection["selected_scope"]["chunks"]:
        chunk_id = str(selected["chunk_id"])
        if chunk_id not in manifest_by_id:
            raise KeyError(f"selected chunk missing from manifest: {chunk_id}")
        manifest_chunk = manifest_by_id[chunk_id]
        runtime_text_path = resolve_under_root(
            Path(str(manifest_chunk["runtime_text_path"])), project_root
        )
        text = runtime_text_path.read_text(encoding="utf-8-sig")
        actual_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        expected_hash = str(selected["text_sha256"])
        if actual_hash != expected_hash:
            raise ValueError(f"text hash mismatch for {chunk_id}")
        if int(manifest_chunk["page_start"]) != int(selected["page_start"]):
            raise ValueError(f"page_start mismatch for {chunk_id}")
        if int(manifest_chunk["page_end"]) != int(selected["page_end"]):
            raise ValueError(f"page_end mismatch for {chunk_id}")
        verified.append(
            ChunkText(
                chunk_id=chunk_id,
                page_start=int(selected["page_start"]),
                page_end=int(selected["page_end"]),
                text_sha256=expected_hash,
                text_char_count=int(selected["text_char_count"]),
                runtime_text_path=str(manifest_chunk["runtime_text_path"]),
                text=text,
            )
        )
    return verified


def split_sections(chunks: list[ChunkText]) -> list[SectionSpec]:
    sections: list[SectionSpec] = []
    seen_pages: set[int] = set()
    for chunk in chunks:
        for page_number, page_text in split_pages(chunk.text):
            if page_number in seen_pages:
                continue
            seen_pages.add(page_number)
            page_sections = split_page_sections(page_text)
            for section_index, (title, text) in enumerate(page_sections, start=1):
                if not text.strip():
                    continue
                section_id = (
                    f"{chunk.chunk_id.replace('::', '__')}"
                    f"__p{page_number:03d}__s{section_index:02d}"
                )
                sections.append(
                    SectionSpec(
                        section_id=section_id,
                        chunk_id=chunk.chunk_id,
                        page_start=page_number,
                        page_end=page_number,
                        section_index=section_index,
                        section_title=title,
                        text=text.strip(),
                    )
                )
    if not sections:
        raise ValueError("no sections were materialized from selected chunks")
    return sections


def split_pages(text: str) -> list[tuple[int, str]]:
    pattern = re.compile(r"(?m)^\[PDF page (?P<page>\d+)\]\s*$")
    matches = list(pattern.finditer(text))
    if not matches:
        return [(1, text)]
    pages: list[tuple[int, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        page_text = text[start:end].strip()
        pages.append((int(match.group("page")), page_text))
    return pages


def split_page_sections(page_text: str) -> list[tuple[str, str]]:
    lines = page_text.splitlines()
    heading_positions = [
        index for index, line in enumerate(lines) if is_probable_section_heading(line)
    ]
    if not heading_positions:
        return [(first_nonblank_line(lines), page_text)]
    sections: list[tuple[str, str]] = []
    for pos_index, start in enumerate(heading_positions):
        end = (
            heading_positions[pos_index + 1]
            if pos_index + 1 < len(heading_positions)
            else len(lines)
        )
        block = "\n".join(lines[start:end]).strip()
        if block:
            sections.append((lines[start].strip(), block))
    leading = "\n".join(lines[: heading_positions[0]]).strip()
    if leading:
        sections.insert(
            0, (first_nonblank_line(lines[: heading_positions[0]]), leading)
        )
    return sections


def is_probable_section_heading(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 4:
        return False
    if re.match(r"^\d+(\.\d+)*\s+[A-Z][A-Z0-9 ,/&()'-]+$", stripped):
        return True
    if stripped.isupper() and any(char.isalpha() for char in stripped):
        return len(stripped) <= 100
    return False


def first_nonblank_line(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped[:100]
    return "untitled section"


def build_ticket_specs(
    *,
    selection: dict[str, Any],
    sections: list[SectionSpec],
    output_dir: Path,
    project_root: Path,
) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for section in sections:
        for record_pass in ("structure", "content_metadata"):
            ticket_id = f"p89_{slug(section.section_id)}_{record_pass}"
            specs.append(
                {
                    "ticket_id": ticket_id,
                    "phase": "P89",
                    "recipe_id": "document-indexing-workflow-v2",
                    "record_pass": record_pass,
                    "corpus_id": selection["corpus"]["corpus_id"],
                    "document_id": selection["document"]["document_id"],
                    "source_sha256": selection["document"]["source_sha256"],
                    "chunk_id": section.chunk_id,
                    "allowed_chunk_ids": selection["selected_scope"]["chunk_ids"],
                    "page_start": section.page_start,
                    "page_end": section.page_end,
                    "section_id": section.section_id,
                    "section_index": section.section_index,
                    "section_label": (
                        f"page_{section.page_start:03d}_section_"
                        f"{section.section_index:02d}"
                    ),
                    "section_title_sha256": hashlib.sha256(
                        section.section_title.encode("utf-8")
                    ).hexdigest(),
                    "section_title_char_count": len(section.section_title),
                    "source_text_char_count": len(section.text),
                    "source_text_sha256": hashlib.sha256(
                        section.text.encode("utf-8")
                    ).hexdigest(),
                    "ticket_path": repo_relative(
                        output_dir / "tickets" / f"{ticket_id}.ticket.md",
                        project_root,
                    ),
                    "candidate_input_path": repo_relative(
                        output_dir
                        / "validation_inputs"
                        / f"{ticket_id}.candidate.jsonl",
                        project_root,
                    ),
                    "live_execution_allowed": False,
                }
            )
    return specs


def write_runtime_tickets(
    *,
    selection: dict[str, Any],
    sections: list[SectionSpec],
    ticket_specs: list[dict[str, Any]],
    output_dir: Path,
    model_placeholder: str,
    project_root: Path,
) -> None:
    section_by_id = {section.section_id: section for section in sections}
    tickets_dir = output_dir / "tickets"
    tickets_dir.mkdir(parents=True, exist_ok=True)
    for spec in ticket_specs:
        section = section_by_id[str(spec["section_id"])]
        text = render_ticket(
            selection,
            spec,
            section_title=section.section_title,
            section_text=section.text,
            model_placeholder=model_placeholder,
        )
        path = project_root / str(spec["ticket_path"])
        path.write_text(text, encoding="utf-8")


def render_ticket(
    selection: dict[str, Any],
    spec: dict[str, Any],
    section_title: str,
    section_text: str,
    model_placeholder: str,
) -> str:
    allowed_chunk_ids = "\n".join(
        f"- `{chunk_id}`" for chunk_id in selection["selected_scope"]["chunk_ids"]
    )
    allowed_types = "\n".join(f"- `{value}`" for value in ALLOWED_OBJECT_TYPES)
    return f"""# P89 Document Indexing Recipe V2 Worker Ticket

## Authority Boundary

- Worker authority: no tools, no commands, no file edits, no browsing, no GitHub actions.
- Use only the source excerpt embedded in this ticket.
- Return JSONL only. Do not wrap output in Markdown fences. Do not add prose.
- This is a dry-run materialized ticket. It is not authorization to contact a live model.

## Mission

Extract `{spec["record_pass"]}` records from one bounded source section.

## Required Identity Fields

- `corpus_id`: `{spec["corpus_id"]}`
- `document_id`: `{spec["document_id"]}`
- `source_sha256`: `{spec["source_sha256"]}`
- `worker_model`: `{model_placeholder}`
- `review_status`: `raw_worker_candidate`

Allowed `chunk_id` values:

{allowed_chunk_ids}

The only source section for this ticket is:

- `section_id`: `{spec["section_id"]}`
- `chunk_id`: `{spec["chunk_id"]}`
- `page_start`: `{spec["page_start"]}`
- `page_end`: `{spec["page_end"]}`
- `section_title`: `{section_title}`

## Output Contract

Return one JSON object per line. Every line must be valid JSON and contain:

{chr(10).join(f"- `{field}`" for field in REQUIRED_FIELDS)}

Allowed `object_type` values:

{allowed_types}

## Rules

- Preserve `corpus_id`, `document_id`, `source_sha256`, and `chunk_id` exactly.
- Use only the allowed `chunk_id` enum; do not invent or normalize chunk IDs.
- Every `record_id` must start with `{spec["document_id"]}::`.
- Include a short `source_quote` copied from the excerpt.
- Use `PDF page {spec["page_start"]}` or a tighter page anchor when supported.
- Extract useful source-anchored records only. Do not add filler.
- If the excerpt contains no useful records, return no records.
- Stop after JSONL records.

## Source Excerpt

```text
section_id: {spec["section_id"]}
chunk_id: {spec["chunk_id"]}
page_range: {spec["page_start"]}-{spec["page_end"]}
section_text_sha256: {spec["source_text_sha256"]}

{section_text.strip()}
```
"""


def write_runtime_validation_inputs(
    ticket_specs: list[dict[str, Any]], output_dir: Path
) -> None:
    validation_dir = output_dir / "validation_inputs"
    validation_dir.mkdir(parents=True, exist_ok=True)
    for spec in ticket_specs:
        path = output_dir / "validation_inputs" / f"{spec['ticket_id']}.candidate.jsonl"
        path.write_text("", encoding="utf-8")


def runtime_index(ticket_specs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P89",
        "generated_utc": now_utc(),
        "recipe_id": "document-indexing-workflow-v2",
        "live_execution_allowed": False,
        "ticket_count": len(ticket_specs),
        "tickets": [
            {
                "ticket_id": spec["ticket_id"],
                "ticket_path": spec["ticket_path"],
                "candidate_input_path": spec["candidate_input_path"],
            }
            for spec in ticket_specs
        ],
        "raw_text_policy": "runtime tickets contain source text and remain ignored under runtime/",
    }


def chunk_id_enum(selection: dict[str, Any], chunks: list[ChunkText]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P89",
        "enum_id": "p89_allowed_chunk_ids",
        "source_slice": selection["slice_id"],
        "document_id": selection["document"]["document_id"],
        "corpus_id": selection["corpus"]["corpus_id"],
        "allowed_chunk_ids": [
            {
                "chunk_id": chunk.chunk_id,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "text_sha256": chunk.text_sha256,
                "text_char_count": chunk.text_char_count,
            }
            for chunk in chunks
        ],
        "unknown_chunk_id_policy": "reject after deterministic repair",
        "public_safety": {
            "raw_text_tracked": False,
            "raw_worker_outputs_tracked": False,
            "provider_urls_or_headers_tracked": False,
        },
    }


def jsonl_validation_contract(
    selection: dict[str, Any],
    chunk_enum: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P89",
        "contract_id": "p89_document_index_jsonl_validation_contract_v2",
        "source_slice": selection["slice_id"],
        "required_fields": list(REQUIRED_FIELDS),
        "allowed_object_types": list(ALLOWED_OBJECT_TYPES),
        "allowed_chunk_ids": [
            item["chunk_id"] for item in chunk_enum["allowed_chunk_ids"]
        ],
        "required_review_status": "raw_worker_candidate",
        "deterministic_repairs": [
            "strip markdown fence lines",
            "drop non-json preamble or trailing prose lines",
            "trim surrounding whitespace",
            "remove one trailing comma immediately before a JSON object close",
        ],
        "non_repairable_defects": [
            "unknown chunk_id after repair",
            "wrong corpus_id",
            "wrong document_id",
            "wrong source_sha256",
            "missing required field",
            "invalid object_type",
            "invalid review_status",
            "non-numeric confidence",
        ],
        "live_execution_allowed": False,
    }


def build_validation_input_manifest(
    ticket_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P89",
        "manifest_id": "p89_validation_input_manifest",
        "candidate_input_count": len(ticket_specs),
        "candidate_inputs": [
            {
                "ticket_id": spec["ticket_id"],
                "record_pass": spec["record_pass"],
                "candidate_input_path": spec["candidate_input_path"],
                "expected_initial_state": "empty_runtime_jsonl_placeholder",
            }
            for spec in ticket_specs
        ],
        "raw_worker_output_policy": "candidate JSONL files remain ignored under runtime/",
    }


def build_materialization_manifest(
    *,
    selection: dict[str, Any],
    chunk_manifest_path: Path,
    ticket_specs: list[dict[str, Any]],
    project_root: Path,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P89",
        "recipe_id": "document-indexing-workflow-v2",
        "status": "dry_run_materialized",
        "source_slice": selection["slice_id"],
        "chunk_manifest": repo_relative(chunk_manifest_path, project_root),
        "ticket_count": len(ticket_specs),
        "ticket_specs": ticket_specs,
        "live_execution_allowed": False,
        "first_possible_live_phase": "P92",
        "public_safety": {
            "raw_documents_tracked": False,
            "raw_text_tracked": False,
            "raw_prompts_tracked": False,
            "raw_worker_outputs_tracked": False,
            "provider_urls_or_headers_tracked": False,
            "personal_paths_tracked": False,
        },
    }


def build_summary(
    selection: dict[str, Any],
    chunks: list[ChunkText],
    sections: list[SectionSpec],
    ticket_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "P89",
        "summary_id": "p89_document_indexing_recipe_v2_dry_run",
        "status": "dry_run_materialized_no_live_model_contact",
        "source_slice": selection["slice_id"],
        "selected_chunk_count": len(chunks),
        "section_count": len(sections),
        "ticket_count": len(ticket_specs),
        "record_passes": sorted({str(spec["record_pass"]) for spec in ticket_specs}),
        "live_execution_allowed": False,
        "p90_ready_inputs": [
            "allowed chunk-ID enum",
            "section-level runtime tickets",
            "candidate JSONL placeholders",
            "deterministic JSONL validation contract",
        ],
        "stop_rules_preserved": selection["stop_rules"],
    }


def validate_jsonl_command(args: argparse.Namespace, project_root: Path) -> None:
    input_path = resolve_under_root(args.input, project_root)
    contract_path = resolve_under_root(args.contract, project_root)
    output_path = resolve_under_root(args.output, project_root)
    repaired_output_path = (
        resolve_under_root(args.repaired_output, project_root)
        if args.repaired_output is not None
        else None
    )

    contract = load_json(contract_path)
    text = input_path.read_text(encoding="utf-8-sig")
    report, repaired_lines = validate_jsonl_text(text, contract)
    write_json(output_path, report)
    if repaired_output_path is not None:
        repaired_output_path.parent.mkdir(parents=True, exist_ok=True)
        repaired_output_path.write_text(
            "\n".join(repaired_lines) + "\n", encoding="utf-8"
        )
    print(f"wrote {repo_relative(output_path, project_root)}")


def validate_jsonl_text(
    text: str,
    contract: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    allowed_chunks = set(str(value) for value in contract["allowed_chunk_ids"])
    required_fields = tuple(str(value) for value in contract["required_fields"])
    allowed_types = set(str(value) for value in contract["allowed_object_types"])
    required_status = str(contract["required_review_status"])
    errors: list[dict[str, Any]] = []
    repaired_lines: list[str] = []
    parsed_count = 0
    repaired_count = 0
    dropped_non_json_lines = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        candidate = line.strip()
        if not candidate or candidate.startswith("```"):
            if candidate.startswith("```"):
                repaired_count += 1
            continue
        if not candidate.startswith("{"):
            dropped_non_json_lines += 1
            repaired_count += 1
            continue
        if candidate.endswith(","):
            candidate = candidate[:-1]
            repaired_count += 1
        record = parse_record(candidate, line_number, errors)
        if record is None:
            continue
        parsed_count += 1
        validate_record(
            record=record,
            line_number=line_number,
            errors=errors,
            required_fields=required_fields,
            allowed_chunks=allowed_chunks,
            allowed_types=allowed_types,
            required_status=required_status,
        )
        repaired_lines.append(json.dumps(record, sort_keys=True, separators=(",", ":")))

    fatal_error_count = sum(1 for error in errors if error["severity"] == "error")
    report = {
        "schema_version": 1,
        "phase": "P89",
        "status": "valid" if fatal_error_count == 0 else "invalid",
        "parseable_record_count": parsed_count,
        "repaired_line_count": repaired_count,
        "dropped_non_json_line_count": dropped_non_json_lines,
        "emitted_repaired_record_count": len(repaired_lines),
        "fatal_error_count": fatal_error_count,
        "errors": errors,
    }
    return report, repaired_lines


def parse_record(
    candidate: str,
    line_number: int,
    errors: list[dict[str, Any]],
) -> dict[str, Any] | None:
    try:
        record = json.loads(candidate)
    except json.JSONDecodeError as exc:
        errors.append(
            {
                "line": line_number,
                "severity": "error",
                "kind": "malformed_json",
                "message": exc.msg,
            }
        )
        return None
    if not isinstance(record, dict):
        errors.append(
            {
                "line": line_number,
                "severity": "error",
                "kind": "non_object_record",
                "message": "JSONL records must be objects",
            }
        )
        return None
    return record


def validate_record(
    *,
    record: dict[str, Any],
    line_number: int,
    errors: list[dict[str, Any]],
    required_fields: tuple[str, ...],
    allowed_chunks: set[str],
    allowed_types: set[str],
    required_status: str,
) -> None:
    for field in required_fields:
        if field not in record:
            errors.append(
                {
                    "line": line_number,
                    "severity": "error",
                    "kind": "missing_required_field",
                    "field": field,
                }
            )
    chunk_id = str(record.get("chunk_id", ""))
    if chunk_id not in allowed_chunks:
        errors.append(
            {
                "line": line_number,
                "severity": "error",
                "kind": "unknown_chunk_id",
                "value": chunk_id,
            }
        )
    object_type = str(record.get("object_type", ""))
    if object_type not in allowed_types:
        errors.append(
            {
                "line": line_number,
                "severity": "error",
                "kind": "invalid_object_type",
                "value": object_type,
            }
        )
    if str(record.get("review_status", "")) != required_status:
        errors.append(
            {
                "line": line_number,
                "severity": "error",
                "kind": "invalid_review_status",
                "value": record.get("review_status"),
            }
        )
    confidence = record.get("confidence")
    if not isinstance(confidence, int | float):
        errors.append(
            {
                "line": line_number,
                "severity": "error",
                "kind": "invalid_confidence",
                "value": confidence,
            }
        )


def ensure_overwritable(paths: list[Path], *, force: bool) -> None:
    if force:
        return
    existing = [path for path in paths if path.exists()]
    if existing:
        listed = ", ".join(str(path) for path in existing[:5])
        raise FileExistsError(f"generated output exists; pass --force: {listed}")


def clean_generated_runtime_files(output_dir: Path) -> None:
    generated_dirs = (output_dir / "tickets", output_dir / "validation_inputs")
    for directory in generated_dirs:
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if path.is_file() and (
                path.name.endswith(".ticket.md")
                or path.name.endswith(".candidate.jsonl")
            ):
                path.unlink()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def resolve_under_root(path: Path, root: Path) -> Path:
    resolved = path if path.is_absolute() else root / path
    resolved = resolved.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path escapes project root: {path}")
    return resolved


def repo_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
