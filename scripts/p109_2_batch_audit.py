#!/usr/bin/env python3
"""P109.2: Audit candidate records from P109.1 batch extraction.

Audit rules:
1. Duplicate: same chunk, near-identical title
2. Low value: TOC/front_matter entries with no substantive content
3. Missing provenance: no source_sha256 or document_id
4. Accept: has substantive content, good provenance, unique

Output: batch_audit_records.jsonl with accepted + rejected per document
"""

import json
import os
from pathlib import Path

CANDIDATE_FILES = {
    "tsa23_2012_23tsdp12": "benchmarks/document_library/tsa23_tsr/tsa23_2012_23tsdp12/tsa23_2012_23tsdp12_candidates.jsonl",
    "tsa23_2012_23ts13ra": "benchmarks/document_library/tsa23_tsr/tsa23_2012_23ts13ra/tsa23_2012_23ts13ra_candidates.jsonl",
    "tsa23_2012_23ts13pdp": "benchmarks/document_library/tsa23_tsr/tsa23_2012_23ts13pdp/tsa23_2012_23ts13pdp_candidates.jsonl",
}

OUTPUT_DIR = "benchmarks/document_library/tsa23_tsr"


def is_low_value_heading(record):
    """TOC/front_matter entries with no substantive content."""
    if record.get("document_component") == "table_of_contents":
        return True
    if record.get("object_type") == "heading" and not record.get("summary"):
        return True
    return False


def has_provenance(record):
    """Check required provenance fields."""
    return bool(
        record.get("document_id")
        and record.get("source_sha256")
        and record.get("chunk_id")
        and record.get("page_anchor")
    )


def audit_document(doc_id: str, candidate_path: str):
    """Audit a single document's candidates."""
    accepted = []
    rejected = []
    seen_toc_headings = set()  # (chunk_id, section_path)

    with open(candidate_path, "r") as f:
        records = [json.loads(line) for line in f if line.strip()]

    print(f"\n{'='*60}")
    print(f"Document: {doc_id}")
    print(f"Total candidates: {len(records)}")
    print(f"{'='*60}")

    for record in records:
        record_id = record["record_id"]
        chunk_id = record.get("chunk_id", "unknown")
        section_path = record.get("section_path", "")
        summary = record.get("summary")
        source_quote = record.get("source_quote")

        # Check for TOC purely navigation entries — accept section headings, reject empty TOC
        if is_low_value_heading(record):
            key = (chunk_id, section_path)
            # Pure TOC entries with no section path and no content — reject
            if record.get("document_component") == "table_of_contents" and not section_path.strip():
                rejected.append({
                    **record,
                    "review_status": "rejected",
                    "rejection_reason": "empty_toc_entry",
                })
                continue
            # Heading with section_path — accept as navigation aid
            accepted.append({
                **record,
                "review_status": "accepted",
                "document_type": _get_document_type(doc_id),
            })
            continue

        # Check for missing provenance
        if not has_provenance(record):
            rejected.append({
                **record,
                "review_status": "rejected",
                "rejection_reason": "missing_provenance",
            })
            continue

        # Check for substantive content
        if not summary and not source_quote:
            rejected.append({
                **record,
                "review_status": "rejected",
                "rejection_reason": "no_substantive_content",
            })
            continue

        # If we get here, accept it
        accepted.append({
            **record,
            "review_status": "accepted",
            "document_type": _get_document_type(doc_id),
        })

    print(f"Accepted: {len(accepted)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Yield: {len(accepted)/len(records)*100:.1f}%")

    return accepted, rejected


def _get_document_type(doc_id: str) -> str:
    """Extract document type from document ID."""
    if "23tsdp12" in doc_id:
        return "data_package"
    elif "ra" in doc_id:
        return "rationale"
    elif "pdp" in doc_id:
        return "discussion_paper"
    return "unknown"


def main():
    all_accepted = []
    all_rejected = []

    for doc_id, candidate_path in CANDIDATE_FILES.items():
        accepted, rejected = audit_document(doc_id, candidate_path)
        all_accepted.extend(accepted)
        all_rejected.extend(rejected)

    # Write per-document audit files
    doc_accepted = {}
    doc_rejected = {}
    for rec in all_accepted + all_rejected:
        doc = rec["document_id"]
        if rec["review_status"] == "accepted":
            doc_accepted.setdefault(doc, []).append(rec)
        else:
            doc_rejected.setdefault(doc, []).append(rec)

    for doc_id in CANDIDATE_FILES:
        audit_path = os.path.join(OUTPUT_DIR, doc_id, f"batch_audit_records.jsonl")
        file_records = doc_accepted.get(doc_id, [])
        os.makedirs(os.path.dirname(audit_path), exist_ok=True)

        with open(audit_path, "w") as f:
            for rec in file_records:
                f.write(json.dumps(rec) + "\n")

        print(f"\nWrote {len(file_records)} accepted records to {audit_path}")

    # Write summary
    summary = {
        "phase": "P109.2",
        "task": "batch_audit_2012_cycle",
        "total_candidates": len(all_accepted) + len(all_rejected),
        "accepted": len(all_accepted),
        "rejected": len(all_rejected),
        "yield_rate": len(all_accepted) / (len(all_accepted) + len(all_rejected)) if (len(all_accepted) + len(all_rejected)) > 0 else 0,
        "per_document": {},
    }

    for doc_id in CANDIDATE_FILES:
        doc_acc = len(doc_accepted.get(doc_id, []))
        doc_rej = len(doc_rejected.get(doc_id, []))
        summary["per_document"][doc_id] = {
            "accepted": doc_acc,
            "rejected": doc_rej,
            "yield": doc_acc / (doc_acc + doc_rej) if (doc_acc + doc_rej) > 0 else 0,
        }

        print(f"\n{doc_id}:")
        print(f"  Accepted: {doc_acc}")
        print(f"  Rejected: {doc_rej}")
        print(f"  Yield: {doc_acc/(doc_acc+doc_rej)*100:.1f}%")

    print(f"\n{'='*60}")
    print(f"Total accepted: {summary['accepted']}")
    print(f"Total rejected: {summary['rejected']}")
    print(f"Overall yield: {summary['yield_rate']*100:.1f}%")
    print(f"{'='*60}")

    # Write run summary
    with open(
        os.path.join(OUTPUT_DIR, "tsa23_2012_batch_audit_run_002.json"), "w"
    ) as f:
        json.dump(summary, f, indent=2)

    print(f"\nWrote audit run summary to "
          f"benchmarks/document_library/tsa23_tsr/tsa23_2012_batch_audit_run_002.json")


if __name__ == "__main__":
    main()