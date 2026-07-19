# P117 Run-Scoped Supervision Daemon Plan

Parent issue: #686  
Child issue: #687  
Branch: `feature/p117-run-scoped-supervision-daemon`  
Status: active planning surface

## Motivation

P116's r11 stale-post-cursor finding showed that a supervision cursor can be
observed after the boundary that was supposed to own it. A run-scoped daemon
needs explicit lease, closure, journal, and flush semantics so stale state
cannot be mistaken for current supervision evidence.

## Approved design

P117 defines a narrow control-plane design with these bounded surfaces:

1. A run-scoped lease identifies the sole active owner and its expiry and
   closure state.
2. A run-scoped append-only journal records sanitized events, cursor movement,
   flush receipts, adapter actions, and closure in deterministic order.
3. A deterministic flusher provides restart-safe, idempotent persistence and
   refuses writes after terminal closure or lease loss.
4. A native session adapter binds any live action to the declared native
   session lineage and authority; it does not create generic autonomous
   authority.
5. One bounded native daemon proof demonstrates the route with explicit stop
   conditions and inspectable artifacts.
6. An offline replay uses sanitized policy inputs to exercise decisions without
   claiming native execution.
7. An evidence audit checks the complete chain and reports quality, protocol,
   and economics independently.

## Planned tasks

### P117.2 - Run-scoped state contract

Define lease acquisition/renewal/loss, journal schema, closure states, cursor
ownership, and terminal-state rules for one run.

### P117.3 - Deterministic flusher

Specify ordering, idempotency, restart recovery, flush receipts, and the
no-write-after-closure behavior. Deterministic checks must cover stale cursor
and duplicate-flush cases.

### P117.4 - Native session adapter

Define the adapter boundary, permitted native session operations, lineage
binding, and the evidence needed to show that actions remained within the
declared run and authority.

### P117.5 - Bounded native daemon proof

Run one bounded native proof against the approved route. Capture the run lease,
journal, flush, closure, session lineage, and stop-condition artifacts. Do not
generalize one proof into a generic daemon capability.

### P117.6 - Offline replay and evidence audit

Replay sanitized policy inputs offline, then audit native and offline artifacts.
Report separately whether quality is validated, protocol is accepted, and
economics is usable. Economics is unassessed and no P107 economics claim is
made by P117.

## Out of scope

No code, provider/model configuration, runtime installation, GitHub mutation,
commit, release, or P107 economics measurement is part of this planning
surface.
