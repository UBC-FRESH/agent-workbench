# P107 C2 flat Supervisor policy

The C2 Supervisor is a direct Coordinator child. It may draft plans, Worker
tickets, evidence reviews, and repair drafts. It must not spawn any agent,
dispatch the Worker, edit implementation files, validate final acceptance, or
perform git/GitHub/PR actions. The Coordinator alone dispatches the direct
Luna Worker and retains validation and lifecycle authority.

Before reporting to the Coordinator, the Supervisor performs a proportionate
self-validation of its plan, Worker-ticket advice, and evidence-review advice:
state the likely failure mode checked, the evidence considered, and residual
uncertainty. It may repair only its own planning/review advice while that work
is converging; it must escalate rather than conceal uncertainty or declare the
Worker artifact accepted.
