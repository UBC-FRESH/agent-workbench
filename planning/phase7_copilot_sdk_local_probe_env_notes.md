# Phase 7 Copilot SDK Local Probe Environment Notes

## Purpose

Phase 7 turns the Phase 6 SDK/Ollama probe scaffold into a locally runnable
environment path. The goal is to separate three questions that were tangled in
P6:

- Can the Python process import the Copilot SDK?
- Can the SDK start a compatible Copilot CLI runtime?
- Can the runtime reach the configured Ollama OpenAI-compatible endpoint?

## Local Environment Setup

Use an ignored local virtual environment. Do not commit the environment,
downloaded runtime, provider headers, or raw probe outputs.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install github-copilot-sdk==1.0.5
.\.venv\Scripts\python.exe -m copilot download-runtime
```

The published SDK wheel is preferred for first runnable probes because it has a
pinned runtime version. A development checkout can be useful for reading or
patching SDK source, but an editable development install may not have a pinned
runtime. In that case, supply `COPILOT_CLI_PATH` or use
`python -m copilot download-runtime --version <runtime-version>` if a compatible
runtime version is known.

## Probe Script Updates

Phase 7 updates `scripts/copilot_sdk_ollama_probe.py` so it can:

- load a local SDK Python source checkout through `--sdk-source` or
  `AGENT_WORKBENCH_COPILOT_SDK_PYTHON`;
- use ignored `runtime/copilot_sdk_home` storage by default, which is required
  for SDK `mode="empty"`;
- pass `available_tools=[]` explicitly so no-tool probes can run in empty mode;
- accept provider access headers through `--provider-headers-json`,
  `--provider-headers-file`, or environment variables without committing them;
- classify `model.call_failure` and `session.error` events as blocked results;
  and
- write concise observed-error summaries before raw event records in ignored
  result files.

## No-Tool Probe Ticket

The first P7 probe uses this ignored local ticket:

```text
You are executing an Agent Workbench worker probe.

Do not use tools.
Do not run commands.
Do not edit files.
Reply with exactly this single line and then stop:

P7_SDK_NO_TOOL_PROBE done
```

Command shape:

```powershell
$env:AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL = "<configured-openai-compatible-url>"
$env:AGENT_WORKBENCH_PROVIDER_HEADERS_FILE = "runtime/local_provider_headers.json"

.\.venv\Scripts\python.exe scripts\copilot_sdk_ollama_probe.py `
  --model qwen3-coder:latest `
  --ticket runtime\agent_jobs\p7_sdk_no_tool_probe.ticket.md `
  --output runtime\agent_jobs\p7_sdk_qwen3_coder.result.md
```

If the provider does not need headers, omit `AGENT_WORKBENCH_PROVIDER_HEADERS_FILE`.
For the current UBC-FRESH worker setup, this value should point at the remote
Ollama server's OpenAI-compatible endpoint. Do not commit the endpoint or access
headers.

The VS Code Ollama provider configuration can be used as a local source of
truth. In this environment it lives in the VS Code user
`chatLanguageModels.json` file and contains a provider named `Ollama` with a
remote URL and Cloudflare Access headers. Keep those values in ignored runtime
files or environment variables only.

One practical access detail matters: direct Python requests with the default
Python user-agent were blocked by the access layer, while requests with an
ordinary user-agent succeeded. The P7 ignored provider-header file therefore
included the provider access headers plus a non-default `User-Agent`.

## Probe Findings

The local P7 run made real progress beyond P6:

- The ignored `.venv` can import `github-copilot-sdk`.
- The published SDK wheel `1.0.5` can download and start Copilot runtime
  `1.0.67`.
- SDK `mode="empty"` works after providing ignored base storage and an explicit
  empty tool list.
- The runtime emits event evidence showing disabled built-in tools and selected
  model.
- The no-tool attempt reaches the remote Ollama model through the SDK runtime.
- `qwen3-coder:latest` returned exactly `P7_SDK_NO_TOOL_PROBE done`.
- `qwen3-coder-next:latest` returned exactly `P7_SDK_NO_TOOL_PROBE done`.
- Both successful runs used explicit model names, ignored provider headers, and
  `available_tools=[]`.

The earlier localhost attempt remains useful only as a negative-control check:
it proved that the classifier marks provider connection failures as blocked
instead of treating `session.idle` as success by itself.

## Decision

The SDK path is now the preferred bridge candidate for controlled worker probes:

- model selection is explicit in the SDK session;
- tool exposure can be set to an explicit empty list;
- provider failures are observable as structured events; and
- result files can be generated without scraping VS Code Chat state.

The next phase should promote the SDK bridge from a probe into a small repeated
model-evaluation harness. The first harness should run the same bounded ticket
several times for `qwen3-coder:latest` and `qwen3-coder-next:latest`, summarize
marker exactness, loop behavior, event errors, runtime duration, and tool
exposure, and keep raw event records ignored.
