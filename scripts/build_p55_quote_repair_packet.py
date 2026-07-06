"""Build a P55 quote-compact repair-prepass packet.

The repair ticket includes raw candidate values, quotes, and selected source
chunks, so it is written only under ignored ``runtime/`` paths. Tracked outputs
from the paired summarizer contain only sanitized field metadata and token
counts.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_COMPARISON = Path(
    "benchmarks/document_library/tsa23_tsr/"
    "p55_wave7_dual_model_typed_fact_ensemble_comparison.json"
)
DEFAULT_VERIFIER_SUMMARY = Path(
    "benchmarks/document_library/tsa23_tsr/"
    "p55_wave8_disagreement_verification_qwen36_summary.json"
)
DEFAULT_PACKET_INDEX = Path(
    "benchmarks/document_library/tsa23_tsr/p55_wave10_quote_repair_packet.json"
)
DEFAULT_RUNTIME_ROOT = Path("runtime/document_library/tsa23_tsr/p55")
DEFAULT_MODEL = "qwen3-coder-next:latest"
DEFAULT_TIMEOUT_SECONDS = 1800
QUOTE_WORD_LIMIT = 25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the P55 Wave 10 quote repair packet.")
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON)
    parser.add_argument("--verifier-summary", type=Path, default=DEFAULT_VERIFIER_SUMMARY)
    parser.add_argument("--output-index", type=Path, default=DEFAULT_PACKET_INDEX)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--base-url-file", default="runtime/ollama_openai_base_url.txt")
    parser.add_argument("--provider-headers-file", default="runtime/local_provider_headers.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    comparison = load_json(args.comparison)
    verifier = load_json(args.verifier_summary)
    target_fields = select_target_fields(comparison, verifier)
    if not target_fields:
        raise ValueError("no quote-repair target fields selected")

    candidate_payloads = load_candidate_payloads(comparison)
    source_chunks = load_source_chunks(comparison)
    packet_id = f"wave10_quote_repair_prepass__{comparison['document_id']}__{slug(args.model)}"
    ticket_path = args.runtime_root / "tickets" / f"{packet_id}.ticket.md"
    manifest_path = args.runtime_root / "manifests" / f"{packet_id}.manifest.json"
    output_dir = args.runtime_root / "eval" / packet_id

    ticket = render_ticket(
        comparison=comparison,
        verifier=verifier,
        candidate_payloads=candidate_payloads,
        target_fields=target_fields,
        source_chunks=source_chunks,
        model=args.model,
    )
    write_text(ticket_path, ticket)
    write_json(
        manifest_path,
        {
            "evaluation_id": packet_id,
            "ticket": slash_path(ticket_path),
            "expected_marker": "",
            "required_sections": [],
            "forbidden_phrases": [
                "would do",
                "would have",
                "ready for",
                "completed successfully",
            ],
            "allow_unexpected_sections": True,
            "allow_preamble": False,
            "require_patch": False,
            "allowed_patch_files": [],
            "models": [args.model],
            "repeats": 1,
            "timeout_seconds": args.timeout_seconds,
            "output_dir": slash_path(output_dir),
            "probe_script": "scripts/copilot_sdk_ollama_probe.py",
            "python_executable": "",
            "base_url": "",
            "base_url_file": args.base_url_file,
            "provider_headers_file": args.provider_headers_file,
            "wire_api": "completions",
            "mode": "empty",
            "base_directory": slash_path(output_dir.parent / "copilot_sdk_home_wave10"),
            "sdk_source": "",
        },
    )
    write_json(
        args.output_index,
        {
            "schema_version": 1,
            "generated_utc": now_utc(),
            "phase": "P55",
            "wave_id": "wave10_quote_repair_prepass",
            "packet_id": packet_id,
            "document_id": comparison["document_id"],
            "source_wave_id": comparison["wave_id"],
            "source_packet_id": comparison["packet_id"],
            "source_verifier_packet_id": verifier["packet_id"],
            "repair_model": args.model,
            "quote_word_limit": QUOTE_WORD_LIMIT,
            "field_count": len(target_fields),
            "fields": [field["field"] for field in target_fields],
            "selection_reasons": {
                field["field"]: field["selection_reasons"] for field in target_fields
            },
            "ticket_path": slash_path(ticket_path),
            "manifest_path": slash_path(manifest_path),
            "output_dir": slash_path(output_dir),
            "raw_ticket_policy": "Repair ticket includes source chunks and raw candidate values; keep ignored under runtime/.",
            "tracked_output_policy": "Track only sanitized repair metrics, hashes, verdict classes, and token counts.",
        },
    )
    print(f"wrote {ticket_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {args.output_index}")
    return 0


def select_target_fields(
    comparison: dict[str, Any],
    verifier: dict[str, Any],
) -> list[dict[str, Any]]:
    reasons: dict[str, set[str]] = {}
    for row in comparison["field_comparisons"]:
        field = row["field"]
        for side in ("left", "right"):
            payload = row[side]
            if payload["source_quote_over_limit"]:
                reasons.setdefault(field, set()).add(f"wave7_{side}_quote_over_limit")
            if payload["confidence_bucket"] == "low":
                reasons.setdefault(field, set()).add(f"wave7_{side}_low_confidence")
            if payload["schema_issue"]:
                reasons.setdefault(field, set()).add(f"wave7_{side}_schema_issue")
            if payload["chunk_id_present"] and not payload["chunk_id_valid"]:
                reasons.setdefault(field, set()).add(f"wave7_{side}_invalid_chunk_id")
    for row in verifier.get("field_verdicts", []):
        field = row["field"]
        if row["source_quote_over_limit"]:
            reasons.setdefault(field, set()).add("wave8_quote_over_limit")
        if row["verdict"] in {"needs_supervisor", "insufficient_evidence"}:
            reasons.setdefault(field, set()).add(f"wave8_{row['verdict']}")
        if row["final_chunk_id_present"] and not row["final_chunk_id_valid"]:
            reasons.setdefault(field, set()).add("wave8_invalid_chunk_id")

    return [
        {"field": field, "selection_reasons": sorted(field_reasons)}
        for field, field_reasons in sorted(reasons.items())
    ]


def load_candidate_payloads(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    summary_path = (
        Path("runtime/document_library/tsa23_tsr/p55/eval")
        / str(comparison["packet_id"])
        / "summary.json"
    )
    summary = load_json(summary_path)
    rows = summary.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"Wave 7 summary rows must be a list: {summary_path}")
    by_model: dict[str, str] = {}
    for row in rows:
        if isinstance(row, dict):
            by_model[str(row.get("model", ""))] = str(row.get("assistant_message", ""))
    payloads: list[dict[str, Any]] = []
    for candidate in comparison["candidate_summaries"]:
        model = str(candidate["model"])
        text = by_model.get(model, "")
        if not text:
            raise ValueError(f"candidate assistant message not found for model: {model}")
        payloads.append({"model": model, "candidate": parse_json_from_text(text)})
    return payloads


def parse_json_from_text(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("text does not contain JSON object")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("parsed JSON is not an object")
    return value


def load_source_chunks(comparison: dict[str, Any]) -> list[dict[str, str]]:
    ticket_path = Path(
        "runtime/document_library/tsa23_tsr/p55/tickets/"
        f"{comparison['packet_id']}.ticket.md"
    )
    text = ticket_path.read_text(encoding="utf-8-sig")
    chunks: list[dict[str, str]] = []
    pattern = re.compile(
        r"```text\s+chunk_id: (?P<chunk_id>[^\n]+)\n"
        r"page_range: (?P<page_range>[^\n]+)\n"
        r"text_sha256: (?P<sha>[^\n]+)\n\n"
        r"(?P<text>.*?)(?=\n```)",
        flags=re.DOTALL,
    )
    for match in pattern.finditer(text):
        chunks.append(
            {
                "chunk_id": match.group("chunk_id").strip(),
                "page_range": match.group("page_range").strip(),
                "text_sha256": match.group("sha").strip(),
                "text": match.group("text").strip(),
            }
        )
    if not chunks:
        raise ValueError(f"no source chunks parsed from {ticket_path}")
    return chunks


def render_ticket(
    *,
    comparison: dict[str, Any],
    verifier: dict[str, Any],
    candidate_payloads: list[dict[str, Any]],
    target_fields: list[dict[str, Any]],
    source_chunks: list[dict[str, str]],
    model: str,
) -> str:
    field_names = [field["field"] for field in target_fields]
    candidate_blocks = []
    for payload in candidate_payloads:
        candidate_blocks.append(
            "\n".join(
                [
                    f"## Candidate From {payload['model']}",
                    "",
                    "```json",
                    json.dumps(selected_candidate(payload["candidate"], field_names), indent=2),
                    "```",
                ]
            )
        )
    verifier_subset = {
        row["field"]: {
            "verdict": row["verdict"],
            "final_status": row["final_status"],
            "source_quote_word_count": row["source_quote_word_count"],
            "source_quote_over_limit": row["source_quote_over_limit"],
            "confidence_bucket": row["confidence_bucket"],
            "reason_code": row["reason_code"],
        }
        for row in verifier.get("field_verdicts", [])
        if row["field"] in field_names
    }
    skeleton = {
        field: {
            "action": "needs_supervisor",
            "repaired_status": "uncertain",
            "repaired_value": None,
            "repaired_units": None,
            "repaired_page_anchor": None,
            "repaired_chunk_id": None,
            "source_quote": None,
            "confidence": 0.0,
            "reason_code": "unreviewed",
        }
        for field in field_names
    }
    source_blocks = []
    for chunk in source_chunks:
        source_blocks.append(
            "\n".join(
                [
                    "```text",
                    f"chunk_id: {chunk['chunk_id']}",
                    f"page_range: {chunk['page_range']}",
                    f"text_sha256: {chunk['text_sha256']}",
                    "",
                    chunk["text"],
                    "```",
                ]
            )
        )
    return f"""# P55 Wave 10 Quote-Compact Repair Prepass Ticket

