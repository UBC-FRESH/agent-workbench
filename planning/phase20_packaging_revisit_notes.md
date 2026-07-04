# Phase 20 Packaging Revisit Notes

Phase 20 revisits interface direction using evidence from P15-P19.

## Evidence Review

P15 showed that the SDK/Ollama harness can compare multiple configured worker
models across stable ticket families. The patch-proposal ticket family remains
the most useful small discriminator.

P16 stabilized command surfaces enough to smoke-check reusable scripts and dry
run the SDK harness without contacting a model provider.

P17 defined a raw-evidence and sanitized-summary boundary, which gives future
tooling a field contract without committing raw transcripts or private provider
details.

P18 confirmed that a read-plus-write VS Code Chat tool trial can be bounded and
verified in ignored runtime paths, but it did not justify tracked-file mutation.

P19 converted those observations into trust levels and kept tracked-file
mutation, GitHub mutation, issue closure, PR merge, release, and closeout
authority supervisor-only.

## Interface Options

| Option | P20 Decision | Reason |
| --- | --- | --- |
| Markdown plus scripts only | Retire as the only surface after P20 | Useful so far, but command discovery is becoming repetitive. |
| Local package and CLI | Start a narrow P21 spike | Command surfaces and evidence schema are stable enough for a small wrapper. |
| VS Code extension | Defer | Chat control, model selection, and response capture are still not robust enough. |
| MCP server | Defer | Worker tool authority remains conservative and local-first. |
| Hosted agent | Defer | The workbench is still focused on local Ollama/GPU worker experiments. |
| Dashboard or benchmark harness | Defer | Evidence summaries need validation before visualization. |

## Decision

Accept ADR 0002: begin a narrow local Python package and CLI spike in P21. The
first slice should wrap supervisor-side local commands without changing worker
authority.

## Next-Tranche Direction

The next tranche should implement packaging one boundary at a time:

- P21: minimal local package and CLI skeleton;
- P22: CLI wrapper for SDK same-ticket evaluation and command smoke checks;
- P23: evidence-summary validation/rendering;
- P24: CLI dogfood on one full no-tool evaluation workflow.

VS Code extension, MCP, hosted agent, and dashboard work remain deferred.
