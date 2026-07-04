# P9-P14 Forward Plan

## Purpose

This note records the next several Agent Workbench phases after P8 so the
project does not drift from one ad hoc trial to the next.

The current evidence says the Copilot SDK/Ollama bridge can run repeated
no-tool marker probes for the configured worker models. The next question is
not yet "can the worker edit a repository safely?" The next question is whether
the worker can produce bounded, parseable work products consistently enough for
a supervisor to verify and, later, apply.

## Sequencing Principle

The planned sequence deliberately moves one risk boundary at a time:

1. Structured assistant output.
2. Patch proposal without mutation.
3. Supervisor-applied local mutation.
4. Restricted worker mutation.
5. GitHub workflow participation.
6. Broader model comparison and packaging decisions.

This avoids mixing model behavior, tool safety, GitHub permissions, and user
interface questions in the same experiment.

## Planned Phases

### P9: SDK Structured Documentation-Output Trial

P9 should use the P8 harness on a tiny documentation-style ticket where the
worker returns a structured Markdown result in the assistant response. The
worker still gets no tools and performs no file mutation.

Success means the harness can classify required sections, missing sections,
extra prose, malformed output, refusal, and loop-like repetition across repeated
runs.

### P10: Patch Proposal Protocol Trial

P10 should ask workers to produce a small, parseable patch proposal without
applying it. The supervisor remains responsible for validating and applying any
candidate patch.

Success means the project has a safe intermediate lane between "model writes a
summary" and "model mutates files."

### P11: Supervisor-Applied Patch Harness

P11 should add a local supervisor-side harness that can parse a worker patch
proposal, apply it to a temporary or explicitly allowed target, run checks, and
classify the result.

Success means mutation is tested through supervisor-controlled application, not
through unrestricted worker autonomy.

### P12: Restricted Tool-Enabled Worker Trial

P12 should test the narrowest tool-enabled worker path available through the
chosen bridge. The worker should receive a tiny ticket, explicit allowed paths,
and a stop condition, while the supervisor checks observed tool evidence.

Success means the project can say whether the current SDK or VS Code bridge is
ready for controlled file mutation, or whether it must stay in proposal-only
mode.

### P13: GitHub Workflow Microtrial

P13 should test a small GitHub workflow behavior such as preparing a progress
comment body, opening a draft/local-only PR description, or running read-only
issue inspection through a controlled ticket. It should not delegate broad phase
closeout.

Success means the project has evidence about which GitHub workflow steps can be
delegated and which must remain supervisor-only.

### P14: Model Matrix And Packaging Decision

P14 should compare the available configured Ollama worker models on the stable
P9-P13 tickets, then decide whether Agent Workbench should stay as scripts and
Markdown, become a small package/CLI, or explore a VS Code extension or hosted
agent surface.

Success means the next architecture move is evidence-based rather than driven
by interface preference alone.

## Guardrails

- Use only configured Ollama models unless a phase explicitly installs and
  verifies more models.
- Keep raw tickets, raw results, transcripts, endpoints, and provider headers in
  ignored runtime paths.
- Promote only sanitized counts, classifications, and representative findings.
- Do not give workers unrestricted file, terminal, or GitHub authority while the
  structured-output and patch-proposal lanes are still immature.
- Do not call the result a benchmark suite until repeat counts, ticket families,
  scoring rules, and versioned environment metadata are stable enough to support
  that claim.