## Mission

Repair only the targeted typed-fact fields. Use the candidate subsets,
Wave 8 verifier metadata, and supplied source chunks. Do not use tools,
commands, files, browsing, GitHub, or outside knowledge.

Return one strict JSON object only. No prose, markdown fences, arrays at the
top level, or chain-of-thought.

## Current State

- phase: `P55`
- wave_id: `wave10_quote_repair_prepass`
- document_id: `{comparison['document_id']}`
- source_packet_id: `{comparison['packet_id']}`
- source_verifier_packet_id: `{verifier['packet_id']}`
- repair_model: `{model}`
- quote_word_limit: `{QUOTE_WORD_LIMIT}`
- target_field_count: `{len(field_names)}`

## Output Schema

Return this top-level object:

```json
{{
  "repair_model": "<ACTIVE_MODEL_NAME>",
  "review_status": "raw_repair_candidate",
  "document_id": "{comparison['document_id']}",
  "source_packet_id": "{comparison['packet_id']}",
  "repairs": {json.dumps(skeleton, indent=2)}
}}
```

Allowed `action` values:

- `repaired`
- `unchanged`
- `needs_verifier`
- `needs_supervisor`

Rules:

- Include exactly one `repairs` entry for each targeted field.
- Preserve every target field key exactly.
- Keep every `source_quote` to {QUOTE_WORD_LIMIT} words or fewer.
- `repaired_chunk_id` must be one of the supplied chunk IDs or null.
- Preserve the original field's value type when repairing a field.
- If the supplied source chunks cannot prove the field, use
  `needs_supervisor`; do not invent a value.
- This is a compact repair prepass, not a full verifier. Do not re-litigate
  fields that have no listed defect.

## Target Fields And Reasons

```json
{json.dumps(target_fields, indent=2)}
```

## Wave 8 Verifier Metadata For Target Fields

```json
{json.dumps(verifier_subset, indent=2)}
```

## Candidate JSON Subsets

{chr(10).join(candidate_blocks)}

## Source Chunks

{chr(10).join(source_blocks)}
"""


def selected_candidate(candidate: dict[str, Any], field_names: list[str]) -> dict[str, Any]:
    fields = candidate.get("fields", {})
    selected = {
        field: fields.get(field)
        for field in field_names
        if isinstance(fields, dict) and field in fields
    }
    return {
        "candidate_id": candidate.get("candidate_id"),
        "worker_model": candidate.get("worker_model"),
        "document_id": candidate.get("document_id"),
        "fields": selected,
    }


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slash_path(path: Path) -> str:
    return path.as_posix()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
