# Ollama Worker Model Install Shortlist

## Purpose

This note records candidate Ollama models to install on the configured
Ollama/GPU worker host before the worker-model evaluation phase.

The intent is to create a small comparison panel for supervised coding-agent
workflows. It is not a complete model zoo, and it does not publish private host
details, endpoints, credentials, or workstation paths.

## Selection Rules

- Use models available from the Ollama library.
- Verify installation with `ollama list` on the worker host before assigning a
  model to a worker ticket.
- Prefer models with coding, tool-use, agentic workflow, or long-context
  claims.
- Include a mix of large-capability candidates and smaller fast baselines.
- Treat model installation as setup work; model performance still needs local
  evidence from bounded Agent Workbench tasks.

## Install First

```bash
ollama pull qwen3-coder-next:latest
ollama pull gpt-oss:120b
ollama pull devstral:24b
ollama pull deepseek-coder-v2:16b
ollama pull codestral:latest
```

### `qwen3-coder-next:latest`

Primary challenger to the current `qwen3-coder:latest` baseline.

Rationale:

- coding-focused model from the Qwen family;
- designed for agentic coding workflows and local development;
- reported as an 80B MoE model with 3B active parameters;
- reported 256K context window;
- useful for testing whether the current qwen behavior improves with the newer
  coding model.

### `gpt-oss:120b`

Large reasoning and agentic-task baseline.

Rationale:

- open-weight model available through Ollama;
- reported 120B class model with 128K context;
- useful as a high-capability non-Qwen comparison point;
- expected to fit the configured high-VRAM worker host better than ordinary
  consumer hardware.

### `devstral:24b`

Fast agentic software-engineering candidate.

Rationale:

- explicitly positioned for software-engineering agents;
- intended for tool use, codebase exploration, and multi-file editing;
- reported 128K context window;
- small enough to be a practical fast worker model.

### `deepseek-coder-v2:16b`

Coding-specialist baseline.

Rationale:

- code-focused MoE model;
- useful as an older but still relevant coding-agent comparison;
- likely to be faster and cheaper to run than the largest candidates;
- good candidate for distinguishing raw coding skill from workflow discipline.

### `codestral:latest`

Compact code-generation baseline.

Rationale:

- Mistral code model;
- reported 22B class model with 32K context;
- useful as a fast baseline for simple bounded tickets;
- helps answer whether smaller code models follow strict tickets better or
  worse than larger agentic models.

## Install Second

```bash
ollama pull gpt-oss:20b
ollama pull devstral-small-2
ollama pull gemma4:31b
```

### `gpt-oss:20b`

Small reasoning baseline.

Rationale:

- reported 20B class model with 128K context;
- useful for speed comparisons against `gpt-oss:120b`;
- may be strong enough for narrow worker tickets.

### `devstral-small-2`

Second Devstral-family software-engineering candidate.

Rationale:

- positioned for agentic software-engineering workflows;
- useful for comparing Devstral variants before relying on either one;
- should be tested on command discipline and evidence reporting, not only code
  quality.

### `gemma4:31b`

General reasoning and agentic-workflow comparison point.

Rationale:

- reported as suitable for reasoning, coding, and agentic workflows;
- useful as a non-Qwen, non-Mistral, non-OpenAI comparison model;
- install after the more coding-specific panel is in place.

## Stretch Candidates

```bash
ollama pull llama4:latest
ollama pull devstral-2
```

### `llama4:latest`

Long-context general model candidate.

Rationale:

- reported large context window;
- may be useful for repository comprehension experiments;
- not the first choice for strict coding-agent workflow tests because it is not
  primarily a coding model.

### `devstral-2`

Large Devstral-family agentic engineering candidate.

Rationale:

- relevant if local installation and runtime behavior are practical;
- should be treated as a later high-capability candidate after the smaller
  Devstral baseline is installed and tested.

## Skip For Now

```bash
# ollama pull qwen3-coder:480b
```

Rationale:

- local `qwen3-coder:480b` is outside the practical memory target for the
  configured 96 GB VRAM worker host;
- it can be revisited only if a larger memory/unified-memory host becomes
  available or if a cloud-backed route is explicitly accepted.

## Post-Install Verification

After installation, run:

```bash
ollama list
```

Record the installed model tags exactly. Worker tickets should use only tags
that appear in the live `ollama list` inventory for the active worker host.

## Current P4 Inventory Snapshot

The following installed-model inventory was provided by the maintainer after
installing `qwen3-coder-next:latest` for Phase 4.

| Model tag | Model ID | Size | P4 role |
| --- | --- | --- | --- |
| `qwen3-coder-next:latest` | `ca06e9e4087c` | 51 GB | Primary A/B candidate. |
| `qwen3-coder:latest` | `06c1097efce0` | 18 GB | Existing baseline. |
| `llama3.1:latest` | `46e0c10c039e` | 4.9 GB | General fallback baseline. |
| `starcoder2:latest` | `9f4ae0aff61e` | 1.7 GB | Small code-model fallback baseline. |
| `nomic-embed-text:latest` | `0a109f422b47` | 274 MB | Embedding model; not a chat worker. |

For the evaluation phase, each model run should record:

- exact model tag;
- timestamp;
- task marker;
- permission mode;
- ticket path;
- supervisor report path;
- whether the session was visible in VS Code Chat;
- whether the bridge found persisted session evidence;
- whether the worker followed command and file boundaries; and
- final supervisor decision.
