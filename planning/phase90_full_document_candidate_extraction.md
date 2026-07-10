# Phase 90 Full-Document Candidate Extraction

## Purpose

P90 is now the first actual extraction phase. Its job is to run worker tickets
from the P89 full-document packet, validate candidate records, and decide
whether the workflow is producing enough useful candidate material to justify
source audit.

## P90.0 Smoke Result

The first live smoke ran one complete section pair from the P89 packet:

- section: `tsa23_2012_23tsdp12__pages_001_008__p004__s02`;
- passes: `structure` and `content_metadata`;
- model lane: `qwen3.6:35b-a3b-q8_0`;
- raw result storage: ignored `runtime/document_library/tsa23_tsr/p90_actual_extraction/`;
- tracked summary:
  `benchmarks/document_library/p90_actual_extraction_smoke_summary.json`.

The two live calls completed and produced 51 valid raw candidate records after
deterministic extraction/repair into JSONL:

- 20 `structure` records; and
- 31 `content_metadata` records.

No records are accepted yet. The result proves that actual extraction can
produce candidate material, not that the candidates are source-audited or ready
for promotion.

## Observed Defects

The model did not obey the output contract cleanly:

- the `structure` pass returned prose and a Markdown-fenced JSONL block instead
  of bare JSONL; and
- the `content_metadata` pass returned key/value blocks instead of JSONL.

Both outputs were repairable into valid candidate JSONL, but this is a real
protocol defect. P90.1 should either harden the prompt, choose a stricter model
lane, or run extraction in smaller batches where deterministic repair remains
cheap and reliable.

## Next Work

P90.1 should define a full-document extraction batch plan that prioritizes
getting a useful complete candidate packet quickly:

- start with structure passes across all 60 section units;
- validate/repair after every ticket, not at the end;
- stop if unknown chunk IDs or unrepaired malformed records recur;
- summarize candidate yield by page/section and object type; and
- audit a bounded high-value sample before claiming accepted records.
