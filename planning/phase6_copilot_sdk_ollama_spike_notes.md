# Phase 6 Copilot SDK Ollama Feasibility Spike Notes

## Purpose

Phase 6 tests whether the GitHub Copilot SDK can become a cleaner bridge for
Ollama-backed worker trials than the VS Code Chat launch path explored in
Phases 3 through 5.

The main question is not whether the SDK exists or whether Ollama can generate
text. The question is whether this repo can get repeatable worker evidence with:

- explicit model selection;
- explicit OpenAI-compatible provider configuration;
- observable assistant/session events;
- low ambient tool exposure; and
- ignored local result files suitable for supervisor verification.

## Local SDK Support Audit

The local Copilot SDK documentation describes BYOK provider support for
OpenAI-compatible endpoints. It lists Ollama under provider type `openai` and
shows an Ollama-style base URL of `http://localhost:11434/v1`.

The same documentation states that custom providers require an explicit `model`
argument. That is the key difference from the VS Code Chat bridge path: the
SDK probe can request `qwen3-coder:latest` or `qwen3-coder-next:latest` in the
session configuration instead of relying on the VS Code model picker or custom
agent frontmatter.

The SDK documentation also describes a client `mode` setting. For this phase,
`mode="empty"` is the preferred probe default because it avoids ambient
CLI-style tools and keeps the first feasibility question focused on model
selection, event capture, and stop behavior.

Documented capability is not the same as local success. Phase 6 treats the SDK
path as a candidate until an actual probe captures event evidence against the
configured Ollama endpoint.

## Probe Scaffold

Phase 6 adds `scripts/copilot_sdk_ollama_probe.py`.

The probe:

- requires an explicit `--model`;
- accepts the OpenAI-compatible provider URL through `--base-url` or the
  `AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL` environment variable;
- accepts exactly one of `--ticket` or `--prompt`;
- defaults to `mode="empty"`;
- defaults to `wire_api="completions"` for broad Ollama compatibility;
- waits for `session.idle` and reports timeout as a blocker; and
- writes a Markdown evidence file under ignored `runtime/` paths.

The probe deliberately does not embed remote endpoint details, credentials, or
worker transcripts in tracked files. Non-local provider URLs are scrubbed from
the generated Markdown result.

## Same-Ticket Trial Protocol

Use a fixed local ticket in `runtime/agent_jobs/`. The ticket should be narrow
enough to expose loop/stop behavior without requiring repository mutation.

Recommended first ticket:

```text
You are executing an Agent Workbench worker probe.

Do not use tools.
Do not run commands.
Do not edit files.
Reply with exactly this single line and then stop:

P6_SDK_NO_TOOL_PROBE done
```

Recommended command shape:

```powershell
$env:AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL = "<configured-openai-compatible-url>"
python scripts/copilot_sdk_ollama_probe.py `
  --model qwen3-coder:latest `
  --ticket runtime/agent_jobs/p6_sdk_no_tool_probe.ticket.md `
  --output runtime/agent_jobs/p6_sdk_qwen3_coder.result.md

python scripts/copilot_sdk_ollama_probe.py `
  --model qwen3-coder-next:latest `
  --ticket runtime/agent_jobs/p6_sdk_no_tool_probe.ticket.md `
  --output runtime/agent_jobs/p6_sdk_qwen3_coder_next.result.md
```

The supervisor should compare:

- whether each run reaches `session.idle`;
- whether the requested model is reflected in the probe configuration;
- whether the assistant output contains exactly the required marker once;
- whether event records show unexpected tool activity; and
- whether either model repeats completion prose after satisfying the ticket.

## Initial Feasibility Decision

The SDK path is worth pursuing because it directly addresses the P4 and P5
blocker: unreliable model selection evidence through VS Code Chat/custom-agent
launches.

It should not yet replace the VS Code Chat bridge. The next decision point is a
real local run against the configured Ollama endpoint. If the SDK probe can run
both qwen models with clean `session.idle` behavior and captured assistant
events, P7 should promote this into a repeatable local model-evaluation harness.

If the SDK probe cannot connect to the configured endpoint, cannot run without
ambient tools, or loops in the same way as VS Code Chat, P7 should instead move
to a raw Ollama API harness and keep the Copilot SDK as a documented dead end or
secondary experiment.
