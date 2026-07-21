from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from dataclasses import replace as dc_replace

import pytest

from agent_workbench.workflow_package import (
    StepResult,
    PackageResult,
    load_workflow_package,
    validate_workflow_package,
    render_workflow_package_markdown,
)


def _step(step_id, inputs, outputs):
    return {
        "workflow_id": "test-workflow",
        "step_id": step_id,
        "title": step_id,
        "purpose": "test purpose",
        "input_artifacts": (
            [
                {
                    "artifact_id": item,
                    "kind": "generated",
                    "path_or_reference": item,
                    "provenance": "test",
                    "public_safety": "safe",
                }
                for item in inputs
            ]
            or [
                {
                    "artifact_id": "seed",
                    "kind": "source",
                    "path_or_reference": "seed",
                    "provenance": "test",
                    "public_safety": "safe",
                }
            ]
        ),
        "transformation": "test transformation",
        "implementation": {"type": "script"},
        "output_artifacts": [
            {
                "artifact_id": item,
                "kind": "generated",
                "path_or_reference": item,
                "provenance": "test",
                "public_safety": "safe",
            }
            for item in outputs
        ],
        "verification": {},
        "token_accounting": {},
        "supervisor_decision": {},
    }


def _package(tmp_path, records, names=None):
    for name, record in records.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(record), encoding="utf-8")
    manifest = tmp_path / "package.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "workflow_package_v1",
                "steps": names or [f"{name}.json" for name in records],
            }
        ),
        encoding="utf-8",
    )
    return manifest


def _validate(manifest):
    pkg = load_workflow_package(manifest)
    return validate_workflow_package(pkg, manifest)


class TestLoadWorkflowPackage:
    def test_loads_valid_package(self, tmp_path):
        manifest = _package(tmp_path, {"a": _step("a", [], ["x"])})
        result = load_workflow_package(manifest)
        assert "manifest" in result
        assert "steps" in result
        assert len(result["steps"]) == 1

    def test_rejects_nonexistent_manifest(self, tmp_path):
        with pytest.raises(ValueError, match="manifest not found"):
            load_workflow_package(tmp_path / "nope.json")

    def test_rejects_bad_schema_version(self, tmp_path):
        manifest = tmp_path / "package.json"
        manifest.write_text(json.dumps({"schema_version": "v0", "steps": []}))
        with pytest.raises(ValueError, match="unsupported schema_version"):
            load_workflow_package(manifest)

    def test_rejects_path_escape(self, tmp_path):
        # Create a file outside the package dir
        (tmp_path / "outside.json").write_text("{}")
        manifest = tmp_path / "package.json"
        manifest.write_text(json.dumps({"schema_version": "workflow_package_v1", "steps": ["../outside.json"]}))
        with pytest.raises(ValueError, match="path escapes package root"):
            load_workflow_package(manifest)

    def test_rejects_nonexistent_step_file(self, tmp_path):
        manifest = tmp_path / "package.json"
        manifest.write_text(json.dumps({"schema_version": "workflow_package_v1", "steps": ["missing.json"]}))
        with pytest.raises(ValueError, match="step file not found"):
            load_workflow_package(manifest)


