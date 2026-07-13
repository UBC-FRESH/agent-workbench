"""Build a sanitized P106 direct-vs-delegated comparison packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agent_workbench.tokens import calculate_token_costs, load_token_record, validate_token_record


def build_packet(
    *,
    gate: Path,
    delegated_summary: Path,
    direct_summary: Path,
    delegated_tokens: Path,
    direct_tokens: Path,
) -> dict[str, Any]:
    config = json.loads(gate.read_text(encoding="utf-8"))
    summaries = {
        "delegated": json.loads(delegated_summary.read_text(encoding="utf-8")),
        "direct": json.loads(direct_summary.read_text(encoding="utf-8")),
    }
    token_paths = {"delegated": delegated_tokens, "direct": direct_tokens}
    lanes: dict[str, Any] = {}
    errors: list[str] = []
    for lane, summary in summaries.items():
        if summary.get("phase") != "P106" or summary.get("lane") != lane:
            errors.append(f"{lane}: invalid P106 lane summary identity")
        expected_model = config["lanes"][lane]["coordinator_model"]
        if summary.get("model") != expected_model:
            errors.append(f"{lane}: exact Coordinator model evidence mismatch")
        token = load_token_record(token_paths[lane])
        validation = validate_token_record(token)
        errors.extend(f"{lane}: {error}" for error in validation.errors)
        provenance = token.get("pricing_provenance", {})
        if provenance.get("qualified") is not True or provenance.get("model_id") != "gpt-5.6-luna":
            errors.append(f"{lane}: catalog-backed GPT-5.6 Luna pricing is required")
        cost = calculate_token_costs(token)
        lanes[lane] = {
            "model": summary.get("model"),
            "record_count": summary.get("record_count", 0),
            "useful_record_count": summary.get("useful_record_count", 0),
            "useful_yield": summary.get("useful_yield", 0),
            "critical_source_anchor_defect_count": summary.get("critical_source_anchor_defect_count", 0),
            "composition_ok": summary.get("composition_ok") is True,
            "quality_gate": summary.get("quality_gate"),
            "protocol_verdict": summary.get("protocol_verdict", "not_provided"),
            "latency_seconds": summary.get("latency_seconds"),
            "token_classes": token["usage"],
            "paid_coordinator_cost_usd": round(cost.supervisor_cost_usd, 6),
            "pricing_provenance": {
                "model_id": provenance.get("model_id"),
                "effective_date": provenance.get("effective_date"),
                "price_source": provenance.get("price_source"),
            },
        }
    total = sum(float(lane["paid_coordinator_cost_usd"]) for lane in lanes.values())
    delegated_cost = float(lanes.get("delegated", {}).get("paid_coordinator_cost_usd", 0))
    if delegated_cost > config["budgets_usd"]["delegated_lane_stop_threshold"]:
        errors.append("delegated lane exceeded its paid stop threshold")
    if total > config["budgets_usd"]["total_paid_coordinator_cap"]:
        errors.append("matched comparison exceeded total paid Coordinator cap")
    quality = all(lane.get("quality_gate") == "pass" for lane in lanes.values()) and not errors
    protocol = all(lane.get("protocol_verdict") == "pass" for lane in lanes.values()) and not errors
    economics = not errors and all(lane["paid_coordinator_cost_usd"] >= 0 for lane in lanes.values())
    return {
        "schema_version": 1,
        "phase": "P106",
        "status": "accepted-candidate" if quality and protocol and economics else "needs-supervisor-review",
        "verdicts": {
            "quality_validated_candidate": quality,
            "protocol_accepted_candidate": protocol,
            "economics_usable": economics,
        },
        "lanes": lanes,
        "total_paid_coordinator_cost_usd": round(total, 6),
        "errors": errors,
        "raw_inputs_excluded": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("gate", "delegated-summary", "direct-summary", "delegated-tokens", "direct-tokens", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    packet = build_packet(
        gate=args.gate,
        delegated_summary=args.delegated_summary,
        direct_summary=args.direct_summary,
        delegated_tokens=args.delegated_tokens,
        direct_tokens=args.direct_tokens,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet, sort_keys=True))
    return 0 if packet["status"] == "accepted-candidate" else 1


if __name__ == "__main__":
    raise SystemExit(main())
