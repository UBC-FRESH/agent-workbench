# Phase 106 Matched Execution Result

Parent issue: #629

Status: complete (qualified diagnostic)

Phase 106 stops after the contract-bounded attempt and repair allowance. It
does not claim an accepted matched economics result.

## Verdicts

- `quality_validated_candidate`: `true`
- `protocol_accepted_candidate`: `false`
- `economics_usable`: `false`

The deterministic comparison packet is
`benchmarks/document_library/p106_matched_execution_comparison.json`.

## Evidence

The direct GPT-5.6 Luna structured-output lane produced 11 valid records with
100% useful yield and zero critical source-anchor defects. Its provider usage
supports a catalog-backed bounded upper cost estimate of `$0.020963`.

The repaired delegated Worker output produced 8 valid records with 100% useful
yield and zero critical source-anchor defects. This proves useful output
quality, but the native delegated attempt and its one allowed repair did not
persist the required configured Worker child or a trustworthy paid Coordinator
token-span boundary.

The direct execution also preceded recovery of the required delegated-first
protocol gate. Therefore neither lane is promoted as protocol accepted, and the
missing delegated token boundary prevents a total paid-cost comparison.

## Non-counting Agent Hub rehearsal

After P111 merged, one explicitly non-counting shadow rehearsal applied the
same P106 extraction shape to the depth-2 Agent Hub. A Supervisor task spawned
one nested Worker task, but persisted session evidence showed a generic OpenAI
child with no configured agent role rather than the required Ollama Worker.
The child emitted only 5 records, failed the P106 composition gate, and was
stopped without repair or retry.

Raw shadow evidence remains ignored under
`runtime/agent_jobs/p106-agent-hub-shadow-r1/`. It does not change the P106
comparison verdicts or consume a new benchmark attempt.

## Post-closeout recursive Supervisor evidence

Two further fresh-session, non-counting rehearsals tested
`ollama_supervisor` at depth 1. In both runs the root used the accepted generic
`gpt-5.6`/`high` multi-agent v1 surface and created the configured
`agent_workbench_ollama` `qwen3-coder:latest` Supervisor with
`fork_context: false` and no model override. The first edge therefore worked as
configured.

The second edge failed in both rehearsals. The R2 Supervisor emitted an
unsupported `multi_agent_v1` call with a malformed nested spawn payload and
then attempted unrelated serial/local commands. The R3 Supervisor emitted
`multi_agent_v1` with an empty payload, received `unsupported call:
multi_agent_v1`, and then issued five prohibited shell calls. Neither run
created an `ollama_worker` child or benchmark artifact.

The initial R2 sanitized verdict reported zero native spawn calls because its
inspector did not classify the malformed function name as a spawn attempt. Raw
persisted trace evidence is authoritative for that distinction; R3's verdict
records the malformed call explicitly. The paired failures establish an
operational role-selection boundary, not a root-cause allocation between model
tool selection and provider/tool-schema normalization.

These rehearsals remain ignored under `runtime/agent_jobs/`, do not reopen
P106, do not consume benchmark attempts, and do not change its qualified
verdicts. They remove `ollama_supervisor` from the accepted recursive
Supervisor path pending new contrary evidence. The accepted recursive profile
remains GPT-5.6 Luna Supervisor -> Ollama Worker.

## Reproduction

```powershell
.venv\\Scripts\\python.exe scripts\\synthesize_p106_comparison.py `
  --gate benchmarks\\document_library\\p106_matched_execution_gate.json `
  --delegated-summary runtime\\agent_jobs\\p106-comparison-inputs\\delegated_summary.json `
  --direct-summary runtime\\agent_jobs\\p106-comparison-inputs\\direct_summary.json `
  --delegated-tokens runtime\\agent_jobs\\p106-comparison-inputs\\delegated.tokens.json `
  --direct-tokens runtime\\agent_jobs\\p106-comparison-inputs\\direct.tokens.json `
  --output benchmarks\\document_library\\p106_matched_execution_comparison.json
```

The command intentionally exits nonzero because the packet status is
`needs-supervisor-review`; the generated packet preserves the passing quality
verdict independently from the failed protocol and economics verdicts.

## Closeout decision

P106 closes as a qualified diagnostic rather than spending more paid tokens on
an out-of-contract third delegated attempt. P107 may use this result to make a
fail-closed no-go or targeted-remediation decision. P108-P110 remain gated.
