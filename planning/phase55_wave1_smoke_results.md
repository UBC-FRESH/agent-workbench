# Phase 55 Wave 1 Smoke Results

Wave 1 ran `qwen3-coder-next:latest` once on `structure_x2` tickets for the
three active 2012 TSA23 documents. The raw worker outputs remain ignored under
`runtime/document_library/tsa23_tsr/p55/eval/` because they contain source
quotes from the PDFs.

Tracked aggregate metrics are in
`benchmarks/document_library/tsa23_tsr/p55_wave1_smoke_summary.json`.

## Commands

The successful provider-backed run used the repo virtual environment:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m agent_workbench.cli eval --manifest <wave1 manifest>
```

An earlier attempt with the system Python failed before provider contact with
`No module named 'copilot'`. That failure was not a model or Ollama failure.

## Aggregate Result

All three worker calls completed. The eval harness classified all three as
`duplicate-marker`, but this is a harness false positive for JSONL-only runs
with an empty `expected_marker`; the run status was `completed` and assistant
messages were captured.

| Document | Records | Malformed Lines | Duplicate IDs | Worker Input Tokens | Worker Output Tokens | Main Signal |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `tsa23_2012_23tsdp12` | 2 | 0 | 0 | 10,659 | 547 | Under-produced; mostly front-matter records. |
| `tsa23_2012_23ts13pdp` | 31 | 0 | 23 | 10,846 | 10,600 | Strong extraction volume, but record IDs are not unique enough. |
| `tsa23_2012_23ts13ra` | 9 | 0 | 1 | 12,844 | 3,387 | Useful structure signal, but page anchors drifted to numeric values. |

Total counted local-worker tokens: 34,349 input and 14,534 output. Cash cost is
zero for the local Ollama worker lane.

## Gate Interpretation

Wave 1 is good enough to show that the recent-document refocus was worthwhile:
the local worker produced parseable JSONL records from all three 2012 documents
without looping, tool use, or malformed JSONL.

It is not good enough to scale unchanged. Before Wave 2 or larger tickets, the
ticket/eval contract should be tightened so that:

- `record_id` uniqueness is enforced;
- `page_anchor` is always a string;
- markdown fences are rejected or stripped deterministically;
- data-package chunks require a minimum coverage target beyond front matter;
- empty-marker runs do not trigger misleading `duplicate-marker`
  classifications.

## Recommendation

Pause before Wave 2. The next best move is a small contract-tightening patch
plus a Wave 1.1 full-document smoke run across all three selected documents, so
the first indexing signal does not skip useful later sections before paying the
overhead of a three-model A/B run.
