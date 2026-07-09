# Phase 74: FoundryTK Profile Optimization Exploration

Phase 74 keeps FoundryTK outside the first custom-agent bridge implementation and treats it as an evaluation and optimization lane. The question is whether model/profile customization can improve delegated Agent Workbench workflows beyond prompt and message-structure tuning alone.

## Exploration Questions

- Can FoundryTK help select, evaluate, or optimize model/profile combinations for Agent Workbench roles?
- Can it provide external evaluation guidance, optional tools, model-selection evidence, or trace/evaluation runners without becoming part of the critical P72 bridge path?
- Can role-specific model or prompt optimization improve reliability, work quality, efficiency, and conversation shape in delegated workflows?

## Design Evidence

The built-in AI agent expert profile from the local VS Code extension is useful design evidence because it combines role-specific instructions with tools for model guidance, prompt improvement, tracing, and evaluation. Agent Workbench should study that pattern without copying private machine paths or assuming the extension profile is an Agent Workbench runtime dependency.

## Evaluation Dimensions

- reliability: follows authority boundaries, writes required artifacts, avoids drift, and stops cleanly;
- work quality: fewer supervisor repairs, better evidence, and better code or documentation output;
- efficiency: useful work per token, time, GPU-watt, and coordinator intervention;
- conversation shape: compact transcripts show the right agents having the right conversation.

## Boundary

No FoundryTK dependency should be added to P72 or P73. Phase 74 starts only after the bridge can reliably launch profile-selected SDK sessions and collect comparable transcript/result evidence.

## P74.1 Local Evaluation Scaffold

The first implementation step is local-only. Agent Workbench should render a FoundryTK-facing optimization plan from existing SDK manifests and P73 profile-run evidence without provisioning Azure resources, adding FoundryTK as a dependency, or changing the Copilot SDK bridge.

The plan must:

- list compared runs, selected profiles, selected overlays, custom tools, controller health, result status, and conversation-shape counts;
- define reliability, work quality, efficiency, and conversation-shape dimensions before any optimization work;
- recommend controller/session-health stabilization before prompt/model optimization when any compared run has controller errors;
- keep raw transcript text, private paths, prompts, credentials, and machine-specific values out of the rendered output.

FoundryTK integration remains a later decision after local evidence rows are stable.

## P74.2 Evaluation Dataset Contract

The second implementation step creates a public-safe dataset shape that could later feed Foundry evaluation, trace analysis, or profile/model comparison tools. This remains local-only and does not require Azure resources.

Each row should include:

- run identity: `run_id`, `phase`, selected profile, selected task overlays, and custom tools;
- reliability fields: controller health, required result-status presence, custom-agent events, and subagent events;
- work-quality fields: result status and whether the result is an accepted candidate;
- efficiency fields: event count, assistant messages, tool events, and permission events;
- conversation-shape fields: user/assistant message counts, custom-agent events, subagent events, and agent-metadata messages;
- warnings and errors from public-safe profile validation.

Rows must exclude raw transcript text, full prompts, private paths, credentials, and machine-specific values. JSONL is the interchange format; Markdown is only a coordinator preview.

## P74.3 Integration Decision

FoundryTK should remain outside the runtime bridge for now. The immediate role is external evaluation guidance using the local profile optimization plan and public-safe evaluation dataset rows.

Deeper integration is deferred:

- optional tool provider: wait until local dataset rows and profile-run summaries are stable across multiple live runs;
- model-selection evidence source: wait for matched profile/model/overlay comparisons;
- trace/evaluation runner: wait until privacy boundaries and row schema are validated against real traces;
- prompt optimization, agent optimizer, or fine-tuning: wait until controller/session health is stable enough that optimization is measuring worker behavior rather than bridge/provider failure.

Before any optimization work, require at least three comparable live SDK runs using named P73 overlays, controller-health versus result-validity scoring, public-safe evaluation rows, compact transcript review, and an explicit treatment comparison plan.
