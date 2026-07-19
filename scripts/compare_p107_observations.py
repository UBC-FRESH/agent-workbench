"""Fail-closed, offline P107 C0-relative comparison contract."""
from __future__ import annotations
import hashlib, json, math, sys
from pathlib import Path
from typing import Any
from validate_p107_advisor_review import validate_review
from validate_p107_accounting_record import validate_accounting_record
from validate_p107_evaluation_block import validate
from validate_p107_run_evidence_manifest import validate_manifest

_CONFIGURATIONS = {"C0", "C1", "C2", "C3", "C4"}
_BOOLEAN_FLAGS = ("evaluation_block_valid", "deterministic_acceptance", "advisor_binding_valid",
                  "contaminated", "accounting_complete", "accounting_provenance_valid",
                  "configuration_topology_valid", "model_identity_valid")

def _cost_valid(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0

def _artifact_valid(row: dict[str, Any], field: str, validator: Any) -> bool:
    path = row.get(field)
    if not isinstance(path, str) or not path.strip():
        return False
    try:
        return not validator(path)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False

def _advisor_artifacts_valid(row: dict[str, Any]) -> bool:
    bundle, verdict = row.get("advisor_bundle_path"), row.get("advisor_verdict_path")
    if not isinstance(bundle, str) or not isinstance(verdict, str):
        return False
    try:
        return not validate_review(bundle, verdict, history_path=row.get("advisor_history_path"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False

def _bind_manifest(row: dict[str, Any]) -> list[str]:
    path, digest = row.get("evidence_manifest_path"), row.get("evidence_manifest_sha256")
    if not isinstance(path, str) or not path.strip(): return ["missing_evidence_manifest"]
    target = Path(path)
    if not target.is_file(): return ["missing_evidence_manifest"]
    if not isinstance(digest, str) or hashlib.sha256(target.read_bytes()).hexdigest() != digest: return ["evidence_manifest_hash_mismatch"]
    if validate_manifest(target): return ["invalid_evidence_manifest"]
    manifest = json.loads(target.read_text(encoding="utf-8"))
    errors = []
    if row.get("run_id") != manifest.get("run_id"): errors.append("run_id_manifest_mismatch")
    if row.get("configuration_id") != manifest.get("configuration_id"): errors.append("configuration_manifest_mismatch")
    if row.get("worktree_path") is not None and row["worktree_path"] != manifest.get("repository_path"): errors.append("worktree_manifest_mismatch")
    return errors

def _reasons(row: dict[str, Any], *, baseline: bool = False, duplicate_ids: bool = False) -> list[str]:
    reasons = []
    reasons.extend(_bind_manifest(row))
    if not isinstance(row.get("run_id"), str) or not row["run_id"].strip(): reasons.append("missing_run_id")
    if row.get("configuration_id") not in _CONFIGURATIONS: reasons.append("invalid_configuration")
    for field in _BOOLEAN_FLAGS:
        if not isinstance(row.get(field), bool):
            if field == "evaluation_block_valid": reasons.append("invalid_evaluation_block")
            else: reasons.append({"deterministic_acceptance": "deterministic_acceptance_failed", "advisor_binding_valid": "advisor_binding_invalid", "contaminated": "contaminated", "accounting_complete": "accounting_ineligible", "accounting_provenance_valid": "accounting_provenance_invalid", "configuration_topology_valid": "configuration_topology_mismatch", "model_identity_valid": "model_identity_mismatch"}[field])
    if duplicate_ids: reasons.append("duplicate_run_id")
    if not isinstance(row.get("evaluation_block_id"), str) or not row["evaluation_block_id"].strip(): reasons.append("missing_evaluation_block")
    elif row.get("evaluation_block_valid") is not True and "invalid_evaluation_block" not in reasons: reasons.append("invalid_evaluation_block")
    if row.get("deterministic_acceptance") is not True: reasons.append("deterministic_acceptance_failed")
    if row.get("advisor_verdict") != "accepted" or not _advisor_artifacts_valid(row): reasons.append("advisor_hard_wait_failure")
    if row.get("contaminated") is not False: reasons.append("contaminated")
    if row.get("accounting_complete") is not True or not _artifact_valid(row, "accounting_record_path", validate_accounting_record): reasons.append("accounting_ineligible")
    if row.get("accounting_provenance_valid") is not True: reasons.append("accounting_ineligible")
    if row.get("configuration_topology_valid") is not True or not _artifact_valid(row, "topology_receipt_path", lambda p: _receipt_errors(p, row, "topology")): reasons.append("topology_session_reuse")
    if row.get("model_identity_valid") is not True: reasons.append("frozen_input_hash_drift")
    if not _cost_valid(row.get("paid_run_cost")): reasons.append("accounting_ineligible")
    if baseline and row.get("baseline_run_id") is not None: reasons.append("baseline_id_invalid")
    if not baseline and (not isinstance(row.get("baseline_run_id"), str) or not row["baseline_run_id"].strip()): reasons.append("missing_baseline_id")
    return list(dict.fromkeys(reasons))

def _receipt_errors(path: str, row: dict[str, Any], kind: str) -> list[str]:
    try:
        receipt = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)]
    if not isinstance(receipt, dict) or receipt.get("valid") is not True or receipt.get("run_id") != row.get("run_id") or receipt.get("kind") != kind:
        return ["receipt is not a validated run-bound artifact"]
    return []

def compare(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8")); rows = data.get("observations", [])
    counts = {}
    for r in rows:
        if isinstance(r, dict): counts[r.get("run_id")] = counts.get(r.get("run_id"), 0) + 1
    by_id = {r.get("run_id"): r for r in rows if isinstance(r, dict) and counts.get(r.get("run_id"), 0) == 1}
    c0 = [r for r in rows if isinstance(r, dict) and r.get("configuration_id") == "C0" and not _reasons(r, baseline=True, duplicate_ids=counts.get(r.get("run_id"), 0) > 1)]
    result = []
    for row in rows:
        if not isinstance(row, dict):
            result.append({"run_id": None, "roi_status": "not_comparable", "reason_codes": ["invalid_observation_shape"], "paid_roi": None})
            continue
        if row.get("configuration_id") == "C0":
            codes = _reasons(row, baseline=True, duplicate_ids=counts.get(row.get("run_id"), 0) > 1)
            result.append({"run_id": row.get("run_id"), "roi_status": "eligible_baseline" if not codes else "not_comparable", "reason_codes": codes, "paid_roi": None}); continue
        codes = _reasons(row, duplicate_ids=counts.get(row.get("run_id"), 0) > 1); base = by_id.get(row.get("baseline_run_id"))
        if not c0: codes.append("missing_eligible_c0")
        if not isinstance(base, dict) or base.get("configuration_id") != "C0": codes.append("baseline_not_eligible")
        else:
            if _reasons(base, baseline=True, duplicate_ids=False): codes.append("baseline_not_eligible")
            if base.get("evaluation_block_id") != row.get("evaluation_block_id"): codes.append("evaluation_block_mismatch")
        codes = list(dict.fromkeys(codes))
        if codes: result.append({"run_id": row.get("run_id"), "roi_status": "not_comparable", "reason_codes": codes, "paid_roi": None}); continue
        base_cost, cost = base["paid_run_cost"], row["paid_run_cost"]
        if not _cost_valid(base_cost) or not _cost_valid(cost): result.append({"run_id": row.get("run_id"), "roi_status": "not_comparable", "reason_codes": ["accounting_ineligible"], "paid_roi": None})
        else: result.append({"run_id": row.get("run_id"), "roi_status": "comparable", "reason_codes": [], "paid_roi": (base_cost-cost)/base_cost})
    return {"comparisons": result}

if __name__ == "__main__": print(json.dumps(compare(sys.argv[1]), indent=2))
