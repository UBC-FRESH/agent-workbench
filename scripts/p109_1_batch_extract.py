"""P109.1: Batch JSONL extraction for 2012 cycle via vLLM.

Calls the local vLLM endpoint (same as P90) to extract structured JSONL
candidate records from the 2012 TSA23 cycle documents.

Usage:
    python scripts/p109_1_batch_extract.py
    python scripts/p109_1_batch_extract.py --doc tsa23_2012_23tsdp12
    python scripts/p109_1_batch_extract.py --dry-run
"""
import argparse
import json
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent.parent
ENV_FILE = Path.home() / ".agent-workbench-env.txt"
DEFAULT_MODEL = "qwen3.6-27b-nvfp4"

# Read provider settings
env = {}
for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("NOTE"):
        k, v = line.split("=", 1)
        env[k] = v

BASE_URL = env.get("AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL", "").rstrip("/")
HEADERS_FILE = env.get("AGENT_WORKBENCH_PROVIDER_HEADERS_FILE", "")
HEADERS = json.loads(Path(HEADERS_FILE).read_text(encoding="utf-8-sig")) if HEADERS_FILE else {}

# Docs
DOCS = [
    "tsa23_2012_23tsdp12",
    "tsa23_2012_23ts13ra",
    "tsa23_2012_23ts13pdp",
]

CORPUS = "bc_tsr_tsa23_public_1995_present"
WORKER_MODEL = "qwen3-27b-vllm"
REVIEW_STATUS = "raw_worker_candidate"

# ---------------------------------------------------------------------------
# Extraction prompt
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = """You are a document metadata extraction worker. Read the raw document text below and produce JSONL records.

Each record must have these fields:
record_id, corpus_id, document_id, source_sha256, chunk_id, page_anchor, document_component, section_path, object_type, title, summary, source_quote, confidence, worker_model, review_status

Valid object_types: heading, section_summary, table, figure, map, acronym, definition, cross_reference, claim, assumption, constraint, policy_reference, model_input, numeric_value, scenario, sensitivity_test, decision_rationale, component_boundary, appendix, other

For each numbered section in the text, produce:
1. A "heading" record for the section number and title
2. A "section_summary" record for the content
3. Additional records for notable items (tables, claims, assumptions, numeric values)

Output ONLY valid JSONL (one JSON object per line, no markdown fence, no preamble).

Document ID: {doc_id}
Source SHA256: {source_sha256}
Chunk ID: {chunk_id}
Corpus ID: {corpus}
Worker model: {worker_model}
Review status: {review_status}

RAW TEXT:
{text}
"""

# ---------------------------------------------------------------------------
# Call vLLM (standard OpenAI /chat/completions)
# ---------------------------------------------------------------------------
def call_vllm(prompt: str, model: str, timeout: int = 300) -> str:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 4096,
    }).encode("utf-8")

    req = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "CF-Access-Client-Id": HEADERS.get("CF-Access-Client-Id", ""),
            "CF-Access-Client-Secret": HEADERS.get("CF-Access-Client-Secret", ""),
            "User-Agent": HEADERS.get("User-Agent", "agent-workbench-worker/1.0"),
        },
    )

    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    # Extract text from completions API format
    text = body.get("choices", [{}])[0].get("message", {}).get("content", "")

    elapsed = time.monotonic() - start
    print(f"  Model response in {elapsed:.1f}s, {len(text)} chars")
    return text.strip()


# ---------------------------------------------------------------------------
# Parse JSONL from model output
# ---------------------------------------------------------------------------
def parse_jsonl(raw: str) -> list[dict]:
    records = []
    # Strip markdown fences if present
    for line in raw.split("\n"):
        line = line.strip()
        # Remove markdown fence markers
        if line.startswith("```"):
            continue
        if not line:
            continue
        try:
            obj = json.loads(line)
            records.append(obj)
        except json.JSONDecodeError:
            continue
    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="P109.1 batch extraction")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--doc", default=None, help="Process single document ID")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    doc_list = [args.doc] if args.doc else DOCS

    print("=" * 60)
    print(f"P109.1: Batch JSONL extraction ({len(doc_list)} docs)")
    print(f"Endpoint: {BASE_URL}")
    print(f"Model: {args.model}")
    print("=" * 60)

    total_records = 0
    total_chunks = 0
    docs_done = []

    for doc_id in doc_list:
        manifest_path = BASE / "benchmarks" / "document_library" / "tsa23_tsr" / doc_id / "chunk_manifest.json"

        if not manifest_path.exists():
            print(f"SKIP {doc_id}: no manifest")
            continue

        manifest = json.loads(manifest_path.read_text())
        source_sha = manifest.get("source_sha256", "pending")
        chunks = manifest.get("chunks", [])
        total_pages = manifest.get("total_pages", 0)

        print(f"\n{'='*50}")
        print(f"{doc_id}: {len(chunks)} chunks, {total_pages} pages")
        print(f"{'='*50}")

        output_path = BASE / "benchmarks" / "document_library" / "tsa23_tsr" / doc_id / f"{doc_id}_candidates.jsonl"
        all_records = []

        for i, chunk in enumerate(chunks):
            chunk_id = chunk["chunk_id"]
            raw_path = BASE / chunk["raw_text_path"]

            if not raw_path.exists():
                print(f"  SKIP {chunk_id}: file missing")
                continue

            text = raw_path.read_text(encoding="utf-8", errors="replace")
            total_chunks += 1

            if args.dry_run:
                print(f"  [DRY RUN] {chunk_id}: {len(text)} chars")
                continue

            print(f"  [{i+1}/{len(chunks)}] {chunk_id}: pages {chunk['page_start']}-{chunk['page_end']}, {len(text)} chars")

            prompt = EXTRACTION_PROMPT.format(
                doc_id=doc_id,
                source_sha256=source_sha,
                chunk_id=chunk_id,
                corpus=CORPUS,
                worker_model=WORKER_MODEL,
                review_status=REVIEW_STATUS,
                text=text,
            )

            try:
                raw_output = call_vllm(prompt, args.model)
                records = parse_jsonl(raw_output)
                print(f"    -> {len(records)} records")
                all_records.extend(records)
            except Exception as e:
                print(f"    ERROR: {e}")
                continue

        # Write output
        if all_records:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            lines = [json.dumps(r) for r in all_records]
            output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            total_records += len(all_records)
            print(f"\n  Wrote {len(all_records)} records to {output_path.name}")

    print(f"\n{'='*60}")
    print(f"SUMMARY: {total_chunks} chunks, {total_records} records")
    print(f"{'='*60}")

    # Result artifact
    result = {
        "phase": "P109.1",
        "description": "Batch JSONL extraction via vLLM (2012 cycle)",
        "chunks_processed": total_chunks,
        "records_produced": total_records,
        "documents": doc_list,
        "status": "complete" if not args.dry_run else "dry_run",
    }
    result_path = BASE / "runtime" / "agent_jobs" / "p109_1_result.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    return 0 if total_records > 0 else 1


if __name__ == "__main__":
    sys.exit(main())