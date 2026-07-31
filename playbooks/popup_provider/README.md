# Popup Provider Framework

Portable framework for standing up short-lived ("popup") OpenAI-compatible LLM
providers on shared HPC clusters and research clouds.

## Purpose

Every bring-up (Sockeye, Alliance, Arbutus) rebuilt the same five concerns by
hand: find capacity, stage a model, launch a server, expose it to a client,
and keep it alive. Each rebuild produced different host-specific scripts and
repeat avoidable defects.

This framework generalizes those concerns into:

- **Target descriptors** (`targets/`) — cluster-specific parameters: scheduler
  kind, submit shape, account, partition, GPU/VRAM shape, access mode, auth
  constraints.
- **Launch profiles** (`profiles/`) — model/server parameters: model ID,
  quantization, serving flags, tool-call parser, context window.
- **Fit preflight** (`preflight/`) — refuse or downsize a request that cannot
  fit the target's VRAM, using measured values.
- **Bring-up scripts** (`bringup/`) — unattended bring-up sequence: wait for
  capacity, stage, serve, expose, verify, report.

## Directory Layout

```
playbooks/popup_provider/
├── README.md                  # this file
├── targets/                   # one YAML per cluster target
│   ├── sockeye.example.yaml   # UBC ARC Sockeye (Slurm, V100 32GB)
│   └── _schema.yaml           # target descriptor schema
├── profiles/                  # one YAML per model/server config
│   ├── qwen25-coder-7b.yaml   # Qwen2.5 Coder 7B Instruct
│   ├── qwen36-27b-nvfp4.yaml  # Qwen3.6 27B NVFP4
│   └── _schema.yaml           # launch profile schema
├── preflight/                 # fit-preflight logic
│   ├── catalog.json           # measured VRAM values per model
│   └── check.py               # preflight checker
└── bringup/                   # unattended bring-up scripts
    ├── submit.sh              # allocation submission wrapper
    ├── autostart.sh           # wait-for-capacity + launch + bridge
    ├── bridge.py              # SSH/srun loopback bridge
    ├── wait-ready.sh          # readiness probe (reused from P119)
    └── verify.sh              # bounded client request + report
```

## Safety Boundary

- Bind model servers to loopback on the provider host unless an already
  established ingress explicitly covers them.
- Reuse human-authenticated sessions on MFA-gated clusters; never attempt to
  authenticate interactively as an agent.
- Keep allocation records, endpoints, credentials, host paths, and raw logs in
  ignored local storage.
- Treat every cluster's scheduler as a shared resource: prefer the smallest
  viable request and the shortest viable walltime.

## Motivating Constraints

1. **Right-size before requesting.** The smallest allocation that fits the
   model schedules soonest. A 7B model that fits one GPU must not request four.
2. **Assume nobody is watching.** Bring-up must complete unattended whenever
   the allocation lands, hours after submission.

## Prior Art Reused (Not Rewritten)

| Asset | Reused As |
| --- | --- |
| `playbooks/hpc_vllm/gpu_capacity_coordinator.md` | multi-cluster capacity watcher pattern |
| `playbooks/vllm_blackwell/scripts/serve-native.sh` + `profiles/*.env` | parameterized launch-profile layer |
| `playbooks/vllm_blackwell/scripts/wait-ready.sh` | readiness probe (port-scanning, host-agnostic) |
| `playbooks/vllm_blackwell/scripts/watchdog-vllm-progress.py` | liveness/wedged-engine recovery |
| `playbooks/vllm_blackwell/scripts/bench_openai*.py` | post-bring-up verification |
| `playbooks/cloudflared_model_provider.md` | public-ingress access mode |
| P124 Sockeye bridge + autostart pattern | private SSH-forward access mode |

## Out of Scope

- Creating, migrating, or replacing tunnels, DNS, or connectors.
- Requesting, extending, or renewing allocations (the capacity coordinator
  handles that separately).
- Throughput, quality, or economics claims about any model.

## Known Defects Encoded as Guards

From the Sockeye PoC (see `notes/operations/sockeye-loopback-bridge.md`):

1. Bridge must auto-discover job ID from `squeue` — never hardcode.
2. `srun` stderr must never go to `/dev/null`.
3. Bridge must refuse connections when no allocation exists.
4. Right-size tensor parallelism (TP=1 for 7B on V100, not TP=4).
5. Autostart must handle multi-hour queue waits unattended.
6. Guard compat wheel surgery with a marker file.
7. Client `context_length` must match server `--max-model-len`.
8. Client model `id` must match server `--served-model-name`.
9. A correct `--tool-call-parser` and a correct chat template are still not
   sufficient. The model must actually emit the format its template asked
   for. Verify tool calling with a live tool-definition request and assert
   `tool_calls` is non-empty — never infer it from configuration.

### Observed instance of defect 9

Sockeye, 2026-07-31, `qwen2.5-coder-7b-instruct`, vLLM 0.10.0 (custom sm70
build), served with `--enable-auto-tool-choice --tool-call-parser hermes`,
`--dtype half`, TP=1.

The checkpoint's embedded template is correct: it emits a `<tools>` block and
instructs the model to reply within `<tool_call></tool_call>` XML tags, which
is exactly what the `hermes` parser consumes. Configuration was sound.

Given a `read_file` tool definition, the model returned:

```
finish_reason: stop
tool_calls: []
content: '```json\n{"name": "read_file", "arguments": {"path": "..."}}\n```'
```

Correct function, correct arguments, wrong wire format — markdown fence
instead of `<tool_call>` tags. The parser had nothing to match, so a Worker
bound to this endpoint reports `BLOCKED` while reasoning correctly.

This is a **model capability limit at this size and precision**, not a
misconfiguration. Do not attempt to fix it with `--chat-template`. Treat
reliable tool-call emission as a per-model, per-quantization property that
must be measured.

10. VRAM fit is necessary but not sufficient. A model can fit comfortably and
    still be unloadable because the target's build lacks the kernels its
    architecture needs. Model registry presence proves the architecture is
    *recognized*, not that its kernels are *compiled*. Older GPUs on bespoke
    builds (sm70/Volta) are where this bites.

### Observed instance of defect 10

Sockeye, 2026-07-31. `qwen3-coder-30b-a3b-instruct` passes VRAM fit easily
(57GB over 4x32GB, TP=4 valid) and `Qwen3MoeForCausalLM` is present in the
vLLM 0.10.0 registry. It still cannot load: the sm70 build has no MoE kernels,
so engine startup dies with
`AttributeError: '_OpNamespace' '_moe_C' object has no attribute 'topk_softmax'`
during `determine_num_available_blocks`.

The fit preflight in `preflight/check.py` models VRAM only and would have
green-lit this swap. Kernel/architecture support is a separate gate that the
preflight does not yet implement — see the note below.

### Known gap: preflight does not check kernel support

`preflight/check.py` answers "does it fit?" but not "can this build run it?"
A complete preflight needs a second gate covering architecture registration
and compiled-kernel availability for the target's runtime. Until that exists,
verify MoE and novel architectures manually against the target build before
committing to a stage-and-swap.

## Acceptance (P125)

P125 concludes only that the framework brought a provider up unattended on at
least two distinct targets and served a bounded client request on each.

## Reporting

Record **Quality**, **Protocol**, and **Economics** separately. Queue waits and
allocation expiry are expected findings — report as observations, not failures.