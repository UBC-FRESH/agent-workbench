# Deployment Environment And Operator Playbook

This playbook describes the supported public-safe operating posture for Agent
Workbench local-supervisor workflows in VS Code or code-server.

Use it before launching local Copilot/Ollama work. The goal is to prevent stale
sessions, wrong-root execution, model mismatches, missing budgets, and repeated
paid-supervisor coordination after the useful learning signal is already
visible.

## Supported Runtime Shape

The supported setup has these components:

- a project checkout that contains `AGENTS.md`, `ROADMAP.md`, `CHANGE_LOG.md`,
  and ignored runtime paths;
- VS Code or code-server with Copilot Chat available;
- a configured Ollama-backed model provider visible to Copilot Chat or the
  Agent Workbench SDK path being used;
- an explicit local model inventory captured before model-specific work;
- deterministic scripts or validators for anything that must be reproducible;
- ignored runtime folders for raw prompts, tickets, transcripts, provider
  details, token traces, and worker outputs; and
- tracked public-safe summaries only after supervisor review.

Supported launch surfaces:

- `code chat --mode agent` and the local bridge described in
  `playbooks/vscode_chat_bridge.md`;
- the Agent Workbench SDK/eval path when a manifest already exists; and
- manual visible Copilot Chat sessions when the operator records enough
  evidence to prove model, root, permission, and output state.

The operator must not track private endpoint names, access headers, server
addresses, credentials, personal home paths, or raw transcripts.

## Permission Mode Expectations

Use the narrowest permission mode that can answer the ticket.

| Mode | Use When | Stop If |
| --- | --- | --- |
| Ask or no-tool mode | The worker only needs to classify, summarize, or draft. | The worker claims it edited files or ran commands. |
| Default approvals | The worker may need visible tool use and the operator wants review. | Approval prompts obscure whether the worker completed the ticket. |
| Bypass approvals | The ticket is bounded to ignored paths and the operator is watching evidence. | The worker touches tracked files or GitHub state. |
| Autopilot | The run is a local-supervisor experiment with a budget gate and stop rule. | The worker loops, changes scope, or loses the expected model/root. |

Do not use autopilot as a substitute for a precise ticket. Autopilot is only
acceptable when the ticket already has allowed actions, stop conditions, output
paths, and verification requirements.

## Runtime Paths

Raw runtime material stays ignored.

Recommended local paths:

- tickets: `runtime/agent_jobs/<run_id>.ticket.md`
- worker results: `runtime/agent_jobs/<run_id>.result.md`
- supervisor reports: `runtime/agent_jobs/<run_id>.supervisor.md`
- transcripts: `tmp/transcripts/<run_id>.md`
- provider traces: `runtime/provider_traces/<run_id>/`
- token ledgers: `runtime/supervisor_tokens/<run_id>/`
- target-project pilots: `<target-project>/tmp/agent_workbench/<phase>/`

Tracked files may contain only sanitized summaries, templates, playbooks,
planning notes, aggregate counts, and public-safe source identifiers.

## Pre-Run Checklist

Run only when every required item is true.

Environment:

- [ ] The active workspace root is the intended project root.
- [ ] `git status --short --branch` is understood before the run.
- [ ] Ignored runtime output paths exist or will be created by deterministic
      tooling.
- [ ] Provider credentials and endpoints are already configured outside tracked
      files.

Model inventory:

- [ ] The model comes from the configured Ollama host inventory.
- [ ] The model name is recorded exactly as the runtime will see it.
- [ ] The ticket does not ask for a model that is merely planned or still
      installing.
- [ ] Model-specific claims will be blocked unless evidence confirms the
      expected model was used.

Ticket:

- [ ] The ticket has a high-entropy run ID.
- [ ] The ticket names allowed files, commands, tools, and output paths.
- [ ] The ticket states stop conditions.
- [ ] The ticket says what final evidence must be written or reported.
- [ ] The ticket does not ask the worker to close issues, merge PRs, publish
      releases, or make final phase-completion claims.

Budget and economics:

- [ ] A P59 budget record exists for any run that will support economics
      claims.
- [ ] Paid-supervisor token checkpoints are defined for supervisor-owned spans.
- [ ] The maximum attempts and maintainer checkpoint are explicit.
- [ ] The run will stop after the declared learning signal or stop condition.

## Launch Checklist

Before launch:

- [ ] Attach only the files the worker needs.
- [ ] Prefer pre-materialized tickets over open-ended chat instructions.
- [ ] Avoid `--maximize` unless the operator explicitly wants VS Code layout
      changes.
- [ ] Keep the visible chat session observable when testing local-supervisor
      behavior.

During launch:

- [ ] Confirm the visible conversation starts from the expected ticket.
- [ ] Watch for immediate model/root/permission mismatch.
- [ ] Cancel if the worker begins repeating completion summaries.
- [ ] Cancel if the worker asks to broaden scope without a supervisor decision.

