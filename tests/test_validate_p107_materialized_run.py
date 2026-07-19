from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_materialized_run import validate_materialized_run


def make_run(tmp_path: Path, configuration: str = "C1") -> Path:
    frozen = tmp_path / "frozen.txt"
    frozen.write_text("public fixture\n", encoding="utf-8")
    digest = hashlib.sha256(frozen.read_bytes()).hexdigest()
    document = {
        "schema_version": "p107_materialized_run_v1", "run_id": "run-1", "configuration_id": configuration,
        "frozen_files": [{"path": "frozen.txt", "sha256": digest}],
        "topology": {"coordinator_children": (["worker", "advisor"] if configuration == "C1" else ["supervisor", "advisor"] if configuration == "C3" else ["supervisor", "worker", "advisor"]), "supervisor_spawned": False},
        "sessions": [{"session_id": "coord-1"}, {"session_id": "advisor-1"}], "prior_session_ids": [],
        "implementation_edits": {"coordinator_paths": []}, "contamination": {"contaminated": False},
        "advisor": {"bundle_path": "bundle.json", "verdict_path": "verdict.json", "bundle_sha256": "a" * 64, "verdict_sha256": "b" * 64,
                    "run_id": "run-1", "bundle_run_id": "run-1", "verdict_run_id": "run-1", "lineage_id": "line-1", "bundle_lineage_id": "line-1", "verdict_lineage_id": "line-1", "verdict": "accepted"},
    }
    path = tmp_path / "run.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


@pytest.mark.parametrize("configuration", ["C1", "C2", "C3", "C4"])
def test_valid_materialized_run_c1_through_c4(tmp_path: Path, configuration: str) -> None:
    assert validate_materialized_run(make_run(tmp_path, configuration)) == []


def test_rejects_hash_topology_and_c2_spawn(tmp_path: Path) -> None:
    path = make_run(tmp_path, "C2")
    doc = json.loads(path.read_text()); doc["frozen_files"][0]["sha256"] = "c" * 64
    doc["topology"]["coordinator_children"] = ["worker"]; doc["topology"]["supervisor_spawned"] = True
    path.write_text(json.dumps(doc))
    errors = validate_materialized_run(path)
    assert "frozen_files[0] hash mismatch" in errors
    assert "topology coordinator children mismatch" in errors
    assert "C2 Supervisor spawn is forbidden" in errors


def test_rejects_session_reuse_edits_contamination_and_advisor_binding(tmp_path: Path) -> None:
    path = make_run(tmp_path)
    doc = json.loads(path.read_text()); doc["sessions"][1]["session_id"] = "coord-1"; doc["prior_session_ids"] = ["coord-1"]
    doc["implementation_edits"]["coordinator_paths"] = ["src/app.py"]; doc["contamination"]["contaminated"] = True
    doc["advisor"]["verdict_run_id"] = "other"; doc["advisor"]["verdict_lineage_id"] = "other"; doc["advisor"]["verdict"] = "pending"
    path.write_text(json.dumps(doc))
    errors = validate_materialized_run(path)
    assert "duplicate session IDs" in errors and "reused session ID" in errors
    assert "Coordinator implementation edits are forbidden for C1/C4" in errors
    assert "contamination must be false" in errors
    assert "Advisor bundle/verdict run binding mismatch" in errors
    assert "Advisor bundle/verdict lineage mismatch" in errors
    assert "Advisor verdict is missing or invalid" in errors
