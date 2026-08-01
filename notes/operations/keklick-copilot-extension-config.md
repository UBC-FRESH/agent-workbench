# Keklick Copilot Custom Endpoints — where the config actually lives

Stop rediscovering this. Everything below is verified against the installed
extension, not inferred.

## Identity

| Fact | Value |
| --- | --- |
| Extension id | `keklick1337.keklick-copilot` |
| Display name | Keklick Copilot Custom Endpoints |
| Install dir | `~/.local/share/code-server/extensions/keklick1337.keklick-copilot-<version>/` |
| Manifest | `<install dir>/package.json` (authoritative list of settings keys) |

## Where config lives

**All model configuration is plain VS Code settings under the `customcopilot.*`
namespace.** There is no sidecar JSON, no `globalStorage/` directory, no
extension-owned config file.

Every contributed key is `scope: window`, so it resolves through the normal
settings cascade:

| Scope | Path |
| --- | --- |
| User (the one in practice) | `~/.local/share/code-server/User/settings.json` |
| Machine | `~/.local/share/code-server/Machine/settings.json` |
| Workspace | `<repo>/.vscode/settings.json` |

Check all three before concluding a value is wrong — a workspace file silently
wins over user settings.

## The keys

| Key | Purpose |
| --- | --- |
| `customcopilot.models` | **The model list.** Array of model objects. This is what you edit. |
| `customcopilot.userAgent` | Default UA for requests |
| `customcopilot.proxyUrl` | Outbound proxy |
| `customcopilot.logLevel` | `off` / verbosity |
| `customcopilot.debugRequestLogging` | Log raw requests |
| `customcopilot.retry` | Object: `enabled`, `max_attempts`, `interval_ms` |
| `customcopilot.chatRetries` / `chatRetryInterval` / `chatRetryJitter` | Chat-specific retry |
| `customcopilot.delay` | Artificial request delay |
| `customcopilot.readFileLines` | File-read chunking |
| `customcopilot.promptOverride.*` | `enabled`, `mode`, `text`, `replacements` |
| `customcopilot.commitLanguage` / `commitMessagePrompt` | Commit-message feature |

## Model object shape

Fields observed in working entries:

```jsonc
{
  "id": "ornith-1.0-35b-fp8",     // MUST equal the server's --served-model-name
  "configId": "fresh-vllm-agent", // stable handle for this endpoint
  "displayName": "Ornith 1.0 35B FP8",
  "owned_by": "fresh-vllm",
  "baseUrl": "https://host/v1",   // include /v1 for apiMode "openai"
  "apiMode": "openai",            // or "ollama" (then omit /v1)
  "context_length": 250000,
  "max_tokens": 4096,
  "tool_calling": true,
  "vision": false,
  "temperature": 0.6,
  "headers": { }                  // e.g. CF-Access-Client-Id / -Secret
}
```

`id` is the wire value sent as `"model"` to the endpoint. `displayName` is only
the label. **A mismatch between `id` and the server's `--served-model-name`
produces a 404 `The model ... does not exist`.**

## How other settings reference a model

These live outside the `customcopilot.*` namespace and must be updated together,
or you get a silent fallback:

| Setting | Format | Example |
| --- | --- | --- |
| `chat.utilityModel` | `customendpoint/<id>` | `customendpoint/ornith-1.0-35b-fp8` |
| `chat.utilitySmallModel` | `customendpoint/<id>` | same |
| `chat.planAgent.defaultModel` | `<displayName> (copilotcustommodelsendpoint)` | `Ornith 1.0 35B FP8 (copilotcustommodelsendpoint)` |
| `inlineChat.defaultModel` | `<displayName> (copilotcustommodelsendpoint)` | same |
| Agent profile `model:` frontmatter | `<displayName> (copilotcustommodelsendpoint)` | same |

Two different reference formats — id-based and displayName-based. Grep for both
after any rename.

## Secrets

API keys are **not** in settings.json. They go to VS Code SecretStorage under:

- `customcopilot.apiKey.<provider>`
- `customcopilot.apiKeySource.<provider>`

