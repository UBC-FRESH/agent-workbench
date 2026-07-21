# P116 Event-Driven Supervision Control Plane Plan

## Decision

## Corrective status — resolved 2026-07-19

P116.1–P116.4 were reopened as local candidates because their earlier closure
overstated native and protocol evidence. The Copilot SDK is rejected as a P116
proof route. The fresh-root native proof and closeout decision below resolved
that reconciliation: bounded control-layer quality and protocol are supported;
economics remains unassessed.

P116 is a planned, narrow control-plane repair for the Agent Hub. Its required
execution architecture is frozen in
`planning/p116_controller_owned_runtime_design.md`. It gives the
Coordinator and Supervisor the evidence path and repeatable invocation path
needed to supervise an already-running Worker. It is not a new model route,
tool bridge, or attempt to force deterministic Worker behavior.

Native transport correction â€” 2026-07-19: a direct proof reused one live
native Luna Worker session and submitted `multi_agent_v1__send_input` with
`interrupt:true` while its shell action was active. The Worker received the
intervention and returned its marker before normal turn completion. This
supersedes the incorrect inference that native Codex lacks mid-turn re-entry.
The remaining P116 implementation seam is automated binding from validated
Worker events to that Coordinator-owned native tool call.

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

Status: complete. `agent_workbench.supervision` now defines the v1 manifest,
event, cursor, Supervisor-packet, and Coordinator-action validation surface.
Focused tests cover valid productive repair, root/path containment, ordered
cursors, forbidden raw payload fields, private-looking values, and structured
decisions.

- Specify JSON schemas, versioning, root containment, size limits, redaction,
  cursor semantics, duplicate-event behavior, and restart recovery.
- Add deterministic fixtures for a successful tool action, normal repair,
  repeated error fingerprint, directive deviation, terminal result, and
  secret/path redaction.
- Define the minimum evidence needed before an intervention is proposed.

### P116.2 - Hook-to-event capture probe

Status: complete with evidence-backed native hook firing. A trusted native
`codex_vscode` session at the exact P116 worktree executed `Get-Location`.
Captured run `p116_hook_vscode_r8` wrote a sanitized `PreToolUse` event with
`tool_name: Bash`, `root_match: true`, and an `event_written` receipt. The hook
path is `Bash` (the inner shell command), not the outer custom `exec` envelope.
Focused P116 tests pass and native hook dispatch evidence is observed. This is
not end-to-end supervision, automatic wake-up, Worker messaging, or native
P116.3/P116.4 proof; economics are unassessed and no P107 economics claim is
made.

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

Status: complete. `agent_workbench.supervision_controller` loads only validated
events, derives a compact unacknowledged-event delta, and atomically records a
review cursor. The companion script can render a delta and optionally
acknowledge it. It does not call a model, send a Worker message, or carry
provider credentials.

- Implement a local Python controller that tails validated events and maintains
  an idempotent cursor/recovery record.
- Reduce events into a compact Supervisor input packet and write all decisions
  to the action log.
- Give the controller no provider credentials, filesystem authority outside the
  declared run root, or ability to execute Worker-provided commands.
- Test ordering, duplicate events, truncation/restart recovery, redaction,
  empty deltas, and terminal handling deterministically.

### P116.4 - Supervisor delta review

Status: complete. `agent_workbench.supervision_review` renders and validates a
local advisory review request over one non-empty sanitized delta. It requires
an exact cursor citation, structured classification/recommendation/confidence,
and a bounded constructive nudge only where intervention is warranted. It does
not invoke a Supervisor, send a Worker message, or carry provider credentials.

- Freeze a compact Supervisor prompt that says the Worker is expected to use
  feedback loops and must not be judged merely for an initial tool failure.
- Require citation of the new event cursor range and a structured
  classification/recommendation, not free-form passive status prose.
- Define constructive nudge style: state the observed fact, relevant tool
  feedback, next validation seam, and current ticket boundary. Never replace
  the ticket or prescribe ungranted authority.

### P116.5 - Re-invocation and same-Worker delivery feasibility

Status: complete. The r8 native probe established the execution contract; the
fresh-root r3 run completed the qualifying same-Supervisor and same-Worker
cycle. These ignored evidence runs are not P107 runs or economics claims.

1. Start exactly one native Luna Worker and one native Luna Supervisor from a
   fresh root Coordinator session with `fork_context:false`; record their exact
   native IDs.
