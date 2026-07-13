# Native Codex With a Remote Ollama Provider: Findings and Pivot Rationale

Date: 2026-07-12

Status: locally proven feasibility; nested delegation not yet proven

Scope: public-safe technical findings and proposed Agent Workbench direction

## Executive Summary

Agent Workbench does not need GitHub Copilot Chat or the Copilot SDK merely to
make a remote, self-hosted Ollama model available to an agent runtime. The
installed Codex CLI can use an OpenAI-compatible model provider directly through
its Responses API support.

Two local probes established the important lower-level capabilities:

1. Codex successfully sent a native Responses request to the configured remote
   Ollama provider and received the exact requested completion marker.
2. The same provider/model successfully participated in a Codex tool loop:
   the model requested a PowerShell command, Codex executed it under a read-only
   policy, returned the command result, and the model produced the expected
   final marker.

This materially changes the development direction. The Copilot-specific bridge
is no longer a prerequisite for free-model delegation. Existing Copilot work
remains useful historical evidence and may remain a secondary interoperability
lane, but the preferred next experiment is native Codex multi-agent delegation.

The decisive unproven claim is still the full hierarchy:

```text
paid Codex Coordinator
  -> custom Codex Supervisor using the configured Ollama provider
       -> custom Codex Worker using the configured Ollama provider
```

No tracked documentation should describe that chain as working until persisted
Codex session evidence proves both delegation edges and the expected provider
and model identities.

## Why This Matters

The earlier Copilot lane combined several independently fragile layers:

- VS Code Chat agent selection;
- custom-agent frontmatter and model selection;
- VS Code terminal and shell integration;
- Copilot SDK process launch and session behavior;
- an OpenAI-compatible provider bridge; and
- Supervisor-to-Worker delegation behavior.

That stack made failures difficult to localize. In particular, a failure could
be reported as missing PowerShell, a missing script, a model-selection mismatch,
or a delegation failure even when the underlying host capabilities existed.

Native Codex removes the Copilot-specific layers from the critical path. Codex
can own the conversation, tools, sandbox, agent profiles, and delegation while
using Ollama only for model inference. This is a simpler architecture and is
better aligned with the Agent Workbench objective: a thin paid Coordinator that
delegates most bounded work to lower-cost Supervisor and Worker agents.

## Environment and Documentation Audit

The local feasibility audit used `codex-cli 0.144.0-alpha.4`.

The current Codex documentation supports the required configuration concepts:

- custom model providers in Codex configuration;
- an explicit provider `base_url`;
- `wire_api = "responses"`;
- request headers sourced from environment variables with
  `env_http_headers`; and
- project custom agents defined as TOML files under `.codex/agents/`.

Custom agents may specify their own model and other configuration overrides.
Codex also exposes an agent-depth setting. A Coordinator -> Supervisor -> Worker
experiment requires a depth of at least two; the default depth of one is not
sufficient for the second delegation edge.

Relevant official references:

