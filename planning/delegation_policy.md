# Delegation Policy And Trust Levels

This policy defines how Agent Workbench supervisors may delegate work to worker
agents. It is based on evidence from P8-P18 and should stay conservative until
future phases produce stronger verification and rollback evidence.

## Trust Levels

| Level | Name | Worker Authority | Current Status |
| --- | --- | --- | --- |
| L0 | No-tool response | Return exact marker or bounded structured text. | Allowed with supervisor verification. |
| L1 | Proposal-only work | Produce plans, summaries, comments, or patch proposals without mutation. | Allowed with parser/rubric checks. |
| L2 | Supervisor-applied mutation | Worker proposes a bounded change; supervisor tooling applies it to an allowed sandbox. | Allowed for ignored sandbox targets. |
| L3 | Restricted sandbox tool use | Worker may use approved tools on explicitly allowed ignored runtime paths. | Allowed for narrow trials only. |
| L4 | Tracked-file mutation | Worker edits tracked repository files directly. | Not allowed. |
| L5 | GitHub mutation | Worker performs issue comments, edits, closure, PR creation, or PR merge. | Not allowed by default. |
| L6 | Release or closeout authority | Worker merges PRs, closes parent phases, cuts releases, or declares final workflow completion. | Nondelegable. |

## Ticket Family Mapping

| Ticket Family | Maximum Level | Notes |
| --- | ---: | --- |
| marker-only SDK probe | L0 | Useful for basic loop/stop behavior. |
| structured documentation output | L1 | Requires section and forbidden-phrase checks. |
| patch proposal | L1 | Proposal only; no worker mutation. |
| supervisor-applied patch | L2 | Supervisor script applies only to ignored sandbox targets. |
| restricted VS Code Chat sandbox write | L3 | Allowed only for ignored runtime paths with observed tool evidence. |
| GitHub comment preparation | L1 | Worker may draft text; supervisor posts after review. |
| GitHub issue closure or PR merge | L6 | Supervisor-only. |

## Nondelegable Actions

The supervisor must retain authority for:

- editing tracked repository files unless a future phase explicitly permits a
  narrower exception;
- committing changes;
- pushing branches;
- creating PRs;
- merging PRs;
- closing parent phase issues;
- closing child issues unless explicitly performing supervisor closeout;
- posting GitHub comments that claim verified completion;
- publishing releases;
- changing model/provider configuration; and
- expanding a worker's tool or file authority.

## Escalation Rules

Escalate to supervisor review when:

- a worker uses a tool outside the ticket boundary;
- a required section, marker, command, or output file is missing;
- a worker claims an action happened but evidence is missing;
- a worker loops, repeats completion prose, or keeps responding after a stop
  condition;
- a worker attempts tracked-file or GitHub mutation; or
- the ticket requires interpreting ambiguous repository workflow state.

## Current Governance Decision

Agent Workbench currently permits L0-L1 work broadly, L2 work only through
supervisor-owned scripts and ignored sandbox targets, and L3 work only for
explicitly bounded VS Code Chat sandbox trials. L4-L6 remain forbidden for
worker agents.

## Managed Loop Policy V0

The managed-loop policy is recorded in
`templates/delegation_loop_policy_v0.json` and
`templates/managed_iteration_stop_rules.json`.

Default rule: extraction, reporting, self-audit, and repair experiments start in
a no-tool L0/L1 lane unless the supervisor explicitly configures a restricted
tool lane. If an SDK or chat session emits a tool call during a no-tool run, the
run is confounded and should be stopped or reclassified rather than treated as a
clean no-tool comparison.

Required bailout rules:

- stop self-audit or repair when primary document/candidate identifiers are not
  preserved;
- stop self-audit when a calibration sample contains known repairable records
  and the local auditor misses them;
- stop or rewrite after repeated malformed JSON/JSONL;
- report missing evidence instead of estimating when token ledgers, source
  anchors, model identity, or worker output records are absent; and
