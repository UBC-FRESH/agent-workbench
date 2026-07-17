"""Fail closed on P107.2 contracts that cannot measure the A/B thesis."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _required(mapping: dict[str, Any], key: str, location: str, errors: list[str]) -> Any:
    if key not in mapping:
        errors.append(f"missing {location}.{key}")
        return None
    return mapping[key]


def _mapping(value: Any, location: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{location} must be an object")
    return {}


def validate_gate(gate_path: str | Path) -> list[str]:
    """Return deterministic errors for a P107.2 A/B preflight contract."""
    try:
        gate = json.loads(Path(gate_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read gate: {exc}"]

    if not isinstance(gate, dict):
        return ["gate root must be an object"]

    errors: list[str] = []
    if gate.get("gate_id") != "P107.2":
        errors.append("gate_id must be P107.2")
    if gate.get("status") != "preflight":
        errors.append("status must be preflight")
    if gate.get("live_inference") is not False:
        errors.append("live_inference must be false before a materialized run")

    experiment = _mapping(_required(gate, "experiment", "gate", errors), "experiment", errors)
    expected_experiment = {
        "kind": "retail_codex_vs_agent_workbench_pilot",
        "materialized_run_packet_required": True,
        "common_baseline_required": True,
        "contaminated_lane_restart_required": True,
    }
    for key, expected in expected_experiment.items():
        if experiment.get(key) != expected:
            errors.append(f"experiment.{key} must be {expected!r}")

    workbench = _mapping(_required(gate, "workbench", "gate", errors), "workbench", errors)
    expected_roles = {
        "coordinator": ("gpt-5.6-luna", "openai", None),
        "supervisor": ("gpt-5.6-luna", "openai", "gpt_luna_supervisor"),
        "worker": ("qwen3-coder:latest", "agent_workbench_ollama", "ollama_qwen_coder_worker"),
    }
    for name, (model, provider, role) in expected_roles.items():
        item = _mapping(_required(workbench, name, "workbench", errors), f"workbench.{name}", errors)
        if item.get("model") != model:
            errors.append(f"workbench.{name}.model must be {model}")
        if item.get("provider") != provider:
            errors.append(f"workbench.{name}.provider must be {provider}")
        if role is not None and item.get("role") != role:
            errors.append(f"workbench.{name}.role must be {role}")
        if item.get("fresh_session_required") is not True:
            errors.append(f"workbench.{name}.fresh_session_required must be true")
    if workbench.get("fork_context") is not False:
        errors.append("workbench.fork_context must be false")
    if workbench.get("overrides") != {}:
        errors.append("workbench.overrides must be empty")
    if workbench.get("coordinator_may_edit_implementation") is not False:
        errors.append("Coordinator implementation edits invalidate a lane")
    if workbench.get("worker_final_is_acceptance") is not False:
        errors.append("Worker final response cannot be acceptance")

    review = _mapping(_required(gate, "review", "gate", errors), "review", errors)
    expected_review = {
        "reviewer_role": "gpt_sol_advisor",
        "reviewer_model": "gpt-5.6-terra",
        "reviewer_reasoning_effort": "medium",
        "reviewer_lane_neutral": True,
        "fresh_session_per_run": True,
        "reuse_advisor_with_send_input": True,
        "max_completed_reviews_per_lane": 3,
        "max_repair_cycles_per_lane": 2,
        "defect_packet_required": True,
        "frozen_acceptance_fixture_required": True,
        "initial_packet_max_estimated_tokens": 16000,
        "repair_delta_max_estimated_tokens": 4000,
    }
    for key, expected in expected_review.items():
        if review.get(key) != expected:
            errors.append(f"review.{key} must be {expected!r}")

    liveness = _mapping(_required(gate, "liveness", "gate", errors), "liveness", errors)
    for key, expected in {
        "artifact_inspection_required": True,
        "bounded_status_nudge_required": True,
        "passive_waiting_allowed": False,
    }.items():
        if liveness.get(key) != expected:
            errors.append(f"liveness.{key} must be {expected!r}")

    economics = _mapping(_required(gate, "economics", "gate", errors), "economics", errors)
    for key, expected in {
        "role_token_checkpoints_required": True,
        "maintainer_intervention_log_required": True,
        "pricing_provenance_required_when_available": True,
        "model_catalog_pin_required": True,
        "effective_config_hash_required": True,
        "economics_claim_before_materialized_run": False,
    }.items():
        if economics.get(key) != expected:
            errors.append(f"economics.{key} must be {expected!r}")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_p107_2_economics_gate.py <gate.json>")
    errors = validate_gate(sys.argv[1])
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("P107.2 A/B preflight contract is valid")
