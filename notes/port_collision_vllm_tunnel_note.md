# vLLM tunnel/port-collision note

## Summary

A local Cloudflare tunnel and multiple vLLM providers can interfere if they are both pointed at the same local origin port, especially when trying to expose more than one provider such as `fresh01-vllm.01101.dev` and `fresh02-vllm.01101.dev`.

## Failure mode

If two separate vLLM instances are started while both are configured to bind to the same local port (for example `18000`), one of them will fail to bind and the exposed endpoint can become inconsistent or return upstream errors such as 502s.

This is especially likely when:

- a second vLLM provider is launched while a first provider is already running,
- both providers are routed through a local tunnel config to the same localhost port,
- a tunnel config is changed without updating the backend port assignments.

## Prevention rules

- Give each vLLM provider its own unique local port when running multiple instances.
- Keep the tunnel ingress targets aligned with the actual backend port in use.
- Before launching a new provider, confirm that the target port is not already bound.
- Prefer a clear mapping such as:
  - provider A: `127.0.0.1:18000`
  - provider B: `127.0.0.1:18001`
- If using a tunnel, update the hostname-to-local-port mapping for each route explicitly.

## Operational reminder

If a public endpoint suddenly starts failing after a second provider attempt, check for:

1. an existing process already listening on the expected port,
2. a tunnel config that points multiple hostnames to the same origin port,
3. a second vLLM launch that may have failed due to address reuse.

## Example sanity check

Use a command like:

```bash
ss -lntp | grep 18000
```

and verify which process is bound to the port before starting a new provider.