- [Codex configuration reference](https://developers.openai.com/codex/config-reference#configtoml)
- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [OpenAI model selection](https://developers.openai.com/api/docs/models)
- [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)

Documentation describes capability, not local success. The two probes below
provide the local execution evidence.

## Provider Configuration Pattern

The successful private probe used this public-safe configuration shape:

```toml
model = "<installed-ollama-model>"
model_provider = "agent_workbench_ollama"
model_reasoning_effort = "low"

[model_providers.agent_workbench_ollama]
name = "Agent Workbench Ollama"
base_url = "<configured-openai-compatible-url-with-v1-suffix>"
wire_api = "responses"
env_http_headers = {
  "CF-Access-Client-Id" = "AW_CF_CLIENT_ID",
  "CF-Access-Client-Secret" = "AW_CF_CLIENT_SECRET",
  "User-Agent" = "AW_PROVIDER_USER_AGENT"
}
```

Important boundaries:

- The real endpoint and credential values remain local and ignored.
- `env_http_headers` stores environment-variable names, not secret values.
- The OpenAI-compatible base URL includes the `/v1` suffix.
- A non-reserved custom provider identifier should be used. Do not assume that
  a built-in provider name can be redefined.
- Provider configuration alone does not prove that a request reached the
  intended model. Persisted session evidence remains authoritative.

The private probe configuration is under ignored `runtime/` storage. It must
not be copied verbatim into a tracked file because it contains a machine-local
provider URL.

## Probe 1: Native Responses Completion

### Question

Can the installed Codex CLI use the configured remote Ollama endpoint as a
native custom Responses provider and complete a minimal no-tool turn?

### Method

- Created an isolated, ignored `CODEX_HOME` for the probe.
- Selected the configured Ollama model explicitly.
- Configured the provider with `wire_api = "responses"`.
- Loaded Cloudflare Access header values into temporary environment variables.
- Ran Codex in a read-only, non-interactive mode.
- Requested one exact output marker and prohibited tools.

### Evidence

The persisted rollout records:

- model: `qwen3-coder:latest`;
- final assistant output: `CODEX_OLLAMA_OK`;
- task-complete event present; and
- duration of approximately 4.4 seconds.

### Verdict

Accepted. Native Codex-to-Ollama Responses inference is locally proven for the
configured provider and model.

## Probe 2: Native Tool Loop

### Question

Can the Ollama-backed model participate in a real Codex tool loop on Windows,
rather than merely return text?

### Method

Codex asked the model to use exactly one shell command to read the first line of
`README.md`, then return a marker containing that line. The session used a
read-only sandbox.

### Evidence

The persisted rollout records this sequence:

1. Codex turn context selected `qwen3-coder:latest` with a read-only sandbox.
2. The model emitted a `shell_command` function call.
3. The requested command was:
   `Get-Content -Path "README.md" -TotalCount 1`.
4. Codex executed the command successfully and returned
   `# Agent Workbench` to the model.
5. The model returned `TOOL_OK: # Agent Workbench`.
6. A task-complete event recorded the same final marker.

### Verdict

Accepted. The configured Ollama model can request a Codex tool, receive the
tool result, and complete the turn correctly on this Windows workspace.

This proves more than endpoint compatibility. It proves that the native Codex
agent loop can mediate tool execution for the remote model.

## What Is Proven

- The configured remote host implements the Responses behavior needed by this
  Codex version for the tested request shapes.
- Cloudflare Access headers can be supplied through Codex provider
  configuration without embedding their values in tracked files.
- `qwen3-coder:latest` can complete a native Codex no-tool turn.
- `qwen3-coder:latest` can emit a valid Codex shell tool call.
- Codex can execute the requested PowerShell command and return its result.
- The model can consume that result and stop with the requested final marker.
- The Copilot Chat environment is not required for these capabilities.

## What Is Not Yet Proven

- A custom Ollama Supervisor can spawn a second custom Ollama Worker.
- Both delegation edges are visible in durable session evidence.
- A Supervisor can monitor, nudge, validate, and stop a Worker economically.
- The TSA23 extraction workflow succeeds through the native nested hierarchy.
- Native Codex delegation is cheaper or more reliable than the earlier paths;
  that requires measured runs, not architectural intuition.
- VS Code-hosted Codex inherits the provider-header environment variables in a
  convenient and safe way. The successful probes used a controlled CLI process.

Direct Coordinator fan-out to configured OpenAI and Ollama child roles is now
proven in a fresh VS Code Codex session. The first recursive probe was invalid
because Codex applied the unset `agents.max_depth` default of `1`, leaving the
depth-`1` Supervisor unable to create a depth-`2` Worker. Project configuration
now explicitly sets `max_depth = 2` with six available threads; a fresh-session
recursive probe must capture the second delegation edge before it is accepted.

## Warnings and Non-Blocking Observations

The successful probe emitted warnings that should be separated from blockers:

- The custom Ollama model was unknown to Codex's built-in model catalog, so
  Codex used fallback model metadata. A durable setup should declare the known
  context window or provide an appropriate model catalog entry.
- Telemetry objected to a colon in the Ollama model tag. This did not prevent
  inference or tool use.
- PowerShell shell snapshots were unavailable. This did not prevent the tool
  command from running.
- The isolated probe home lacked the normal account/plugin state and emitted an
  unrelated plugin-cache authentication warning. This did not affect the custom
  provider request.

These warnings should be cleaned up where practical, but none invalidates the
two accepted probe results.

## Proposed Agent Roles and Escalation Relationships

The target is not the largest possible agent hierarchy. It is a small hierarchy
that spends expensive reasoning only where it changes the outcome:

```text
Coordinator: fast, low-cost paid GPT; owns orchestration and acceptance
  |
  +-- Advisor: expensive deep-thinking GPT; mandatory at defined decision gates
  |
  +-- Supervisor: free Ollama model; decomposes and verifies bounded work
        |
        +-- default Worker(s): free Ollama models
        |
        +-- paid rescue Workers: economy -> balanced -> premium escalation
```

This is a quality ladder, not an ideology that free models must finish every
task. Repeatedly sending an unsuitable task back to free Workers is not cost
discipline. It spends Coordinator attention, increases latency, pollutes
context, and still fails to deliver useful work. The system needs a deliberate
point at which it buys a stronger Worker instead of continuing to thrash.

## Coordinator Role and Model Candidates

The Coordinator should be the cheapest and fastest paid GPT configuration that
still reliably performs these duties:

- interpret a loosely specified maintainer goal;
- inspect current repository and governance state;
- convert the goal into a small number of bounded Supervisor assignments;
- monitor without constant polling or narration;
- recognize stalls, protocol defects, and missing evidence;
- invoke the Advisor and paid-worker escape hatches at the right time;
- independently verify returned evidence; and
- own commits, GitHub actions, acceptance decisions, and completion claims.

Implementation nuance: in the target hierarchy the Coordinator is normally the
root Codex session, not a spawned subagent. Its durable model/reasoning defaults
may therefore belong in a named Codex launch profile plus Coordinator
instructions, while Supervisor, Advisor, and Worker roles belong in
`.codex/agents/*.toml`. A Coordinator custom-agent file is useful only when some
other root session will spawn that Coordinator. The role contract should stay
the same regardless of which configuration surface launches it.

Official model guidance currently describes GPT-5.6 Luna as the cost-sensitive
GPT-5.6 option, Terra as the intelligence/cost balance, and Sol as the flagship
for complex reasoning and coding. Codex custom agents can pin both `model` and
`model_reasoning_effort`. In TOML the relevant low-effort value is `"low"`;
the product UI may describe the corresponding intelligence setting as Light.

Recommended candidate order:

1. **Default candidate: `gpt-5.6-luna` with `model_reasoning_effort = "low"`.**
   This is the most promising starting point because coordination is frequent,
   much of it should be procedural, and the current Luna/Light delegation trial
   has been qualitatively encouraging. It still needs a repeatable reliability
   evaluation before becoming the durable default.
2. **Cost challenger: `gpt-5.4-mini` with medium or low effort.** Official
   documentation describes GPT-5.4 mini as suited to coding, computer use, and
   subagents. It may be attractive for tightly specified coordination, but it
   should not be assumed to handle ambiguous workflow recovery as well as the
   GPT-5.6 family without evidence.
3. **Reliability fallback: `gpt-5.6-terra` with low effort.** Use this if Luna
   misses escalation triggers, loses workflow state, or produces unreliable
   acceptance decisions. Terra is the natural middle tier before paying for a
   flagship Coordinator.
4. **Expensive control: `gpt-5.6-sol` with low effort.** This tests whether a
   stronger base model at low reasoning effort is more reliable or more
   economical overall than a smaller model that requires repairs. It should be
   a benchmark/control, not the presumed default.

Do not choose from price labels alone. API list prices may not match the
effective accounting of a particular Codex subscription or product surface.
The project should benchmark each available candidate on the same small suite
and record observed token spans, latency, retries, Advisor calls, false
completion claims, and final acceptance quality.

Minimum Coordinator promotion suite:

- loose goal -> coherent Supervisor ticket without maintainer micromanagement;
- successful native Supervisor delegation and evidence collection;
- recognition of a deterministic Worker failure;
- correct Advisor invocation at a mandatory trigger;
- correct paid-worker escalation after free-worker exhaustion;
- refusal to escalate when the blocker is environmental rather than cognitive;
  and
- correct final separation of quality, protocol, and economics verdicts.

The default should be the lowest-cost candidate that passes the suite at the
required reliability threshold, not simply the model with the cheapest nominal
tokens.

## Advisor Role and Mandatory Invocation Policy

The Advisor is a bounded, expensive second opinion. It should use a strong model
and higher reasoning effort because it is invoked rarely and specifically when
better judgment is worth more than speed.

Recommended starting configuration:

- model: `gpt-5.6-sol`;
- reasoning effort: `high` for normal consultations;
- reasoning effort: `xhigh` or `max` only for an explicitly bounded exceptional
  audit when the selected model and product surface support it;
- sandbox: read-only by default; and
- authority: advise and audit, but do not mutate tracked files, GitHub state,
  provider configuration, or final acceptance state.

Useful Advisor jobs include:

- deciding between materially different architecture or workflow approaches;
- checking a plan before a high-blast-radius or difficult-to-reverse change;
- diagnosing a repeated failure when the Coordinator's current theory is not
  producing new evidence;
- reviewing a proposed exception to delegation or cost policy;
- auditing whether a roadmap phase is genuinely ready for closeout;
- challenging a public readiness, security, economics, or quality claim;
- resolving conflicting Supervisor reports or ambiguous validation evidence;
- deciding whether a task deserves a paid rescue Worker; and
- performing postmortem analysis when a run consumed its retry budget.

A vague instruction such as "use the Advisor when helpful" is not sufficient.
Current Codex documentation says local Codex delegates after a direct request or
when applicable project or skill instructions request it. Therefore Advisor use
should be encoded as explicit mandatory gates in the Coordinator profile and
durable repository instructions.

The Coordinator **must consult the Advisor** before proceeding when any of these
triggers occurs:

- **stuck trigger:** two attempts, nudges, or hypotheses have failed to produce
  materially new evidence;
- **big-swing trigger:** the next action changes architecture, provider setup,
  public API, data model, permission boundary, roadmap direction, or many files;
- **closeout trigger:** a phase, release, public-readiness claim, or other
  externally visible milestone is about to be declared complete;
- **uncertainty trigger:** important evidence conflicts, the acceptance basis is
  mostly judgment, or the Coordinator cannot state why its plan should work;
- **policy-exception trigger:** the Coordinator proposes overriding a delegation,
  security, cost, privacy, or governance default;
- **paid-escalation trigger:** the Supervisor requests a paid rescue Worker; or
- **budget trigger:** a live run is about to exceed its approved paid-token,
  retry, or elapsed-time budget.

Advisor invocation should produce a small auditable consultation packet:

- decision or question being reviewed;
- evidence already inspected;
- options considered;
- Coordinator's current recommendation;
- requested Advisor output;
- Advisor verdict and confidence;
- Coordinator decision after receiving the advice; and
- explanation when the Coordinator does not follow the advice.

The policy needs enforcement as well as prose. Candidate mechanisms, in order
of increasing strength:

1. Put the mandatory triggers directly in the Coordinator custom agent's
   `developer_instructions`.
2. Give the Advisor a precise `description` naming these trigger situations so
   Codex can select it correctly.
3. Repeat the gates in the applicable `AGENTS.md` or a required coordination
   skill so they enter each relevant task context.
4. Require an `advisor_consulted`, `advisor_not_required`, or
   `advisor_required_but_blocked` field in decision and closeout artifacts.
5. Make deterministic closeout validation fail when a mandatory trigger is
   present but no Advisor evidence exists.

This makes "why did you not invoke the Advisor?" answerable from evidence and
reduces dependence on the maintainer noticing that the Coordinator is stuck.

## Free Workers and Paid Rescue Workers

The Supervisor should prefer free Ollama Workers, but it should not be forced to
repeat a failing strategy indefinitely. The desired escalation ladder is:

1. Delegate one bounded ticket to an appropriate installed Ollama Worker.
2. Independently inspect the artifact or validator result.
3. Allow one targeted repair, alternative decomposition, or different installed
   Ollama Worker only when the first failure identifies a concrete fix.
4. If the result remains unacceptable, stop free-worker retries and write a
   paid-escalation request.
5. Consult the Advisor when the escalation meets a mandatory trigger.
6. Launch one low-cost paid rescue Worker under the approved scope and budget.
7. Have the free Supervisor verify the paid Worker's artifact; the paid Worker
   does not become the acceptance authority.
8. If the result is still unacceptable, stop and write a new escalation packet
   identifying the exact defects that survived the cheaper paid attempt.
9. Use a balanced or premium paid Worker only when that evidence justifies the
   higher tier and the remaining mission budget permits it.
10. Return the evidence and verdict to the Coordinator.

The paid ladder should have three distinct profiles:

| Tier | Suggested role | Starting model/effort | Intended use |
| --- | --- | --- | --- |
| P1 economy | `paid_economy_worker` | `gpt-5.4-mini` at `medium`, or `gpt-5.6-luna` at `low` | First paid attempt for a narrow task that exceeded the available Ollama Workers. |
| P2 balanced | `paid_balanced_worker` | `gpt-5.6-terra` at `medium` | Second-line rescue when P1 produced useful evidence but did not reach acceptance. |
| P3 premium | `paid_premium_worker` | `gpt-5.6-sol` at `high` | Last-resort specialist for unusually ambiguous, high-risk, or cross-cutting work. |

These are starting candidates, not permanent assignments. The economy tier
should be benchmarked with both GPT-5.4 mini and Luna because the cheapest
nominal token price may not produce the lowest total mission cost after retries.

All paid rescue tiers have the same authority boundary:

- purpose: one bounded implementation, debugging, analysis, or repair task that
  exceeded the demonstrated capability of the lower tiers;
- authority: the same narrow file/tool boundary as the failed ticket; and
- stop condition: one primary attempt plus at most one exact-defect repair if
  the mission budget explicitly permits it.

P2 requires evidence from P1, and P3 requires evidence from both lower-cost
paths or a documented reason they are clearly unsuitable. P3 also requires an
Advisor recommendation and explicit Coordinator approval. A stronger paid
Worker is useful only when it receives a clean failure packet rather than being
asked to rediscover the entire problem.

The paid-escalation request must include:

- original task and acceptance criteria;
- free Worker model(s) and attempts used;
- exact artifacts and validators inspected;
- concrete defects that remain;
- why another free retry is unlikely to help;
- why the blocker is cognitive rather than environmental;
- proposed paid model, reasoning effort, token/span budget, and stop condition;
  and
- files, commands, and authority granted to the paid Worker.

Do **not** spend paid Worker tokens when the actual blocker is a missing file,
credential, permission, executable, dependency, requirement, or maintainer
decision. A stronger model cannot reason its way past absent authority or state.

The Supervisor may invoke a paid rescue Worker without a fresh maintainer prompt
only when the enclosing mission explicitly pre-authorizes that escalation,
defines its budget, and the request satisfies the evidence gates above.
Otherwise, the Coordinator must request approval. This preserves automation
without turning a free-worker failure into an unbounded paid fan-out.

A paid-tier failure ends that tier unless its output exposes a single exact,
low-risk repair already covered by the budget. The system must not automatically
walk through every paid tier. By default, no mission may traverse more than two
paid tiers without fresh maintainer approval. It must return a useful failure
packet, not a vague apology and another invitation to retry.

## Recommended Architecture Direction

Treat native Codex as the primary orchestration host:

- paid OpenAI model: thin Coordinator;
- configured Ollama model: default Supervisor;
- configured Ollama models: bounded Workers;
- paid Advisor: selective but mandatory at explicit decision gates;
- tiered paid GPT rescue Workers: economy first, stronger models only after
  evidence-gated escalation;
- Codex custom-agent TOML: role definitions and provider/model overrides;
- `AGENTS.md` and skills: durable shared workflow rules;
- ignored `runtime/` artifacts: tickets, results, transcripts, and proof; and
- deterministic validators: acceptance authority wherever possible.

Copilot-specific assets should not be deleted impulsively. They preserve useful
comparative evidence and may remain valuable for users who prefer that host.
However, new core workflow investment should not assume Copilot is the only
route to a remote Ollama provider.

## Next Bounded Experiment

The next experiment should answer exactly one question:

> Can one native Codex Coordinator spawn an Ollama-backed Supervisor that in
> turn spawns an Ollama-backed Worker, with persisted evidence of both edges and
> a deterministic final proof artifact?

Use trivial work. The content is not under test; delegation is.

Suggested acceptance evidence:

- Coordinator session identifies the paid Coordinator model/provider.
- Supervisor session identifies the expected custom agent and Ollama model.
- Worker session identifies the expected custom agent and Ollama model.
- Worker writes or returns a unique marker.
- Supervisor independently observes the marker and returns a second marker.
- Coordinator inspects both pieces of evidence and records an acceptance
  decision.
- Session records show two actual spawn/delegation edges, not prose claims.
- No tracked files, Git state, GitHub state, provider configuration, or model
  inventory are mutated by the proof job.

Cost discipline for this gate:

- one paid Coordinator session;
- one Supervisor session;
- one Worker session;
- no continuous polling;
- at most one evidence-based repair after a concrete, understood defect; and
- stop after two unsuccessful attempts in this lane.

Only after this proof should the project run a substantive TSA23 extraction job
through the native hierarchy.

## Repository and Governance Implications

This finding is project-shaping, but it does not erase the active workflow
contract. At the time of writing:

- P100 issue `#603` is open;
- PR `#604` is open from `feature/p100-public-alpha-readiness-review` to `main`;
  and
- the worktree already contains unrelated maintainer changes that must be
  preserved.

Before implementing the native Codex profile and bootstrap surfaces, the next
session should explicitly place that work inside the active roadmap/issue lane
or finish P100 and activate the next phase. It must not silently open an
unapproved parallel phase.

Any tracked implementation must remain generic and public-safe:

- no personal hostnames or home-directory paths;
- no credentials or literal provider-header values;
- no private TSA document contents;
- no raw session transcripts; and
- no claim of nested delegation until the proof exists.

## Decision

Proceed with native Codex/Ollama integration as the preferred next technical
lane. Preserve the Copilot bridge as historical and optional interoperability
work, but stop treating it as a prerequisite for low-cost delegated agents.

The immediate gate is the minimal native Coordinator -> Supervisor -> Worker
proof. The substantive TSA23 delegation job comes afterward.
