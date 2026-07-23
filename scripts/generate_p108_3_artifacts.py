"""P108.3: Generate validation and audit contracts for the full 18-document TSA23 corpus."""

import json
import hashlib
import os
import glob
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCHMARKS = os.path.join(BASE, "benchmarks")
TSR_DIR = os.path.join(BENCHMARKS, "document_library", "tsa23_tsr")
RUNTIME_EXTRACTS = os.path.join(BASE, "runtime", "extracts", "tsa23")
RUNTIME_AGENT_JOBS = os.path.join(BASE, "runtime", "agent_jobs")

# Ensure output dirs exist
os.makedirs(RUNTIME_AGENT_JOBS, exist_ok=True)

now_utc = datetime.now(timezone.utc).isoformat()

# ── Step 1: Read all 18 chunk manifests ──
manifest_paths = sorted(glob.glob(os.path.join(TSR_DIR, "tsa23_*", "chunk_manifest.json")))
print(f"[scan] Found {len(manifest_paths)} document manifests")

all_chunks = []  # (doc_id, page_start, page_end, chunk_manifest_entry)
document_ids = []

for mp in manifest_paths:
    manifest = json.load(open(mp))
    doc_id = manifest["document_id"]
    if doc_id not in document_ids:
        document_ids.append(doc_id)
    for chunk in manifest.get("chunks", []):
        all_chunks.append({
            "document_id": doc_id,
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "chunk_id_internal": chunk.get("chunk_id", ""),
            "raw_text_path": chunk.get("raw_text_path", ""),
        })

print(f"[scan] {len(document_ids)} documents, {len(all_chunks)} total chunks")

# ── Helper: read raw text and compute hash ──
def read_chunk_text(raw_text_path):
    """Read raw text file; return (char_count, sha256_hex)."""
    full_path = os.path.join(BASE, raw_text_path)
    if not os.path.exists(full_path):
        return 0, ""
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            text = f.read()
        char_count = len(text)
        sha256_hex = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else ""
        return char_count, sha256_hex
    except Exception as e:
        print(f"[warn] Could not read {full_path}: {e}")
        return 0, ""

# ── Artifact 1: Chunk ID Enum ──
chunk_ids_list = []
for c in all_chunks:
    chunk_id = f"{c['document_id']}::pages_{c['page_start']:03d}_{c['page_end']:03d}"
    text_char_count, text_sha256 = read_chunk_text(c["raw_text_path"])
    chunk_ids_list.append({
        "chunk_id": chunk_id,
        "document_id": c["document_id"],
        "page_start": c["page_start"],
        "page_end": c["page_end"],
        "text_char_count": text_char_count,
        "text_sha256": text_sha256,
    })

artifact1 = {
    "corpus_id": "tsa23_tsr",
    "document_count": len(document_ids),
    "chunk_id_count": len(chunk_ids_list),
    "enum_id": "p108_3_chunk_id_enum",
    "phase": "P108.3",
    "schema_version": 1,
    "chunk_ids": chunk_ids_list,
    "public_safety": {
        "personal_paths_tracked": False,
        "provider_urls_or_headers_tracked": False,
        "raw_source_text_tracked": False,
        "raw_worker_output_tracked": False,
        "source_quotes_tracked": False,
    },
    "generated_utc": now_utc,
}

artifact1_path = os.path.join(BENCHMARKS, "document_library", "p108_3_chunk_id_enum.json")
with open(artifact1_path, "w", encoding="utf-8") as f:
    json.dump(artifact1, f, indent=2, ensure_ascii=False)
print(f"[artifact1] Written {artifact1_path} ({len(chunk_ids_list)} chunks)")

