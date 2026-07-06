# P66-P70 Task-Level Delegation Tranche

## Context

The FEMIC P108 delegation pilot showed that a local Copilot/Ollama supervisor
can complete substantial real work when given a strong ticket. The delegate
created a new public instance repository, linked it as a submodule, generated a
coherent bootstrap scaffold, interacted with GitHub issues, and opened a PR.

The same run also exposed control-loop weaknesses:

- whole-phase delegation was too broad;
- the delegate stalled repeatedly and needed user nudges;
- Windows shell assumptions caused avoidable friction;
- result reports became stale after later fixes;
- issue checklist synchronization lagged behind comments and closures; and
- the useful behavior trace had to be archived manually after the fact.

P65 solved the last point by making Copilot session archival systematic. P66-P70
turn the remaining lessons into a tighter delegation controller.

## Direction

The default delegation unit should become one roadmap child task, not one whole
phase. The paid or high-reliability coordinator owns phase setup, sequencing,
acceptance, repair decisions, PR merge, parent issue closure, and final claims.
The local/free supervisor owns bounded child-task execution and reports back
through structured files.

## Phase Sequence

### P66: Task-Level Delegation Protocol

Define one-child-task delegation as the normal control unit. Produce reusable
ticket, result, decision, and repair packet templates. Record why phase-level
delegation remains experimental.

### P67: Heartbeat And Nudge Protocol

Make stalls observable. Require heartbeat, result, and blocker files. Define
stale heartbeat detection, canned nudges, and stop rules after repeated failed
nudges.

### P68: Copilot Task Controller V0

Package the manual launch/archive/check/nudge loop. A controller run should tie
together the ticket, session id, model id, permission mode, heartbeat, result
file, chat archive, and coordinator review packet.

### P69: Behavior Analytics From Archives

Use P65 archives to compute reusable behavior metrics: stalls, nudge count,
tool-call count, shell mismatch, repeated summary loops, premature completion
claims, and user intervention burden.

### P70: FEMIC P108 Repair Dogfood

Use the real P108 cleanup surface as the first task-level dogfood case. This
tests whether the new controller can delegate bounded cleanup tasks without
repeating the whole-phase control problems.

## Success Criterion

After P70, a future real-project phase should be launched as:

1. coordinator creates phase/branch/issues/budget;
2. controller launches one child-task ticket;
3. local supervisor works until result/blocker/heartbeat stop;
4. archive and behavior manifest are captured automatically;
5. coordinator accepts, rejects, or issues one repair ticket; and
6. the next child task starts only after the previous one is reconciled.
