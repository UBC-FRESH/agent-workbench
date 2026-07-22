# TOC-First, Section-by-Section Extraction Playbook

**Purpose**: Produce structured JSONL candidate records from PDF-extracted text
chunks without overwhelming the model's context window.

**Problem this solves**: Feeding a full 20-30KB chunk and asking the model to
produce 30-50 JSONL records in one turn causes stalling. The model can't handle
huge input + huge output in one pass.

**Solution**: Narrow the turn. Read one chunk, extract its section headers first,
then produce 1-3 records per section, one section at a time.

---

## Workflow

### Phase 1: Chunk Preparation (one-time, script)

Run `scripts/p109_reextract_2012.py` (or equivalent) to:
1. Download PDFs from source URLs
2. Split into 8-page chunks (~17-21KB text each)
3. Write raw text to `runtime/extracts/tsa23/{doc_id}/chunk_*.txt`
4. Update `chunk_manifest.json` and `provenance.json`

**Why 8 pages?**: ~20KB raw text fits comfortably in a Copilot session alongside
the prompt and output. Larger chunks risk context overflow.

### Phase 2: Section-by-Section Extraction (agent, one chunk per turn)

For each chunk:

1. **Read the raw text** — `runtime/extracts/tsa23/{doc_id}/chunk_XX.txt`
2. **Extract table of contents** — identify numbered section headers and their
   page anchors from the chunk
3. **For each section, produce 1-3 records**:
   - `heading` record (section number, title, page)
   - `section_summary` record (content summary)
   - `table`/`numeric_value`/`claim`/`assumption` records for notable items
4. **Append to JSONL output** — `{doc_id}_candidates.jsonl`
5. **Move to next chunk**

### Output Format

Each JSONL record has 15 required fields (P89 schema v2):
- `record_id`, `corpus_id`, `document_id`, `source_sha256`, `chunk_id`
- `page_anchor`, `document_component`, `section_path`, `object_type`
- `title`, `summary`, `source_quote`, `confidence`, `worker_model`, `review_status`

See `benchmarks/document_library/p89_jsonl_validation_contract.json` for full schema.

### Validation

After all chunks complete:
```bash
python scripts/build_p89_document_indexing_recipe_v2.py validate-jsonl \
  --input benchmarks/document_library/tsa23_tsr/{doc_id}/{doc_id}_candidates.jsonl \
  --contract benchmarks/document_library/p89_jsonl_validation_contract.json \
  --output runtime/agent_jobs/validation_result.json
```

---

## Anti-Patterns (Do Not Do)

- **Do not** feed all 8 chunks in one turn and ask for 200 records. Context overflow.
- **Do not** try to extract every sentence. A section gets 1-3 records, not 20.
- **Do not** fabricate `source_sha256` or `source_quote`. Read from provenance.json
  and exact document text.
- **Do not** use subagent delegation for extraction. Direct read/write is more
  reliable than spawning workers that stall.

## Economics

- **Coordinator** (paid lane): narrows the scope per turn, no heavier lifting needed
- **Model** (local Ollama): each turn reads ~20KB, outputs ~5-15 lines of JSON
- **No delegation overhead** — no manifest generation, session management, or
  result aggregation needed