Set them via the command palette: **Set API Key For Source**
(`customcopilot.setProviderApikey`). They are not greppable on disk in
plaintext. Endpoints using header auth (e.g. Cloudflare Access) put creds in the
model's `headers` object instead, which *is* in settings.json.

## Commands

| Command | Title |
| --- | --- |
| `customcopilot.openConfig` | Open Configuration UI |
| `customcopilot.setProviderApikey` | Set API Key For Source |
| `customcopilot.generateGitCommitMessage` | Generate Commit Message |
| `customcopilot.abortGitCommitMessage` | Stop Commit Message Generation |

## Debugging checklist

1. `grep -n 'customcopilot' ~/.local/share/code-server/User/settings.json`
2. Check the Machine and workspace scopes too.
3. Compare `id` against the live server:
   `curl -s <baseUrl>/models | python3 -c "import sys,json;print(json.load(sys.stdin)['data'][0]['id'])"`
4. Grep both reference formats (`customendpoint/<id>` and
   `<displayName> (copilotcustommodelsendpoint)`).
5. The extension registers only one `onDidChangeConfiguration` hook — after
   editing `customcopilot.models`, **reload the window** rather than trusting
   hot-reload. A stale model picker is usually just an unreloaded window.
6. Ignore hits in `User/caches/`, `workspaceStorage/`, `*.backup-*`,
   `*.bak-*` — those are history, not config, and they will waste your time.

## Related

- Local vLLM launch profiles: `~/projects/tmp/vllm-blackwell/profiles/*.env`
  (`VLLM_SERVED_MODEL_NAME` must match the Copilot model `id`).
- `notes/operations/vllm-bootstrap-triage.md`

## JupyterHub code-server deployment formula

Use this procedure to reproduce a known-good Copilot + Keklick environment on
a JupyterHub-hosted code-server account. It exists because copying settings or
extensions in isolation is not sufficient.

### Non-negotiable rule

**Diff the known-good environment before changing the target.** Do not infer
compatibility from extension names, cache timestamps, or a successful
`--list-extensions` command.

Compare these surfaces first:

```bash
code-server --version
ps -eo user,pid,ppid,args | rg '[c]ode-server'
find ~/.local/share/code-server/extensions -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort
jq '[.[] | select(.identifier.id | test("^(github\\.copilot|keklick1337\\.keklick)"))]' \
  ~/.local/share/code-server/extensions/extensions.json
```

Also compare the **non-secret** `customcopilot.*`, `chat.*`,
`inlineChat.*`, and `github.copilot.*` settings. Redact `headers` before
putting command output in a tracked note or issue.

### What a matching modern runtime looks like

The known-good pattern is:

| Layer | Required state |
| --- | --- |
| code-server runtime | Same package and embedded VS Code version as the working environment |
| Chat implementation | Built into the modern code-server runtime as `GitHub.copilot-chat` |
| User extensions | `GitHub.copilot` plus `keklick1337.keklick-copilot` |
| Extension metadata | The two user extensions are machine-scoped in `extensions.json` |
| Models | `customcopilot.models` and its id/display-name references agree |
| Authentication | A real GitHub authentication session exists for the target OS user |

On the verified modern runtime, the built-in Chat manifest is at:

```text
/usr/lib/code-server/lib/vscode/extensions/copilot/package.json
```

It declares `GitHub.copilot-chat`. **Do not install a second user-scoped
`github.copilot-chat` VSIX on top of that runtime.** The duplicate can shadow
the built-in extension and put Chat back into the broken setup/install loop.

Older code-server releases may instead need a separate compatible Chat VSIX,
but that is a compatibility bridge, not the target state when the source
environment already uses the newer built-in Chat architecture.

### Safe deployment order

1. **Freeze the rollout to one target user.** Do not touch the second user
   until the first user has a working Chat session and model picker.
2. **Back up before changing the shared runtime.** Create a container/VM
   snapshot, archive the existing code-server runtime and package metadata,
   and back up the target user's `extensions.json` and settings.
