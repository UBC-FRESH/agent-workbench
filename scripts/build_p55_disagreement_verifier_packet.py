"""Build a P55 disagreement-only verifier packet.

The verifier ticket includes raw candidate values, quotes, and selected source
chunks, so it is written only under ignored ``runtime/`` paths. The tracked
packet index records sanitized metadata needed to reproduce the run.
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
DEFAULT_PACKET_INDEX = Path("benchmarks/document_library/tsa23_tsr/p55_wave8_verifier_packet.json")
DEFAULT_RUNTIME_ROOT = Path("runtime/document_library/tsa23_tsr/p55")
DEFAULT_MODEL = "deepseek-r1:latest"
DEFAULT_TIMEOUT_SECONDS = 3600


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the P55 Wave 8 verifier packet.")
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON)
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
    candidate_payloads = load_candidate_payloads(comparison)
    fields = fields_requiring_verification(comparison)
    if not fields:
        raise ValueError("comparison has no fields requiring verification")
    packet_id = f"wave8_disagreement_verification__{comparison['document_id']}__{slug(args.model)}"
    ticket_path = args.runtime_root / "tickets" / f"{packet_id}.ticket.md"
    manifest_path = args.runtime_root / "manifests" / f"{packet_id}.manifest.json"
    output_dir = args.runtime_root / "eval" / packet_id
    source_chunks = load_source_chunks(comparison)
    ticket = render_ticket(
        comparison=comparison,
        candidate_payloads=candidate_payloads,
        fields=fields,
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
            "base_directory": slash_path(output_dir.parent / "copilot_sdk_home_wave8"),
            "sdk_source": "",
        },
    )
    packet_index = {
        "schema_version": 1,
        "generated_utc": now_utc(),
        "phase": "P55",
        "wave_id": "wave8_disagreement_verification",
        "packet_id": packet_id,
        "document_id": comparison["document_id"],
        "source_wave_id": comparison["wave_id"],
        "source_packet_id": comparison["packet_id"],
        "verifier_model": args.model,
        "field_count": len(fields),
        "fields": [field["field"] for field in fields],
        "agreement_classes": sorted({field["agreement_class"] for field in fields}),
        "ticket_path": slash_path(ticket_path),
        "manifest_path": slash_path(manifest_path),
        "output_dir": slash_path(output_dir),
        "raw_ticket_policy": "Verifier ticket includes source chunks and raw candidate values; keep ignored under runtime/.",
        "tracked_output_policy": "Track only sanitized verifier metrics and verdict classes.",
    }
    write_json(args.output_index, packet_index)
    print(f"wrote {ticket_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {args.output_index}")
    return 0


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
        payloads.append(
            {
                "model": model,
                "candidate": parse_candidate_from_result(text),
            }
        )
    return payloads


def parse_candidate_from_result(text: str) -> dict[str, Any]:
    assistant_message_match = re.search(
        r"## Assistant Message\s+```text\s+(.*?)\s+```",
        text,
        flags=re.DOTALL,
    )
    candidate_text = assistant_message_match.group(1) if assistant_message_match else text
    start = candidate_text.find("{")
    end = candidate_text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("candidate result does not contain JSON object")
    value = json.loads(candidate_text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("candidate JSON is not an object")
    return value


def fields_requiring_verification(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for row in comparison["field_comparisons"]:
        if row["agreement_class"] not in {"both_not_found", "value_agreement"}:
            fields.append(row)
            continue
        if (
            row["left"]["schema_issue"]
            or row["right"]["schema_issue"]
            or row["left"]["source_quote_over_limit"]
            or row["right"]["source_quote_over_limit"]
            or (row["left"]["chunk_id_present"] and not row["left"]["chunk_id_valid"])
            or (row["right"]["chunk_id_present"] and not row["right"]["chunk_id_valid"])
        ):
            fields.append(row)
    return fields


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
    candidate_payloads: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    source_chunks: list[dict[str, str]],
    model: str,
) -> str:
    field_names = [field["field"] for field in fields]
    candidate_blocks = []
    for payload in candidate_payloads:
        candidate_blocks.append(
            "\n".join(
                [
                    f"## Candidate From {payload['model']}",
                    "",
                    "```json",
                    json.dumps(redacted_candidate(payload["candidate"], field_names), indent=2),
                    "```",
                ]
            )
        )
    comparison_block = json.dumps(
        [
            {
                "field": field["field"],
                "agreement_class": field["agreement_class"],
                "left_model": field["left_model"],
                "right_model": field["right_model"],
            }
            for field in fields
        ],
        indent=2,
    )
    verdict_skeleton = json.dumps(
        {
            field["field"]: {
                "verdict": "needs_supervisor",
                "final_status": "uncertain",
                "final_value": None,
                "final_units": None,
                "final_page_anchor": None,
                "final_chunk_id": None,
                "source_quote": None,
                "confidence": 0.0,
                "reason_code": "unreviewed",
            }
            for field in fields
        },
        indent=2,
    )
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
    return f"""# P55 Wave 8 Disagreement Verifier Ticket

