"""Run one P106 Luna extraction request with strict structured output.

This launcher is intentionally inert until explicitly invoked. It reads the
operator's Codex API key without printing it and writes raw response material
only below the caller-selected ignored runtime directory.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path
from typing import Any


def load_api_key() -> str:
    auth = json.loads((Path.home() / ".codex" / "auth.json").read_text(encoding="utf-8"))
    key = auth.get("OPENAI_API_KEY") or auth.get("tokens", {}).get("OPENAI_API_KEY")
    if not isinstance(key, str) or not key:
        raise RuntimeError("Codex auth.json does not contain an API key")
    return key


def schema(contract: dict[str, Any]) -> dict[str, Any]:
    fields = contract["required_fields"]
    properties: dict[str, Any] = {}
    for field in fields:
        if field in {"section_path"}:
            properties[field] = {"type": "array", "items": {"type": "string"}}
        elif field == "confidence":
            properties[field] = {"type": "number", "minimum": 0, "maximum": 1}
        else:
            properties[field] = {"type": "string"}
    properties["record_pass"] = {"type": "string", "enum": ["structure", "content_metadata"]}
    properties["object_type"] = {"type": "string", "enum": contract["allowed_object_types"]}
    return {
        "type": "object",
        "properties": {
            "records": {
                "type": "array",
                "minItems": contract["records"]["minimum"],
                "maxItems": contract["records"]["maximum"],
                "items": {
                    "type": "object",
                    "properties": properties,
                    "required": [*fields, "record_pass"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["records"],
        "additionalProperties": False,
    }


def build_prompt(source: str, contract: dict[str, Any]) -> str:
    return (
        "Extract source-anchored P106 candidate records from the supplied text. "
        "Return only the requested structured object. Include at least three "
        "structure and three content_metadata records. Every source_quote must "
        "be an exact contiguous quote. Use only the supplied source.\n\n"
        f"Use corpus_id={contract['corpus_id']}, document_id={contract['document_id']}, "
        f"source_sha256={contract['source_sha256']}, chunk_id={contract['chunk_id']}, "
        "review_status=raw_worker_candidate, worker_model=GPT-5.6 Luna.\n\n"
        "SOURCE TEXT:\n" + source
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--p89-contract", type=Path, required=True)
    parser.add_argument("--p105-contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    p89 = json.loads(args.p89_contract.read_text(encoding="utf-8"))
    p105 = json.loads(args.p105_contract.read_text(encoding="utf-8"))
    contract = {
        **p89,
        "corpus_id": p105["source"]["corpus_id"],
        "document_id": p105["source"]["document_id"],
        "source_sha256": p105["source"]["source_sha256"],
        "chunk_id": p105["source"]["chunk_id"],
        "records": {
            "minimum": p105["records"]["minimum"],
            "maximum": p105["records"]["maximum"],
        },
    }
    source = args.source.read_text(encoding="utf-8")
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": "gpt-5.6-luna",
        "input": build_prompt(source, contract),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "p106_candidate_records",
                "strict": True,
                "schema": schema(contract),
            }
        },
    }
    started = time.time()
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {load_api_key()}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=240) as response:
        raw = response.read().decode("utf-8")
        status = response.status
    body = json.loads(raw)
    (output_dir / "raw_response.json").write_text(raw, encoding="utf-8")
    structured = "".join(
        content.get("text", "")
        for item in body.get("output", [])
        if isinstance(item, dict)
        for content in item.get("content", [])
        if isinstance(content, dict) and isinstance(content.get("text"), str)
    )
    structured_payload = json.loads(structured)
    records = structured_payload["records"]
    (output_dir / "structured_output.json").write_text(structured, encoding="utf-8")
    (output_dir / "output.jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    (output_dir / "run_meta.json").write_text(
        json.dumps(
            {
                "lane": "direct",
                "model": "GPT-5.6 Luna",
                "http_status": status,
                "coordinator_span_start": started,
                "coordinator_span_end": time.time(),
                "usage": body.get("usage", {}),
                "structured_output_schema_evidence": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "usage": body.get("usage", {})}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
