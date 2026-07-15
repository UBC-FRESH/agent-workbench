# P113.3 Native Worker Reliability Decision

Status: complete

## Operational decision

Accept the constrained one-tool adapter as a quality, protocol, and Worker
reliability candidate. Do not resume P107 or activate P108.

## Evidence

- Focused deterministic adapter tests and the public-safe fixture validator
  pass.
- Five independently fresh `qwen3-coder:latest` Workers each completed one
  exact `apply_patch` call, changed both allowed ignored targets, and completed
  the custom-tool follow-up normally.
- The adapter rejected malformed provider calls and invalid history during
  development without forwarding an unvalidated patch to Codex.
- Each counted trial has one native `apply_patch` call, an expected two-file
  ignored-target diff, a terminal marker, and no adapter rejection.
- A PowerShell wrapper stopped one non-counting launch before a Worker session
  began; it is preserved as launcher evidence, not a trial retry.
- A clean normal-provider control after the loopback route was removed produced
  textual pseudo-tool markup rather than a native call. This confirms that the
  constrained adapter is required for this provider/model path.

## Outcome separation

| Outcome | Status | Reason |
| --- | --- | --- |
| `quality_validated_candidate` | accepted | Expected two-file native patch completed on an ignored target. |
| `protocol_accepted_candidate` | accepted | One call, containment, history translation, native result, and normal terminal completion were observed. |
| Worker reliability | accepted candidate | Five independently fresh Workers met the exact one-call gate. |
| `economics_usable` | out of scope | P107 remains parked. |

This result is the P113.3 closeout evidence. It permits a separate P107-resume
decision; it does not resume P107 or activate P108. Raw provider events,
prompts, session records, and target diffs remain in the ignored P113 runtime
evidence directory.
