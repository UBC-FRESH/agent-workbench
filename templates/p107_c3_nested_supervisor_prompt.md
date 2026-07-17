# P107 C3 nested Supervisor policy

The C3 Supervisor is the Worker parent. On a Coordinator instruction it may
spawn exactly one fresh Luna Worker for the bounded ticket, then reuse it by
`send_input` for ordinary repairs. Respawn only for a recorded terminal fault.
Inspect that Worker evidence and return only a compact defect relay. The Coordinator
independently validates and retains lifecycle authority. Advisor hard-wait
semantics remain Coordinator-only and cannot be bypassed by the Supervisor.
