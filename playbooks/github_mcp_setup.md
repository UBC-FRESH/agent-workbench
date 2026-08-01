# GitHub MCP Server Setup Playbook

**Purpose**: Reusable procedure for setting up authenticated GitHub MCP tools in VS Code that persist across sessions without re-prompting for tokens.

**Provenance**: Executed and verified on one Linux + code-server environment on 2026-07-31. Windows steps follow the same design but are unverified until tested.

**Why this exists**: Previous attempts used `${input:}` prompts which re-prompted for tokens every session on headless Linux (no keyring). This approach uses `envFile` to avoid that issue.

---

## Environment Detection

First, detect which environment you're in:

```bash
uname -s && which code-server 2>/dev/null || which code 2>/dev/null
```

- **Linux + code-server**: Follow the Linux column
- **Windows 11 + VS Code Desktop**: Follow the Windows column
- **Do not guess** — check explicitly

---

## Step 1 — Install the binary

Download the latest release from https://github.com/github/github-mcp-server/releases

| | Windows 11 | Linux + code-server |
|---|---|---|
| Asset | `github-mcp-server_Windows_x86_64.zip` | `github-mcp-server_Linux_x86_64.tar.gz` |
| Install to | `%LOCALAPPDATA%\github-mcp\github-mcp-server.exe` | `~/.local/bin/github-mcp-server` |
| Post-install | — | `chmod +x` |

Use the `arm64` asset if on ARM. Verify with:

```bash
github-mcp-server --version
```

Expected output: `GitHub MCP Server Version: 1.x.x`

**Do not substitute** with `@modelcontextprotocol/server-github` via npx, Docker, or wrappers.

---

## Step 2 — Create the token file

| | Windows 11 | Linux + code-server |
|---|---|---|
| Path | `%USERPROFILE%\.config\github-mcp\.env` | `~/.config/github-mcp/.env` |
| Permissions | `icacls` (remove inheritance, grant only current user) | `chmod 700` dir, `chmod 600` file |

Contents (exactly one line):

```
GITHUB_PERSONAL_ACCESS_TOKEN=<your_token_here>
```

**Create the file empty** and tell the user to paste their token in themselves. Do not ask for the token in chat, echo it, or read the file back.

If the user doesn't have a PAT: direct them to https://github.com/settings/tokens. Prefer a fine-grained token scoped only to the required repositories and operations. Use classic `repo` only when the required operation cannot be expressed with a fine-grained token; add `read:org` and `read:user` only when org/team queries actually require them.

---

## Step 3 — Write the MCP config

**User-level config only** — never workspace `.vscode/mcp.json`.

| Environment | Path |
|---|---|
| Windows 11 | `%APPDATA%\Code\User\mcp.json` (`Code - Insiders` if applicable) |
| Linux + code-server | `~/.local/share/code-server/User/mcp.json` |

**On Linux, check all three locations:**
- `~/.local/share/code-server/User/mcp.json`
- `~/.vscode-server/data/User/mcp.json`
- `~/.config/Code/User/mcp.json`

If multiple exist, back each up with timestamped suffix and write identical content to all. Divergent copies cause confusing behavior.

**Content:**

```json
{
  "servers": {
    "github": {
      "type": "stdio",
      "command": "<absolute_path_from_step_1>",
      "args": ["stdio"],
      "envFile": "<absolute_path_to_env_file_from_step_2>"
    }
  }
}
```

**Back up any existing config before overwriting.**

---

## Step 4 — Start the server

1. Open Command Palette (Ctrl+Shift+P)
2. Type `MCP: List Servers`
3. Select `github` from the list
4. Click **Restart Server** (or Start if stopped)

**Note**: After config changes, you may need to reload the window (Command Palette → `Developer: Reload Window`) for the new config to take effect.

---

## Step 5 — Verification (do not skip)

A well-formed config is **not** evidence that anything works. Prove it:

1. **Call `get_me`**: Ask Copilot to "call the github get_me tool" — should return your GitHub login
2. **Call a repo read**: Ask to "show me issue 114 in UBC-FRESH/ws3" — should return the issue title
3. **Confirm the process**:
   - Linux: `pgrep -af github-mcp-server`
   - Windows: `Get-Process github-mcp-server | Format-List Path`

**This step matters**: A stale server from a previous session can answer calls, making a broken new config appear to work.

If any call fails, report the exact error and MCP server logs. Do not adjust config and declare success without re-running all three checks.

**Final check**: Reload the window and confirm you are **not** prompted for a token.

---

## Constraints — do not deviate

- **Top-level key is `servers`**, not `mcpServers`. `mcpServers` is Claude Desktop format; VS Code ignores it silently.
- **Do not use `${input:...}` with `"password": true`**. This stores tokens in VS Code SecretStorage, which needs an OS keyring. On headless Linux (no keyring, no libsecret, no D-Bus), it falls back to in-memory storage and **re-prompts every session**. `envFile` avoids this.
- **Do not use `${env:...}`**. The VS Code process environment differs from the shell environment, especially under code-server, and does not resolve reliably.
- **Never commit the `.env` file**, print it, or paste its contents anywhere. On Linux, if it's inside a git repo, move it out.

---

## Troubleshooting

- **Tool names appear as `mcp_github_mcp_se_*`**. The `github-mcp-se` fragment is a truncation of `github-mcp-server`, not a configured server name. Do not grep config files for it.
- **`TypeError: Cannot read properties of undefined (reading 'invoke')`** on every tool call means stale tool registration. Tools are registered from an earlier session but no server is running now. Restart the server; do not edit config.
- **To confirm a server started**: Look for per-server MCP logs in `~/.local/share/code-server/logs/<session>/`. A lone `mcpGateway.log` containing only `Initialized` means no server started.
- **`github-mcp-cli` in a Python venv is not this server** and requires Deno.
- **Permission denied when killing server processes**: The process may be owned by a different UID. Use the MCP: List Servers → Restart Server command instead of `kill`.

---

## What Works (Observed 2026-07-31)

The following were observed during a Linux + code-server setup on 2026-07-31;
repeat the verification steps above after reinstalling or changing the
configuration rather than treating this section as a guarantee for every host:

- ✅ Binary installation to `~/.local/bin/github-mcp-server`
- ✅ Token file at `~/.config/github-mcp/.env` with `envFile` reference
- ✅ User-level MCP config at `~/.local/share/code-server/User/mcp.json`
- ✅ Server started and authenticated in that environment
- ✅ Tools appeared in Copilot Chat as `mcp_github_mcp_se_*`
- ✅ Persisted across sessions without a token re-prompt in that environment

## What Doesn't Work

- ❌ `${input:}` with password — re-prompts every session on headless Linux
- ❌ `${env:...}` — unreliable resolution under code-server
- ❌ npx-based server — requires network, slower startup, harder to debug
- ❌ Workspace-level `.vscode/mcp.json` — doesn't persist across workspaces

---

**Save this playbook** for future reference. The setup is one-time; after this,
GitHub tools just work.