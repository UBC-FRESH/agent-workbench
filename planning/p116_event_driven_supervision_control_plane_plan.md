# P116 Event-Driven Supervision Control Plane Plan

## Decision

P116 is a planned, narrow control-plane repair for the Agent Hub. It gives the
Coordinator and Supervisor the evidence path and repeatable invocation path
needed to supervise an already-running Worker. It is not a new model route,
tool bridge, or attempt to force deterministic Worker behavior.

The triggering evidence is the July 18 P107/P114 Qwen coding run: the Worker
was active and making tool-assisted repairs, but the native lifecycle interface
only exposed terminal state and the chat Supervisor stopped executing after it
returned. The Coordinator had the Worker/session evidence and message channel;
the Supervisor did not have a durable evidence cursor or controller that could
ask it to assess each new delta.

The desired operating pattern is ordinary agent repair: a Worker receives
clear tool feedback, attempts a repair, validates, and continues. Supervision
should distinguish productive repair from a material repeat, directive
deviation, or real block, then deliver a concise, evidence-based cue through
the Coordinator when that can help. It must not fabricate a deterministic
pass/fail test around normal model variation.

## Scope and role contract

| Role | Owns | Does not own |
| --- | --- | --- |
| Coordinator | binds run/session paths and identities; starts/stops the local controller; re-invokes the Supervisor; sends approved input to the same Worker; validates/accepts outcome | interpreting raw deltas as the Supervisor, Worker implementation |
| Supervisor | reads the new sanitized evidence delta; identifies current stage, accepted actions, error/repeat pattern, and recommended nudge or escalation | tools, file edits, Worker messaging, result acceptance |
| Worker | performs the bounded ticket using its declared tools and reacts to normal tool feedback | controller lifecycle, supervision policy, acceptance |
| Advisor | independent review of material design/closeout decisions | routine monitoring or run control |

P116 retains direct Coordinator fan-out. It does not require nested spawning.

## Public-safe artifact contract

For each run, ignored local artifacts live under:

```text
runtime/agent_jobs/<run_id>/supervision/
  manifest.json
  events.jsonl
  cursor.json
  supervisor_packets.jsonl
  coordinator_actions.jsonl
  controller.log
```

`manifest.json` binds the run ID, Worker session ID, Supervisor session ID,
ticket digest, literal workspace root, permitted event source, and artifact
paths. It must not contain provider headers or credentials.

Each event carries only: monotonically increasing sequence, timestamp, source
cursor, event kind, tool/stage label, bounded outcome class, exit/status code,
redacted error fingerprint, allowed-path classification, and a bounded
correlation ID. It excludes raw tool arguments, raw output, environment values,
file contents, and paths outside the declared root. The schema includes a
version and an explicit `redaction_applied` field.

Each Supervisor packet names the input cursor range, observed stage, evidence
summary, classification (`productive_repair`, `material_repeat`,
`directive_deviation`, `blocked`, or `terminal`), confidence, recommended
Coordinator action, and an optional concise nudge. It cannot carry a command
to execute directly.

Each Coordinator action records the packet hash, decision, actual message
delivery identifier if any, and post-action cursor. It is the audit bridge
between a recommendation and a Worker message.

## Implementation tasks

### P116.1 - Freeze contracts

- Specify JSON schemas, versioning, root containment, size limits, redaction,
  cursor semantics, duplicate-event behavior, and restart recovery.
- Add deterministic fixtures for a successful tool action, normal repair,
  repeated error fingerprint, directive deviation, terminal result, and
  secret/path redaction.
- Define the minimum evidence needed before an intervention is proposed.

### P116.2 - Hook-to-event capture probe

- Run a local, no-provider probe to capture the actual Codex command-hook
  payload, hook ordering, failure behavior, and coexistence with existing
  hooks on Windows.
- Implement one command handler that validates and reduces that payload to the
  P116 event contract. It writes only within the run's ignored supervision
  directory.
- Fail closed on unknown payload shape, oversized payload, disallowed source,
  or failed redaction; record a bounded local error event instead of raw data.

The hook is a signal source, not an agent launcher. Command hooks cannot be
assumed to call a model. P116 therefore separates capture from controller
invocation.

