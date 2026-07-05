# Phase 55 Wave 0 Chunking Results

Wave 0 generated reproducible text chunks, tracked sanitized chunk manifests,
and ignored worker tickets/eval manifests for the P55 TSA23 indexing battery.
No model worker was contacted in this wave.

## Commands

```powershell
python scripts\build_tsa23_indexing_battery.py
```

```powershell
$env:PYTHONPATH='src'
python -m agent_workbench.cli eval-batch `
  --manifest-dir runtime\document_library\tsa23_tsr\p55\manifests `
  --output-dir runtime\document_library\tsa23_tsr\p55\dry_run `
  --dry-run `
  --continue-on-failure
```

## Generated Tracked Artifacts

- `scripts/build_tsa23_indexing_battery.py`
- `benchmarks/document_library/tsa23_tsr/chunk_manifests/tsa23_2012_23tsdp12.json`
- `benchmarks/document_library/tsa23_tsr/chunk_manifests/tsa23_2012_23ts13pdp.json`
- `benchmarks/document_library/tsa23_tsr/chunk_manifests/tsa23_2012_23ts13ra.json`
- `benchmarks/document_library/tsa23_tsr/p55_eval_packet_index.json`

Raw extracted text, worker tickets, eval manifests, and dry-run logs remain
ignored under `runtime/document_library/tsa23_tsr/p55/`.

## Chunking Results

| Document | PDF pages | Chunk count | Extracted text chars | Immediate implication |
| --- | ---: | ---: | ---: | --- |
| `tsa23_1995_23ts95ra` | 38 | 2 | 663 | `pypdf` extraction is probably too sparse for this older PDF; may need OCR or a different extractor before worker tests. |
| `tsa23_2006_23ts06ra` | 51 | 3 | 160194 | Text extraction works, but 24-page chunks are too large for the current ticket cap. |
| `tsa23_2012_23ts13ra` | 48 | 3 | 156341 | Text extraction works, but 24-page chunks are too large for the current ticket cap. |

## Eval Packet Results

The builder generated 9 ignored eval packets:

- 3 Wave 1 single-model smoke packets;
- 1 Wave 2 model A/B packet;
- 3 Wave 3 size-scale packets;
- 1 Wave 4 repeatability packet;
- 1 Wave 5 content-metadata probe packet.

All 9 manifests dry-ran successfully through `agent-workbench eval-batch`.

## Design Finding Before Worker Contact

The originally planned 24-page window is not a good universal default for this
mini-corpus:

- the 1995 PDF needs an OCR/different-extractor decision before a fair worker
  test;
- the 2006 and 2012 PDFs should likely use smaller page windows before running
  x2/x4/x8 comparisons, otherwise the current ticket character cap collapses
  the scale-test shapes into a single included chunk; and
- Wave 1 can still run on the generated packets as a smoke test, but its result
  would partly test the current chunking weakness rather than just model
  extraction quality.

Decision after maintainer review: refocus the active P55 worker battery on the
most recent TSA23 documents. The 1995 sparse-extraction result remains useful
evidence that older documents may need OCR or a different extractor, but it
should not consume the first worker-evaluation signal.

Refocused documents:

- `tsa23_2012_23tsdp12`;
- `tsa23_2012_23ts13pdp`;
- `tsa23_2012_23ts13ra`.

Recommended next move: regenerate Wave 0 with smaller page windows for the
three 2012 PDFs before worker contact.

## Refocused Wave 0 Results

The active P55 battery now focuses on the three 2012 documents. The builder
default changed to 8-page windows with 1-page overlap.

| Document | PDF pages | Chunk count | Extracted text chars | Immediate implication |
| --- | ---: | ---: | ---: | --- |
| `tsa23_2012_23tsdp12` | 41 | 6 | 106859 | Good candidate for Wave 1 smoke. |
| `tsa23_2012_23ts13pdp` | 17 | 3 | 41343 | Good candidate for Wave 1 smoke. |
| `tsa23_2012_23ts13ra` | 48 | 7 | 167655 | Good primary comparison document. |

The regenerated clean manifest directory contains 9 eval packets:

- 3 Wave 1 smoke packets across the three 2012 documents;
- 1 Wave 2 model A/B packet on `tsa23_2012_23ts13ra`;
- 3 Wave 3 size-scale packets on `tsa23_2012_23ts13ra`;
- 1 Wave 4 repeatability packet on `tsa23_2012_23ts13ra`;
- 1 Wave 5 content-metadata probe on `tsa23_2012_23ts13ra`.

All 9 recent-document manifests dry-ran successfully through
`agent-workbench eval-batch`.

Remaining caveat: `structure_x8` still truncates to 4 included chunks under the
current ticket character cap for `tsa23_2012_23ts13ra`. The x2 and x4 shapes are
now meaningful; x8 should be treated as a ticket-cap boundary test unless we
raise the cap or use smaller chunk units.
