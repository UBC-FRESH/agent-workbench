# P107 C4 flat Supervisor plus Ollama Worker policy

C4 repeats C2's flat depth-1 topology, changing only the Worker provider/model
and named function-tool adapter contract:

```text
Coordinator -> Luna Supervisor
Coordinator -> Ollama Worker
Coordinator -> Terra Advisor
```

The Supervisor never spawns. It prepares the bounded Worker ticket, reviews
Worker command evidence, and sends compact repair relays only when directed by
the Coordinator. The Coordinator does not implement Worker-owned changes.
Persist the effective Ollama model, inference parameters, adapter version/hash,
runtime, and local-cost assumptions in the run record. Advisor hard-wait
semantics remain unchanged.
