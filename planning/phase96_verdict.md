# Phase 96 Verdict

## Scope

- Phase: P96 Yield And Audit-Cost Model Comparison
- Parent issue: #585
- Child issues: #588 (execution), #589 (verdict)
- Run id: `p96-3-lane-compare-tsa23-2012-23ts13ra-a`

## Verdict

`attempted_with_partial_signal` — full bounded run (p96_4) completed; token-level
yield signal obtained but full accepted-record classification per P96 protocol was not executed.

## Why (Original Attempt)

The comparison protocol and model-lane selection were completed, and a bounded
execution attempt was performed for both explicit lanes:

- baseline: `qwen3.6:35b-a3b-bf16`
- candidate: `qwen3.6:35b-a3b-q8_0`

The original run (p96_3) failed before model-call events with:

- `OSError: [WinError 193] %1 is not a valid Win32 application`

This was caused by an environmental issue (`COPILOT_CLI_PATH` env var set to a
non-executable path) in the session that attempted the probe. The failure was
environmental, not protocol or economics.

## Corrective Run (p96_4)

Both lanes were re-run successfully after correcting the environment:
- Set `$env:AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL = 'https://fresh01x.01101.dev/v1'`
- Removed stale `COPILOT_CLI_PATH` env var
- Ran probe script as a file (not inline one-liner to avoid PowerShell quoting issues)

**Evidence:**
- Baseline lane: `runtime/agent_jobs/p96_4_baseline_probe.md` — status: `completed`
- Candidate lane: `runtime/agent_jobs/p96_4_candidate_probe.md` — status: `completed`
- Both lanes emitted full event sequences including `assistant.usage`, `assistant.message`,
  `assistant.reasoning`, and `session.idle`.

## Evidence

- Protocol: `planning/phase96_comparison_protocol.md`
- Lane selection: `planning/phase96_model_lane_selection.md`
- Manifest: `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_manifest.json`
- Original blocked baseline: `runtime/agent_jobs/p96_3_baseline_probe.md` (status: `blocked`)
- Original blocked candidate: `runtime/agent_jobs/p96_3_candidate_probe.md` (status: `blocked`)
- Successful baseline run: `runtime/agent_jobs/p96_4_baseline_probe.md` (status: `completed`)
- Successful candidate run: `runtime/agent_jobs/p96_4_candidate_probe.md` (status: `completed`)
- Blocker packet: `runtime/agent_jobs/p96_3_lane_comparison_blocker.md`

## P60 Outcome Semantics

- `quality_validated_candidate`: **partial** — token-level proxy signal obtained
  (336 vs 311 output tokens, -7.4% delta). Full accepted-record classification per
  the P96 yield measurement protocol was not executed. This is a real directional
  finding but does not satisfy the P96 protocol's explicit yield measurement
  requirements.
- `protocol_accepted_candidate`: **true** — both lanes completed, obeyed comparison
  boundaries, and emitted proper event sequences
- `economics_usable`: **null (structurally unavailable)** — local Ollama endpoint
  provides no $/token pricing or paid API gateway routing; audit-cost computation
  is impossible with current infrastructure

## Boundary Warnings

- The original p96_3 verdict claiming `insufficient_evidence` was incorrect.
  Both lanes ran successfully in the corrective p96_4 run.
- The WinError 193 defect was environmental (env var configuration), not protocol.
- Actual model-yield and audit-cost quantitative comparison remains partially done:
  token-level delta captured (336 vs 311 output tokens, -7.4%), but accepted-record
  classification yield is null (structurally impossible without P96 protocol's record-classification step).

## Recommended Follow-On

1. Compute lane-level yield metrics from event logs (partial: token delta captured).
2. Supervisor audit-token spans per lane require API gateway routing; cannot be
   computed from local Ollama endpoint.
3. Compare bf16 vs q8_0 on yield and cost to produce the quantitative verdict.
4. Update `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_execution_summary.json`
   with corrected outcome semantics.
5. Note: token-level comparison is sufficient for qualified closeout; full
   accepted-record classification would be needed for a definitive go/no-go on
   q8_0 quantization adoption.
4. Update `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_execution_summary.json` with corrected outcome semantics.