After launch:

- [ ] Record whether the expected output file exists.
- [ ] Record whether the expected run ID appears in the output.
- [ ] Record whether the claimed model/root/permission surface matches the
      ticket.
- [ ] Preserve raw outputs only in ignored runtime paths.

## Evidence Collection Checklist

Worker prose is not proof. Verify the underlying surfaces.

- [ ] Inspect output files directly.
- [ ] Inspect any command evidence the worker claims.
- [ ] Inspect Git state and diffs when files may have changed.
- [ ] Validate JSON, JSONL, Markdown, or schema outputs with deterministic
      tools when available.
- [ ] Classify outcomes using P60 semantics:
      `quality_validated_candidate`, `protocol_accepted_candidate`,
      `economics_usable`, `final_decision`, and `rejection_reasons`.
- [ ] Record stale, aborted, malformed, or loop-contaminated runs as diagnostic
      evidence, not successful economics evidence.
- [ ] Promote only sanitized aggregate findings to tracked files.

## Do-Not-Run Gates

Do not launch the worker when:

- no budget record exists for an economics run;
- the workspace root is uncertain;
- the requested model is not in the live Ollama inventory;
- prior chat-session evidence may be stale or contaminated;
- the ticket lacks a stop condition;
- the ticket requires tracked-file mutation by the worker;
- the ticket asks the worker to mutate GitHub state;
- two attempts in the same lane have already failed or become protocol-noisy;
- raw private data would need to be pasted into the chat; or
- the next action is a supervisor-only responsibility such as PR merge, issue
  closure, release publication, or final phase-completion claim.

## Troubleshooting

### Stale Chat Session

Symptoms:

- output references an old run ID;
- the visible chat answers a prior ticket;
- stored evidence shows a different model or permission state;
- the worker reports work that does not exist on disk.

Response:

- cancel the current chat request;
- start a fresh chat session;
- use a new high-entropy run ID;
- attach the ticket again from the ignored runtime file; and
- block model-comparison or economics claims for the stale run.

### Wrong Workspace Root

Symptoms:

- output files appear in the wrong repository;
- commands mention unexpected project files;
- `git status` belongs to a different checkout.

Response:

- stop the worker;
- verify the intended root with `git status --short --branch`;
- relaunch only after the ticket names the correct root and output path; and
- record the failed attempt as wrong-root diagnostic evidence.

### Model Mismatch

Symptoms:

- persisted or visible evidence reports a different model than the ticket;
- a custom-agent name loaded but the backend model did not change;
- the model was recently installed but not visible in the active provider.

Response:

- stop model-specific claims;
- verify the configured Ollama inventory from the serving environment;
- reload VS Code or provider configuration only when inventory/config changed;
- relaunch only after model evidence can be captured.

### Runaway Loop

Symptoms:

- the worker repeats completion claims;
- the worker keeps summarizing after the ticket says stop;
- the output grows without new evidence or file changes.

Response:

- cancel the chat request immediately;
- save or note the loop evidence in an ignored diagnostic file if useful;
- do not ask the same session to stop repeatedly;
- start a new session only with a narrower ticket and a fresh run ID; and
- after two noisy attempts, stop the lane and ask the maintainer.

### Provider Or Model Failure

Symptoms:

- provider timeout or gateway error;
- incomplete/truncated model output;
- missing final marker;
- deterministic validators fail because output was cut off.

Response:

- classify the run as provider/model diagnostic evidence;
- do not repair-expand unless the budget gate allows it;
- test whether the failure correlates with response length, ticket size,
  provider transport, or model runtime only in a follow-on gated run; and
- avoid running a paid direct-supervisor baseline until a quality-valid
  delegated candidate exists.

### Restart Decision

Prefer resetting VS Code/Copilot state when:

- the visible chat loops;
- the wrong session answers;
- permission mode or model selection appears stale; or
- custom-agent configuration changed.

Prefer restarting or reloading the Ollama/model service only when:

- the model is unavailable outside Copilot Chat;
- direct provider probes fail;
- model inventory changed and the service does not reflect it; or
- multiple fresh VS Code sessions fail with the same provider/model error.

Do not restart services as the first response to a prompt-design, stale-chat, or
wrong-root problem.

## Post-Run Checklist

- [ ] Output exists where expected.
- [ ] Run ID matches.
- [ ] Model evidence matches.
- [ ] Root evidence matches.
- [ ] Deterministic validators passed or defects are recorded.
- [ ] Raw output stayed ignored.
- [ ] Tracked summaries are sanitized.
- [ ] Budget and token spans are complete when economics are claimed.
- [ ] The next action is either accept, bounded retry, reject, or maintainer
      checkpoint.

## Related Playbooks

- `playbooks/vscode_chat_bridge.md`
- `playbooks/real_project_deployment.md`
- `playbooks/document_indexing_recipe.md`