## Mission

You are the local verifier for a dual-model TSR metadata extraction ensemble.
Resolve only the listed disagreement or schema-issue fields. Use the supplied
source chunks and candidate JSON only. Do not use tools, commands, files,
browsing, or GitHub.

Return one strict JSON object only. No prose, markdown fences, arrays at the
top level, or chain-of-thought. If you need to reason, keep it internal and
return only the final structured verdicts.

## Current State

- phase: `P55`
- wave_id: `wave8_disagreement_verification`
- source_wave_id: `{comparison['wave_id']}`
- source_packet_id: `{comparison['packet_id']}`
- document_id: `{comparison['document_id']}`
- verifier_model: `{model}`
- fields_to_verify: `{len(fields)}`

## Output Schema

Return this top-level object:

```json
{{
  "verifier_model": "<ACTIVE_MODEL_NAME>",
  "review_status": "raw_verifier_candidate",
  "document_id": "{comparison['document_id']}",
  "source_packet_id": "{comparison['packet_id']}",
  "verdicts": {{
    "field_name": {{
      "verdict": "left_correct",
      "final_status": "found",
      "final_value": null,
      "final_units": null,
      "final_page_anchor": null,
      "final_chunk_id": null,
      "source_quote": null,
      "confidence": 0.0,
      "reason_code": "source_supported"
    }}
  }}
}}
```

Allowed `verdict` values:

- `left_correct`
- `right_correct`
- `both_correct_equivalent`
- `both_wrong`
- `insufficient_evidence`
- `needs_supervisor`

Allowed `final_status` values:

- `found`
- `not_found`
- `uncertain`

Rules:

- Include exactly one verdict entry for each requested field.
- The `verdicts` object keys must be exactly the requested field names.
- Do not use verdict labels such as `both_wrong`, `insufficient_evidence`,
  `left_correct`, or `right_correct` as field names.
- Every verdict entry must include all nine keys shown in the skeleton:
  `verdict`, `final_status`, `final_value`, `final_units`,
  `final_page_anchor`, `final_chunk_id`, `source_quote`, `confidence`, and
  `reason_code`.
- Use `final_units`, `final_page_anchor`, and `final_chunk_id`; do not shorten
  these keys to `units`, `page_anchor`, or `chunk_id`.
- Keep every `source_quote` to 25 words or fewer.
- `final_chunk_id` must be one of the supplied chunk IDs or null.
- If the source chunks do not prove a value, use `insufficient_evidence` or
  `needs_supervisor`; do not guess.
- Prefer `both_correct_equivalent` when candidate values differ only by
  formatting and both are source-supported.
- Use compact `reason_code` values, not prose explanations.

## Fields Requiring Verification

```json
{comparison_block}
```

## Required Verdict Skeleton

Fill this skeleton. Preserve the field keys exactly:

```json
{verdict_skeleton}
```

## Candidate JSON Subsets

{chr(10).join(candidate_blocks)}

## Source Chunks

{chr(10).join(source_blocks)}
"""


def redacted_candidate(candidate: dict[str, Any], field_names: list[str]) -> dict[str, Any]:
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
