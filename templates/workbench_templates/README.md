# Workbench Template Envelopes

These templates are public-safe starter envelopes for reproducible
AI-assisted work. They are not workflow runners.

The envelope shape intentionally borrows FreshForge's graph vocabulary:

- `workflow`: named work bundle;
- `nodes`: bounded role/capability steps;
- `needs`: explicit dependencies between steps;
- `provider`: implementation namespace such as supervisor, local worker,
  FreshForge, project CLI, notebook, CI, or script;
- `inputs` and `outputs`: declared information flow;
- `artifacts`: source, generated, promoted, or rejected evidence; and
- `diagnostics`: validation, claim-review, or policy warnings.

Use them to organize:

- supervisor intent;
- source artifacts;
- worker tickets;
- generated artifacts;
- project-native commands;
- evidence summaries;
- claim review;
- token/cash accounting; and
- promoted outputs.

Execution stays with the target project's existing tools: FreshForge, project
CLIs, notebooks, Snakemake, GitHub Actions, Quarto, CI, release scripts, or
human review.

Template families:

- `agentic_graph_envelope.json`
- `software_task_template.md`
- `paper_task_template.md`
- `proposal_task_template.md`
- `benchmark_task_template.md`
- `document_library_index_graph.json`

Copy the relevant template into an ignored target-project runtime path first.
Promote only sanitized findings into tracked project files.

`document_library_index_graph.json` is the starter graph for public technical
document library indexing workflows. It covers corpus registration, text
chunking, local-worker structure/content extraction, source-anchored repair
prepass, paid supervisor audit calibration, and promoted index assembly.
