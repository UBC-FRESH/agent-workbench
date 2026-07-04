# Benchmark Task Workbench Envelope

## Task Identity

- benchmark family:
- model candidates:
- ticket family:
- supervisor owner:

## Role And Capability

- role:
- capability:
- implementation candidates:
  - local worker model:
  - comparison script:
  - human reviewer:

## Graph Envelope

| Node | Provider | Needs | Role | Capability | Implementation |
| --- | --- | --- | --- | --- | --- |
| define_ticket | supervisor.task_selection |  | supervisor | benchmark design | human supervisor |
| run_worker_a | agent_workbench.eval | define_ticket | worker | model response | local model A |
| run_worker_b | agent_workbench.eval | define_ticket | worker | model response | local model B |
| compare_outputs | agent_workbench.compare | run_worker_a, run_worker_b | analyst | comparison | comparison script |
| update_profile | supervisor.promotion | compare_outputs | supervisor | model profile update | human supervisor |

## Source Artifacts

| Artifact | Kind | Path Or Reference | Provenance | Public-Safety Note |
| --- | --- | --- | --- | --- |
| worker ticket | source |  |  |  |
| expected output rubric | source |  |  |  |

## Execution Surface

Use existing Agent Workbench evaluation and comparison commands only for
benchmark harnessing:

- `agent-workbench eval`
- `agent-workbench compare eval`
- `agent-workbench evidence validate`
- `agent-workbench accounting synthesize`
- `agent-workbench policy tune`

For target-project tasks, project-native tools remain authoritative.

## Generated Artifacts

| Artifact | Kind | Path Or Reference | Verifier | Supervisor Decision |
| --- | --- | --- | --- | --- |
| model output | generated |  |  |  |
| comparison report | generated |  |  |  |
| model profile update | promoted |  |  |  |

## Evaluation

- repeats:
- pass/fail criteria:
- claim quality:
- loop/refusal behavior:
- consistency:
- supervisor cleanup cost:

## Token/Cash Accounting

- worker tokens:
- supervisor review tokens:
- direct-work counterfactual:
- expected savings:

## Promotion Gate

- [ ] Results are scoped to the tested task family.
- [ ] Model profile updates cite concrete evidence.
- [ ] Broad model rankings are avoided.
- [ ] Raw outputs remain ignored.
