# Proposal Task Workbench Envelope

## Task Identity

- proposal or planning target:
- decision needed:
- deadline or planning horizon:
- supervisor owner:

## Role And Capability

- role:
- capability:
- implementation candidates:
  - local worker for option generation:
  - paid supervisor for synthesis:
  - human principal investigator:
  - project-native reporting command:

## Graph Envelope

| Node | Provider | Needs | Role | Capability | Implementation |
| --- | --- | --- | --- | --- | --- |
| frame_decision | supervisor.task_selection |  | supervisor | decision framing | human supervisor |
| gather_options | agent_workbench.local_worker | frame_decision | analyst | option generation | local worker |
| gather_project_evidence | freshforge_or_project_cli | frame_decision | analyst | evidence report | FreshForge or project-native report |
| synthesize_decision | supervisor.synthesis | gather_options, gather_project_evidence | supervisor | decision synthesis | human or paid supervisor |
| promote_memo | supervisor.promotion | synthesize_decision | supervisor | promotion decision | human supervisor |

## Source Artifacts

| Artifact | Kind | Path Or Reference | Provenance | Public-Safety Note |
| --- | --- | --- | --- | --- |
| roadmap excerpt | source |  |  |  |
| evidence packet | source |  |  |  |

## Generated Artifacts

| Artifact | Kind | Path Or Reference | Verifier | Supervisor Decision |
| --- | --- | --- | --- | --- |
| option list | generated |  |  |  |
| decision memo | promoted |  |  |  |
| unsupported assumptions | rejected |  |  |  |

## Project-Native Execution

Use existing project reports, FreshForge summaries, notebooks, or analysis
scripts as authoritative evidence. Agent Workbench organizes the decision
packet and accounting trail.

## Decision Packet

- options considered:
- evidence used:
- accepted claims:
- rejected claims:
- unresolved questions:
- recommended decision:

## Token/Cash Accounting

- direct supervisor estimate:
- delegated evidence intake tokens:
- synthesis tokens:
- cleanup tokens:
- decision value:

## Promotion Gate

- [ ] Recommendation is traceable to source artifacts.
- [ ] Open assumptions are listed.
- [ ] Project-native evidence was not replaced by generated prose.
- [ ] Supervisor owns the final decision.
