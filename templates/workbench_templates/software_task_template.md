# Software Task Workbench Envelope

## Task Identity

- project:
- governing issue or roadmap task:
- task type:
- risk:
- critical path position:
- supervisor owner:

## Role And Capability

- role:
- capability:
- allowed authority:
- implementation candidates:
  - FreshForge or project-native CLI:
  - local worker:
  - paid supervisor:
  - human maintainer:

## Graph Envelope

| Node | Provider | Needs | Role | Capability | Implementation |
| --- | --- | --- | --- | --- | --- |
| select_task | supervisor.task_selection |  | supervisor | task selection | human supervisor |
| worker_proposal | agent_workbench.local_worker | select_task | reviewer/programmer | evidence intake or patch proposal | local worker model |
| project_native_verification | freshforge_or_project_cli | worker_proposal | programmer | verification | FreshForge or project-native CLI |
| supervisor_promotion | supervisor.promotion | worker_proposal, project_native_verification | supervisor | promotion decision | human or paid supervisor |

Use `templates/workbench_templates/agentic_graph_envelope.json` when a
machine-readable graph record is useful.

## Source Artifacts

| Artifact | Kind | Path Or Reference | Provenance | Public-Safety Note |
| --- | --- | --- | --- | --- |
|  | source |  |  |  |

## Worker Ticket

- ticket path:
- model:
- protocol:
- stop conditions:
- forbidden authority:

## Project-Native Execution

Use the target project's existing execution surface. Examples:

- `python -m pytest`
- `python -m build`
- `twine check dist/*`
- `sphinx-build -b html docs _build/html -W`
- FreshForge or project-specific CLI commands

Agent Workbench records these commands and outputs; it does not replace them.

## Generated Artifacts

| Artifact | Kind | Path Or Reference | Verifier | Supervisor Decision |
| --- | --- | --- | --- | --- |
| worker proposal | generated |  |  |  |
| accepted patch/docs/tests | promoted |  |  |  |
| rejected claims | rejected |  |  |  |

## Evidence And Claim Review

- evidence summary:
- decision packet:
- accepted claims:
- rejected claims:
- needs-evidence claims:

## Token/Cash Accounting

- accounting record:
- direct supervisor estimate:
- delegated supervisor tokens:
- worker tokens:
- verification tokens:
- cleanup/retry tokens:
- net savings estimate:

## Promotion Gate

- [ ] Accepted claims are source-supported.
- [ ] Project-native checks passed.
- [ ] Raw worker outputs remain ignored.
- [ ] GitHub mutation remains supervisor-owned.
- [ ] Tracked changes are public-safe.
