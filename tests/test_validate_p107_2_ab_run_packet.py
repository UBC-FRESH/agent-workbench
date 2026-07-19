from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_p107_2_ab_run_packet import validate_run_packet


TEMPLATE = ROOT / "templates" / "p107_2_ab_run_packet_template.json"


def materialized_packet() -> dict[str, object]:
    document = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    document["run_id"] = "p107-2-pilot"
    document["baseline_commit"] = "a" * 40
    for lane in document["lanes"].values():
        lane["worktree"] = "C:\\\\p107-2-worktree"
    for name in ("ticket", "acceptance_fixture", "usability_rubric"):
        document[name]["path"] = f"C:\\\\p107-2\\\\{name}"
        document[name]["sha256"] = "b" * 64
    document["acceptance_fixture"]["command"] = "python -m pytest acceptance -q"
    document["implementation_scope"]["allowed_paths"] = ["src/example.py"]
    document["accounting"]["record_path"] = "C:\\\\p107-2\\\\accounting.json"
    return document


def write_packet(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_template_is_deliberately_not_materialized() -> None:
    assert validate_run_packet(TEMPLATE)


def test_materialized_packet_is_valid(tmp_path: Path) -> None:
    assert validate_run_packet(write_packet(tmp_path, materialized_packet())) == []


def test_rejects_non_neutral_reviewer_and_missing_restart_policy(tmp_path: Path) -> None:
    document = materialized_packet()
    document["review_policy"]["reviewer_lane_neutral"] = False
    document["contamination_policy"]["restart_affected_lane_required"] = False

    errors = validate_run_packet(write_packet(tmp_path, document))

    assert "review_policy.reviewer_lane_neutral must be True" in errors
    assert "contamination_policy.restart_affected_lane_required must be true" in errors


def test_rejects_soft_review_cap(tmp_path: Path) -> None:
    document = materialized_packet()
    document["review_policy"]["review_cap_kind"] = "soft_measured_stop_condition"
    document["review_policy"]["max_completed_reviews_per_lane"] = 8
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert any("exactly 3" in error for error in errors)
    assert any("exact_three_review_cap" in error for error in errors)


def test_rejects_nudge_and_forbidden_wait_action(tmp_path: Path) -> None:
    document = materialized_packet()
    for action in ("nudge", "timeout", "silence_inference", "repair", "implementation_spawn", "accept", "reject", "lane_end"):
        document["liveness"]["missed_interval_action"] = f"wait_then_{action}"
        errors = validate_run_packet(write_packet(tmp_path, document))
        assert any("metadata-only hard wait" in error for error in errors)
    document["liveness"]["missed_interval_action"] = "inspect_metadata_only_until_schema_valid_verdict"
    document["liveness"]["forbidden_wait_actions"] = ["nudge"]
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert any("exactly the forbidden" in error for error in errors)


def test_rejects_incorrect_review_counts(tmp_path: Path) -> None:
    document = materialized_packet()
    document["review_policy"]["max_repair_cycles_per_lane"] = 1
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert "review_policy.max_repair_cycles_per_lane must be exactly 2" in errors