2. Bind both IDs to the inactive run manifest before the Worker uses a tool.
3. Have the bound Worker perform one harmless live shell action that produces a
   validated meaningful event while the Worker remains addressable.
4. Give that sanitized delta to the same Supervisor through native
   `send_input`; require a cursor-citing recommendation packet.
5. Record the Coordinator's explicit approval decision, then—only for an
   approved nudge—use native `send_input` to deliver one bounded message to
   that same Worker ID.
6. Inspect raw Worker and Supervisor session evidence plus the event, packet,
   action, delivery submission, and post-action Worker acknowledgement; then
   restore the temporary hook/MCP transaction.

The proof is accepted only when the Supervisor ID is identical at spawn and
re-invocation; the Worker ID is identical at binding and delivery; the packet
cites the new cursor; the action log binds the packet, approval, IDs, and
delivery submission; and the Worker session shows the intervention took
effect. Missing evidence is an incomplete P116.5 result with the exact absent
field. Copilot SDK and app-server material are diagnostic only and cannot
substitute for this native proof.

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

### P116.7 decision record - 2026-07-19

The fresh-root native run `p116_native_coding_r3_20260719` is the qualifying
P116.6 evidence. The Coordinator staged the run-scoped MCP and hook settings
before launching a fresh native `codex exec` controller. That controller bound
Worker `019f7e0f-a3e0-7182-b83f-a26d0e90350e` and Supervisor
`019f7e0f-a687-70b2-b9fe-21dd9a183910` before Worker tool use. The Supervisor's
native tool inventory exposed the run-scoped P116 MCP tool, directly received
the ordered root-matched `events:1-3` delta, and recommended a bounded repair.
The Coordinator validated the `events:1-3` packet, recorded the packet hash and
delivery submission, and sent the bounded cue to that same Worker. The Worker
repaired malformed `--repair-errors` JSON handling and the focused test passed.
The run transaction restored the temporary settings afterward.

- Quality: supported for the bounded control layer. The Worker repair and the
  deterministic focused P116 suite passed; the exact r3 task command passed
  after the cue.
- Protocol: supported for the bounded fresh-controller route. Raw native
  sessions, manifest binding, ordered event delta, Supervisor tool invocation,
  packet, cursor, action, same-Worker delivery, and restore receipts agree.
- Economics: unassessed. P116 captured no accepted P107-boundary token or cash
  ledger, so it makes no economics-usable claim.

Decision: P107 C4 may use the P116 control plane in a fresh measurement only
when its run-scoped MCP/hook configuration is staged before the native
Coordinator starts, and when it captures its own token/cash ledger. The prior
same-process r2 missing-tool observation is explained by cached controller
state and is not evidence that the staged MCP registration is unavailable.

## VS Code in-session deployment follow-up — 2026-07-19

The native control layer is also available to the active VS Code Codex
Coordinator session, not only to the historical fresh-controller proof route.
The Coordinator itself spawns one Worker and one advisory Supervisor, binds
their native session IDs with `supervision_start_run`, receives sanitized
progress through `supervision_wait_delta`, optionally re-invokes the same
Supervisor, and uses its own `send_input` to steer that same Worker when the
Coordinator approves a cue. No SDK, app-server, external controller, or daemon
is part of this route.

The initial in-session run exposed one implementation defect: hook capture
projected successful native tools as `tool_completed`, while the broker treated
that class as permanently routine and waited until timeout. The repair makes a
new sanitized `tool_completed` delta wake the in-session Coordinator for
review. A fresh VS Code native run then bound Worker
`019f7e37-cba9-7e21-8510-efa9345e1965` and Supervisor
`019f7e37-e02a-7601-96f8-d37c0960732f`; `supervision_wait_delta` returned one
root-matched Worker event in 0.83 seconds before terminal completion. The
Coordinator correctly left the advisory Supervisor idle for ordinary productive
progress, and the Worker added a bounded workflow-package CLI regression test
with 20 focused tests passing.

- Quality: the broker regression suite and the bounded workflow-package test
  passed.
- Protocol: the native in-session bind, live delta, bounded Worker execution,
  and run closure were observed. A Supervisor consultation and same-Worker cue
  remain conditional actions, not mandatory for productive progress.
- Economics: unassessed. Neither this deployment follow-up nor P116 supplies a
  P107 measurement ledger.

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

## P116.8 diagnostic-envelope refinement — active

