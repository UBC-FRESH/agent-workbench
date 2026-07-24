# VS Code Native-Ollama Tool-Call Proof

Date: 2026-07-23

Status: accepted narrow interoperability proof; not an agent-quality acceptance

## Question

Can an Ollama-served model make a structured Copilot built-in tool call, have
VS Code execute it, and receive the resulting tool output through the VS Code
Copilot Chat agent loop?

## Proven Setup

The accepted session used the **Keklick Copilot Custom Endpoints** extension,
not the official Ollama VS Code provider.

| Component | Observed configuration |
| --- | --- |
| VS Code | `1.130.0` |
| GitHub Copilot Chat | `0.58.0` |
| Custom endpoint extension | Keklick Copilot Custom Endpoints `1.0.22` |
| Provider protocol | Custom Copilot native Ollama mode: `apiMode: "ollama"` |
| Base URL shape | Remote Ollama origin with **no** `/v1` suffix |
| Target model entry | `qwen3-coder:latest`, config ID `ollama-qwen3-coder-native` |
| Declared model capability | `tool_calling: true` |
| Remote Ollama server | `0.32.0` |
| Authorization | Local VS Code settings supplied the required request headers; values are intentionally not recorded here |

The relevant, public-safe Custom Copilot model shape is:

```json
{
  "id": "qwen3-coder:latest",
  "configId": "ollama-qwen3-coder-native",
  "displayName": "qwen3-coder:latest (Custom Copilot / native Ollama API)",
  "owned_by": "fresh-ollama",
  "baseUrl": "https://<remote-ollama-origin>",
  "apiMode": "ollama",
  "context_length": 131072,
  "max_tokens": 4096,
  "vision": false,
  "tool_calling": true,
  "headers": {
    "<authorization-header>": "<local-secret>"
  }
}
```

This path is distinct from both of the following:

- the existing working vLLM route through Custom Copilot with `apiMode: "openai"`
  and an OpenAI-compatible `/v1` endpoint; and
- the official Ollama VS Code extension, which contributes models under its own
  `Ollama` picker group and calls native `/api/chat` itself.

## Test Ticket

The Copilot Chat agent received this bounded request:

```text
Use exactly one built-in VS Code tool.

Run a read-only command that lists only the names of items in the workspace root.
Do not inspect subdirectories, edit files, create files, use GitHub, or invoke
subagents.

After the tool returns, reply with exactly:

TOOL_LOOP_OK: <first item name returned by the command>

If you cannot use a tool, reply exactly:

TOOL_LOOP_FAILED
```

## Accepted Evidence

Persisted Copilot transcript:

```text
workspaceStorage/.../GitHub.copilot-chat/transcripts/
dbd1926a-28fb-43eb-99c3-404cc2b89af8.jsonl
```

Observed sequence:

1. The model emitted a structured `run_in_terminal` request with command
   `ls -Name`.
2. VS Code recorded `tool.execution_start` for `run_in_terminal`.
3. VS Code recorded `tool.execution_complete` roughly 1.1 seconds later.
4. On its next turn, the model described the returned directory listing. This
   demonstrates that the tool result was returned to the model.

The emitted tool-call identifier began `ollama_tc_`. This is decisive routing
evidence: Keklick Custom Copilot's native Ollama adapter constructs that exact
identifier format when it translates a returned Ollama `message.tool_calls`
value into VS Code's `LanguageModelToolCallPart`. It is not the identifier
format used by the OpenAI-compatible Custom Copilot path.

## Result and Limits

This accepts the narrow compatibility claim:

```text
remote Ollama model
  -> Custom Copilot native Ollama adapter
  -> VS Code Copilot built-in terminal tool
  -> tool result returned to the model
```

It does **not** accept the model as a reliable Copilot agent. After the first
successful tool result, the model violated the ticket by issuing a
`task_complete` tool call with an unsolicited repository analysis, then made a
second terminal request (`ls -la src/`). The second command was also unsuitable
for PowerShell. It never emitted the required `TOOL_LOOP_OK` response.

Verdicts for this session:

- **Quality:** failed — it did not follow the bounded task or final-output
  contract.
- **Protocol:** accepted for one structured terminal tool call and result
  return; failed for stop and tool-count discipline.
- **Economics:** not captured by the persisted transcript.

## Reproduction and Next Comparison

1. Reload VS Code after configuring the native-Ollama entry.
2. In Copilot Chat's model picker, choose
   `qwen3-coder:latest (Custom Copilot / native Ollama API)`.
3. Use the test ticket above in Agent mode.
4. Inspect the persisted transcript for a `run_in_terminal` request with an
   `ollama_tc_` call ID, followed by `tool.execution_start` and
   `tool.execution_complete`.
5. Evaluate constraint following separately from transport success.

The next controlled comparison should run the same ticket through:

1. the official `Ollama` picker entry;
2. Custom Copilot native Ollama mode; and
3. Custom Copilot OpenAI-compatible `/v1` mode.

Capture the selected UI model, every requested tool, every executed tool, final
response text, elapsed time, and any provider logs for each run. Do not record
endpoint URLs, authorization headers, raw private transcripts, or credentials
in tracked planning artifacts.
