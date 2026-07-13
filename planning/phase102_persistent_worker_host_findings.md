# P102 Persistent Worker-Host Finding

## Question

Can a local Worker runtime call the configured remote OpenAI-compatible Ollama
provider repeatedly without per-task Windows sandbox authorization dialogs?

## Result

Yes, for no-tool tickets through the ignored runtime boundary.

The native app-server exposes a one-time Windows sandbox readiness/setup
operation. After that setup, a read-only app-server turn can reach the configured
Ollama provider without starting a nested CLI sandbox. One observed app-server
turn produced the expected marker but did not emit its terminal completion
event, so this alpha completion path is not the accepted Worker runtime.

The persistent Responses Worker host instead submits one non-streaming request
per ticket, writes the model result under `runtime/agent_jobs/`, and emits
compact start/completion JSON records. In the bounded marker run, two sequential
tickets returned HTTP 200 and their exact markers. The second request completed
quickly after the model was warm.

A follow-up serial proof used the same transport for a remote Supervisor
dispatch marker, a Worker marker, and a remote Supervisor verification marker.
All three requests returned HTTP 200 and the markers matched. The Coordinator
relayed the ticket between the serial turns, so this is not evidence of a direct
Supervisor-owned Worker invocation.

## Verdicts

| Verdict | Status | Evidence |
| --- | --- | --- |
| `quality_validated_candidate` | true for the no-tool Worker-host boundary | two exact ignored-runtime marker outputs and HTTP 200 responses |
| `protocol_accepted_candidate` | qualified true for a Supervisor-authored ticket handoff | Supervisor shell evidence shows the ignored ticket creation; the persistent Worker host consumed that exact ticket and a fresh Supervisor verified its result |
| `economics_usable` | false | no paid Coordinator span was measured for a persistent-host dispatch run |

## Next Gate

Keep substantive TSA23 work out of scope. The next bounded experiment must add
paid Coordinator-span economics and repeat the accepted handoff on a small
non-trivial ticket before any substantive delegation authorization.
