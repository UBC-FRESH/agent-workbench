# vLLM bootstrap triage notes

## Problem framing

The goal here is not to run a long-serving production model endpoint. The goal is a short smoke test that proves a model-serving path can come up quickly enough to be useful for popup-style LLM provider setup.

## What we learned

### 1. Interactive allocations are fragile

- A popup-style request can sit in queue unexpectedly long.
- The interactive pool on FIR is small and highly contended.
- Even when resources are technically available, the request shape can still be a poor fit for the scheduler.

### 2. The request shape matters

- Requests that look too minimal or too generic, such as a single-GPU H100 request without explicit partition context, are often a weaker fit for the queue.
- An explicit GRES request and a broader GPU partition are stronger choices for this workflow.

### 3. Batch submission is better than waiting in interactive mode

- The batch path gives a job ID immediately and lets the operator inspect progress later.
- This is especially useful when the job sits in the queue and the operator wants to keep moving on other work.

## Recommended pattern

For future clusters and future smoke tests:

- prefer batch submission
- keep the wall time short
- use an explicit GRES request instead of a generic GPU request
- record the resulting job ID and inspect it later
- compare queue behavior across clusters so the KB improves over time

## Durable takeaway

Treat vLLM bootstrap smoke tests as short, opportunistic scheduler tasks rather than interactive debugging sessions. This mindset makes the workflow more resilient and more likely to succeed on contested clusters.

## Planned deployment guardrails

We should capture a lightweight model catalog and a VRAM-fit preflight for popup-style vLLM deployments:

- Record per-model VRAM requirements in a catalog that is stable across clusters and GPUs as far as practical.
- Before requesting a GPU allocation, evaluate whether the requested model or model set can fit in the available VRAM budget for the current allocation.
- If the fit check fails, fail fast with a verbose, coding-agent-friendly message that explains the shortage and suggests smaller alternatives from the catalog.
- Apply the same preflight check on the client side of the deployment harness before we waste time waiting for an allocation that can never host the requested model.
- For multiple models in one remote GPU allocation, plan for multiple vLLM server processes, each with its own forwarded TCP port and its own model alias.
- Measure the actual VRAM usage of one representative model at a time and store the observed numbers so the catalog can be updated from evidence rather than guesswork.

### How to measure a model's minimum VRAM requirement

1. Start from a clean GPU allocation that is known to be large enough for the model.
2. Launch the target model under `vllm serve` with the normal production-style settings for the deployment.
3. Record GPU memory usage before loading the model and after the model has finished loading.
4. Capture both the total memory reported by the GPU runtime and the model's peak resident-set usage during idle and a small prompt burst.
5. Repeat the same measurement for each model family we intend to support.
6. Store the observed value in the model catalog as a measured value, with a note about the GPU type and whether the figure is a floor, a typical value, or a peak value.

The practical measurement loop should use a simple script like:

```bash
python playbooks/vllm_blackwell/scripts/probe_runtime.py
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
```

and then compare the numbers before and after the model loads. The preflight helper should treat the measured value as the authoritative requirement for the catalog and should be conservative enough to avoid overcommitting a small MIG slice or a small GPU allocation.
