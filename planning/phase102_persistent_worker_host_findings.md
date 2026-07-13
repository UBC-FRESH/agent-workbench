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

## Verdicts

| Verdict | Status | Evidence |
| --- | --- | --- |
| `quality_validated_candidate` | true for the no-tool Worker-host boundary | two exact ignored-runtime marker outputs and HTTP 200 responses |
| `protocol_accepted_candidate` | false | the Coordinator submitted Worker tickets; a Supervisor-direct Worker dispatch edge was not observed |
| `economics_usable` | false | no paid Coordinator span was measured for a persistent-host dispatch run |

## Next Gate

Keep substantive TSA23 work out of scope. The next bounded experiment must show
one configured Supervisor creating or submitting a ticket to the persistent
Worker host, then independently verifying the result, with no nested CLI
sandbox and no per-task Windows authorization dialog.
