# Phase 14 Model Matrix And Packaging Decision

## Configured Model Inventory

The configured Ollama-compatible provider inventory was refreshed through the
ignored local provider configuration. Endpoint and header details remain local.

Sanitized model IDs observed:

- `codestral:latest`
- `deepseek-coder-v2:16b`
- `devstral-2:latest`
- `devstral-small-2:latest`
- `devstral:24b`
- `gemma4:31b`
- `gpt-oss:120b`
- `gpt-oss:20b`
- `llama3.1:latest`
- `nomic-embed-text:latest`
- `qwen3-coder-next:latest`
- `qwen3-coder:latest`
- `starcoder2:latest`

## Ticket-Family Matrix

| Phase | Ticket family | Bridge | Model evidence | Result |
| --- | --- | --- | --- | --- |
| P8 | exact no-tool marker | SDK/Ollama | qwen pair | both models exact marker, two repeats each |
| P9 | structured Markdown output | SDK/Ollama | qwen pair | both models structured output, two repeats each |
| P10 | patch proposal, no mutation | SDK/Ollama | qwen pair | qwen-next complete proposals; qwen missing verification section |
| P11 | supervisor-applied patch | supervisor harness | qwen-next proposal reused | sandbox apply succeeded |
| P12 | restricted ignored-file mutation | VS Code Chat bridge | qwen3-coder observed | allowed file created, no deviations |
| P13 | GitHub comment preparation | SDK/Ollama plus supervisor `gh` | qwen-next | worker candidate missing section; supervisor comment succeeded |

## Cross-Model Findings

The current repeated qwen evidence supports these narrow conclusions:

- Both qwen models handled exact no-tool markers in P8.
- Both qwen models handled small structured Markdown output in P9.
- `qwen3-coder-next:latest` handled the stricter P10 patch-proposal format
  better than `qwen3-coder:latest` in the small sample.
- Neither result is enough to claim broad model superiority.

Observed failure modes still relevant:

- VS Code Chat sessions can loop or repeat completion summaries in some modes.
- Worker-prepared GitHub text can be incomplete even when syntactically useful.
- Custom-agent model frontmatter is not reliable model-selection evidence in
  the tested setup.

## Packaging And Interface Options

| Option | Decision | Rationale |
| --- | --- | --- |
| Markdown plus local scripts | Continue | Current workflow is moving quickly and remains inspectable. |
| Python package / CLI | Defer | The scripts are useful, but command contracts are still changing every phase. |
| VS Code extension | Defer | VS Code integration is attractive, but session/tool behavior is still unstable. |
| MCP server | Defer | MCP would add another tool-permission layer before the core protocol is stable. |
| Hosted agent service | Defer | Premature until local evidence, scoring, and data retention rules stabilize. |

## Architecture Decision

Decision: keep Agent Workbench as Markdown protocols plus local scripts for the
next tranche.

The next tranche should expand the model matrix across the newly available
configured models and keep using ignored runtime evidence. A package or
extension should wait until the stable command surfaces are clear enough to
avoid wrapping churn.

## Next Recommended Phases

- Add a P15 model-family expansion trial using the P8-P10 ticket families.
- Add a P16 command-surface stabilization pass if the local scripts keep being
  reused.
- Revisit packaging only after repeated model-family evidence exists.

