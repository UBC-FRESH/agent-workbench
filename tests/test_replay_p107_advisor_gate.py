from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from replay_p107_advisor_gate import validate_replay

def write(tmp_path: Path, events: list[dict], review_cap: int = 8) -> Path:
    path=tmp_path/"replay.json"; path.write_text(json.dumps({"max_completed_reviews":review_cap,"events":events}),encoding="utf-8"); return path

def prefix() -> list[dict]:
    return [{"to":"COORDINATOR_PRECHECK"},{"to":"FREEZE_REVIEW_BUNDLE"},{"to":"ADVISOR_HARD_WAIT"}]

def test_accepts_wait_then_defect_repair_then_accept(tmp_path: Path) -> None:
    events=prefix()+[{"action":"wait","to":"ADVISOR_HARD_WAIT"},{"to":"DEFECT_PACKET"},{"to":"IMPLEMENT"}]+prefix()+[{"to":"ACCEPTED"}]
    assert validate_replay(write(tmp_path,events))==[]

def test_rejects_nudge_during_advisor_wait(tmp_path: Path) -> None:
    errors=validate_replay(write(tmp_path,prefix()+[{"action":"nudge","to":"ADVISOR_HARD_WAIT"}]))
    assert "forbidden during Advisor wait: nudge" in errors

def test_rejects_review_beyond_configured_soft_cap(tmp_path: Path) -> None:
    events=[]
    for _ in range(3):
        events += prefix()+[{"to":"DEFECT_PACKET"},{"to":"IMPLEMENT"}]
    errors=validate_replay(write(tmp_path,events,review_cap=2))
    assert "more than 2 completed Advisor reviews" in errors