# ── Artifact 2: Validation Input Manifest ──
candidate_inputs = []
for c in all_chunks:
    chunk_id = f"{c['document_id']}::pages_{c['page_start']:03d}_{c['page_end']:03d}"
    for record_pass in ["structure", "content_metadata"]:
        ticket_id = f"{chunk_id}_{record_pass}"
        candidate_path = (
            f"runtime/document_library/tsa23_tsr/p108_3_extraction_candidate_packet/"
            f"{chunk_id.replace('::', '_')}{record_pass}.{record_pass}.candidate.jsonl"
        )
        candidate_inputs.append({
            "candidate_input_path": candidate_path,
            "expected_initial_state": "empty_runtime_jsonl_placeholder",
            "record_pass": record_pass,
            "ticket_id": ticket_id,
        })

artifact2 = {
    "corpus_id": "tsa23_tsr",
    "document_count": len(document_ids),
    "chunk_count": len(all_chunks),
    "candidate_input_count": len(candidate_inputs),
    "candidate_inputs": candidate_inputs,
    "public_safety": {
        "personal_paths_tracked": False,
        "provider_urls_or_headers_tracked": False,
        "raw_source_text_tracked": False,
        "raw_worker_output_tracked": False,
        "source_quotes_tracked": False,
    },
    "generated_utc": now_utc,
}

artifact2_path = os.path.join(BENCHMARKS, "document_library", "p108_3_validation_input_manifest.json")
with open(artifact2_path, "w", encoding="utf-8") as f:
    json.dump(artifact2, f, indent=2, ensure_ascii=False)
print(f"[artifact2] Written {artifact2_path} ({len(candidate_inputs)} candidates)")

# ── Artifact 3: Audit Sample Manifest ──
samples = []
for idx, c in enumerate(all_chunks, 1):
    chunk_id = f"{c['document_id']}::pages_{c['page_start']:03d}_{c['page_end']:03d}"
    for record_pass in ["structure", "content_metadata"]:
        candidate_path = (
            f"runtime/document_library/tsa23_tsr/p108_3_extraction_candidate_packet/"
            f"{chunk_id.replace('::', '_')}_{record_pass}.candidate.jsonl"
        )
        samples.append({
            "chunk_id": chunk_id,
            "document_id": c["document_id"],
            "record_pass": record_pass,
            "candidate_path": candidate_path,
        })

audit_sample_manifest = {
    "audit_manifest_id": "p108_3_audit_sample_manifest",
    "phase": "P108.3",
    "corpus_id": "tsa23_tsr",
    "document_count": len(document_ids),
    "chunk_count": len(all_chunks),
    "sample_count": len(samples),
    "sample_classes": {
        "structure_per_chunk": 1,
        "content_metadata_per_chunk": 1,
    },
    "samples": samples,
    "public_safety": {
        "personal_paths_tracked": False,
        "provider_urls_or_headers_tracked": False,
        "raw_source_text_tracked": False,
        "raw_worker_output_tracked": False,
        "source_quotes_tracked": False,
    },
    "generated_utc": now_utc,
}

artifact3_path = os.path.join(BENCHMARKS, "document_library", "p108_3_audit_sample_manifest.json")
with open(artifact3_path, "w", encoding="utf-8") as f:
    json.dump(audit_sample_manifest, f, indent=2, ensure_ascii=False)
print(f"[artifact3] Written {artifact3_path} ({len(samples)} samples)")

# ── Result artifact ──
result = {
    "status": "accepted",
    "phase": "P108.3",
    "task": "validation_and_audit_contracts",
    "artifact_count": 3,
    "artifact_paths": [
        artifact1_path,
        artifact2_path,
        artifact3_path,
    ],
    "document_count": len(document_ids),
    "chunk_id_count": len(all_chunks),
    "validation_candidate_count": len(candidate_inputs),
    "audit_sample_count": len(samples),
    "generated_utc": now_utc,
}

result_path = os.path.join(RUNTIME_AGENT_JOBS, "p108_3_validation_result.json")
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n[RESULT] Status: accepted")
print(f"  Documents: {len(document_ids)}")
print(f"  Chunks: {len(all_chunks)}")
print(f"  Validation candidates: {len(candidate_inputs)}")
print(f"  Audit samples: {len(samples)}")
print(f"  Artifacts: 3 written")
TSR_DIR = os.path.join(BENCHMARKS, "document_library", "tsa23_tsr")
RUNTIME_EXTRACTS = os.path.join(BASE, "runtime", "extracts", "tsa23")
RUNTIME_AGENT_JOBS = os.path.join(BASE, "runtime", "agent_jobs")