### P116.3 - Coordinator event reducer/controller

- Implement a local Python controller that tails validated events and maintains
  an idempotent cursor/recovery record.
- Reduce events into a compact Supervisor input packet and write all decisions
  to the action log.
- Give the controller no provider credentials, filesystem authority outside the
  declared run root, or ability to execute Worker-provided commands.
- Test ordering, duplicate events, truncation/restart recovery, redaction,
  empty deltas, and terminal handling deterministically.

### P116.4 - Supervisor delta review

- Freeze a compact Supervisor prompt that says the Worker is expected to use
  feedback loops and must not be judged merely for an initial tool failure.
- Require citation of the new event cursor range and a structured
  classification/recommendation, not free-form passive status prose.
- Define constructive nudge style: state the observed fact, relevant tool
  feedback, next validation seam, and current ticket boundary. Never replace
  the ticket or prescribe ungranted authority.

### P116.5 - Re-invocation and same-Worker delivery feasibility

- Probe the supported local route that lets the Coordinator re-invoke the same
  Supervisor session/thread and submit one approved input to the same live
  Worker session.
- Record the exact API/controller boundary, session identifiers, lifecycle
  behavior, and unsupported cases. Do not promise autonomous wake-up before
  this probe succeeds.
- If native re-invocation is unavailable, retain event capture/controller work
  and make the next repair explicitly about the missing invocation surface.

### P116.6 - Native end-to-end proof

- Use one bounded real coding ticket with a declared worktree, allowed paths,
  validation command, Worker profile, Supervisor profile, and Coordinator
  session.
- Inspect raw Worker session evidence plus P116 events, Supervisor packets,
  Coordinator actions, target diff, validation output, and token boundary.
- Success is an observed evidence-to-recommendation-to-action loop with an
  appropriate post-action outcome. It is not contingent on the Worker never
  making an initial invalid call or completing a task in a fixed number of
  turns.

### P116.7 - P107 decision packet and closeout

- State separately whether P116 control-plane quality, protocol, and economics
  are supported.
- Decide whether P107 C4 may use the supervision control plane for a fresh
  measurement. No P107 economics claim transfers from P116.
- Synchronize roadmap, changelog, issue task checklist, tests, and PR evidence.

## Observability and intervention logic

The controller triggers a review from new evidence, not a fixed wall-clock
window alone. Useful triggers include a stage transition, a tool denial/error,
a validation result, a changed-file milestone, a terminal event, or a repeated
fingerprint without intervening progress. A quiet interval can prompt a
status review, but is not itself a conclusion that the Worker is stuck.

The Supervisor sees only the delta since its acknowledged cursor plus a compact
run summary. It may recommend `continue`, `nudge`, `escalate`, or `terminal`.
The Coordinator independently checks that recommendation against the ticket
and declared authority before sending anything. This preserves human/operator
control while making active supervision possible.

## Verification matrix

| Claim | Required evidence |
| --- | --- |
| Event contract works | deterministic schema/redaction/cursor tests |
| Hook capture works | inspected hook payload probe and sanitized event file |
| Controller works | deterministic reduction, idempotency, restart tests |
| Supervisor is active | raw Supervisor input/output cites the new cursor and returns a packet |
| Coordinator intervention works | action log plus same-Worker message-delivery evidence |
| End-to-end result is useful | raw Worker/session delta, target diff, validator, and post-action observation |
| Economics is usable | a separate accepted token/cash ledger at the P107 measurement boundary |

## Dependencies and decision boundaries

P114 is complete and remains the accepted capability route; P116 must not
replace or widen it. P107's baseline C4 route is admitted, but its economics
gate remains unassessed. P116 supplies a potential supervision control plane
for that later measurement only after P116's own native proof.

P115 stays planned and independent. It begins only under its stated gates; P116
does not authorize scientific artifact inspection.

## Advisor review incorporated

The independent Advisor review identified three concrete seams reflected in
this plan: lifecycle waiting lacks intermediate evidence, a chat Supervisor is
not persistent after it returns, and evidence/authority were split between the
Coordinator and Supervisor. The plan assigns a cursor-based evidence feed and
re-invocation loop to the Coordinator rather than asking the Worker to become
deterministic or the Supervisor to monitor without data.
