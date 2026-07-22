# P119 Blackwell vLLM Crash Forensics Note

Date: 2026-07-22

Scope: sanitized follow-up to the P119 Blackwell vLLM concurrency profile after
a long-running concurrent subagent session ended with a vLLM engine crash.

## Summary

The Blackwell vLLM profile ran useful concurrent agent work for hours before a
single late crash. That is positive stability evidence for the profile's normal
operating envelope. The crash evidence points to a rare GPU-kernel fault on a
specific long-context request shape, not to overload, ordinary out-of-memory
pressure, or general concurrency collapse.

The current best interpretation is:

- Quality: the server sustained real multi-agent work for hours, then failed on
  a likely kernel edge case.
- Protocol: the investigation preserved sanitized evidence only. Raw logs,
  endpoint details, credentials, and local private paths remain untracked.
- Economics: no durable provider-cost accounting was captured for this
  incident; the finding is operational, not an economics result.

## Observed Crash Shape

The vLLM process terminated at approximately 2026-07-21 23:01 local time with
`CUDA error: an illegal instruction was encountered`.

The immediately associated scheduler dump showed:

- One running request and zero waiting requests.
- KV cache usage around 6.3 percent.
- A prompt length of 99,870 tokens.
- Prefix-cache hits for 97,600 tokens.
- A newly scheduled continuation/prefill chunk of 2,270 tokens.
- Empty speculative-decoding stats at the crash step.

This makes overload unlikely. The request shape is more interesting than the
concurrency level at the instant of failure: a very long cached prefix plus a
continuation prefill appears to have triggered the fatal path.

Kernel logs at the same timestamp recorded NVIDIA Xid 13 faults, including
`SM Warp Exception` with `Out Of Range Register`, followed by Xid 43 channel
termination for the vLLM engine process. That combination is consistent with an
application GPU kernel executing invalid code or invalid register access, after
which the driver terminated the application channel.

## Likely Failure Class

The profile combines several high-performance Blackwell paths:

- NVFP4 model weights.
- FP8 KV cache.
- FlashInfer attention.
- Prefix caching.
- Chunked prefill.
- Asynchronous scheduling.
- MTP speculative decoding.
- Hybrid attention/GDN execution for the Qwen model family.

Because CUDA errors surface asynchronously, the Python stack frame where the
exception appeared is not necessarily the failing kernel. The strongest local
hypothesis is a Blackwell long-prefix continuation prefill edge case somewhere
in the FlashInfer attention, Triton/FLA GDN, NVFP4 linear, CUDA graph, or
Inductor execution path.

MTP is a lower-probability primary cause for this specific crash because the
fatal step was still a prefill step and speculative-decoding stats were empty.
It remains a valid A/B variable if the fault is reproducible.

## Low-Overhead Mitigation Applied Locally

The local ignored vLLM lab launcher was updated to enable CUDA exception
coredump capture by default:

```bash
CUDA_ENABLE_COREDUMP_ON_EXCEPTION=1
CUDA_ENABLE_CPU_COREDUMP_ON_EXCEPTION=0
CUDA_COREDUMP_FILE=<private shared coredump directory>/vllm-cuda-coredump-%p-%h-%t
```

This should have negligible steady-state throughput cost. It does not change
the production performance profile: FlashInfer, FP8 KV, prefix caching,
asynchronous scheduling, MTP, and the current batched-token ceiling remain
enabled.

The intentionally slower diagnostics should remain opt-in for replay only:

- `CUDA_LAUNCH_BLOCKING=1`
- vLLM eager execution
- disabling prefix caching
- BF16 KV instead of FP8 KV
- reducing `max-num-batched-tokens`
- disabling MTP

Those switches are useful for narrowing the guilty backend, but they should not
be enabled globally until evidence identifies a specific failing path.

## Recommended Deterministic Replay Sequence

1. Keep the production profile unchanged except for CUDA exception coredumps.
2. If the crash repeats, preserve the coredump and the matching vLLM scheduler
   dump before restarting or pruning logs.
3. Reproduce the long-prefix shape on a diagnostic instance using the same
   model and a prompt near the observed token length.
4. Add synchronization only for the replay run, starting with
   `CUDA_LAUNCH_BLOCKING=1` and/or eager execution to make the failing operation
   easier to localize.
5. Change one variable at a time: prefix cache, GDN prefill backend, KV dtype,
   MTP, then batched-token ceiling.
6. Patch or profile-gate the specific backend or request-shape combination that
   fails, instead of broadly downgrading the whole server profile.

## Service Hardening Recommendation

The vLLM server should be packaged as a host-managed service before it is used
as a routine agent endpoint.

Recommended shape:

- Run vLLM under `systemd` with private environment files for endpoint secrets.
- Use `Restart=on-failure` with a short `RestartSec`, not an unbounded tight
  crash loop.
- Add `StartLimitIntervalSec` and `StartLimitBurst` so repeated kernel faults
  fail closed and preserve evidence.
- Send stdout/stderr to journald and keep the CUDA coredump directory outside
  tracked repo paths.
- Add a lightweight health-check helper that verifies the OpenAI-compatible
  `/v1/models` or chat endpoint and reports the active served-model name.
- Optionally add an external monitor or timer that alerts when health remains
  bad after the service restart window.

This would improve user experience after a rare engine-channel crash: the
endpoint can revive automatically when the GPU and driver remain healthy, while
still preserving coredumps and logs for root-cause analysis if the failure
becomes repeatable.

## Service Hardening Follow-Up

A bounded `systemd` service template was added to the P119 Blackwell playbook at
`playbooks/vllm_blackwell/systemd/vllm-blackwell.service.example`.

The intended operator posture is:

- keep the high-performance vLLM profile unchanged;
- enable CUDA exception coredumps in the launcher;
- let `systemd` restart the service after isolated engine failures;
- let a progress watchdog restart the service when EngineCore is alive but
  running requests stop advancing token counters while GPU SM remains high;
- cap restart attempts so repeat kernel faults fail closed and preserve
  evidence;
- verify readiness with the OpenAI-compatible `/v1/models` endpoint after
  service start or restart.

This records the operational insight without tracking a host-specific unit file,
live endpoint, credential path, raw log, or private transcript.

## Alive-But-Wedged Follow-Up

A later sequential extraction run produced a different failure mode from the
Xid crash. The process stayed alive, `/health` and `/v1/models` still responded,
and no NVIDIA Xid appeared, but vLLM metrics showed two running requests with
no waiting requests while prompt, generation, and accepted speculative token
counters stopped advancing. GPU SM stayed pinned at 100 percent with no useful
token progress. Restarting `vllm-blackwell.service` cleared the stuck requests
and restored the endpoint.

That observation motivates `scripts/watchdog-vllm-progress.py` and
`systemd/vllm-blackwell-watchdog.service.example`. The watchdog detects the
specific alive-but-wedged state by combining service health, running request
count, frozen token counters, and high GPU utilization before restarting.

## Open Questions

- Which backend emitted the invalid-register kernel: FlashInfer attention,
  Triton/FLA GDN, NVFP4 linear, CUDA graph, Inductor, or another fused path?
- Does the crash reproduce only with a very high prefix-cache hit ratio?
- Is there a threshold around the observed continuation size or the current
  batched-token ceiling?
- Does a newer FlashInfer, vLLM, PyTorch, or NVIDIA driver build contain a
  targeted fix for this Blackwell request shape?
- Should service packaging become the next operator-hardening phase after P119
  and P118 settle?