# Ensure output dirs exist
os.makedirs(RUNTIME_AGENT_JOBS, exist_ok=True)

now_utc = datetime.now(timezone.utc).isoformat()

# ── Step 1: Read all 18 chunk manifests ──
manifest_glob = os.path.join(TSR_DIR, "tsa23_*", "chunk_manifest.json")
manifest_paths = sorted(glob.glob(manifest_glob))
print(f"[chunk_enum] Loading {len(manifest_paths)} chunk manifests...")

all_chunks = []  # List of (doc_id, chunk_id, page_start, page_end, char_count, sha256)
document_ids = []

for mp in manifest_paths:
    with open(mp, "r") as f:
        manifest = json.load(f)
    doc_id = manifest["document_id"]
    document_ids.append(doc_id)
    for chunk in manifest.get("chunks", []):
        page_start = chunk["page_start"]
        page_end = chunk["page_end"]
        # Construct chunk_id: document_id::pages_<start>_<end> (zero-padded 3 digits)
        chunk_id = f"{doc_id}::pages_{page_start:03d}_{page_end:03d}"
        
        # Read raw text file
        raw_text_path = os.path.join(
            RUNTIME_EXTRACTS, doc_id, chunk["raw_text_path"].split("/")[-1]
        )
        # raw_text_path from manifest is like "runtime/extracts/tsa23/<doc_id>/chunk_XX.txt"
        if not os.path.isabs(raw_text_path.replace("\\", "/")):
            raw_text_path = os.path.join(BASE, chunk["raw_text_path"])
        
        char_count = 0
        text_sha256 = ""
        if os.path.exists(raw_text_path) and os.path.getsize(raw_text_path) > 0:
            with open(raw_text_path, "r", encoding="utf-8") as tf:
                content = tf.read()
            char_count = len(content)
            text_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
            print(f"  [{doc_id}] {chunk_id}: {char_count} chars, sha256={text_sha256[:12]}...")
        else:
            print(f"  [{doc_id}] {chunk_id}: FILE MISSING/EMPTY ({raw_text_path})")
        
        all_chunks.append({
            "chunk_id": chunk_id,
            "document_id": doc_id,
            "page_start": page_start,
            "page_end": page_end,
            "text_char_count": char_count,
            "text_sha256": text_sha256,
        })

print(f"[chunk_enum] Total chunks: {len(all_chunks)} across {len(document_ids)} documents")

# ── Artifact 1: Chunk ID Enum ──
chunk_id_enum = {
    "corpus_id": "tsa23_tsr",
    "document_count": len(document_ids),
    "chunk_id_count": len(all_chunks),
    "enum_id": "p108_3_chunk_id_enum",
    "phase": "P108.3",
    "schema_version": 1,
    "chunk_ids": all_chunks,
    "public_safety": {
        "provider_urls_or_headers_tracked": False,
        "raw_text_tracked": False,
        "raw_worker_outputs_tracked": False,
    },
    "generated_utc": now_utc,
}

artifact1_path = os.path.join(BENCHMARKS, "document_library", "p108_3_chunk_id_enum.json")
with open(artifact1_path, "w") as f:
    json.dump(chunk_id_enum, f, indent=2)
print(f"[artifact1] Written {artifact1_path} ({len(all_chunks)} chunk_ids)")

# ── Artifact 2: Validation Input Manifest ──
candidate_inputs = []
for chunk in all_chunks:
    cid = chunk["chunk_id"]
    for record_pass in ["structure", "content_metadata"]:
        ticket_id = f"{cid}_{record_pass}"
        candidate_path = (
            f"runtime/document_library/tsa23_tsr/p108_3_extraction_candidate_packet/"
            f"{cid}_{record_pass}.candidate.jsonl"
        )
        candidate_inputs.append({
            "candidate_input_path": candidate_path,
            "expected_initial_state": "empty_runtime_jsonl_placeholder",
            "record_pass": record_pass,
            "ticket_id": ticket_id,
        })

