"""Build ignored P63 document-indexing runtime tickets and eval manifests.

The tracked P63 pilot plan names sanitized chunks and hashes. This helper reads
that plan plus the tracked chunk manifest, verifies the ignored runtime chunk
files, and writes one bounded worker ticket plus one SDK eval manifest under
``runtime/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path(
    "benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_plan.json"
)
DEFAULT_OUTPUT_DIR = Path("runtime/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot")
DEFAULT_MODEL = "qwen3.6:35b-a3b-q8_0"
DEFAULT_TIMEOUT_SECONDS = 2400


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize the ignored P63 bounded TSA23 recipe pilot runtime pack."
    )
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated runtime ticket and manifest files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path.cwd()
    plan_path = resolve_under_root(args.plan, project_root)
    output_dir = resolve_under_root(args.output_dir, project_root)

    plan = load_json(plan_path)
    chunk_manifest_path = resolve_under_root(
        Path(plan["selected_document"]["tracked_chunk_manifest"]), project_root
    )
    chunk_manifest = load_json(chunk_manifest_path)

    selected_chunks = verify_selected_chunks(plan, chunk_manifest, project_root)

    tickets_dir = output_dir / "tickets"
    manifests_dir = output_dir / "manifests"
    tickets_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    ticket_path = tickets_dir / "p63_section_map_typed_fact_ticket.md"
    manifest_path = manifests_dir / "p63_section_map_typed_fact_manifest.json"
    runtime_index_path = output_dir / "p63_runtime_index.json"

    for path in (ticket_path, manifest_path, runtime_index_path):
        if path.exists() and not args.force:
            raise FileExistsError(f"{path} already exists; pass --force to overwrite")

    ticket_text = render_ticket(plan, selected_chunks, args.model)
    ticket_path.write_text(ticket_text, encoding="utf-8")

    manifest = render_eval_manifest(
        project_root=project_root,
        output_dir=output_dir,
        ticket_path=ticket_path,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    write_json(manifest_path, manifest)

    runtime_index = {
        "schema_version": 1,
        "generated_utc": now_utc(),
        "pilot_id": plan["pilot_id"],
        "phase": plan["phase"],
        "model": args.model,
        "ticket": repo_relative(ticket_path, project_root),
        "manifest": repo_relative(manifest_path, project_root),
        "output_dir": repo_relative(Path(manifest["output_dir"]), project_root),
        "raw_text_policy": "ticket, raw chunks, prompts, provider details, and worker outputs stay ignored under runtime/",
        "selected_document": plan["selected_document"],
        "selected_chunks": [
            {
                "chunk_id": chunk["chunk_id"],
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "text_char_count": chunk["text_char_count"],
                "text_sha256": chunk["text_sha256"],
                "runtime_text_path": chunk["runtime_text_path"],
            }
            for chunk in selected_chunks
        ],
    }
    write_json(runtime_index_path, runtime_index)

    print(f"wrote {repo_relative(ticket_path, project_root)}")
    print(f"wrote {repo_relative(manifest_path, project_root)}")
    print(f"wrote {repo_relative(runtime_index_path, project_root)}")
    return 0


def verify_selected_chunks(
    plan: dict[str, Any], chunk_manifest: dict[str, Any], project_root: Path
) -> list[dict[str, Any]]:
    manifest_by_id = {chunk["chunk_id"]: chunk for chunk in chunk_manifest["chunks"]}
    verified: list[dict[str, Any]] = []

    for selected in plan["selected_chunks"]:
        chunk_id = selected["chunk_id"]
        if chunk_id not in manifest_by_id:
            raise KeyError(f"selected chunk missing from tracked manifest: {chunk_id}")
        manifest_chunk = manifest_by_id[chunk_id]
        runtime_text_path = resolve_under_root(
            Path(manifest_chunk["runtime_text_path"]), project_root
        )
        if not runtime_text_path.exists():
            raise FileNotFoundError(f"runtime text chunk missing: {runtime_text_path}")

        text = runtime_text_path.read_text(encoding="utf-8")
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if text_hash != selected["text_sha256"]:
            raise ValueError(f"text hash mismatch for {chunk_id}")
        expected_count = int(selected["text_char_count"])
        if len(text) != expected_count and not (
            len(text) == expected_count + 1 and text.endswith("\n")
        ):
            raise ValueError(f"text char count mismatch for {chunk_id}")
        if manifest_chunk["page_start"] != selected["page_start"]:
            raise ValueError(f"page_start mismatch for {chunk_id}")
        if manifest_chunk["page_end"] != selected["page_end"]:
            raise ValueError(f"page_end mismatch for {chunk_id}")

        verified.append(
            {
                **selected,
                "runtime_text_path": manifest_chunk["runtime_text_path"],
                "text": text,
            }
        )

    return verified


def render_ticket(plan: dict[str, Any], chunks: list[dict[str, Any]], model: str) -> str:
    document = plan["selected_document"]
    corpus = plan["corpus"]
    chunk_ids = "\n".join(f"- `{chunk['chunk_id']}`" for chunk in chunks)
    chunk_payload = "\n\n".join(render_chunk(chunk) for chunk in chunks)

    return f"""# P63 Bounded TSA23 Recipe Pilot Worker Ticket

