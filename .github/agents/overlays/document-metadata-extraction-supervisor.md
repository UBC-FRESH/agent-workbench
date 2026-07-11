# Document Metadata Extraction Supervisor Overlay

Use this overlay when the assigned task is a whole-document metadata extraction
supervisor job.

- Read the complete assigned document package before deciding the report is
  impossible.
- Produce a useful first-pass seed, not a production index.
- Extract document metadata, major structure, table/caption inventory,
  assumptions, constraints, scenarios, named quantities, model inputs, caveats,
  and gaps.
- Use source anchors for every candidate record. Exact quotes are preferred,
  but table captions, page anchors, and clearly labeled synthesized table facts
  are acceptable repairable anchors.
- Do not reject useful table-derived facts merely because they are not verbatim
  quote strings.
- Separate `quality`, `protocol`, and `economics` observations in the report.
- If the result is below minimum quality, return a compact gap report that a
  coordinator can turn into one bounce ticket.
- Final evidence must identify the report path, candidate-record count,
  confidence bins, known gaps, and recommended next action.
