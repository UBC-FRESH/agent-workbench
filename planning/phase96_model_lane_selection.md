# Phase 96 Model Lane Selection

This document documents the selection of candidate model lane(s) for the P96
comparison run against the established baseline.

**Status:** provisionally selected — awaiting worker verification of host availability.

## Baseline Lane (Established from P87-P94)

| Field | Value |
| --- | --- |
| Model name | `qwen3.6:35b-a3b-bf16` |
| Variant type | BF16 (full precision) |
| First seen in P94 index | Yes — all 47 records produced by this lane |
| Reason for baseline | Default unquantized weight variant; reference quality point for the qwen3.6:35b-a3b family |

## Candidate Lane(s)

Per the Advisor insight (2026-07-11), the primary comparison target is a
**quantization variant** of the same model family — specifically `qwen3.6:35b-a3b-q8_0`
(8-bit quantized). This is intentionally a narrow comparison (same architecture,
different precision) rather than a broad model-family scan.

| Field | Value |
| --- | --- |
| Model name | `qwen3.6:35b-a3b-q8_0` |
| Variant type | Q8_0 (quantized) |
| Expected advantage | Lower memory footprint → potentially lower supervisor cost if batch size or concurrency changes |
| Expected risk | Higher rejection rate due to quantization-induced precision loss |

## Selection Rationale

1. **Stays within recipe-stability framing.** Comparing quantization variants of the same model family tests whether the indexing recipe is robust to precision differences, rather than asking which architecture is superior.

2. **Directly affects accepted-record yield OR audit cost.** If q8_0 produces materially fewer accepted records due to precision loss, that's a yield signal. If it allows cheaper batch processing that reduces auditor tokens per review cycle, that's an audit-cost signal. Either way the comparison answers the ROI question.

3. **Explicitly avoids profile-evidence-review-in-disguise.** Comparing `qwen3.6:35b-a3b-bf16` vs `qwen3.6:35b-a3b-q8_0` is a single-variable change — it is not a 6-model sweep disguised as model comparison. The strategic arc (p87_p92) would call such a sweep out-of-scope.

4. **One lane to compare.** Per the P96 task spec, exactly one candidate lane must be selected. q8_0 is that single lane. Additional candidates can be explored in later runs after this baseline comparison is documented.

## Worker Verification Requirements

Before P96.3 executes, the worker agent must verify model availability on the **remote Ollama host** (configured via VS Code Ollama extension):

1. Open Copilot Chat in VS Code and switch the provider to `ollama`.
2. Inspect the full model list shown in the picker for the remote host.
3. Confirm both `qwen3.6:35b-a3b-bf16` (baseline) and
  `qwen3.6:35b-a3b-q8_0` (candidate) appear in that list.
4. If either model is absent, record a blocker and include the exact visible
  ollama model list in the result packet.
5. If models need to be installed, document pull/install evidence from the
  remote host workflow and stop the comparison run until verification is
  complete.

**Important:** do not use `localhost:11434` checks from this workspace terminal.
The local machine does not host Ollama for this workflow.

## Alternative Candidate (If q8_0 Unavailable)

If `qwen3.6:35b-a3b-q8_0` is confirmed absent from the configured host inventory:

| Field | Value |
| --- | --- |
| Model name | `qwen3.6:35b-a3b-q4_K_M` or other quantization variant |
| Rationale | Any quantization variant provides a valid single-variable comparison with BF16 baseline on the same architecture family |
| Note | Must document which variant was selected and why q8_0 was unavailable |

## Run Manifest Update (P96.2 to P96.3 Handoff)

When P96.2 hands off to P96.3, the run manifest from `phase96_comparison_protocol.md`
must be updated with actual model names confirmed present on the host:

```yaml
baseline_lane:
  model_name: qwen3.6:35b-a3b-bf16
  verification_method: copilot_chat_ollama_provider_list_snapshot
  host_verification_time: ""                   # P96.3 fills this
candidate_lane:
  model_name: qwen3.6:35b-a3b-q8_0             # may be replaced if absent on host
  verification_method: copilot_chat_ollama_provider_list_snapshot
  host_verification_time: ""                   # P96.3 fills this
```

## References

- `planning/phase96_comparison_protocol.md` — Full boundary, measurement, and verdict protocol
- `planning/delegation_policy.md` § Model Attribution Risk — Model identity verification rules
- `planning/ollama_worker_model_install_shortlist.md` — Model installation history and available variants
