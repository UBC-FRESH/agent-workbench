# Phase 55 Wave 1 Rerun And Full-Document Smoke

This checkpoint reran Wave 0 and Wave 1 after tightening the worker-ticket
contract, then added a Wave 1.1 full-document smoke lane so the test would not
skip later pages.

Raw worker outputs remain ignored under
`runtime/document_library/tsa23_tsr/p55/eval/`.

Tracked aggregate metrics are in
`benchmarks/document_library/tsa23_tsr/p55_wave1_full_document_rerun_summary.json`.

## Wave 0 Rerun

The battery now generates 12 eval packets:

- 3 original `structure_x2` smoke packets;
- 3 new `structure_full` full-document smoke packets;
- 6 later-wave packets for model A/B, size scale, repeatability, and content
  probing.

The new full-document tickets cover:

| Document | Unique PDF Pages | Chunks | Overlapped Page-Slots |
| --- | ---: | ---: | ---: |
| `tsa23_2012_23tsdp12` | 41 | 6 | 46 |
| `tsa23_2012_23ts13pdp` | 17 | 3 | 18 |
| `tsa23_2012_23ts13ra` | 48 | 7 | 54 |

All 12 manifests dry-ran successfully without provider contact.

## Worker Rerun Result

| Document | Lane | Status | JSON Records | Format Defects | Worker Input | Worker Output |
| --- | --- | --- | ---: | --- | ---: | ---: |
| `tsa23_2012_23tsdp12` | `structure_x2` | completed | 4 | 1 duplicate ID | 10,756 | 1,233 |
| `tsa23_2012_23ts13pdp` | `structure_x2` | completed | 10 | 1 document ID mismatch | 10,943 | 3,156 |
| `tsa23_2012_23ts13ra` | `structure_x2` | completed | 0 | 10 brace-less JSON-like lines | 12,947 | 3,517 |
| `tsa23_2012_23tsdp12` | `structure_full` | blocked | 0 | 20 TSV lines; observed 524 model-call failures | 28,759 | 3,103 |
| `tsa23_2012_23ts13pdp` | `structure_full` | completed | 15 | none in aggregate parse | 12,965 | 5,353 |
| `tsa23_2012_23ts13ra` | `structure_full` | completed | 18 | loop-like repetition and mixed pretty/brace-less output | 39,288 | 7,435 |

Total counted local-worker tokens: 116,658 input and 23,897 output. Local
worker cash cost remains zero.

## Interpretation

The full-document expansion was worth running because it confirmed that later
pages contain indexable material that the opening-chunk smoke skipped. The data
package full run surfaced later table candidates; the rationale full run found
appendix and cross-reference material; the public discussion paper completed
cleanly over its full 17-page range.

The single huge-ticket pattern is not stable enough to scale as-is. The failure
mode is not that the model knows nothing; it is that large tickets increase
format drift:

- TSV instead of JSONL for the data package;
- brace-less JSON-like lines for the rationale rerun;
- mixed parseable JSON plus loop-like repetition for the full rationale.

## Recommendation

Do not proceed directly to Wave 2 with one huge ticket per document. The next
best move is to split full-document extraction into deterministic per-chunk or
small-bundle jobs, then add a delegated repair/normalization step that converts
TSV, brace-less JSON-like lines, and pretty JSON into strict JSONL before any
paid supervisor audit.