3. **Install the exact code-server package from the known-good environment.**
   Verify its checksum before installation and verify both outputs afterwards:

   ```bash
   code-server --version
   jq '{version, commit}' /usr/lib/code-server/lib/vscode/product.json
   ```

4. **Match the extension topology, not merely the names.** Keep the working
   user `GitHub.copilot` and Keklick versions; remove stale user-scoped
   `github.copilot-chat-*` directories and registry entries when the upgraded
   runtime provides built-in Chat.
5. **Preserve the JupyterHub launch context.** The code-server child launched
   by `jupyter-server-proxy` inherits at least:

   ```text
   JUPYTERHUB_USER
   JUPYTERHUB_SERVICE_PREFIX
   JUPYTERHUB_BASE_URL
   ```

   Prefer restarting it through the JupyterHub/Jupyter Server proxy. If a
   manual recovery launch is unavoidable, preserve the original user, port,
   user-data directory, extensions directory, launch flags, and the three
   variables above. Losing the service-prefix environment breaks browser
   subpath-aware flows such as GitHub OAuth.
6. **Reload the target user's browser window only after the new child process
   is listening on the original proxied port.** Check the proxy route first;
   do not assume a successful package install restarted an existing process.
7. **Authenticate interactively as the target user.** Do not copy OAuth
   tokens, SecretStorage, browser profiles, or keychain material between
   hosts. Complete the GitHub login in the browser for that OS account.

### The misleading "Set up Chat" dialog

The generic **Set up Chat** action calls the product Marketplace installer for
the default chat extension. On installations where the Marketplace gallery is
disabled, this can report that `GitHub.copilot-chat` "was not found" even when
the correct built-in Chat extension is active.

Treat that dialog as a diagnostic signal, not proof that the extension files
are absent. Verify the active runtime, extension topology, and authentication
state first. Use the Accounts menu to sign in to GitHub rather than repeatedly
retrying the generic installer.

### Verification gates

All of these must pass before declaring the first-user deployment done:

```bash
# 1. Runtime is the expected one.
code-server --version

# 2. The user registry contains only the intended user extensions.
code-server --list-extensions | rg '^(github\.copilot|keklick1337\.keklick-copilot)$'

# 3. Built-in Chat exists in the runtime.
jq '{id:(.publisher + "." + .name), version, engine:.engines.vscode}' \
  /usr/lib/code-server/lib/vscode/extensions/copilot/package.json

# 4. The running child has the JupyterHub subpath context.
tr '\0' '\n' </proc/<code-server-pid>/environ \
  | rg '^(JUPYTERHUB_USER|JUPYTERHUB_SERVICE_PREFIX|JUPYTERHUB_BASE_URL)='

# 5. The proxy reaches the code-server child at the normal user route.
# Run this through the established JupyterHub access path; do not publish
# tokens or private URLs in tracked output.
```

Then inspect the target user's current logs:

```text
~/.local/share/code-server/logs/<current>/exthost*/vscode.github-authentication/GitHub Authentication.log
~/.local/share/code-server/logs/<current>/exthost*/GitHub.copilot-chat/GitHub Copilot Chat.log
```

Success criteria:

- GitHub Authentication reports at least one session for the requested scopes.
- Copilot Chat no longer reports `no Copilot token source` or `GitHub login failed`.
- A newly created chat session records the intended model and auth state.
- The Keklick custom models appear in the model picker and can be selected.

### Failure signatures and response

| Symptom | Likely cause | Correct response |
| --- | --- | --- |
| `GitHub.copilot-chat` "was not found" | Old runtime, duplicate Chat VSIX, or disabled gallery setup loop | Match the runtime; use built-in Chat; do not keep retrying the installer |
| Chat works locally but not remotely after copying settings | Runtime or extension topology differs | Perform the full environment diff before changing settings |
| `Got 0 sessions` in GitHub Authentication log | No OAuth session exists for that OS user | Complete interactive GitHub sign-in; never copy secrets |
| `GitHub login failed` / `no Copilot token source` | Authentication callback/session failed | Verify JupyterHub service-prefix environment and retry interactive sign-in |
| New package installed but old behavior persists | Existing code-server process still maps deleted/old binaries | Restart the proxy-managed child and verify the running version |
| Proxy returns connection refused after a manual restart | Proxy-managed child was killed but not respawned | Restore the child on its original port immediately, then repair the supervised restart path |

