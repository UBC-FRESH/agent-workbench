# Phase 19 Delegation Policy Notes

Phase 19 converts the P8-P18 evidence into an explicit delegation policy. The
policy is intentionally conservative: the workbench has enough evidence for
no-tool output, proposal-only work, supervisor-applied sandbox mutation, and
narrow ignored-path tool trials, but not enough evidence for worker-owned
tracked-file mutation or GitHub closeout.

## Evidence Basis

- P8-P10 showed that the SDK/Ollama path can evaluate no-tool marker,
  structured-output, and patch-proposal ticket families.
- P11 showed that supervisor-owned code can apply a worker patch proposal to an
  ignored sandbox target.
- P12 and P18 showed that VS Code Chat can perform bounded ignored-runtime file
  mutation with observable tool evidence.
- P13 showed that workers may prepare GitHub text, but supervisor-owned GitHub
  mutation remains the safer boundary.
- P15 showed that model families differ most usefully on richer proposal tasks,
  not marker-only tasks.

## Policy Artifacts

- `planning/delegation_policy.md` defines trust levels L0-L6.
- `AGENTS.md` now points agents at the trust-level boundary.
- `playbooks/evidence_store.md` remains the evidence-promotion companion.

## Decision

Current maximum delegated authority:

- no-tool SDK/Ollama workers: L1 for structured output and patch proposals;
- supervisor-applied patch flow: L2 for ignored sandbox targets;
- VS Code Chat bridge workers: L3 only for explicitly allowed ignored runtime
  paths; and
- GitHub workflow: L1 for draft text only.

Tracked-file mutation, issue closure, PR merge, release actions, and final phase
closeout remain supervisor-only.
