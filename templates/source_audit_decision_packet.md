# Source Audit Decision Packet Template

*This template is derived from the Phase 91 source‑audit decision packet and generalized for any non‑document‑indexing use case.*

## Overview
- **Purpose**: Summarize the results of a bounded source‑audit sample, separating factual quality, protocol compliance, and economic considerations.
- **Scope**: Works with sanitized audit rows produced by a reporting worker. Does not include raw source text, provider URLs, or private paths.

## Required Sections (Markdown headings)
```
## Factual Summary
## Model And Packaging Comparison (optional)
## Anomalies
## Economics Boundary
## Claims Requiring Supervisor Approval
## Recommended Next Audit Target
```

### 1. Factual Summary
Provide counts of records in each quality category. Below is a concrete example extracted from **Phase 91** source‑audit decision packet (see `benchmarks/document_library/p91_source_audit_decision_packet.json`).

| Category | Count |
|----------|------:|
| accepted | 8 |
| repairable | 7 |
| rejected | 1 |
| needs_review | 0 |
| **total audited** | **16** |

Percentages (of total audited):

- Accepted: **50 %**
- Repairable: **44 %**
- Rejected: **6 %**

The sample useful yield reported was **0.938**.

### 2. Model And Packaging Comparison (optional)
If multiple model lanes were evaluated, give a brief comparison of:
- Yield per lane (accepted/repairable counts).
- Token‑span or cost differences observed.
- Any protocol deviations unique to a lane.

### 3. Anomalies
During Phase 91 the dominant protocol risk was **zero_record_defect**. The defect class counts were:

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

Key anomalies:

1. **Zero‑record defects (6)** – runs that produced no records, reducing overall yield.
2. **Schema or protocol defects (2)** – required bounded schema repair.
3. **Source quote issues** – a few quotes needed human‑anchor repair or exact anchor synthesis.

### 4. Economics Boundary
The Phase 91 audit highlighted governance overhead rather than direct monetary cost. Relevant excerpt from the packet:

> "P91 required roadmap, changelog, issue, PR, and validation work that must remain separate from intrinsic task economics."

No explicit paid‑supervisor token cost is recorded for this bounded sample; the primary economic consideration is the **governance overhead** before scaling to full audits.

### 5. Claims Requiring Supervisor Approval
From the Phase 91 packet the following claim requires supervisor approval:

* **Decision:** `promote_seed` – promotion of the seed for downstream indexing must be approved by a supervisor before any broader rollout.

### 6. Recommended Next Audit Target
Based on the observed zero‑record defects and repairable counts, the recommended next audit target is:

1. **Increase sample size** to obtain a more stable estimate of zero‑record frequency.
2. **Run a repair iteration ticket** focusing on schema/protocol defects.
3. **Consider alternate model lane** if zero‑record rate remains high after repairs.

---
*All placeholders must be filled with sanitized data before submission.*