### Rollback

Keep the pre-upgrade container/VM snapshot and the user-level extension/settings
backup until the first target user has completed a successful authenticated chat
request. If the upgraded runtime prevents access, restore the snapshot rather
than trying a sequence of ad-hoc package downgrades.

## GitHub MCP deployment formula

GitHub MCP is a separate deployment surface from Copilot sign-in. A working
Copilot Chat session does **not** prove that the GitHub MCP server can start.

### Required components

For a stdio-based GitHub MCP server, verify all of the following as the target
OS user:

| Component | Requirement |
| --- | --- |
| MCP declaration | `User/mcp.json` has the expected `github` server entry |
| Server executable | The configured command path exists and is executable |
| `envFile` | If declared, the file exists, is readable by that user, and has mode `600` |
| Environment variables | The file supplies every variable required by the chosen server binary |
| Authentication | The target user has authorization appropriate to the configured token or CLI flow |

The MCP declaration may refer to an `envFile` outside the code-server user-data
directory. Copying only `mcp.json` and the executable therefore produces the
misleading startup error:

```text
Failed to read envFile '<path>': ENOENT
```

### Safe rollout and verification

1. Inventory the known-good declaration without printing values from `env`,
   `headers`, or the referenced env file.
2. Install the matching executable for the target architecture and set its
   owner and execute mode for the target OS user.
3. Create the referenced env-file directory with restrictive permissions and
   install the env file with mode `600`.
4. Treat any personal access token in an env file as user-specific. Do not
   copy it between different people or accounts without explicit authorization.
   A same-user migration between trusted environments is still a credential
   transfer and must be handled without logging its contents.
5. Validate the actual stdio protocol, not merely `--version`: send an MCP
   `initialize` request followed by `tools/list`, and confirm both responses
   arrive without server errors.
6. Reload the code-server window or start a new chat so the remote extension
   host re-reads the MCP declaration.

Useful non-secret checks:

```bash
jq '.servers.github | {command, args, envFile, envKeys:(.env // {} | keys)}' \
  ~/.local/share/code-server/User/mcp.json
test -x ~/.local/bin/github-mcp-server
stat -c '%U:%G %a %n' ~/.config/github-mcp/.env
```

## Keklick SecretStorage and header-authenticated models

Keklick resolves per-provider API keys from VS Code `SecretStorage`, using
keys named `customcopilot.apiKey.<provider>` (or an API-key source secret).
Depending on the code-server encryption backend, these may be memory-only and
can disappear after a code-server restart even when `settings.json` is intact.

### Diagnosis before changing anything

When Chat reports `API key not configured`:

1. Identify the selected model's `owned_by` provider and confirm the model
   still exists in `customcopilot.models`.
2. Confirm whether its endpoint already authenticates through configured
   custom headers. Do not print header values.
3. Probe a read-only endpoint with the configured headers and no bearer key.
   If it succeeds, the endpoint itself is healthy and the failure is Keklick's
   pre-request secret guard.
4. Prefer the supported **Set API Key For Source** command to store a genuine
   provider key for the target user.

For the verified Cloudflare Access pattern, models that carry both
`CF-Access-Client-Id` and `CF-Access-Client-Secret` can be accepted by the
backend without a provider bearer key. A narrowly scoped, version-local
Keklick provider patch was used only after confirming that every affected
endpoint returned success with those headers and a harmless fallback bearer
value. That patch is not durable across Keklick updates: back up the original
`provider.js`, verify the exact extension version and direct endpoint behavior,
then reapply and retest only if the same failure recurs.

Never copy VS Code SecretStorage, browser profiles, keychains, or a provider
API key from one user account to another to address this symptom.
