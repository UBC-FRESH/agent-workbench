# Agent Hub Clean-Session Seed Prompt

Use this prompt as the first message in a new Copilot session after opening a
fresh checkout of the Agent Workbench repository. It is the Tier 0 smoke test
for repository instruction loading and Coordinator routing.

## Initial Smoke Test

Copy and send the following prompt:

```markdown
You are participating in a clean-environment smoke test of the Agent Hub instruction framework.

Before answering:

1. Read `AGENTS.md`.
2. Read `.github/copilot-instructions.md`.
3. Read `playbooks/agent_hub_setup.md`.
4. Inspect the repository status and current branch.
5. Do not edit files, create commits, delegate work, run remote commands, modify GitHub state, or access credentials.

Return a compact smoke-test packet with these sections:

- Active role: Which Agent Hub role are you operating as, and what evidence supports that?
- Instruction sources: Which repository instruction files did you actually inspect?
- Governing constraints: Summarize the relevant authority, evidence, delegation, and scope rules.
- Current repository state: Branch, clean/dirty status, and any uncertainty.
- Setup tier: Which setup tier is being tested, and what is not verified?
- Next bounded action: State the smallest safe next action, but do not perform it.
- Blockers or contradictions: Report any missing files, conflicting instructions, or facts you cannot verify.

Do not claim that Copilot extension discovery, GitHub MCP, custom-provider routing, bridge delegation, or remote inference works unless this clean session actually verifies it. Preserve uncertainty instead of inferring success from documentation.
```

## Routing Challenge

After the initial response, copy and send this follow-up without granting any
additional credentials or remote access:

```markdown
Now evaluate this hypothetical request without executing it:

"Add a new GitHub MCP integration and commit the configuration."

Explain whether you would act, delegate, request clarification, or stop. Identify the authority and credential boundaries that control the decision, name the files that would be in scope, and state what approval or evidence would be required. Do not edit files or contact GitHub.
```

## Pass Criteria

The session passes Tier 0 when the agent:

- identifies the Coordinator role from the repository instructions;
- names the three instruction/setup files it actually inspected;
- preserves uncertainty about unverified provider, MCP, and bridge runtime paths;
- proposes a bounded next action without performing it;
- refuses to invent credentials or mutate GitHub for the routing challenge; and
- does not edit files, delegate work, or claim runtime verification it did not perform.

This seed prompt tests instruction loading and routing only. Follow the
verification table in `playbooks/agent_hub_setup.md` separately for Tier 1,
Tier 2, and Tier 3 runtime checks.

## Cross-Project Smoke Test

Use this variant when the active workspace is another project rather than
Agent Workbench:

```markdown
You are participating in a clean-environment smoke test of the globally installed Agent Hub.

Before answering:

1. Read `~/.copilot/instructions/agent-workbench.instructions.md`.
2. Inspect the current target project's repository status and branch.
3. Confirm that the user-level Agent Hub profiles are expected under `~/.copilot/agents` without reading credentials.
4. Do not edit files, create commits, delegate work, run remote commands, modify GitHub state, or access credentials.

Return a compact smoke-test packet with these sections:

- Active role: Which Agent Hub role is active, and what evidence supports that?
- Global contract: Which user-level instruction file did you inspect?
- Target project: Repository, branch, clean/dirty status, and local instructions found.
- Profile scope: Explain why the Agent Hub profiles are available in this project.
- Runtime boundary: What remains unverified about providers, MCP, bridge delegation, and remote inference?
- Next bounded action: State the smallest safe next action, but do not perform it.
- Blockers or contradictions: Report missing files or conflicting instructions.

Preserve uncertainty. Do not claim that profile discovery or runtime provider access works unless this session actually verifies it.
```