validation_input_manifest = {
    "corpus_id": "tsa23_tsr",
    "phase": "P108.3",
    "manifest_id": "p108_3_validation_input_manifest",
    "schema_version": 1,
    "document_count": len(document_ids),
    "chunk_count": len(all_chunks),
    "candidate_input_count": len(candidate_inputs),
    "candidate_inputs": candidate_inputs,
    "public_safety": {
        "provider_urls_or_headers_tracked": False,
        "raw_text_tracked": False,
        "raw_worker_outputs_tracked": False,
    },
    "generated_utc": now_utc,
}

artifact2_path = os.path.join(BENCHMARKS, "document_library", "p108_3_validation_input_manifest.json")
with open(artifact2_path, "w") as f:
    json.dump(validation_input_manifest, f, indent=2)
print(f"[artifact2] Written {artifact2_path} ({len(candidate_inputs)} candidates)")

# ── Artifact 3: Audit Sample Manifest ──
samples = []
for chunk in all_chunks:
    cid = chunk["chunk_id"]
    doc_id = chunk["document_id"]
    for record_pass in ["structure", "content_metadata"]:
        candidate_path = (
            f"runtime/document_library/tsa23_tsr/p108_3_extraction_candidate_packet/"
            f"{cid}_{record_pass}.candidate.jsonl"
        )
        samples.append({
            "chunk_id": cid,
            "document_id": doc_id,
            "record_pass": record_pass,
            "candidate_path": candidate_path,
        })

audit_sample_manifest = {
    "audit_manifest_id": "p108_3_audit_sample_manifest",
    "phase": "P108.3",
    "corpus_id": "tsa23_tsr",
    "document_count": len(document_ids),
    "chunk_count": len(all_chunks),
    "sample_count": len(samples),
    "sample_classes": {
        "structure_per_chunk": 1,
        "content_metadata_per_chunk": 1,
    },
    "samples": samples,
    "public_safety": {
        "personal_paths_tracked": False,
        "provider_urls_or_headers_tracked": False,
        "raw_source_text_tracked": False,
        "raw_worker_output_tracked": False,
        "source_quotes_tracked": False,
    },
    "schema_version": 1,
    "generated_utc": now_utc,
}

artifact3_path = os.path.join(BENCHMARKS, "document_library", "p108_3_audit_sample_manifest.json")
with open(artifact3_path, "w") as f:
    json.dump(audit_sample_manifest, f, indent=2)
print(f"[artifact3] Written {artifact3_path} ({len(samples)} samples)")

# ── Result artifact ──
result = {
    "status": "accepted",
    "phase": "P108.3",
    "task": "validation_and_audit_contracts",
    "artifact_count": 3,
    "artifact_paths": [
        artifact1_path,
        artifact2_path,
        artifact3_path,
    ],
    "document_count": len(document_ids),
    "chunk_id_count": len(all_chunks),
    "validation_candidate_count": len(candidate_inputs),
    "audit_sample_count": len(samples),
    "generated_utc": now_utc,
}

result_path = os.path.join(RUNTIME_AGENT_JOBS, "p108_3_validation_result.json")
with open(result_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"\n[RESULT] Status: accepted")
print(f"  Documents: {len(document_ids)}")
print(f"  Chunks: {len(all_chunks)}")
print(f"  Validation candidates: {len(candidate_inputs)}")
print(f"  Audit samples: {len(samples)}")
print(f"  Artifacts: 3 written")
print(f"\nPacket:")
print(json.dumps({
    "status": "accepted",
    "artifact_count": 3,
    "chunk_id_count": len(all_chunks),
    "validation_candidate_count": len(candidate_inputs),
    "document_count": len(document_ids),
}, indent=2))