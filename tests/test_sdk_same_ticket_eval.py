from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def test_structured_section_report_matches_bare_required_names_to_markdown_headings() -> None:
    evaluator = load_evaluator()
    report = evaluator.structured_section_report(
        "\n".join(
            [
                "## Factual Summary",
                "A compact summary.",
                "## Model And Packaging Comparison",
                "A compact comparison.",
            ]
        ),
        ["Factual Summary", "Model And Packaging Comparison"],
    )

    assert report["missing_sections"] == []
    assert report["unexpected_sections"] == []
    assert not report["has_preamble"]


def test_structured_section_report_matches_markdown_required_names_to_bare_normal_form() -> None:
    evaluator = load_evaluator()
    report = evaluator.structured_section_report(
        "## Factual Summary\nA compact summary.",
        ["## Factual Summary"],
    )

    assert report["missing_sections"] == []
    assert report["unexpected_sections"] == []


def test_empty_expected_marker_classifies_nonempty_message_as_freeform_output() -> None:
    evaluator = load_evaluator()
    classification = evaluator.classify_result(
        status="completed",
        blocker="",
        error="",
        assistant_message='{"record_id":"x"}',
        expected_marker="",
        required_sections=[],
        forbidden_phrases=[],
        allow_unexpected_sections=True,
        allow_preamble=True,
        require_patch=False,
        allowed_patch_files=[],
    )

    assert classification == "freeform-output"


def load_evaluator() -> ModuleType:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "sdk_same_ticket_eval.py"
    spec = importlib.util.spec_from_file_location("sdk_same_ticket_eval", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
