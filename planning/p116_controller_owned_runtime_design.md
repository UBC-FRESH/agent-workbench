# P116 Controller-Owned Runtime Design

## Purpose

Turn P116 from local event-processing primitives into one usable, bounded
Agent Hub control loop. The loop must observe a live Worker, obtain a
Supervisor assessment of meaningful new evidence, let a Coordinator decide,
and deliver one bounded response to the same Worker session.

This is a control-plane design only. It does not make a P107 quality,
protocol, or economics claim.

## Non-negotiable host contract

The selected host adapter must own all three session handles for one run and
provide all of the following:

1. Create or resume an identified Worker, Supervisor, and Coordinator session
   in the declared workspace and permission mode.
2. Subscribe to ordered Worker lifecycle/tool events while the Worker runs.
3. Invoke the Supervisor again with a bounded evidence delta.
4. Submit one Coordinator-approved message to the exact identified Worker
   session and return a durable delivery receipt.
5. Close the three sessions and expose terminal status.

An adapter missing any item is not a P116 execution route. It may be retained
as diagnostic evidence, but the controller must reject it before a run starts.

## Current route assessment

| Route | Event stream | Same-session delivery | Current status |
| --- | --- | --- | --- |
| Native Codex Agent Hub | Hooks and raw native session record | Coordinator `multi_agent_v1__send_input` accepts exact-session interrupt submissions | primary P116 route; automated event-to-tool binding remains to be implemented |
| Native Codex app-server + Ollama Worker | Yes | Yes at thread level | diagnostic only: Worker stream closes before response completion |
| Copilot SDK host | Source adapter has callbacks, resume, and send | Yes in adapter design | excluded from P116: not the requested Codex route |

The native direct-input proof established that a live Coordinator can submit an
`interrupt:true` message to the exact active Worker session. The Worker received
the message and returned its intervention marker before the requested shell
turn naturally completed. This proves the delivery half of P116. It does not
yet attach a local event controller to that native tool surface.

## Runtime components

```text
HostAdapter
  -> Worker event subscription
  -> session invoke/send/close operations

RunController
  -> run lease and journal (P117)
  -> event normalizer and P116 cursor reducer
  -> trigger policy
  -> Supervisor invocation
  -> Coordinator invocation and authority check
  -> same-Worker delivery and receipt recording

P116 artifacts
  -> manifest, events, cursor, packets, actions, controller log
```

`HostAdapter` is the only component permitted to call host APIs. For the
primary route it must be embedded in, or delegated by, the live native
Coordinator context because only that context owns
`multi_agent_v1__send_input`. It exposes typed operations `start_run`,
`subscribe_worker`, `invoke_supervisor`, `invoke_coordinator`, `send_worker`,
`inspect`, and `close_run`. The controller never invokes a model provider
directly and never reconstructs a session from a chat transcript.

The controller reuses the existing P116 event validation/reducer/review
contracts and P117 lease/journal/idempotency rules. Those modules are support
libraries, not the runtime itself.

## One event-to-action cycle

1. The adapter receives a Worker event and emits a sanitized, ordered record
   tied to the run and Worker session.
2. The controller validates it, appends it to the run journal, and selects a
   review only for a stage transition, tool denial/failure, validation result,
   material repeat, or terminal state.
3. The controller sends the unacknowledged delta to the same Supervisor
   session. The Supervisor returns a schema-valid advisory packet.
4. The controller sends that packet and the fixed ticket boundary to the same
   Coordinator session. The Coordinator may choose `continue`, `nudge`,
   `escalate`, or `terminal`.
5. Only a validated `nudge` is sent through `send_worker`; the adapter returns
   a delivery receipt bound to the Worker session ID and idempotency key.
6. The controller records the packet, Coordinator decision, receipt, and
   acknowledged cursor atomically. Unknown delivery pauses the run; it never
   retries blindly.

Routine successful progress produces no Supervisor turn and no Coordinator
turn. The control plane is event-triggered, not a paid polling loop.

## Containment and failure rules

- One run, one workspace root, one Worker/Supervisor/Coordinator lineage.
- Worker authority remains limited to its declared workspace and ticket.
- Supervisor is read-only and advisory. Coordinator retains acceptance and
  final developer escalation.
- Raw commands, outputs, headers, credentials, and source contents never enter
  the Supervisor packet or tracked records.
- Missing event subscription, missing delivery receipt, stream disconnect,
  identity mismatch, invalid packet, or uncertain delivery immediately pauses
  the run and writes a local diagnostic. None becomes a quality or economics
  result.

## Proof sequence

1. Implement a fake `HostAdapter` contract test covering normal delivery,
   duplicate event, restart, identity mismatch, invalid Supervisor packet, and
   uncertain delivery.
2. Qualify exactly one real host with a no-mutation Worker ticket: observe a
   tool event, invoke the Supervisor, invoke the Coordinator, deliver one
   message to the same Worker, and capture the receipt.
3. Run one bounded coding ticket only after step 2 passes. Inspect raw session
   lineage, P116 artifacts, diff, validator, and post-action Worker outcome.
4. Only then decide whether that qualified route can enter a fresh P107 C4
   observation. P116 itself remains non-economic evidence.

## P116/P117 treatment

P116 is incomplete until a real host passes the proof sequence. P117 remains a
useful supporting library for run ownership, durable journaling, and delivery
idempotency; it is not a daemon and is not an execution route. No closed phase
or prior proof is evidence that this runtime exists.
