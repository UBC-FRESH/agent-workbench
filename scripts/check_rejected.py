#!/usr/bin/env python3
"""Check what the 28 rejected records from the first audit were."""
import json

# Read the original candidates
path = 'benchmarks/document_library/tsa23_tsr/tsa23_2012_23tsdp12/tsa23_2012_23tsdp12_candidates.jsonl'
records = [json.loads(l) for l in open(path) if l.strip()]

# Find records that would have been rejected (TOC entries, no summary, no section_path)
for r in records:
    is_toc = r.get("document_component") == "table_of_contents"
    no_summary = not r.get("summary")
    no_section = not r.get("section_path", "").strip()
    
    if is_toc or (no_summary and no_section):
        print(f"{r['record_id']} | comp={r['document_component']} | obj={r['object_type']} | section='{r['section_path']}' | quote='{r.get('source_quote','')[:60]}...'")