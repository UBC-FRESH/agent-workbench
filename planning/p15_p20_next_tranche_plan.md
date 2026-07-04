# P15-P20 Next-Tranche Plan

## Basis

P9-P14 established a useful but still narrow evidence base:

- SDK/Ollama repeated trials are reliable for no-tool marker, structured output,
  and patch-proposal tasks.
- `qwen3-coder-next:latest` outperformed `qwen3-coder:latest` on the stricter
  patch-proposal format in the small P10 sample.
- The supervisor-applied patch path can safely apply a narrow add-only patch
  inside an ignored sandbox.
- VS Code Chat can perform a tiny restricted ignored-file mutation with
  observable tool evidence.
- Worker-prepared GitHub text still requires supervisor review and mutation.
- Packaging should wait until command surfaces and model-family evidence
  stabilize.

## Sequencing Principle

The next tranche should broaden evidence before broadening authority.

The order is:

1. Expand the model matrix across configured models.
2. Stabilize local command surfaces that are already being reused.
3. Normalize ignored evidence and summaries.
4. Run richer restricted tool trials only in sandboxes.
5. Write a trust/delegation policy from observed evidence.
6. Revisit packaging with stable interfaces and broader data.

## Planned Phases

### P15: Model-Family Expansion Trial

Run P8-P10 ticket families across selected configured models beyond the qwen
pair. Use small repeats and the same ignored evidence protocol.

Recommended initial model set:

- `qwen3-coder-next:latest`
- `devstral-2:latest`
- `devstral-small-2:latest`
- `gpt-oss:20b`
- `codestral:latest`
- `deepseek-coder-v2:16b`

Keep very large models optional until latency and stability are characterized.

### P16: Command Surface Stabilization

Review and stabilize local script command contracts. Add shared manifest fields,
consistent redaction, consistent report metadata, and a small smoke-test suite
without turning the repo into a package yet.

### P17: Evidence Store And Summary Schema

Define a normalized ignored evidence layout and sanitized summary schema for
model runs, bridge runs, patch trials, and GitHub microtasks.

### P18: Richer Restricted Tool Trial

Run a slightly richer tool-enabled sandbox trial that involves one read, one
allowed ignored-file mutation, and one supervisor verification report. Keep
tracked files and GitHub mutations out of worker control.

### P19: Delegation Policy And Trust Levels

Convert observed evidence into a written delegation policy. Define what workers
may do unaided, what requires supervisor application, and what remains
supervisor-only.

### P20: Packaging Revisit And Interface Decision

Revisit packaging and interface options using P15-P19 evidence. Decide whether
to stay scripts/Markdown or introduce a package/CLI, VS Code extension, MCP
server, or hosted-agent surface.

## Guardrails

- Use configured Ollama models only unless a phase explicitly installs and
  verifies new models.
- Keep endpoint, headers, raw transcripts, raw results, and sandbox targets
  ignored.
- Do not increase worker authority and model breadth in the same phase.
- Do not package unstable command surfaces.
- Treat supervisor-owned GitHub closure and PR merge as nondelegable unless a
  future phase produces strong contrary evidence.