class TestValidateWorkflowPackage:
    def test_orders_steps_deterministically(self, tmp_path):
        manifest = _package(
            tmp_path,
            {"c": _step("c", ["b"], ["c"]), "a": _step("a", [], ["a"]), "b": _step("b", ["a"], ["b"])},
            ["c.json", "a.json", "b.json"],
        )
        result = _validate(manifest)
        assert result.ok
        assert result.step_order == ["a", "b", "c"]

    def test_rejects_malformed_record(self, tmp_path):
        manifest = _package(tmp_path, {"bad": {"step_id": "bad"}})
        result = _validate(manifest)
        assert not result.ok
        assert any("missing required field" in e for e in result.steps[0].errors)

    def test_rejects_cycle(self, tmp_path):
        manifest = _package(
            tmp_path,
            {"a": _step("a", ["b"], ["a"]), "b": _step("b", ["a"], ["b"])},
        )
        result = _validate(manifest)
        assert not result.ok
        assert any("cycle" in e for e in result.errors)

    def test_rejects_missing_producer(self, tmp_path):
        manifest = _package(tmp_path, {"a": _step("a", ["missing"], ["a"])})
        result = _validate(manifest)
        assert not result.ok
        assert any("missing producer" in e for e in result.errors)

    def test_rejects_duplicate_output(self, tmp_path):
        manifest = _package(
            tmp_path,
            {"a": _step("a", [], ["shared"]), "b": _step("b", [], ["shared"])},
        )
        result = _validate(manifest)
        assert not result.ok
        assert any("duplicate produced artifact_id: shared" in e for e in result.errors)

    def test_rejects_duplicate_step_id(self, tmp_path):
        manifest = _package(
            tmp_path,
            {"first": _step("shared-step", [], ["first-output"]),
             "second": _step("shared-step", [], ["second-output"])},
        )
        result = _validate(manifest)
        assert not result.ok
        assert "duplicate step_id: shared-step" in result.errors
        assert not any("cycle" in error for error in result.errors)

    def test_single_step(self, tmp_path):
        manifest = _package(tmp_path, {"a": _step("a", [], ["x"])})
        result = _validate(manifest)
        assert result.ok
        assert result.step_order == ["a"]

    def test_chain_of_five(self, tmp_path):
        records = {}
        for i in range(5):
            inp = [str(i - 1)] if i > 0 else []
            records[str(i)] = _step(str(i), inp, [str(i)])
        manifest = _package(tmp_path, records)
        result = _validate(manifest)
        assert result.ok
        assert result.step_order == ["0", "1", "2", "3", "4"]


class TestRenderWorkflowPackageMarkdown:
    def test_valid_package_markdown(self, tmp_path):
        manifest = _package(tmp_path, {"a": _step("a", [], ["x"])})
        pkg = load_workflow_package(manifest)
        result = validate_workflow_package(pkg, manifest)
        md = render_workflow_package_markdown(result)
        assert "# Workflow Package Report" in md
        assert "**Status:** VALID" in md

    def test_invalid_package_markdown(self, tmp_path):
        manifest = _package(tmp_path, {"bad": {"step_id": "bad"}})
        pkg = load_workflow_package(manifest)
        result = validate_workflow_package(pkg, manifest)
        md = render_workflow_package_markdown(result)
        assert "**Status:** INVALID" in md

    def test_markdown_contains_step_info(self, tmp_path):
        manifest = _package(tmp_path, {"a": _step("a", [], ["x"])})
        pkg = load_workflow_package(manifest)
        result = validate_workflow_package(pkg, manifest)
        md = render_workflow_package_markdown(result)
        assert "`a`" in md


class TestWorkflowPackageCLI:
    def test_cli_renders_deterministic_dependency_ordered_report(self, tmp_path):
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        manifest = _package(
            input_dir,
            {"second": _step("second", ["first-output"], ["second-output"]),
             "first": _step("first", [], ["first-output"])},
            ["second.json", "first.json"],
        )
        output_one = tmp_path / "output-one"
        output_two = tmp_path / "output-two"

        def run(output_dir):
            environment = os.environ.copy()
            source_root = str(Path(__file__).resolve().parents[1] / "src")
            environment["PYTHONPATH"] = (
                source_root
                if not environment.get("PYTHONPATH")
                else source_root + os.pathsep + environment["PYTHONPATH"]
            )
            return subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_workbench.cli",
                    "workflow",
                    "package",
                    "--input",
                    str(manifest),
                    "--output-dir",
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )

        first_run = run(output_one)
        second_run = run(output_two)

        assert first_run.returncode == 0
        assert second_run.returncode == 0
        report_one = (output_one / "package.md").read_text(encoding="utf-8")
        report_two = (output_two / "package.md").read_text(encoding="utf-8")
        assert report_one == report_two
        assert report_one.index("`first`") < report_one.index("`second`")


class TestStepResult:
    def test_defaults(self):
        sr = StepResult(step_id="x", valid=True)
        assert sr.errors == []
        assert sr.input_artifacts == []
        assert sr.output_artifacts == []

    def test_replacement(self):
        sr = StepResult(step_id="x", valid=False, errors=["err1"])
        new_sr = dc_replace(sr, valid=True, errors=[])
        assert new_sr.valid is True
        assert new_sr.errors == []


class TestPackageResult:
    def test_defaults(self):
        pr = PackageResult(ok=True)
        assert pr.step_order == []
        assert pr.steps == []
        assert pr.errors == []
