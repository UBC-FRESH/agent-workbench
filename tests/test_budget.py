from __future__ import annotations

import copy
import json
from pathlib import Path

from agent_workbench.budget import (
    render_budget_validation,
    validate_budget_declaration,
)


ROOT = Path(__file__).resolve().parents[1]


def load_template() -> dict:
    return json.loads(
        (ROOT / "templates" / "supervisor_budget_declaration.json").read_text(
            encoding="utf-8"
        )
    )


def test_supervisor_budget_template_is_valid() -> None:
    data = load_template()

    result = validate_budget_declaration(data)

    assert result.ok, result.errors
    rendered = render_budget_validation(data, result)
    assert "Supervisor Budget Validation" in rendered
    assert "budget_declared" in rendered


def test_budget_requires_checkpoint_spans() -> None:
    data = load_template()
    data["checkpoint_spans"] = []

    result = validate_budget_declaration(data)

    assert not result.ok
    assert any("checkpoint_spans" in error for error in result.errors)


def test_budget_rejects_attempt_count_over_limit() -> None:
    data = load_template()
    data["summary_status"]["attempt_count"] = 3

    result = validate_budget_declaration(data)

    assert not result.ok
    assert any("attempt_count cannot exceed max_attempts" in error for error in result.errors)


def test_budget_exceeded_requires_stop_rule() -> None:
    data = load_template()
    data["summary_status"]["budget_exceeded"] = True
    data["summary_status"]["stop_rule_triggered"] = False

    result = validate_budget_declaration(data)

    assert not result.ok
    assert any("budget_exceeded=true" in error for error in result.errors)


def test_tracked_budget_rejects_private_paths() -> None:
    data = copy.deepcopy(load_template())
    data["experiment_question"] = "Audit files under C:" + r"\Users\example\secret"

    result = validate_budget_declaration(data)

    assert not result.ok
    assert any("private-looking" in error for error in result.errors)
