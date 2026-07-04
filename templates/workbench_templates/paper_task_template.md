# Paper Task Workbench Envelope

## Task Identity

- project or manuscript:
- research question:
- artifact family:
- supervisor owner:

## Role And Capability

- role:
- capability:
- implementation candidates:
  - human researcher:
  - local worker for outline/proposal only:
  - project-native analysis script:
  - notebook or Quarto document:

## Graph Envelope

| Node | Provider | Needs | Role | Capability | Implementation |
| --- | --- | --- | --- | --- | --- |
| select_question | supervisor.task_selection |  | supervisor | research question selection | human researcher |
| organize_evidence | agent_workbench.local_worker | select_question | analyst | evidence organization | local worker or paid supervisor |
| run_analysis | notebook_or_project_script | organize_evidence | analyst | project-native analysis | notebook, Quarto, or script |
| review_claims | supervisor.claim_review | organize_evidence, run_analysis | supervisor | scientific claim review | human supervisor |
| promote_outline | supervisor.promotion | review_claims | editor | promotion decision | human supervisor |

## Source Artifacts

| Artifact | Kind | Path Or Reference | Provenance | Public-Safety Note |
| --- | --- | --- | --- | --- |
| evidence summary | source |  |  |  |
| analysis output | source |  |  |  |

## Project-Native Execution

Use notebooks, Quarto, project analysis scripts, or existing report commands for
analysis and rendering. Agent Workbench may record the command and evidence but
does not become the analysis engine.

## Generated Artifacts

| Artifact | Kind | Path Or Reference | Verifier | Supervisor Decision |
| --- | --- | --- | --- | --- |
| outline draft | generated |  |  |  |
| promoted outline | promoted |  |  |  |
| unsupported claims | rejected |  |  |  |

## Claim Review

- accepted scientific claims:
- rejected claims:
- needs-evidence claims:
- required human/domain review:

## Token/Cash Accounting

- direct supervisor estimate:
- delegated outline/review tokens:
- cleanup tokens:
- net value judgment:

## Promotion Gate

- [ ] Scientific claims are evidence-supported.
- [ ] Domain interpretation was reviewed by a human supervisor.
- [ ] Generated prose is edited before promotion.
- [ ] Raw transcripts remain ignored.
