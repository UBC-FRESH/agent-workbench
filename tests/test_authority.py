from __future__ import annotations

import copy
import json
from pathlib import Path

from agent_workbench.authority import (
    render_supervisor_job_contract,
    render_supervisor_report,
    validate_supervisor_job_contract,
    validate_supervisor_report,
)


ROOT = Path(__file__).resolve().parents[1]


def load_template(name: str) -> dict:
    return json.loads((ROOT / "templates" / name).read_text(encoding="utf-8"))


def test_supervisor_job_contract_template_is_valid() -> None:
    data = load_template("supervisor_job_contract.json")

    result = validate_supervisor_job_contract(data)

    assert result.ok, result.errors
    rendered = render_supervisor_job_contract(data)
    assert "Supervisor Job Contract" in rendered
    assert "`job_complete`" in rendered


def test_supervisor_report_template_is_valid() -> None:
    data = load_template("supervisor_job_report.json")

    result = validate_supervisor_report(data)

    assert result.ok, result.errors
    rendered = render_supervisor_report(data)
    assert "Supervisor Report" in rendered
    assert "`needs_coordinator_review`" in rendered


def test_contract_requires_all_authority_roles() -> None:
    data = load_template("supervisor_job_contract.json")
    data["authority_model"]["levels"] = data["authority_model"]["levels"][:-1]

    result = validate_supervisor_job_contract(data)

    assert not result.ok
    assert any("missing roles" in error for error in result.errors)


def test_tracked_contract_rejects_private_paths() -> None:
    data = load_template("supervisor_job_contract.json")
    data["workspace"]["root"] = "C:" + r"\Users\example\Projects\agent-workbench"
    data["workspace"]["root_policy"] = "absolute_runtime_path"

    result = validate_supervisor_job_contract(data)

    assert not result.ok
    assert any("private-looking value" in error for error in result.errors)


def test_runtime_contract_can_use_absolute_workspace_root() -> None:
    data = load_template("supervisor_job_contract.json")
    data["workspace"]["root"] = "C:" + r"\Users\example\Projects\agent-workbench"
    data["workspace"]["root_policy"] = "absolute_runtime_path"
    data["public_safety"]["tracked_artifact"] = False

    result = validate_supervisor_job_contract(data)

    assert result.ok, result.errors


def test_report_rejects_unknown_final_signal() -> None:
    data = copy.deepcopy(load_template("supervisor_job_report.json"))
    data["final_signal"] = "done_but_vague"

    result = validate_supervisor_report(data)

    assert not result.ok
    assert any("final_signal" in error for error in result.errors)


def test_report_requires_subagent_payload_excerpt_when_attempted() -> None:
    data = copy.deepcopy(load_template("supervisor_job_report.json"))
    del data["verification"]["subagent_payload_excerpt"]

    result = validate_supervisor_report(data)

    assert not result.ok
    assert any("subagent_payload_excerpt" in error for error in result.errors)


def test_report_requires_subagent_result_status_when_attempted() -> None:
    data = copy.deepcopy(load_template("supervisor_job_report.json"))
    del data["verification"]["subagent_result_status"]

    result = validate_supervisor_report(data)

    assert not result.ok
    assert any("subagent_result_status" in error for error in result.errors)


def test_report_requires_repair_summary_for_repaired_subagent_result() -> None:
    data = copy.deepcopy(load_template("supervisor_job_report.json"))
    data["verification"]["subagent_result_status"] = "accepted_after_supervisor_repair"
    data["verification"]["subagent_repair_summary"] = ""

    result = validate_supervisor_report(data)

    assert not result.ok
    assert any("subagent_repair_summary" in error for error in result.errors)


def test_report_without_subagent_attempt_does_not_require_payload_excerpt() -> None:
    data = copy.deepcopy(load_template("supervisor_job_report.json"))
    data["verification"]["subagent_invocation_attempted"] = False
    for field in (
        "subagent_invocation_observed_by_supervisor",
        "subagent_name",
        "subagent_payload_excerpt",
        "subagent_result_status",
        "subagent_repair_summary",
    ):
        data["verification"].pop(field, None)

    result = validate_supervisor_report(data)

    assert result.ok, result.errors