## Authority Boundary

- Worker authority: no tools, no commands, no file edits, no GitHub actions.
- Use only the document text embedded in this ticket.
- Do not infer facts from outside knowledge.
- Return JSONL only. Do not wrap output in Markdown fences. Do not add prose.
- The supervisor will validate schema, source identity, chunk IDs, and public safety.

## Mission

Extract a section map and typed indexing facts from the bounded TSA23 public
data-package slice.

This is not a full-document summary. Produce source-anchored records that would
help build a machine-readable technical-document metadata index for future
forest-estate-model setup work.

## Required Identity Fields

- `document_id`: `{document['document_id']}`
- `corpus_id`: `{corpus['corpus_id']}`
- `worker_model`: `{model}`
- `review_status`: `raw_worker_candidate`

Allowed `chunk_id` values:

{chunk_ids}

## Output Contract

Return one JSON object per line. Every line must be valid JSON and must contain
these fields:

- `record_type`: one of `component_boundary`, `heading`, `table`, `figure`,
  `map`, `acronym`, `definition`, `cross_reference`, `tsr_fact`,
  `assumption`, `constraint`, `data_source`, `section_summary`, or `other`.
- `document_id`: exact required document ID.
- `corpus_id`: exact required corpus ID.
- `chunk_id`: one of the allowed chunk IDs.
- `page_start`: integer page start for the source evidence.
- `page_end`: integer page end for the source evidence.
- `title_or_label`: heading, table label, fact label, acronym, or concise label.
- `normalized_key`: stable lowercase snake_case key when useful, otherwise `""`.
- `value_summary`: concise extracted meaning or metadata value.
- `source_quote`: short source-anchored excerpt. Target 25 words or fewer, but
  do not omit important evidence only to hit the target.
- `source_anchor`: page, table, figure, section, or nearby heading reference.
- `confidence`: number from 0.0 to 1.0.
- `worker_model`: exact required worker model.
- `review_status`: `raw_worker_candidate`.
- `notes`: concise uncertainty note, or `""`.

## Extraction Priorities

Prioritize:

1. Major document components and heading hierarchy.
2. Tables, figures, maps, and appendices.
3. Acronyms and definitions.
4. Cross-references to other TSR documents, appendices, tables, figures, maps,
   datasets, or legislation.
5. Typed TSR facts useful for future modelling setup, including management-unit
   identity, land-base categories, inventory/data sources, analysis units,
   growth/yield assumptions, constraints, disturbance assumptions, harvest-flow
   assumptions, and socioeconomic or First Nations context.
6. Uncertainties, assumptions, or places where the text says values are
   pending, preliminary, reviewed elsewhere, or subject to change.

There is no hidden record cap. Extract all useful records from the supplied
chunks. If a chunk is dense, prefer more records over a terse summary.

## Source Text

{chunk_payload}
"""


def render_chunk(chunk: dict[str, Any]) -> str:
    return f"""### Chunk `{chunk['chunk_id']}`

Pages: {chunk['page_start']}-{chunk['page_end']}

```text
{chunk['text']}
```"""


def render_eval_manifest(
    project_root: Path,
    output_dir: Path,
    ticket_path: Path,
    model: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    return {
        "evaluation_id": "p63_bounded_tsa23_recipe_pilot_section_map_typed_fact",
        "ticket": repo_relative(ticket_path, project_root),
        "expected_marker": "",
        "required_sections": [],
        "forbidden_phrases": [
            "I cannot",
            "I can't",
            "would have",
            "would do",
            "```",
        ],
        "allow_unexpected_sections": True,
        "allow_preamble": True,
        "require_patch": False,
        "allowed_patch_files": [],
        "models": [model],
        "repeats": 1,
        "timeout_seconds": timeout_seconds,
        "output_dir": repo_relative(output_dir / "eval" / "section_map_typed_fact", project_root),
        "probe_script": "scripts/copilot_sdk_ollama_probe.py",
        "python_executable": ".venv/Scripts/python.exe",
        "base_url": "",
        "base_url_file": "runtime/ollama_openai_base_url.txt",
        "provider_headers_file": "runtime/local_provider_headers.json",
        "wire_api": "completions",
        "mode": "empty",
        "base_directory": repo_relative(output_dir / "copilot_sdk_home", project_root),
        "sdk_source": "",
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_under_root(path: Path, root: Path) -> Path:
    resolved = path if path.is_absolute() else root / path
    resolved = resolved.resolve()
    root_resolved = root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ValueError(f"path escapes project root: {path}")
    return resolved


def repo_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
