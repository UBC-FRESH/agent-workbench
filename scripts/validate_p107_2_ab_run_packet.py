"""Validate a materialized P107.2 A/B run packet before either lane starts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from hashlib import sha256
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


def _materialized_file(value: Any, name: str, root: Path, declared_sha: Any, errors: list[str]) -> None:
    path_text = _nonempty(value, f"{name}.path", errors)
    _sha(declared_sha, f"{name}.sha256", errors)
    if not path_text:
        return
    path = Path(path_text)
    if not path.is_absolute():
        errors.append(f"{name}.path must be absolute and canonical")
        return
    try:
        resolved = path.resolve(strict=True)
        allowed_root = root.resolve(strict=True)
        resolved.relative_to(allowed_root)
    except (OSError, ValueError):
        errors.append(f"{name}.path must be an existing file under the run root")
        return
    if str(path) != str(resolved) or path.is_symlink() or not resolved.is_file():
        errors.append(f"{name}.path must be a canonical regular non-symlink file")
        return
    if isinstance(declared_sha, str) and SHA256.fullmatch(declared_sha):
        actual = sha256(resolved.read_bytes()).hexdigest()
        if actual != declared_sha:
            errors.append(f"{name}.sha256 does not match file contents")


def _worktree(value: Any, name: str, baseline: str, errors: list[str]) -> Path | None:
    text = _nonempty(value, f"{name}.worktree", errors)
    if not text:
        return None
    path = Path(text)
    if not path.is_absolute() or not path.is_dir() or path.is_symlink():
        errors.append(f"{name}.worktree must be an existing non-symlink directory")
        return None
    try:
        top = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, timeout=5,
        ).stdout.strip()
        head = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=5,
        ).stdout.strip()
        if Path(top).resolve() != path.resolve():
            raise ValueError("not a git worktree root")
        if head != baseline:
            raise ValueError("worktree is not at baseline commit")
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        errors.append(f"{name}.worktree must be a git worktree at baseline_commit")
        return None
    return path.resolve()


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
    baseline = packet.get("baseline_commit", "")
    worktrees = []
    for name, lane in (("lanes.retail", retail), ("lanes.workbench", workbench)):
        candidate = _worktree(lane.get("worktree"), name, baseline, errors)
        if candidate is not None:
            worktrees.append((name, candidate))
        if lane.get("fresh_implementation_session_required") is not True:
            errors.append(f"{name}.fresh_implementation_session_required must be true")
    if len(worktrees) == 2 and worktrees[0][1] == worktrees[1][1]:
        errors.append("lanes.retail.worktree and lanes.workbench.worktree must be distinct")
    for key, expected in {
        "coordinator_role": "gpt-5.6-luna",
        "supervisor_role": "gpt_luna_supervisor",
        "worker_role": "ollama_qwen_coder_worker",
        "fork_context": False,
        "overrides": {},
    }.items():
        if workbench.get(key) != expected:
            errors.append(f"lanes.workbench.{key} must be {expected!r}")

    run_root = Path(path).resolve().parent
    for section_name in ("ticket", "acceptance_fixture", "usability_rubric"):
        section = _object(packet.get(section_name), section_name, errors)
        _materialized_file(section.get("path"), section_name, run_root, section.get("sha256"), errors)
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
        "review_cap_kind": "exact_three_review_cap",
        "hard_wait": True,
        "hard_wait_allowed_action": "wait_for_schema_valid_verdict",
        "hard_wait_forbidden_actions": ["nudge", "timeout", "silence_inference", "repair", "implementation_spawn", "accept", "reject", "lane_end"],
    }
    for key, expected in expected_review.items():
        if review.get(key) != expected:
            errors.append(f"review_policy.{key} must be {expected!r}")
    review_cap = review.get("max_completed_reviews_per_lane")
    repair_cap = review.get("max_repair_cycles_per_lane")
    if review_cap != 3:
        errors.append("review_policy.max_completed_reviews_per_lane must be exactly 3")
    if repair_cap != 2:
        errors.append("review_policy.max_repair_cycles_per_lane must be exactly 2")
    if not isinstance(review.get("defect_packet_required_fields"), list):
        errors.append("review_policy.defect_packet_required_fields must be a list")
    if review.get("initial_packet_max_estimated_tokens") != 16000:
        errors.append("review_policy.initial_packet_max_estimated_tokens must be 16000")
    if review.get("repair_delta_max_estimated_tokens") != 4000:
        errors.append("review_policy.repair_delta_max_estimated_tokens must be 4000")

    liveness = _object(packet.get("liveness"), "liveness", errors)
    if not isinstance(liveness.get("interval_seconds"), int) or liveness["interval_seconds"] <= 0:
        errors.append("liveness.interval_seconds must be a positive integer")
    if liveness.get("missed_interval_action") != "inspect_metadata_only_until_schema_valid_verdict":
        errors.append("liveness.missed_interval_action must be metadata-only hard wait")
    forbidden = set(liveness.get("forbidden_wait_actions", []))
    required_forbidden = {"nudge", "timeout", "silence_inference", "repair", "implementation_spawn", "accept", "reject", "lane_end"}
    if forbidden != required_forbidden:
        errors.append("liveness.forbidden_wait_actions must contain exactly the forbidden hard-wait actions")

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

    accounting = _object(packet.get("accounting"), "accounting", errors)
    _nonempty(accounting.get("record_path"), "accounting.record_path", errors)
    if accounting.get("record_schema") != "p107_accounting_record_v1":
        errors.append("accounting.record_schema must be p107_accounting_record_v1")
    required_accounting_fields = {
        "source_session_identity", "pricing_catalog", "run_accounting", "roles",
        "tokens", "token_usd", "checkpoints", "provider", "model", "provenance",
    }
    if set(accounting.get("required_fields", [])) != required_accounting_fields:
        errors.append("accounting.required_fields must include all token and provenance fields")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_p107_2_ab_run_packet.py <materialized-run-packet.json>")
    errors = validate_run_packet(sys.argv[1])
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("P107.2 A/B run packet is valid")
