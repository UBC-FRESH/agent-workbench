"""Validate the public-safe P114 C4 capability-parity preregistration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_CONTRACT = Path("benchmarks/document_library/p114_c4_capability_contract.json")
REQUIRED_CAPABILITIES = {
    "effective_identity",
    "literal_worktree_binding",
    "repository_read_surface",
    "native_patch_surface",
    "declared_shell_validation",
    "tool_history_continuation",
    "repair_continuation",
    "result_artifact_flow",
    "role_authority_boundaries",
    "unsupported_tool_fail_closed",
}
REQUIRED_STAGES = {"P114.1", "P114.2", "P114.3", "P114.4", "P114.5"}


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["contract must be a JSON object"]
    if data.get("contract_id") != "p114_c4_capability_parity_v1":
        errors.append("unexpected contract_id")
    if data.get("phase") != "P114" or data.get("status") != "preregistered":
        errors.append("contract must be a preregistered P114 record")
    if data.get("live_inference") is not False:
        errors.append("preregistration must not enable live inference")
    frozen = data.get("frozen_before_live")
    if not isinstance(frozen, dict):
        errors.append("missing frozen_before_live block")
    else:
        candidate = frozen.get("candidate_worker")
        if not isinstance(candidate, dict) or candidate.get("role") != "ollama_qwen_coder_worker" or candidate.get("model") != "qwen3-coder:latest" or candidate.get("fresh_session_required") is not True:
            errors.append("candidate Worker identity must be frozen")
        skills = frozen.get("skills")
        if not isinstance(skills, dict) or skills.get("required") is not False or not isinstance(skills.get("reason"), str):
            errors.append("skills scope must be explicitly declared")
    capabilities = data.get("required_capabilities")
    if not isinstance(capabilities, list):
        errors.append("required_capabilities must be a list")
    else:
        by_id = {item.get("id"): item for item in capabilities if isinstance(item, dict)}
        if set(by_id) != REQUIRED_CAPABILITIES:
            errors.append("required capabilities must match the declared minimum interface")
        for capability_id, item in by_id.items():
            if not isinstance(item.get("owner"), str) or not item["owner"]:
                errors.append(f"{capability_id}: missing owner")
            if not isinstance(item.get("required_evidence"), str) or not item["required_evidence"]:
                errors.append(f"{capability_id}: missing required evidence")
            if item.get("failure_class") not in {"bridge_host", "protocol"}:
                errors.append(f"{capability_id}: invalid failure class")
    stages = data.get("execution_stages")
    if not isinstance(stages, list):
        errors.append("execution_stages must be a list")
    else:
        by_id = {item.get("id"): item for item in stages if isinstance(item, dict)}
        if set(by_id) != REQUIRED_STAGES:
            errors.append("execution stages must contain P114.1 through P114.5")
        for stage_id, item in by_id.items():
            if not isinstance(item.get("pass_rule"), str) or not item["pass_rule"]:
                errors.append(f"{stage_id}: missing pass rule")
        if by_id.get("P114.1", {}).get("live_inference") is not False or by_id.get("P114.2", {}).get("live_inference") is not False or by_id.get("P114.3", {}).get("live_inference") is not False:
            errors.append("P114.1-P114.3 must not use live inference")
        if by_id.get("P114.4", {}).get("live_inference") is not True or by_id.get("P114.5", {}).get("live_inference") is not True:
            errors.append("P114.4-P114.5 must declare live inference")
    stop_rules = data.get("stop_rules")
    if not isinstance(stop_rules, dict) or set(stop_rules) != {"engineering_stage_attempts", "live_battery_restart", "repeated_failure", "paid_integration_budget"}:
        errors.append("stop rules must define attempts, restart, repeated failure, and paid integration budget")
    prerequisites = data.get("comparison_prerequisites")
    if not isinstance(prerequisites, dict) or not isinstance(prerequisites.get("p107_may_resume_only_after"), list) or len(prerequisites["p107_may_resume_only_after"]) < 4:
        errors.append("P107 comparison prerequisites must be explicit")
    if not isinstance(data.get("external_validity"), str) or not data["external_validity"]:
        errors.append("external validity scope is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()
    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"p114 C4 capability contract: invalid ({exc})")
        return 1
    errors = validate(data)
    if errors:
        print("p114 C4 capability contract: invalid")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("p114 C4 capability contract: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
