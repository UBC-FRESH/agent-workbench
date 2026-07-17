"""Deterministically replay P107 Advisor-gate transitions without live agents."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ALLOWED = {
    "IMPLEMENT": {"COORDINATOR_PRECHECK"},
    "COORDINATOR_PRECHECK": {"FREEZE_REVIEW_BUNDLE"},
    "FREEZE_REVIEW_BUNDLE": {"ADVISOR_HARD_WAIT"},
    "ADVISOR_HARD_WAIT": {"ACCEPTED", "DEFECT_PACKET", "VERIFIED_BLOCKER", "ADVISOR_GATE_PAUSED"},
    "DEFECT_PACKET": {"IMPLEMENT"},
    "ADVISOR_GATE_PAUSED": {"ADVISOR_HARD_WAIT"},
}
FORBIDDEN_DURING_WAIT = {"nudge", "timeout", "repair", "spawn", "accept", "reject", "end"}

def validate_replay(path: str | Path) -> list[str]:
    data=json.loads(Path(path).read_text(encoding="utf-8")); state="IMPLEMENT"; reviews=0; errors=[]
    review_cap=data.get("max_completed_reviews", 8)
    if not isinstance(review_cap, int) or not 1 <= review_cap <= 8:
        return ["max_completed_reviews must be an integer from 1 through 8"]
    for event in data.get("events", []):
        action=event.get("action")
        if state=="ADVISOR_HARD_WAIT" and action=="wait" and event.get("to")==state:
            continue
        if state=="ADVISOR_HARD_WAIT" and action in FORBIDDEN_DURING_WAIT:
            errors.append(f"forbidden during Advisor wait: {action}"); continue
        target=event.get("to")
        if target not in ALLOWED.get(state,set()):
            errors.append(f"invalid transition {state}->{target}"); continue
        if target in {"ACCEPTED","DEFECT_PACKET","VERIFIED_BLOCKER"}:
            reviews += 1
            if reviews > review_cap: errors.append(f"more than {review_cap} completed Advisor reviews")
        state=target
    if state not in {"ACCEPTED","VERIFIED_BLOCKER","ADVISOR_HARD_WAIT","ADVISOR_GATE_PAUSED"}:
        errors.append(f"terminal or waiting state required, got {state}")
    return errors

if __name__=="__main__":
    errors=validate_replay(sys.argv[1])
    if errors: print("\n".join(errors)); raise SystemExit(1)
    print("P107 Advisor-gate replay valid")