The live VS Code run `p116_ui_870087267e6f48e1` proved that the in-session
control loop can deliver incremental acknowledged deltas, re-invoke the same
Supervisor, record Coordinator decisions, and send a bounded same-Worker cue.
It also exposed a productive-control limit: a failed declared test was visible
only as `shell_command`, exit code `1`, and `nonzero_exit`. That is enough to
stop blind retries, but not enough to distinguish a syntax error from a failed
assertion or missing input without disclosing raw command/output material.

An independent native Sol Advisor reviewed the proposed remedy and returned
`REVISE`: retain the narrow direction but exclude raw-output fingerprints and
observed paths. P116.8 therefore introduces a new event v2 under an immutable
pre-tool policy, rather than silently widening v1.

The v2 event may contain only:

- `policy_id`: opaque identifier for the frozen run policy;
- `operation_class`: `inspect`, `edit`, `test`, `agent_manage`, or `unknown`;
- `scope_status`: `within_ticket`, `outside_ticket`, or `unclassified`;
- optional declared `check_id`, only after an exact versioned normalized-command
  digest match;
- bounded `failure_class`, defaulting to `unknown`; and
- optional correlated `exit_code`.

It must never emit command text/arguments, stderr, matched substrings, raw
output digests, source text, credentials, undeclared paths, or parser captures.
Missing, duplicate, reordered, or ambiguous `call_id` correlation, policy
binding, command matching, or patch-path containment fails closed to
`unknown`/`unclassified`; it grants no authority to retry, edit, message, or
accept a result. Existing v1 events remain readable through an explicit
compatibility path.

P116.8 acceptance requires deterministic policy/correlation/redaction tests
and one fresh native run with exactly one Worker and the same Supervisor,
`fork_context:false`, policy bound before Worker tool use, a recognized declared
check failure, an unclassified undeclared command and patch, exactly-once
acknowledgement, and no excluded raw material in the event/packet/action
artifacts. Quality and protocol remain unaccepted until that evidence exists;
economics is not assessed.

### P116.8 result — 2026-07-20

Implementation added immutable v2 policy binding at native in-session run
start, `call_id` correlation across incremental tails, v1 compatibility, and
safe event projection. Focused P116/P114 validation passed with 72 tests.

Fresh native run `p116_v2_diagnostic_native_20260720` bound Worker
`019f8072-d0b5-7750-9c42-d6af5e1bd9d9` and same Supervisor
`019f8072-e6f0-7c61-b5c3-87acae05d46d` before Worker tool use. Its immutable
policy declared only one normalized missing-test command. The resulting v2
event contained `check_id: controlled-missing-test`, `operation_class: test`,
`scope_status: within_ticket`, `exit_code: 1`, and
`failure_class: missing_file`, with no command/output/path leakage. The same
Supervisor recommended terminal closure; the Coordinator recorded/acknowledged
that terminal decision and closed the run. The Worker's initial no-tool status
response was corrected once by the Coordinator, then the declared check ran.

- Quality: supported for the bounded v2 classification, compatibility, and
  redaction contract.
- Protocol: supported for the bounded native declared-failure detection and
  same-Supervisor terminal-review cycle. This is not a demonstrated automatic
  repair of an arbitrary implementation failure.
- Economics: unassessed. No P107 accounting boundary was used.

## Advisor review incorporated

The independent Advisor review identified three concrete seams reflected in
this plan: lifecycle waiting lacks intermediate evidence, a chat Supervisor is
not persistent after it returns, and evidence/authority were split between the
Coordinator and Supervisor. The plan assigns a cursor-based evidence feed and
re-invocation loop to the Coordinator rather than asking the Worker to become
deterministic or the Supervisor to monitor without data.

## Closeout — 2026-07-21

P116 is complete as a bounded native control layer. The accepted implementation
supports run binding, safe event reduction, same-Supervisor review, and a
Coordinator-approved same-Worker cue when observed evidence warrants one.
P116.8 added the final versioned diagnostic envelope without raw command,
output, source, credential, or arbitrary-path leakage.

- Quality: supported for the bounded control-layer implementation and focused
  regression suite.
- Protocol: supported for the native fresh-controller and VS Code in-session
  routes evidenced in this plan.
- Economics: intentionally not a P116 result; P107/P118 runs must capture
  their own role-bound ledgers.

This does not claim an unattended daemon, automatic intervention for all Worker
failures, or deterministic model behavior. P118 may use the layer as an
optional Coordinator-owned cue path.
