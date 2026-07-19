"""Replay a supplied synthetic P107.2 observation without external side effects."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping
from p107_contract_codes import REASON_CODES, REVIEW_CAP


def _bool(state: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return state.get(key) is True if key in state else default


def _advisor_terminal(state: Mapping[str, Any]) -> str | None:
    summary = state.get("advisor_validator_result")
    evidence = state.get("advisor_evidence_summary")
    if not isinstance(summary, Mapping) or summary.get("valid") is not True:
        return None
    if not isinstance(evidence, Mapping) or not evidence.get("events_observed"):
        return None
    events = state.get("advisor_events")
    if events is None:
        return None
    if not isinstance(events, list):
        return None
    forbidden = {"nudge", "timeout", "repair", "spawn", "accept", "reject", "end"}
    state_name, verdict = "IMPLEMENT", False
    allowed = {
        "IMPLEMENT": {"COORDINATOR_PRECHECK"},
        "COORDINATOR_PRECHECK": {"FREEZE_REVIEW_BUNDLE"},
        "FREEZE_REVIEW_BUNDLE": {"ADVISOR_HARD_WAIT"},
        "ADVISOR_HARD_WAIT": {"ACCEPTED", "DEFECT_PACKET", "VERIFIED_BLOCKER", "ADVISOR_GATE_PAUSED"},
        "DEFECT_PACKET": {"IMPLEMENT"},
        "ADVISOR_GATE_PAUSED": {"ADVISOR_HARD_WAIT"},
    }
    reviews = 0
    cap = state.get("max_completed_reviews", REVIEW_CAP)
    if cap != REVIEW_CAP:
        return None
    for event in events:
        if not isinstance(event, dict):
            return None
        action, target = event.get("action"), event.get("to")
        if state_name == "ADVISOR_HARD_WAIT" and action == "wait" and target == state_name:
            continue
        if action in forbidden:
            return None
        if action != "wait" and action is not None:
            return None
        if target not in allowed.get(state_name, set()):
            return None
        if target in {"ACCEPTED", "DEFECT_PACKET", "VERIFIED_BLOCKER"}:
            reviews += 1
            if reviews > cap:
                return None
            verdict = target == "ACCEPTED"
        state_name = target
    terminal = {"ACCEPTED": "accepted", "VERIFIED_BLOCKER": "verified_blocker"}.get(state_name)
    asserted = state.get("advisor_terminal")
    if asserted is not None and asserted != terminal:
        return None
    return terminal


def replay_contract(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return exactly one ``eligible`` or ``not_comparable`` synthetic outcome."""
    if not isinstance(state, Mapping):
        return {"outcome": "not_comparable", "reason_codes": ["accounting_ineligible"], "roi": None}
    reasons: list[str] = []
    topology_ok = _bool(state, "topology_valid") and not _bool(state, "session_reuse")
    if not topology_ok:
        reasons.append("topology_session_reuse")
    if not _bool(state, "frozen_inputs_valid") or _bool(state, "hash_drift"):
        reasons.append("frozen_input_hash_drift")
    advisor_terminal = _advisor_terminal(state)
    if advisor_terminal is None:
        reasons.append("advisor_hard_wait_failure")
    if not _bool(state, "accounting_valid"):
        reasons.append("accounting_ineligible")
    if _bool(state, "contaminated") or state.get("contamination_valid") is False:
        reasons.append("contaminated")
    if not _bool(state, "c0_eligible") or _bool(state, "c0_mismatched"):
        reasons.append("c0_absent_or_mismatched")
    reasons = list(dict.fromkeys(reasons))
    if advisor_terminal == "verified_blocker":
        reasons.append("verified_blocker")
    reasons = list(dict.fromkeys(reasons))
    if not set(reasons).issubset(REASON_CODES):
        raise ValueError("replay emitted an unknown P107 reason code")
    return {"outcome": "eligible" if not reasons else "not_comparable", "reason_codes": reasons, "roi": None}


def replay_path(path: str | Path) -> dict[str, Any]:
    """Replay one explicitly supplied JSON summary; never discovers other files."""
    return replay_contract(json.loads(Path(path).read_text(encoding="utf-8")))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("summary")
    args = parser.parse_args()
    print(json.dumps(replay_path(args.summary), sort_keys=True))
