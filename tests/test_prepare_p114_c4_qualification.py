from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prepare_p114", ROOT / "scripts" / "prepare_p114_c4_qualification.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_prepare_rejects_missing_or_tampered_frozen_inputs(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()
    for name in MODULE.INPUTS:
        (source / name).write_text("wrong\n", encoding="utf-8")

    try:
        MODULE.prepare(tmp_path, tmp_path / "run", source)
    except ValueError as exc:
        assert "frozen input hash mismatch" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("tampered bundle was accepted")


def test_qualification_manifest_declares_only_frozen_workload_paths() -> None:
    assert MODULE.BASELINE == "139e725ee069c27cf68c797dd66aa88b5bb2824d"
    assert MODULE.WORKLOAD_ID == "p107-provenance-audit-bundle-v1"
    assert set(MODULE.INPUTS) == {
        "p107_suite_provenance_audit_bundle_ticket.md",
        "p107_suite_provenance_audit_bundle_acceptance.py",
        "p107_suite_provenance_audit_bundle_workload_manifest.json",
    }


def test_prepare_accepts_an_explicit_short_worktree_path(tmp_path: Path) -> None:
    assert "worktree" in inspect.signature(MODULE.prepare).parameters
