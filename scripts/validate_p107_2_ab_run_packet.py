"""Validate a materialized P107.2 A/B run packet before either lane starts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _object(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{name} must be an object")
    return {}


def _nonempty(value: Any, name: str, errors: list[str]) -> str:
    if isinstance(value, str) and value.strip() and "REPLACE_WITH" not in value:
        return value
    errors.append(f"{name} must be materialized")
    return ""


def _sha(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        errors.append(f"{name} must be a lowercase SHA-256")


def validate_run_packet(path: str | Path) -> list[str]:
    try:
        packet = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read run packet: {exc}"]
    if not isinstance(packet, dict):
        return ["run packet root must be an object"]

    errors: list[str] = []
    if packet.get("schema_version") != "p107_2_ab_run_packet_v1":
        errors.append("schema_version must be p107_2_ab_run_packet_v1")
    _nonempty(packet.get("run_id"), "run_id", errors)
    if not isinstance(packet.get("baseline_commit"), str) or not COMMIT.fullmatch(packet["baseline_commit"]):
        errors.append("baseline_commit must be a 40-character lowercase commit")

    lanes = _object(packet.get("lanes"), "lanes", errors)
    retail = _object(lanes.get("retail"), "lanes.retail", errors)
    workbench = _object(lanes.get("workbench"), "lanes.workbench", errors)
    for name, lane in (("lanes.retail", retail), ("lanes.workbench", workbench)):
        _nonempty(lane.get("worktree"), f"{name}.worktree", errors)
        if lane.get("fresh_implementation_session_required") is not True:
            errors.append(f"{name}.fresh_implementation_session_required must be true")
    for key, expected in {
        "coordinator_role": "gpt-5.6-luna",
        "supervisor_role": "gpt_luna_supervisor",
        "worker_role": "ollama_qwen_coder_worker",
        "fork_context": False,
        "overrides": {},
    }.items():
        if workbench.get(key) != expected:
            errors.append(f"lanes.workbench.{key} must be {expected!r}")

    for section_name in ("ticket", "acceptance_fixture", "usability_rubric"):
        section = _object(packet.get(section_name), section_name, errors)
        _nonempty(section.get("path"), f"{section_name}.path", errors)
        _sha(section.get("sha256"), f"{section_name}.sha256", errors)
    if not _nonempty(
        _object(packet.get("acceptance_fixture"), "acceptance_fixture", errors).get("command"),
        "acceptance_fixture.command",
        errors,
    ):
        pass

    scope = _object(packet.get("implementation_scope"), "implementation_scope", errors)
    if not isinstance(scope.get("allowed_paths"), list) or not scope["allowed_paths"]:
        errors.append("implementation_scope.allowed_paths must be a nonempty list")

    review = _object(packet.get("review_policy"), "review_policy", errors)
    expected_review = {
        "reviewer_role": "gpt_sol_advisor",
        "reviewer_model": "gpt-5.6-terra",
        "reviewer_reasoning_effort": "medium",
        "reviewer_lane_neutral": True,
        "fresh_session_per_run": True,
        "reuse_advisor_with_send_input": True,
        "review_cap_kind": "soft_measured_stop_condition",
    }
    for key, expected in expected_review.items():
        if review.get(key) != expected:
            errors.append(f"review_policy.{key} must be {expected!r}")
    review_cap = review.get("max_completed_reviews_per_lane")
    repair_cap = review.get("max_repair_cycles_per_lane")
    if not isinstance(review_cap, int) or not 1 <= review_cap <= 8:
        errors.append("review_policy.max_completed_reviews_per_lane must be an integer from 1 through 8")
    if not isinstance(repair_cap, int) or repair_cap != max((review_cap or 0) - 1, 0):
        errors.append("review_policy.max_repair_cycles_per_lane must equal max_completed_reviews_per_lane minus one")
    if not isinstance(review.get("defect_packet_required_fields"), list):
        errors.append("review_policy.defect_packet_required_fields must be a list")
    if review.get("initial_packet_max_estimated_tokens") != 16000:
        errors.append("review_policy.initial_packet_max_estimated_tokens must be 16000")
    if review.get("repair_delta_max_estimated_tokens") != 4000:
        errors.append("review_policy.repair_delta_max_estimated_tokens must be 4000")

    liveness = _object(packet.get("liveness"), "liveness", errors)
    if not isinstance(liveness.get("interval_seconds"), int) or liveness["interval_seconds"] <= 0:
        errors.append("liveness.interval_seconds must be a positive integer")
    if liveness.get("missed_interval_action") != "inspect_then_one_bounded_nudge_or_verified_blocker":
        errors.append("liveness.missed_interval_action is invalid")

    contamination = _object(packet.get("contamination_policy"), "contamination_policy", errors)
    for key in (
        "restart_affected_lane_required",
        "coordinator_implementation_edit_invalidates_lane",
        "shared_mutable_checkout_invalidates_lane",
        "fixture_mutation_invalidates_lane",
        "cross_lane_context_leak_invalidates_lane",
    ):
        if contamination.get(key) is not True:
            errors.append(f"contamination_policy.{key} must be true")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_p107_2_ab_run_packet.py <materialized-run-packet.json>")
    errors = validate_run_packet(sys.argv[1])
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("P107.2 A/B run packet is valid")
