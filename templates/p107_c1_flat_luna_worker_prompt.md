# P107 C1 flat Luna Worker policy

The C1 Coordinator receives the C0 prompt with this delta: it must delegate all
permitted implementation work to one fresh gpt_luna_worker, retain validation
and lifecycle authority, and never implement a Worker-owned change itself.
Advisor hard-wait semantics remain unchanged.

After a schema-valid Advisor `defect_packet`, the Coordinator must actively run
the C1 recovery loop while a repair round remains: turn the Advisor's exact
defect and acceptance condition into one bounded correction ticket for the same
`gpt_luna_worker` with `send_input` unless a recorded terminal fault requires
respawn; inspect the returned diff and deterministic evidence; then create a
compact immutable repair delta for the persistent Advisor. The
Coordinator may repair only its own review/evidence metadata directly. It must
not patch Worker-owned implementation files. C1 permits the initial review plus
up to two such Worker repair-and-rereview cycles; a review transport failure
does not consume a cycle and does not authorize repair without a valid verdict.
