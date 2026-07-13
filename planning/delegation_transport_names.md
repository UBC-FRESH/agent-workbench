# Delegation transport names

Use these names consistently in conversation, code, runtime artifacts, and
documentation. These names describe transport and authority shape, not model
quality.

## `responses_nested_tree`

OpenAI Responses API `multi_agent` transport with hosted recursive subagents:

```text
Coordinator -> Supervisor -> Worker
```

The parent and child agents receive the Responses multi-agent hosted actions,
including nested `spawn_agent`, `wait_agent`, and messaging operations. This is
the consistently proven full nested-tree path. Its current limitation is that
hosted child agents do not provide the required per-child Ollama model/provider
selection for the P106 role split.

## `codex_native_handoff`

Native Codex/app-server orchestration with explicit role and provider bindings:

```text
Coordinator -> Supervisor
Coordinator -> Worker
```

The Coordinator currently mediates the Supervisor-authored ticket and Worker
execution. It supports the required distinct Ollama identities and has passed
the P106 quality path, but the Supervisor does not yet receive an executable
nested spawn tool in the current local subagent wrapper. Do not call this
transport a native nested tree until a real Supervisor child-session event is
captured.

## `copilot_sdk`

Copilot SDK/Chat bridge transport. It remains supported and is not deprecated.
It has demonstrated useful end-to-end delegation, but Copilot Chat/session
availability can stall or fail unpredictably. Its runtime evidence must remain
separately labeled and must not be substituted for the native Codex paths in
P102-P110 experiments.

## Naming rule

Use the exact identifiers above in manifests and summaries. In prose, the
short forms are “Responses tree”, “Native handoff”, and “Copilot SDK”. Never
use “nested” for `codex_native_handoff` unless the Supervisor-owned spawn edge
has independently persisted a child-session event.
