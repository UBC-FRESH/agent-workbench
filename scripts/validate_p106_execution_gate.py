"""Fail-closed validator for the P106 live-run gate manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.validate_p105_matched_benchmark import validate as validate_p105
except ModuleNotFoundError:  # direct script execution from the scripts directory
    from validate_p105_matched_benchmark import validate as validate_p105


def validate(gate_path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    try:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"P106 gate unreadable: {exc}"]
    if gate.get("phase") != "P106" or gate.get("status") != "live_run_gate":
        errors.append("P106 live-run gate identity is required")
    if gate.get("live_inference_allowed") is not False:
        errors.append("P106 gate must remain closed until coordinator evidence review")
    budgets = gate.get("budgets_usd", {})
    if budgets.get("total_paid_coordinator_cap") != 0.25:
        errors.append("total paid Coordinator cap must be $0.25")
    if budgets.get("delegated_lane_stop_threshold") != 0.125:
        errors.append("delegated stop threshold must be $0.125")
    pricing = gate.get("pricing", {})
    for key in ("catalog_required", "exact_model_required", "effective_date_required"):
        if pricing.get(key) is not True:
            errors.append(f"pricing requirement missing: {key}")
    if gate.get("attempts") != {"initial": 1, "evidence_based_repairs_max": 1}:
        errors.append("attempt and repair limits must be one initial plus one evidence-based repair")
    quality = gate.get("delegated_quality_gate", {})
    if quality.get("minimum_useful_yield") != 0.9 or quality.get("critical_source_anchor_defects_max") != 0:
        errors.append("delegated quality gate must require 90% useful yield and zero critical anchor defects")
    p105_path = root / gate.get("p105_contract", "")
    if not p105_path.is_file():
        errors.append("referenced P105 contract is missing")
    else:
        errors.extend(validate_p105(p105_path, root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.gate, args.root)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"valid P106 live-run gate: {args.gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
