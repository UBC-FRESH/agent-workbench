"""Fail-closed, offline P107 C0-relative comparison contract."""
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

def _reasons(row: dict[str, Any], *, baseline: bool = False) -> list[str]:
    reasons = []
    if not isinstance(row.get("evaluation_block_id"), str) or not row["evaluation_block_id"].strip(): reasons.append("missing_evaluation_block")
    elif row.get("evaluation_block_valid") is not True: reasons.append("invalid_evaluation_block")
    if row.get("deterministic_acceptance") is not True: reasons.append("deterministic_acceptance_failed")
    if row.get("advisor_verdict") != "accepted": reasons.append("advisor_not_accepted")
    if row.get("advisor_binding_valid") is not True: reasons.append("advisor_binding_invalid")
    if row.get("contaminated") is not False: reasons.append("contaminated")
    if row.get("accounting_complete") is not True: reasons.append("accounting_ineligible")
    if row.get("accounting_provenance_valid") is not True: reasons.append("accounting_provenance_invalid")
    if row.get("configuration_topology_valid") is not True: reasons.append("configuration_topology_mismatch")
    if row.get("model_identity_valid") is not True: reasons.append("model_identity_mismatch")
    if not baseline and row.get("paid_run_cost") is None: reasons.append("accounting_ineligible")
    return list(dict.fromkeys(reasons))

def compare(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8")); rows = data.get("observations", [])
    by_id = {r.get("run_id"): r for r in rows if isinstance(r, dict)}
    c0 = [r for r in rows if isinstance(r, dict) and r.get("configuration_id") == "C0" and not _reasons(r, baseline=True)]
    result = []
    for row in rows:
        if not isinstance(row, dict): continue
        if row.get("configuration_id") == "C0":
            codes = _reasons(row, baseline=True)
            result.append({"run_id": row.get("run_id"), "roi_status": "eligible_baseline" if not codes else "not_comparable", "reason_codes": codes, "paid_roi": None}); continue
        codes = _reasons(row); base = by_id.get(row.get("baseline_run_id"))
        if not c0: codes.append("missing_eligible_c0")
        if not isinstance(base, dict) or base.get("configuration_id") != "C0": codes.append("baseline_not_eligible")
        else:
            if _reasons(base, baseline=True): codes.append("baseline_not_eligible")
            if base.get("evaluation_block_id") != row.get("evaluation_block_id"): codes.append("evaluation_block_mismatch")
        codes = list(dict.fromkeys(codes))
        if codes: result.append({"run_id": row.get("run_id"), "roi_status": "not_comparable", "reason_codes": codes, "paid_roi": None}); continue
        base_cost, cost = float(base["paid_run_cost"]), float(row["paid_run_cost"])
        if base_cost <= 0: result.append({"run_id": row.get("run_id"), "roi_status": "not_comparable", "reason_codes": ["accounting_ineligible"], "paid_roi": None})
        else: result.append({"run_id": row.get("run_id"), "roi_status": "comparable", "reason_codes": [], "paid_roi": (base_cost-cost)/base_cost})
    return {"comparisons": result}

if __name__ == "__main__": print(json.dumps(compare(sys.argv[1]), indent=2))
