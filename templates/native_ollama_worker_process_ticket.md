# Native Ollama Worker Process Ticket

Run id: `<run-id>`

## Task

Return exactly the requested worker marker. Do not call tools, read provider
configuration, read credentials, modify files, invoke Git/GitHub, or start
other agents.

## Required marker

`<worker-marker>`

## Stop condition

Return the marker and stop.
