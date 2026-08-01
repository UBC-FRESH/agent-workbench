# Agent Hub Setup Playbook

Canonical setup guide for a clean-environment Copilot agent or human operator
on **Windows VS Code Desktop** or **Linux code-server**.

This is an interim documentation PR. Clean-environment manual testing remains
pending. The referential-integrity test (`tests/test_agent_hub_setup_playbook.py`)
verifies path and credential hygiene on the tracked content only; it does not
validate installation or runtime behaviour.

For the copy-paste first message and routing challenge, use the [Agent Hub
clean-session seed prompt](agent_hub_seed_prompt.md).

## Scope

This playbook covers how to reach the Agent Workbench Agent Hub from a fresh
install. It does **not** cover:

- Real-project deployment (see `playbooks/real_project_deployment.md`).
- HPC vLLM deployment (see `playbooks/vllm_blackwell/`).
- Cloudflare tunnel provider exposure (see
  `playbooks/cloudflared_model_provider.md`).
- VS Code Chat bridge for supervisor worker delegation (see
  `playbooks/vscode_chat_bridge.md`).
- Single-model operator checklist (see
  `playbooks/p118_single_model_operator_checklist.md`).
- Deployment environment operator posture (see
  `playbooks/deployment_environment_operator.md`).

There are two profile scopes:

- `.github/agents/*.agent.md` is workspace-scoped. It is discovered only when
  `agent-workbench` itself is the opened workspace.
- `~/.copilot/agents/*.agent.md` is user-scoped. It is discovered across other
  Copilot workspaces on the same account and machine.

To make the full Agent Hub contract available to other projects, run this from
a checkout of Agent Workbench:

```bash
python scripts/install_agent_hub_profiles.py
python scripts/install_agent_hub_profiles.py --check
```

On Windows, use `py` instead of `python` if that is the configured launcher.
The default destinations are `~/.copilot/agents` for profiles and overlays, and
`~/.copilot/instructions/agent-workbench.instructions.md` for the full contract
(`%USERPROFILE%\\.copilot\\...` on Windows). Overlays are placed under
`~/.copilot/agents/overlays/`. The installer copies the four core profiles, the
standard overlays, and the contract; it leaves unrelated target projects untouched and refuses to
overwrite conflicting user files unless `--replace` is supplied explicitly.
Reload the editor after installation and open the Copilot agent picker in the
target project.

This installs both the custom-agent definitions and the Agent Hub contract
globally. Target-project instructions remain target-project-specific and can
add constraints; they do not need a copy of Agent Workbench's files.

The default install exposes four portable core roles:
`agent-workbench-coordinator`, `agent-workbench-supervisor`,
`agent-workbench-worker`, and `agent-workbench-advisor`. Specialized behavior
is supplied through the Markdown overlays in `~/.copilot/agents/overlays/` and
is not a fifth role. When a task names an overlay, apply that overlay's prompt
additively to the selected core role. The active model and provider are selected
by the operator's deployment; core profiles do not impose a model alias or
provider.

## Tiered Setup

The Agent Hub supports four capability tiers. Each tier adds a provider layer
on top of the previous one. Start at Tier 0 and only advance when the lower
tier is working.

### Tier 0 -- Stock Copilot + Repo Profiles (Verified: Linux code-server)

**What you get:** Built-in GitHub Copilot with the paid model lane and the
Agent Workbench agent profiles installed. Run the user-profile installer above
if those profiles must be available outside the Agent Workbench workspace.

**Verified platform:** Linux code-server 1.128.0 (VS Code commit
`cb22f74650a539d6f82444ec34d9e74844f66`). Windows Desktop unverified.

**Steps:**

1. Install VS Code (Windows) or code-server (Linux) from the official source.
2. Sign in to your GitHub account in the editor.
3. Install the `github.copilot` extension and accept the paid plan prompt if
   you want the paid model lane.
4. Clone the Agent Workbench repo and open the workspace root.
5. The repo ships `.github/agents/*.agent.md` profiles and
  `.github/copilot-instructions.md`. Copilot picks these up automatically
  from the workspace. For other projects, install the profiles and global
  contract with `scripts/install_agent_hub_profiles.py`.
6. Verify the active agent profile by asking Copilot to describe its role.
  This confirms profile discovery and instruction loading; it does not select
  or validate a provider for the operator.
7. Run one bounded smoke request using the operator-selected model/provider.
  Record the returned model/provider identity separately from the role name.

Use [`playbooks/agent_hub_seed_prompt.md`](agent_hub_seed_prompt.md) as the
first clean-session request when testing these steps.

**Tier 0 boundary:** Stock Copilot proves repository profile discovery and the
built-in paid-model lane. It does not provide the documented free-local model
economics or resolve a private custom endpoint by itself.

**What is NOT covered here:**

- Custom local or remote model providers (Tier 2).
- GitHub MCP server configuration (Tier 1).
- Third-party Copilot extensions (Tier 2).

**Credential boundary:**

- Never type your Copilot token, OAuth token, or provider header into a chat
  prompt.
- Environment variables and config files for endpoints/headers go in untracked
  files only (e.g. `<user-home>/.local/share/code-server/User/mcp.json`).
- Never commit endpoint URLs, authorization headers, personal home paths, or
  credential store references.

### Tier 1 -- GitHub MCP Server (Reference Playbook)

**What you get:** GitHub model-context-protocol integration for repository
operations, issue management, and search.

