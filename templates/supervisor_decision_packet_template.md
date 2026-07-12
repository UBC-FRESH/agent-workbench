# Supervisor Decision Packet Template

*This template captures the compact ROI decision for a supervisor after reviewing a reporting worker’s packet. It is generic and can be used across different phases.*

## Required Sections (Markdown headings)
```
## Decision Summary
## Quality Assessment
## Protocol Compliance
## Economic Impact
## Recommended Action
## Next Steps
```

### 1. Decision Summary
Provide a brief statement of the overall decision:
- `accept` – seed is ready for further processing.
- `repair` – issues identified that require repair before proceeding.
- `switch lane` – change model or workflow lane.
- `stop` – halt further work on this line of inquiry.

**Concrete example (Phase 91)**:
The decision extracted from `benchmarks/document_library/p91_source_audit_decision_packet.json` is:

```
"decision": "promote_seed"
```

Thus the coordinator should record **Decision:** `accept` (promote seed) after supervisor sign‑off.

### 2. Quality Assessment
Summarize the factual quality metrics (e.g., accepted vs. rejected records, percentages).

**Phase 91 sample data:**

| Metric | Count |
|--------|------:|
| Accepted | 8 |
| Repairable | 7 |
| Rejected | 1 |
| Needs Review | 0 |
| **Total audited** | **16** |

Percentages: Accepted 50 %, Repairable 44 %, Rejected 6 %.

### 3. Protocol Compliance
Note any deviations from expected supervisor‑worker contracts, validation failures, or missing evidence.

**Protocol findings (Phase 91):**

- Dominant risk: `zero_record_defect` (6 occurrences).
- Defect class counts:
```json
{
	"malformed_or_not_useful": 1,
	"none": 8,
	"schema_or_protocol_defect": 2,
	"source_quote_contains_exact_anchor_plus_synthesis": 3,
	"source_quote_needs_human_anchor_repair": 2,
	"zero_record_defect": 6
}
```

- Functional success levels: 8 accepted, 3 minor repair, 4 repairable, 7 protocol failures.

### 4. Economic Impact
State the measured paid‑supervisor token cost for this review and any local worker cash cost if applicable. Do **not** claim net savings unless a full cost accounting has been performed.

**Economic note (Phase 91):**
The packet reports significant *governance overhead* rather than direct monetary cost:

> "P91 required roadmap, changelog, issue, PR, and validation work that must remain separate from intrinsic task economics."

No explicit paid‑supervisor token count is recorded for this bounded sample.

### 5. Recommended Action
List concrete actions the coordinator should take next, such as:
- Expand audit sample size.
- Run a repair‑iteration ticket targeting schema/protocol defects (2 occurrences).
- Consider an alternate model lane if zero‑record defect rate remains high after repairs.
- Obtain supervisor sign‑off on the `promote_seed` decision before downstream indexing.

### 6. Next Steps
Provide a short roadmap of immediate follow‑up tasks and any required issue or PR updates.

1. Update issue #600 with the promoted seed decision.
2. Open a repair ticket (P98.1 – Audit existing artifacts) to address zero‑record defects.
3. After repairs, run a larger audit sample and record updated economics.
4. Upon supervisor approval, merge changes into `main` and close Phase 91 related tasks.

---
*All placeholders must be filled with sanitized data before submission.*
