# Modelling-Agent Retrieval Example

This example shows how a downstream modelling agent discovers and cites
source-backed facts from the P94 promoted index using the `agent-workbench
retrieve` CLI.

The workflow demonstrates two use cases:

1. **Page/Chunk Anchor Lookup** — "find all source-backed facts about pages X-Y
   of document D"
2. **Full-Document Provenance Trace** — "show every record from document D,
   grouped by model lane and audit status"

## Prerequisites

- Python 3.10+ with the agent-workbench editable install
- Access to the TSL/TSR corpus in `benchmarks/document_library/tsa23_tsr`

## Use Case 1: Page/Chunk Anchor Lookup

**Agent query:** "What does document 23tsdp12 say about pages 1–8?"

### Step 1: Discover indexed documents

```bash
agent-workbench retrieve list-docs
```

Output (16 total records across 3 docs):

```
Indexed documents (16 total records):
  tsa23_2012_23ts13pdp: 3 records
  tsa23_2012_23ts13ra: 7 records
  tsa23_2012_23tsdp12: 6 records [dedup=6]
```

The `[dedup=6]` flag tells the agent that all 6 records from `tsa23_2012_23tsdp12`
are pending dedup review. The agent may choose to cite them with a lower
confidence weight or note this in its output.

### Step 2: Query pages 1–8 for document 23tsdp12

```bash
agent-workbench retrieve page-range \
  --document-id tsa23_2012_23tsdp12 \
  --page-start 1 \
  --page-end 8
```

Returns JSON output with:

- `source_hash` — SHA-256 of the source chunk for verifiable citation
- `document_id` — canonical document identifier
- `page_anchor` — primary page reference (e.g., page 4)
- `chunk_id` — deterministic chunk key (`tsa23_2012_23tsdp12::pages_001_008`)
- `model_lane` — which model produced this record (`qwen3.6:35b-a3b-bf16`)
- `audit_status` — review outcome (`accepted_pending_dedup`, `accepted`)
- `text_file` — path to the extracted text on disk for direct content reading
- `is_dedup` — boolean flag indicating dedup-pending status

### Step 3: Agent cites the retrieved facts

With the query result, the modelling agent constructs a citation like:

> According to the TSA23 document 23tsdp12 (page 4), [fact content from
> text_file]. Source hash: `8ed28555...`. This record is in audit status
> `accepted_pending_dedup` and was produced by model lane `qwen3.6:35b-a3b-bf16`.

The agent uses the `is_dedup` flag to add a confidence qualifier if dedup status
matters for the downstream decision.

## Use Case 2: Full-Document Provenance Trace

**Agent query:** "Show me every record from document 23ts13ra, grouped by audit
status."

### Step 1: Run full-document trace with grouping

```bash
agent-workbench retrieve trace \
  --document-id tsa23_2012_23ts13ra \
  --group-by audit_status
```

Returns JSON with three top-level keys:

- `query` — echo of the input parameters
- `grouped_by_audit_status` — records bucketed by their `audit_status` field
- `flat_array` — all records in page-order regardless of status
- `metadata` — total record count, group-by strategy, timestamp

For document 23ts13ra (7 accepted records), the output shows:

```json
{
  "query": {
    "document_id": "tsa23_2012_23ts13ra",
    "group_by": "audit_status"
  },
  "grouped_by_audit_status": {
    "accepted": [ /* 7 records */ ]
  },
  "flat_array": [ /* all 7 records in page order */ ],
  "metadata": {
    "total_record_count": 7,
    "group_by": "audit_status",
    "returned_at": "2026-07-12T00:35:35+00:00"
  }
}
```

### Step 2: Agent verifies provenance completeness

The agent uses the trace output to:

1. Confirm **all** records from the document are accounted for (`metadata.total_record_count`)
2. Check that **every record** has the expected `model_lane` and `audit_status` values
3. Use the `flat_array` for ordered reading if needed by a summarization pipeline
4. Cross-reference `source_hash` values against any prior citation to detect duplicates

### Step 3: Group by model lane instead

```bash
agent-workbench retrieve trace \
  --document-id tsa23_2012_23tsdp12 \
  --group-by model_lane
```

This variant groups records by the model that produced them, useful when comparing
multiple model lanes on the same document. For `tsa23_2012_23tsdp12`, all 6
records share lane `qwen3.6:35b-a3b-bf16` and are marked `is_dedup=true`.

## Synthetic Run: End-to-End Flow

Here is a minimal self-contained run demonstrating the full
query → retrieve → cite flow:

```bash
# 1. List available documents
echo "=== Indexed Documents ==="
agent-workbench retrieve list-docs

# 2. Query specific page range
echo -e "\n=== Page 1-8 of 23tsdp12 ==="
agent-workbench retrieve page-range \
  --document-id tsa23_2012_23tsdp12 \
  --page-start 1 \
  --page-end 8 > /tmp/page_query.json

# 3. Agent reads output and constructs citation
python -c "
import json
with open('/tmp/page_query.json') as f:
    data = json.load(f)
for rec in data['flat_array']:
    print(f\"Citation: {rec['source_hash'][:12]}... (page {rec['page_anchor']})\")
    print(f\"  Status: {rec.get('audit_status', 'N/A')}\")
    print(f\"  Dedup:  {rec.get('is_dedup', False)}\")
"

# 4. Full-document provenance trace
echo -e "\n=== Provenance Trace for 23ts13ra ==="
agent-workbench retrieve trace \
  --document-id tsa23_2012_23ts13ra \
  --group-by audit_status > /tmp/trace_output.json

echo "Total records: $(python -c \"import json; print(json.load(open('/tmp/trace_output.json'))['metadata']['total_record_count'])\")"
```

## Schema Reference

The retrieval CLI output follows the JSON schemas defined in
`templates/query_schemas/`:

- `use_case_1_page_chunk_anchor_lookup_input.json` — input parameters
- `use_case_1_page_chunk_anchor_lookup_output.json` — output format (array of records)
- `use_case_2_full_document_provenance_trace_input.json` — trace input parameters
- `use_case_2_full_document_provenance_trace_output.json` — trace output (oneOf: flat_array, grouped_by_audit_status, grouped_by_model_lane)

## Notes for Agents

- **Always check `is_dedup`** before citing records from dedup-pending documents
- **Use `source_hash`** to verify you are referencing the exact same chunk in
  follow-up queries or audit trails
- **Cross-reference `text_file` paths** when the agent needs actual content beyond
  structured metadata — the file contains the extracted page text
- **Respect `audit_status`** as a signal of review completeness; `accepted_pending_dedup`
  means the record passed initial review but will be merged with duplicates
