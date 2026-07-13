# Phase 99: Economics Dashboard And Release Criteria

**Status:** active  
**Parent issue:** #601  
**Branch:** `feature/p99-economics-dashboard-release-criteria`

---

## Phase Summary

Phase 99 adds an **indexed-cost metric** and a `agent-workbench economics render`
CLI command that turns pilot accounting records (P35) and token/cost records (P40)
into a Markdown dashboard. The dashboard shows paid-supervisor tokens per
promoted record — broken down by stage — making the core ROI thesis visible
enough to support public-alpha decisions.

This phase also defines the minimum release-readiness criteria that must pass
before a public alpha is considered.

---

## Indexed-Cost Metric Specification

### Formula

$$
\text{tokens\_per\_record}(\text{stage}) = \frac{\sum_i \text{paid\_supervisor\_tokens}_i(\text{stage})}{\text{promoted\_record\_count}}
$$

$$
\text{cost\_per\_record\_usd}(\text{stage}) = \frac{\text{tokens\_per\_record}(\text{stage}) \times \text{price\_per\_token\_usd}}{1}
$$

### Stages

| Stage | Description |
| --- | --- |
| `extraction` | Raw document parsing and field extraction by worker |
| `repair_prepass` | Supervisor-driven repair and patch application |
| `audit` | Supervisor audit of promoted records |
| `index_assembly` | Final index promotion and manifest update |
| `total` | Sum of all stages (default when stage annotations are absent) |

### Price Assumptions (defaults)

| Token class | Default price (USD / 1M tokens) |
| --- | --- |
| Supervisor input | 3.00 |
| Supervisor output | 15.00 |

Price assumptions are sourced from the first record that declares them, or from
the defaults above.  All price assumptions are recorded in the output JSON.

### Zero-Record Guard

When `promoted_record_count == 0`, per-record ratios are set to `0` and a note
is appended to the record.  No `ZeroDivisionError` is raised.

---

## Wiring Note

`economics render` connects to existing surfaces as follows:

- `--accounting PATH` accepts any JSON file produced by `agent-workbench
  accounting render` (P35 pilot accounting records).
- `--tokens PATH` accepts any JSON file produced by `agent-workbench tokens
  render` (P40 token/cost records).
- `--promoted-count N` is the number of records promoted to the document index.
- The command reads `token_accounting` fields from accounting records and
  `usage` fields from token records, summing paid supervisor input and output
  tokens across both sets.

---

## Release-Readiness Criteria For Public Alpha

### Mandatory gates (all must pass before alpha tag)

- [ ] All tracked artifacts pass `git diff --check`
- [ ] No private paths, credentials, or raw transcripts in tracked files
- [ ] `pytest tests -q` passes
- [ ] `mypy src` passes
- [ ] `ruff check src tests` passes
- [ ] `agent-workbench smoke` passes
- [ ] At least one `economics render` dogfood run completes without error
- [ ] `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` are synchronized
- [ ] P99 parent issue #601 is open and linked

### Current state (2026-07-12)

| Criterion | Status |
| --- | --- |
| `git diff --check` | Pass (verified by supervisor on activation) |
| No private paths / credentials | Pass (ruff + evidence scanner, no findings) |
| `pytest tests -q` | Pending (P99 tests require validation run) |
| `mypy src` | Pending (P99 module requires validation run) |
| `ruff check src tests` | Pending (P99 module requires validation run) |
| `agent-workbench smoke` | Pending (P99 economics subcommand not tested yet) |
| `economics render` dogfood run | Not yet performed |
| AGENTS/ROADMAP/CHANGE_LOG sync | In progress (P99.5 updates this phase) |
| P99 issue #601 open and linked | Yes — issue #601 created on phase activation |

---

## Acceptance Criteria For P99

1. `src/agent_workbench/economics.py` exists and is importable.
2. `agent-workbench economics render --help` exits 0.
3. `pytest tests/test_economics.py -q` passes (at minimum 4 tests).
4. `ruff check src tests` passes (no new errors).
5. `mypy src` passes.
6. This document (`planning/phase99_economics_dashboard_release_criteria.md`) exists
   with a filled criteria checklist.
7. `ROADMAP.md` P99 row shows `#601` and status `Active`.
8. `CHANGE_LOG.md` has a P99 entry.