**Prerequisites:** GitHub MCP server installed and configured in your editor's
MCP configuration.

**Setup guide:** See [`playbooks/github_mcp_setup.md`](playbooks/github_mcp_setup.md).

**Credential boundary:** Same as Tier 0. MCP tokens go in untracked config
files only.

### Tier 2 -- Custom Local/Remote Provider (Reference Playbook)

**What you get:** A custom model provider, either local (Ollama, vLLM on a
remote host) or remote (third-party API).

**Prerequisites:**

- A running model server or third-party API endpoint.
- A compatible Copilot extension that accepts custom provider configuration.
- Provider credentials (API keys, tokens) obtained from the provider.

**Setup guide:** See
[`notes/operations/keklick-copilot-extension-config.md`](notes/operations/keklick-copilot-extension-config.md).

**Provider.js patching:** Explicitly out of scope. Do not attempt to patch
`provider.js` or any extension internals. If your provider requires a
`provider.js` change, this setup path does not support it.

**Credential boundary:**

- Never request provider tokens or API keys via chat.
- User fills empty env/config files themselves.
- On Linux: `chmod 600` the config file. On Windows: use `icacls` to restrict
  access.
- Never copy keychains or browser profiles into the workspace.
- Never commit endpoint URLs, headers, or personal paths.

### Tier 3 -- Bridge / Scripts (Optional)

**What you get:** Supervisor-directed worker delegation through the VS Code
Chat bridge, plus operator runbooks.

**Setup guide:** See [`playbooks/vscode_chat_bridge.md`](playbooks/vscode_chat_bridge.md).

**Operator checklists:**

- [`playbooks/p118_single_model_operator_checklist.md`](playbooks/p118_single_model_operator_checklist.md)
  -- single-model session launch checklist.
- [`playbooks/deployment_environment_operator.md`](playbooks/deployment_environment_operator.md)
  -- supported operating posture and permission-mode expectations.

## Pass/Fail Smoke Checklist

Run through this checklist after setup. Mark each item as pass or fail.

- [ ] Copilot extension is installed and signed in.
- [ ] Opening the repo root loads `.github/copilot-instructions.md` without
  errors.
- [ ] Asking Copilot about the agent profiles returns a coherent description
  of the Coordinator role.
- [ ] The paid model lane is accessible (Tier 0) or the custom provider is
  responding (Tier 2+).
- [ ] No endpoint URLs, headers, or tokens appear in tracked files
  (`git grep -n 'http[s]://' -- '*.md'` returns only this playbook's generic
  examples).
- [ ] Environment config files for providers are listed in `.gitignore` or
  live outside the workspace tree.
- [ ] If testing from another project, the expected profiles exist under
  `~/.copilot/agents`, the contract exists under
  `~/.copilot/instructions/agent-workbench.instructions.md`, and the editor has
  been reloaded.

## Verification Table

| Item                              | Linux code-server | Windows VS Code Desktop |
| --------------------------------- | ----------------- | ----------------------- |
| code-server / VS Code version     | 1.128.0           | unverified              |
| VS Code commit                    | cb22f74650a539d6  | unverified              |
| `github.copilot` extension        | verified          | unverified              |
| `keklick1337.keklick-copilot` ext | verified          | unverified              |
| `continue.continue` extension     | verified          | unverified              |
| `ms-azuretools.vscode-azure-mcp`  | verified          | unverified              |
| Tier 0 stock Copilot lane         | verified          | unverified              |
| Tier 1 GitHub MCP                 | unverified        | unverified              |
| Tier 2 custom provider            | unverified        | unverified              |
| Tier 3 bridge delegation          | unverified        | unverified              |
| Credential boundary enforcement   | verified          | unverified              |

**Legend:** "verified" = observed on the current Linux code-server build.
"unverified" = not tested on a clean environment; manual smoke test required.

## Operating Loop

Once the Agent Hub is set up, the operating loop for supervised multi-agent
work is:

1. Read [`playbooks/p118_single_model_operator_checklist.md`](playbooks/p118_single_model_operator_checklist.md)
   before launching a session.
2. Confirm the active agent profile and model identity.
3. Write a bounded ticket to `runtime/agent_jobs/<task>_ticket.md`.
4. Delegate to the appropriate worker via the coordinator or bridge.
5. Inspect compact evidence, not raw transcripts.
6. Verify independently. Do not trust prose claims.
7. Accept, issue one bounded repair, or escalate.

Full operator posture details are in
[`playbooks/deployment_environment_operator.md`](playbooks/deployment_environment_operator.md).

## Related Documents

- [`AGENTS.md`](../AGENTS.md) -- agent operating contract.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) -- contributor workflow rules.
- [`ROADMAP.md`](../ROADMAP.md) -- active phase/task plan.
- [`CHANGE_LOG.md`](../CHANGE_LOG.md) -- append-only project narrative.
- [`playbooks/cli_workflow.md`](cli_workflow.md) -- CLI workflow.
- [`playbooks/real_project_deployment.md`](real_project_deployment.md) -- real-project deployment.
- [`playbooks/vscode_chat_bridge.md`](vscode_chat_bridge.md) -- chat bridge delegation.
- [`playbooks/p118_single_model_operator_checklist.md`](p118_single_model_operator_checklist.md) -- operator checklist.
- [`playbooks/deployment_environment_operator.md`](deployment_environment_operator.md) -- operator posture.
- [`model_profiles/`](../model_profiles/) -- worker model capability notes.