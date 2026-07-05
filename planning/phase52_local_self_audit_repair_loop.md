# Phase 52 Local Self-Audit And Repair Loop

## Purpose

P52 dogfooded the P51 managed-loop idea on the existing MP11 qwen x16 audit
sample. The question was whether a zero-cash local self-audit plus repair loop
could reduce paid supervisor audit/repair cost before scaling document-library
metadata indexing.

The test used the existing MP11 sample from `agent-delegation-lab`:

- sample size: 30 candidate records;
- existing supervisor calibration: 21 accepted, 9 repairable, 0 rejected;
- raw source excerpts stayed in ignored target-project runtime paths;
- tracked Agent Workbench artifacts contain only sanitized metrics.

## Implemented Artifacts

- `templates/local_self_audit_ticket.md`
- `templates/delegated_repair_iteration_ticket.md`
- `scripts/build_mp11_repair_loop_packet.py`
- `planning/phase52_mp11_repair_loop_summary.json`

The packet builder writes ignored tickets and manifests under the target
project's runtime tree. It can also rebuild a repair ticket from a completed
self-audit result, which makes the repair node reproducible without tracking
raw source excerpts.

## Worker Iteration

The first `gpt-oss:120b` self-audit attempt failed before any assistant output
because the provider connection failed. That attempt is treated as transport
evidence only, not model-quality evidence.

The successful self-audit pass used `gpt-oss:20b`. It produced parseable JSONL,
but it failed the important supervisor-alignment checks:

- 27 parseable records for a 30-record sample;
- all 27 records were labeled `accepted_candidate`;
- 0 records preserved the original sample record identifiers;
- 0 of 9 supervisor-known repairable records were detected.

The first `gpt-oss:20b` repair attempt failed before assistant output because
the Copilot SDK/provider path surfaced an invalid tool-call request.

The fallback repair pass used `qwen3-coder-next:latest`. It completed and
produced parseable JSONL, but it inherited the bad self-audit state:

- 27 parseable repair records;
- all 27 records used `unchanged_supported`;
- 0 records preserved the original sample record identifiers;
- 0 records were repaired;
- 0 records were marked ready for supervisor delta-review.

The failed repair attempt also confirms that the SDK path is not inherently
no-tool. The session reported tool execution events before failing with
`invalid tool call arguments`. That means SDK-based workers can encounter a
tool-capable surface, but Agent Workbench should not rely on it for benchmark
work until a later phase explicitly defines allowed tools, disables unwanted
tools, and records tool-call evidence. For P52, unrestricted tool behavior is a
confounder, not a feature.

## Economics Result

P52 did not improve the economics margin. The measured supervisor
delta-review span for diagnosing the loop and recording the result cost
`$0.434535`, while the existing direct source-audit calibration for this
30-record sample cost `$0.288374`.

That does not mean local self-audit/repair is a bad idea. It means this
particular ticket/model/protocol combination is not yet useful:

- it failed to preserve primary identifiers;
- it missed known repairable cases;
- repair mode reinforced the flawed self-audit result;
- one SDK repair attempt hit uncontrolled tool-call behavior; and
- supervisor cost went up because the supervisor had to diagnose the loop
  failure.

## Decision

Do not scale this self-audit/repair shape. P53 can proceed with the document
library pilot, but it should treat local self-audit/repair as experimental and
should use tighter identifier-preservation checks before any repair node runs.

P54 should add a bailout rule: if self-audit preserves zero primary candidate
IDs or detects zero repairable records in a calibration sample known to contain
repairables, stop the loop and revise the ticket/model pairing instead of
running repair.
