# Phase 113: Codex-Ollama Function-Tool Adapter Sandbox

## Decision

P107 is parked until a configured Ollama Worker has a reliable, bounded native
file-edit surface. Phase 113 is the targeted repair phase. It does not reopen
P107 economics work and does not authorize P108.

## Starting evidence

See also `planning/p107_2_ollama_apply_patch_compatibility.md` for the
transport-evidence record carried into this phase.

A bounded native-child experiment established that an Ollama-backed Qwen Worker
can complete a native Codex patch when a narrow local adapter:

1. converts Codex's custom/freeform `apply_patch` declaration to one standard
   function, `apply_patch(patch: string)`;
2. forces that single function for the initial provider request;
3. converts the returned function-call stream into Codex custom-tool events;
4. translates the resulting custom-tool history back into ordinary function
   history for the provider follow-up.

The child completed normally after the expected ignored-file patch. It also
made malformed patch retries before its valid call. This establishes capability,
not reliability or production acceptance.

## Scope

- Implement and test the one-tool adapter only.
- Keep provider-specific headers, raw prompts, raw Responses streams, runtime
  tickets, and child transcripts ignored.
- Operate solely on explicitly allowed ignored worktree targets.
- Preserve native Codex patch handling, approvals, and diff evidence.

## Non-goals

- No general Responses proxy or Code Mode compatibility layer.
- No MCP translation.
- No shell-writing fallback presented as native patch success.
- No P107 economics run, P108 work, GitHub release, or production deployment.

## Hard blockers for a usable adapter

| Blocker | Required evidence |
| --- | --- |
| First-call validity | A Worker emits exactly one valid patch call without malformed retries. |
| Containment | Outside-root paths, extra calls, and unsupported tools fail before mutation. |
| History fidelity | Call IDs and tool results round-trip deterministically through completion. |
| Failure behavior | Malformed provider output produces a precise fail-closed result. |

## Task sequence

1. P113.1 (#649): write the adapter contract and deterministic fixtures before
   expanding the prototype.
2. P113.2 (#650): implement the constrained adapter and focused tests.
3. P113.3 (#651): run fresh native Worker trials requiring a single function
   call with two expected edits, then decide whether P107 can resume.

## Acceptance framing

- `quality_validated_candidate`: the Worker makes the expected bounded native
  patch and the deterministic target check passes.
- `protocol_accepted_candidate`: containment, one-call behavior, history
  translation, and raw evidence satisfy the defined contract.
- `economics_usable`: explicitly out of scope until P107 resumes.

## Evidence locations

The initial capability evidence remains under ignored runtime paths from the
P107.2 wire probe. P113 will create fresh, phase-namespaced ignored evidence;
it will not promote raw request or provider material into tracked files.

## P113.3 decision

Fresh native evidence demonstrated one complete bounded path: the configured
Qwen Worker made one exact `apply_patch` call, changed two allowed ignored
targets, and completed the custom-tool history follow-up normally. Combined
with the deterministic contract suite, this accepts the adapter as both a
`quality_validated_candidate` and a `protocol_accepted_candidate`.

Five independently fresh `qwen3-coder:latest` Workers subsequently completed
the exact one-call, two-file ignored-target task and normal follow-up. Each
fresh session recorded one native `apply_patch` call, the expected diff, and
the terminal marker; no counted adapter verdict was rejected. This accepts
Worker reliability as a P113.3 candidate. It permits a separate P107-resume
decision only: P107 remains parked, `economics_usable` remains untested, and
P108 remains unauthorized.

A post-cleanup normal-provider control produced only textual pseudo-tool markup
and no native mutation. The constrained adapter is therefore a required
compatibility layer for this Ollama Worker path, not an optional convenience.
