# P87-P92 Real-Project ROI Roadmap

## Decision

Agent Workbench should pivot its leading roadmap edge away from additional
profile-evidence-review battery loops and back to real-project ROI:

```text
reduce paid supervisor cost per useful, source-backed unit of real project work
```

The next detailed tranche is P87-P92. Its practical target is public
technical-document indexing with explicit supervisor-overhead reduction.

Profile-evidence-review batteries remain useful support evidence, but they are
not the product lane. Do not run another profile/model battery unless it
answers a direct real-project ROI question.

## Evidence Base

P55 showed the first real document-indexing signal:

- generic open-ended structure extraction was weaker than typed fact extraction
  plus disagreement verification;
- document extraction quality depends heavily on ticket shape, model lane,
  source anchors, and repair/validation nodes;
- source-level supervisor audit cost is real and must be measured instead of
  hidden inside broad closeout cost; and
- P55 should remain an evidence packet, not a production indexing workflow.

P63 showed why the document-indexing recipe needs repair before scale:

- the bounded TSA23 pilot produced plausible candidate records but stopped
  after the single budgeted attempt;
- observed defects included provider/proxy 524 failure, fenced-output protocol
  noise, invalid chunk IDs, and incomplete JSONL;
- the accepted decision was to adjust the recipe before any repeat; and
- a future repeat needs a new budget gate, smaller tickets, deterministic
  JSONL validation/repair, chunk-ID hardening, and explicit stop rules.

P85 showed the profile-evidence-review contract is no longer the blocking
problem:

- the repaired battery produced 48 analyzable rows;
- final statuses were 47 `accepted-candidate`, 1 `needs-supervisor-review`,
  and 0 `blocked`; and
- the result supports the repaired profile-evidence-review behavior claim, but
  does not by itself claim real-project ROI or model superiority.

P86 removed a local validation caveat:

- `mypy src` and `pre-commit run --all-files` now pass from the repository's
  reproducible `dev` extra; and
- future planning and implementation phases can use these checks as normal
  gates instead of reporting them as environment caveats.

## Strategic Arc

P87-P92 is the real-project ROI tranche:

- reset roadmap state and park profile-battery work as support evidence;
- rebuild the document-indexing recipe around smaller section-level tickets,
  deterministic validation/repair, source-anchored audit, and compact decision
  packets; and
- measure task economics separately from repository governance overhead.

P93-P96 is the scale and index-usability tranche:

- apply the repaired recipe to a second public technical corpus;
- promote accepted or repaired records into a project-owned index format;
- add retrieval/use cases that help modelling agents find source-backed facts;
  and
- compare worker/model lanes only where they affect accepted-record yield or
  supervisor audit cost.

P97-P100 is the workbench productization tranche:

- package reusable workflow graph templates, reporting-worker templates,
  evidence summaries, and economics dashboards;
- turn successful recipes into reusable playbooks for UBC-FRESH projects; and
- prepare a public alpha only after one end-to-end real-project workflow shows
  net value.

## P87-P92 Detailed Tranche

P87 resets the roadmap and evidence base. It marks P86 complete, adds this
planning note, records the P55/P63/P85/P86 decision evidence, and points the
roadmap, changelog, issues, and PR state at the real-project ROI lane.

P88 defines the real-corpus benchmark registry. It records candidate public
technical corpora, corpus value, source availability, expected downstream use,
risk, and audit burden, then selects exactly one bounded first corpus slice for
the next live run.

P89 builds document-indexing recipe v2. It repairs the P63 recipe shape with
smaller section-level tickets, explicit chunk-ID enum handling, deterministic
JSONL validation, and deterministic repair where possible. Acceptance is a
dry-run/materialization path, not live model execution.

P90 adds the source-anchored repair and audit loop. It creates a local-worker
repair-prepass ticket over candidate records plus compact source excerpts,
defines supervisor audit classifications, and measures audit cost per accepted
or repairable record.

P91 introduces reporting-worker decision packets. It delegates sanitized
experiment-summary reporting to a local worker while keeping source audit and
final acceptance supervisor-owned. Task economics and repository governance
overhead must be reported separately.

P92 runs the packaged graph-shaped pilot. It represents the repaired workflow
as a FreshForge-shaped graph template and runs one bounded pilot only after
P88-P91 gates are satisfied.

## Interfaces And Artifacts

Reuse existing public-safe artifact families before adding CLI surface:

- corpus records;
- worker tickets;
- FreshForge-shaped graph templates;
- evidence summaries;
- token records; and
- decision packets.

Add new artifacts only when needed by the tranche:

- corpus-slice selection record;
- document-indexing recipe v2 ticket;
- source-anchored repair/audit packet; and
- reporting-worker decision packet.

Tracked artifacts must stay public-safe. Raw PDF text, raw worker outputs, raw
transcripts, prompts, provider URLs, headers, credentials, and personal paths
remain in ignored runtime or target-project-owned data paths.

## Validation Policy

Every implementation phase in this tranche must run:

```powershell
python -m ruff format src tests
python -m ruff check src tests
python -m mypy src
python -m pytest tests -q
python -m pre_commit run --all-files
git diff --check
```

Planning-only phases must additionally verify that no raw transcript text, raw
PDF text, provider URLs, headers, credentials, or personal paths were tracked.

Live-run phases must add an explicit budget gate, one named model/provider
lane, one bounded corpus slice, hard stop rules, compact public-safe evidence,
and no direct-supervisor baseline until a quality-valid delegated candidate
exists.
