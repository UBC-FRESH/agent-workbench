# Phase 53 Document Library Index Pilot

P53 opens the first multi-document document-library indexing pilot. The pilot
uses the BC Timber Supply Review public document collection as a real,
high-return delegation target, but keeps the first implementation step focused
on reproducible corpus setup and extraction metadata scaffolding.

## Mini-Corpus

The P53 mini-corpus is all public TSR PDF documents for TSA 23, 100 Mile House,
from 1995 onward. The corpus is resolved from FEMIC's public TSR registry rather
than rediscovered by hand.

Tracked corpus metadata lives in:

- `benchmarks/document_library/tsa23_tsr/corpus_registry.json`
- `benchmarks/document_library/tsa23_tsr/chunk_manifest_scaffold.json`
- `benchmarks/document_library/tsa23_tsr/audit_calibration_scaffold.json`

Raw PDFs, raw extracted text, prompts, worker outputs, token traces, and
provider details remain ignored under `runtime/`.

## Reproducible Materialization

The tracked script `scripts/materialize_tsa23_tsr_corpus.py` is the durable
entrypoint for recreating the P53 corpus state. It reads FEMIC's
`metadata/tsr/tsa_documents.json`, filters public PDF records for TSA 23 from
1995 onward, writes the sanitized Agent Workbench registry, and can optionally
call FEMIC's built-in TSR fetch command to materialize the PDFs into ignored
runtime storage.

Dry registry/scaffold regeneration:

```powershell
python scripts\materialize_tsa23_tsr_corpus.py --femic-root ..\femic
```

PDF materialization plus registry/scaffold regeneration:

```powershell
python scripts\materialize_tsa23_tsr_corpus.py --femic-root ..\femic --materialize
```

The materialization run exercised FEMIC's built-in fetch lane:

- selected document count: 18;
- cached document count: 18;
- failure count: 0.

The generated registry records SHA256 values for the materialized PDFs without
tracking raw PDF content.

## Corpus Shape

The mini-corpus contains 18 public PDFs:

- 1995: 6 documents;
- 2001: 6 documents;
- 2006: 3 documents;
- 2012: 3 documents.

Document type distribution:

- data package: 1;
- discussion paper: 2;
- rationale: 2;
- supporting document: 13.

## Pilot Scaffold

The first cross-document scaffold selects three rationale/supporting documents
across the available time span:

- `tsa23_1995_23ts95ra`;
- `tsa23_2006_23ts06ra`;
- `tsa23_2012_23ts13ra`.

The scaffold defines comparable metadata for:

- page-window chunking;
- structure extraction;
- content metadata extraction;
- local self-audit;
- delegated repair;
- supervisor audit calibration.

No worker run is claimed in P53. The point of this phase is to make the
multi-document pilot reproducible and ready for controlled P54+ policy tuning
and later document-indexing experiments.

## Policy Lessons For P54

P53 should feed P54 with these requirements:

- document-indexing loops must preserve stable document and record identifiers;
- every scaled worker run needs a known corpus registry, chunk manifest, model
  lane, and token/economics record before results are interpreted;
- local worker tool use must be an explicit lane, not an accidental SDK side
  effect;
- raw public documents can be materialized locally, but tracked artifacts should
  stay metadata-only unless a future phase explicitly promotes a derived index.