- require a paid supervisor checkpoint before scaling a local-worker result
  beyond the calibrated task shape.

Promising current task lanes:

- sanitized reporting from already-validated experiment summaries;
- public technical-document structure/content extraction from bounded chunks;
- deterministic orchestration and scaffold generation by scripts; and
- restricted local-worker repair only after identifier preservation and
  calibration detection are proven.

Blocked or unproven current task lanes:

- broad high-level planning by local workers;
- local self-audit that lacks stable source/candidate IDs;
- repair loops driven by bad self-audit labels; and
- worker tool use without an explicit allowlist, permission policy, event log,
  and ignored runtime boundary.

## SDK Tool Boundary

The Copilot SDK path can expose tool-capable behavior, but Agent Workbench does
not treat tool access as the default worker authority. The no-tool SDK probe
passes `available_tools=[]`; that remains the default for economic and model
comparison benchmarks.

Restricted SDK tool use is a separate L3 lane. A valid L3 experiment must name
the allowed tools, allowed filesystem roots, permission-handler behavior,
expected tool-event evidence, and rollback or discard boundary before the worker
starts. Tool calls observed outside that lane are evidence of a confounded run,
not evidence that a no-tool delegation protocol succeeded.

## Missing Evidence Rules

Future benchmark reports may not claim delegation economics unless every
supervisor-owned subtask has measured start/end supervisor-token checkpoints.
They may not claim model comparison evidence unless worker input/output token
counts, model identity, and parseability status are recorded. They may not claim
source-level quality unless source chunks, page anchors, document IDs, and
source hashes are available to the supervisor audit.

## Policy Tuning Loop

Real-project pilots may update delegation guidance only through sanitized P35
accounting records and supervisor review.

Use:

```powershell
agent-workbench policy tune `
  --input-dir <pilot-runtime-dir> `
  --output <policy-tuning-report.md>
```

The first tuning loop is rules-based:

- maintain or promote task/model/protocol groups when repeated records are
  mostly promising, net savings are positive, and accepted claims exceed
  rejected claims;
- hold groups steady when evidence is sparse or mixed;
- lower trust when records are mostly poor, net savings are negative, or
  rejected claims exceed accepted claims;
- use one retry for sparse or mixed evidence;
- allow two retries only for positive groups with repeat evidence; and
- bail out after two poor outcomes for the same task/model/protocol group
  unless the supervisor rewrites the ticket or changes the model.

Machine-learning policy optimization is out of scope until the sanitized record
set is large, varied, and independently verifiable. The current threshold is at
least 100 records, 6 task types, and 3 model or project groups.

## Model Attribution Risk

Agent Workbench must never treat a `model:` frontmatter field in `.agent.md`
files as proof of actual model selection for non-paid agents (local/worker).
This is a known issue tracked at:
https://github.com/microsoft/vscode/issues/310138

**Rules:**

- For **paid Copilot agents** (advisor), the `model:` frontmatter is pinned by
  the native provider and reliably selects Claude Opus 4.8 / Claude Sonnet 4.5 /
  GPT-5 via the picker.
- For **local/self-hosted agents** (coordinator, supervisor, workers), `model:`
  frontmatter is documentation of intent only. Actual model selection is
  picker-dependent or must be enforced by out-of-band tooling
  (`scripts/ollama_worker_call.py`).
- **Do not accept** a worker's claim about which model produced its output based
  solely on the agent file frontmatter. Persisted session evidence (event logs,
  tool invocations, `ollama list` snapshots) must show the expected model before
  a result counts for model comparison or audit.
- **Do not treat** Copilot SDK provider/model configuration as proof of successful
  model execution either — captured event/output evidence must show the run
  reached its expected stop condition before it counts.
- **Do not assume** any local agent ran on the "intended" model from frontmatter.
  If model identity matters for a benchmark claim, verify it from persisted
  evidence, not inference.

This rule protects the ROI thesis and model comparison lane (P96+) from becoming
unverifiable: you cannot compare models if you do not independently know which
model produced each result.
