# Optional Cloudflare Tunnel provider exposure

Use `agent-workbench-tunnel-provider` only when a model provider must be
consumed from another environment—for example, a VS Code chat client on a
student laptop. It maps one public HTTPS hostname to an **already-established**
Cloudflare Tunnel connector and its existing private origin route.

## No-Cloudflare fallback: client-owned SSH forwarding

When no Cloudflare option is invoked, keep the provider bound to loopback on
the provider host and create the network path from each client environment.
The client owns an SSH local forward that maps its local loopback port to the
provider's loopback port:

```bash
ssh -N \
  -L 127.0.0.1:18000:127.0.0.1:8000 \
  user@provider-host
```

In this example, the client application uses
`http://127.0.0.1:18000/v1`; SSH carries it to
`127.0.0.1:8000` on `provider-host`. Choose a free client-side port per
provider and leave the provider process bound to `127.0.0.1`, not `0.0.0.0`.
For a scheduler node that is reachable only through a login host, use the
site's approved `ProxyJump` route rather than opening a new public listener:

```bash
ssh -N \
  -J user@login-host \
  -L 127.0.0.1:18000:127.0.0.1:8000 \
  user@provider-node
```

Run the forward in a dedicated terminal or managed SSH profile, then validate
`http://127.0.0.1:18000/v1/models` with the provider's required local
authentication before selecting the model in the client extension. The tunnel
is intentionally per-client: it creates no public DNS record, connector, or
shared access path.

## Non-negotiable safety boundary

This helper **does not** create a tunnel, copy credentials, install or start a
`cloudflared` service, replace a live configuration, or migrate ingress. The
connector's existing topology remains the authority. A separate reviewed
operations change must add the hostname ingress rule to that connector first.

The default execution is a plan with a read-only `cloudflared tunnel info`
inspection. Copy the public-safe template to an ignored local path, then render
a candidate only for review or manual merging:

```bash
agent-workbench-tunnel-provider \
  --config local/model-provider-tunnel.yaml \
  --write-candidate runtime/model-provider-cloudflared-candidate.yml
```

The candidate has a `/v1` public base URL suitable for OpenAI-compatible
clients. Configure client extensions with the resulting HTTPS base URL and the
provider's normal authentication scheme; do not place provider keys in the
tunnel configuration or commit them to the repository.

## Attach DNS only after a manual ingress review

Before attaching DNS, an authorized operator must verify that the active
connector config already has an ingress rule whose hostname and private origin
exactly match the local config. The `--apply-dns` path then:

1. inspects the specified existing tunnel;
2. reads and checks the live config's tunnel ID and matching ingress rule;
3. makes a timestamped backup of that live config without modifying it;
4. creates the CNAME with `cloudflared tunnel route dns`;
5. reinspects the tunnel and requests the configured HTTPS health URL.

Run it only with the exact tunnel UUID shown by the live topology review:

```bash
agent-workbench-tunnel-provider \
  --config local/model-provider-tunnel.yaml \
  --apply-dns \
  --confirm-tunnel-id '<existing-tunnel-uuid>'
```

`verification_url` must be a safe, externally reachable health endpoint. If it
fails, treat the setup as incomplete: do not redirect clients or replace the
current access path. The helper does not roll back DNS automatically because
it must not delete or alter pre-existing records without an explicit reviewed
operation.

## Client model-provider contract

- The provider should expose an OpenAI-compatible API beneath `https://<host>/v1`.
- Set a client-specific API key through that client's local secret store.
- Use Cloudflare Access or equivalent authorization in front of non-public
  endpoints; public DNS does not make a model API safe to expose unauthenticated.
- Check model discovery and a small authenticated chat from a client laptop
  before rolling the endpoint into a shared configuration.
