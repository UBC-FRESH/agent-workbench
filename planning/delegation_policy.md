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
