# P27-P30 Forward Plan

The FreshForge deployment pilot showed that Agent Workbench is useful for
proposal-assist work, but still needs a stronger supervisor packet pipeline
before it should be used routinely across projects.

## P27 Supervisor Decision Packets

Goal: turn several proposal-only worker runs into one supervisor-facing packet.

This phase should fix the output-isolation gap seen during the FreshForge pilot
and add package-native synthesis of validated evidence summaries.

Deliverables:

- isolated multi-ticket pilot pack scaffolds;
- per-ticket eval output and provider scratch directories;
- evidence synthesis into one Markdown decision packet; and
- CLI workflow documentation for supervisor review.

## P28 Claim Review Aids

Goal: make unsupported worker claims easier to catch.

This phase should not attempt fully automated fact-checking. It should add
lightweight claim categories, reviewer prompts, and evidence-summary fields for
accepted, rejected, and needs-evidence claims.

Deliverables:

- claim-review template updates;
- evidence schema notes for claim disposition;
- optional packet sections for unsupported claims; and
- dogfood review against prior real-project worker outputs.

## P29 Repeat-Run And Model Comparison

Goal: measure whether worker behavior is stable enough to trust for specific
ticket families.

This phase should compare repeated runs across installed Ollama worker models
using identical proposal tickets and the P27 packet workflow.

Deliverables:

- repeat-run pack examples;
- model/repeat summary packet conventions;
- consistency scoring notes; and
- a recommendation for which ticket families each worker model can handle.

## P30 Real-Project Deployment Playbook

Goal: make the workflow repeatable for other UBC-FRESH projects.

This phase should convert P26-P29 lessons into a concise deployment playbook
that starts with no-tool proposal assistance and keeps supervisor authority over
tracked code, GitHub, and closeout.

Deliverables:

- real-project deployment checklist;
- supervisor decision gate examples;
- target-project cleanup and promotion rules; and
- criteria for when to stop using workers and keep work in the supervisor lane.
