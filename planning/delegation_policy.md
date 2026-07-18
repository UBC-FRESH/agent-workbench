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
| L4 | Tracked-file mutation | Worker edits tracked repository files directly. | Allowed in productive-delegation mode, only within the ticket's allowed paths, under an explicit coordinator/developer-authorized implementation ticket. |
| L5 | GitHub mutation | Worker performs issue comments, edits, closure, PR creation, or PR merge. | Not allowed by default. |
| L6 | Release or closeout authority | Worker merges PRs, closes parent phases, cuts releases, or declares final workflow completion. | Nondelegable. |

## Ticket Family Mapping

| Ticket Family | Maximum Level | Notes |
| --- | ---: | --- |
| marker-only SDK probe | L0 | Useful for basic completion behavior. |
| structured documentation output | L1 | Requires section and forbidden-phrase checks. |
| patch proposal | L1 | Proposal only; no worker mutation. |
| supervisor-applied patch | L2 | Supervisor script applies only to ignored sandbox targets. |
| restricted VS Code Chat sandbox write | L3 | Allowed only for ignored runtime paths with observed tool evidence. |
| GitHub comment preparation | L1 | Worker may draft text; supervisor posts after review. |
| GitHub issue closure or PR merge | L6 | Supervisor-only. |

## Nondelegable Actions

The supervisor must retain authority for:

- editing tracked repository files outside an explicit productive-delegation
  ticket's allowed paths (see Productive-Delegation Mode);
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
- a worker loops, repeats completion prose, or keeps responding outside the
  declared task boundary;
- a worker attempts tracked-file or GitHub mutation; or
- the ticket requires interpreting ambiguous repository workflow state.

## Current Governance Decision

Agent Workbench permits L0-L1 work broadly, L2 work through supervisor-owned
scripts and ignored sandbox targets, and L3 work for explicitly bounded tool
trials.

### Productive-Delegation Mode (L4)

For real UBC-FRESH software, science, and engineering work, an explicit
implementation ticket authorized by the coordinator or developer may raise a
worker to **L4 (tracked-file mutation)**, subject to all of the following:

- the ticket names the exact allowed files or path globs, allowed commands, and
  task boundary;
- edits stay within those allowed paths; edits outside them are a boundary
  violation and must be reverted;
- the supervisor reviews the worker's diff and runs the ticket's validation
  gates before returning a compact packet; and
- L5 (GitHub mutation) and L6 (release/closeout) remain nondelegable and stay
  with the coordinator/developer.

Without such a ticket, workers default to L0-L1. Productive-delegation runs must
go through the tool-enabled `copilot-sdk` bridge, not the no-tool probe (see the
SDK Tool Boundary section).

## Managed Loop Policy V0

The managed-loop policy is recorded in
`templates/delegation_loop_policy_v0.json` and the recorded iteration evidence.

Default rule: extraction, reporting, self-audit, and repair experiments start in
a no-tool L0/L1 lane unless the supervisor explicitly configures a restricted
tool lane. If an SDK or chat session emits a tool call during a no-tool run, the
run is confounded and must be reclassified rather than treated as a clean
no-tool comparison.

Required evidence discipline:

- treat missing primary document/candidate identifiers as invalid evidence;
- treat a missed known calibration record as evidence that the audit route needs
  repair;
- use repeated malformed JSON/JSONL to diagnose the format or ticket route;
- report missing evidence instead of estimating when token ledgers, source
  anchors, model identity, or worker output records are absent; and
- record why a broader local-worker result is justified by the accumulated
  evidence.

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

Two distinct SDK paths exist and must not be confused:

- **No-tool evaluation probe** (`scripts/copilot_sdk_ollama_probe.py`) passes
  `available_tools=[]` by design. It is for economic and model-comparison
  benchmarks only. It cannot perform delegated work and must never be used as
  the delegation path.
- **Tool-enabled bridge** (`agent-workbench copilot-sdk` over
  `src/agent_workbench/copilot_sdk_bridge.py`) resolves `sdk.available_tools`,
  custom agent profiles, and Agent Workbench custom tools. Productive-delegation
  (L4) runs must use this path with `sdk.available_tools` set to a productive
  set and a worker-capable supervisor profile selected.

Restricted SDK tool use below L4 remains a bounded lane: a valid experiment must
name the allowed tools, allowed filesystem roots, permission-handler behavior,
expected tool-event evidence, and rollback or discard boundary before the worker
starts. Tool calls observed outside the declared lane are evidence of a
confounded run.

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
- choose another run only when it has a stated question and a different
  evidence-based rationale; and
- reassess task/model/protocol fit when outcomes repeat without changing the
  diagnosis or producing a useful decision signal.

Machine-learning policy optimization is out of scope until the sanitized record
set is large, varied, and independently verifiable. The current threshold is at
least 100 records, 6 task types, and 3 model or project groups.

## Remote Ollama Host (Workspace-Specific Note)

The configured Ollama server is accessed via the **VS Code Ollama extension**, not a local `localhost:11434` endpoint. This workspace has no local Ollama instance running.

**Rules for all P96+ model comparison work:**

- Do **not** attempt to curl `http://localhost:11434/api/tags` or run `ollama list` in this terminal session — these will fail.
- Model inventory must be verified by inspecting the **Copilot Chat provider dropdown → ollama models list** in VS Code (where the extension surfaces remote host models).
- Worker tasks that require model availability checks must instruct the worker to capture a text listing of available ollama models from the Copilot Chat picker, not from local CLI commands.
- Model installation (pull) is done through the VS Code Ollama extension context or via the configured remote host's own terminal/SSH session, never via `localhost:11434`.

This rule applies to all coordinator, supervisor, and worker agent tasks in phases P96 through P100.

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
  (the `agent-workbench copilot-sdk` bridge — see SDK Tool Boundary section).
- **Do not accept** a worker's claim about which model produced its output based
  solely on the agent file frontmatter. Persisted session evidence (event logs,
  tool invocations, `ollama list` snapshots) must show the expected model before
  a result counts for model comparison or audit.
- **Do not treat** Copilot SDK provider/model configuration as proof of successful
  model execution either — captured event/output evidence must show the expected
  terminal result before it counts.
- **Do not assume** any local agent ran on the "intended" model from frontmatter.
  If model identity matters for a benchmark claim, verify it from persisted
  evidence, not inference.

This rule protects the ROI thesis and model comparison lane (P96+) from becoming
unverifiable: you cannot compare models if you do not independently know which
model produced each result.
