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
    bundle = tmp_path / "bundle.json"; bundle.write_text("{}", encoding="utf-8")
    verdict = tmp_path / "verdict.json"; verdict.write_text("{}", encoding="utf-8")
    active = {"C0": ["coordinator", "advisor"], "C1": ["coordinator", "worker", "advisor"], "C2": ["coordinator", "supervisor", "worker", "advisor"], "C3": ["coordinator", "supervisor", "advisor", "worker"], "C4": ["coordinator", "supervisor", "worker", "advisor"]}[configuration]
    sessions = [{"session_id": f"{role}-1", "role": role, "provider": "fixture", "model_class": "fixture"} for role in active]
    document = {
        "schema_version": "p107_materialized_run_v1", "run_id": "run-1", "configuration_id": configuration,
        "frozen_files": [{"path": "frozen.txt", "sha256": digest}],
        "topology": {"coordinator_children": (["supervisor", "advisor"] if configuration == "C3" else active[1:]), "supervisor_spawned": False, "nested_worker_spawned": configuration == "C3"},
        "sessions": sessions, "prior_session_ids": [],
        "implementation_edits": {"coordinator_paths": []}, "contamination": {"contaminated": False},
        "advisor": {"bundle_path": "bundle.json", "verdict_path": "verdict.json", "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(), "verdict_sha256": hashlib.sha256(verdict.read_bytes()).hexdigest(),
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
    doc = json.loads(path.read_text()); doc["sessions"][1]["session_id"] = "coordinator-1"; doc["prior_session_ids"] = ["coordinator-1"]
    doc["implementation_edits"]["coordinator_paths"] = ["src/app.py"]; doc["contamination"]["contaminated"] = True
    doc["advisor"]["verdict_run_id"] = "other"; doc["advisor"]["verdict_lineage_id"] = "other"; doc["advisor"]["verdict"] = "pending"
    path.write_text(json.dumps(doc))
    errors = validate_materialized_run(path)
    assert "duplicate session IDs" in errors and "reused session ID" in errors
    assert "Coordinator implementation edits are forbidden for C1-C4" in errors
    assert "contamination must be false" in errors
    assert "Advisor bundle/verdict run binding mismatch" in errors
    assert "Advisor bundle/verdict lineage mismatch" in errors
    assert "Advisor verdict is missing or invalid" in errors


def test_rejects_topology_custody_and_unsafe_artifacts(tmp_path: Path) -> None:
    path = make_run(tmp_path, "C3")
    doc = json.loads(path.read_text())
    doc["topology"]["coordinator_children"] = ["supervisor", "advisor", "advisor"]
    doc["topology"]["nested_worker_spawned"] = False
    doc["sessions"][0].pop("provider")
    doc["implementation_edits"]["coordinator_paths"] = ["src/app.py"]
    doc["advisor"]["bundle_path"] = "../bundle.json"
    doc["advisor"]["verdict_path"] = "bundle.json"
    path.write_text(json.dumps(doc))
    errors = validate_materialized_run(path)
    assert "topology coordinator children mismatch" in errors
    assert "C3 nested Worker spawn is required" in errors
    assert "sessions[0].provider must be declared" in errors
    assert "Coordinator implementation edits are forbidden for C1-C4" in errors
    assert "advisor.bundle_path must be beneath the materialized-run directory" in errors


def test_rejects_c3_direct_worker_child_and_missing_worker_session(tmp_path: Path) -> None:
    path = make_run(tmp_path, "C3")
    doc = json.loads(path.read_text())
    doc["topology"]["coordinator_children"].append("worker")
    doc["sessions"] = [session for session in doc["sessions"] if session["role"] != "worker"]
    path.write_text(json.dumps(doc))
    errors = validate_materialized_run(path)
    assert "topology coordinator children mismatch" in errors
    assert "sessions must contain each active role exactly once" in errors


@pytest.mark.parametrize("configuration", ["C0", "C1", "C2", "C4"])
def test_rejects_supervisor_spawn_in_flat_configurations(tmp_path: Path, configuration: str) -> None:
    path = make_run(tmp_path, configuration)
    doc = json.loads(path.read_text())
    doc["topology"]["supervisor_spawned"] = True
    path.write_text(json.dumps(doc))
    assert f"{configuration} Supervisor spawn is forbidden" in validate_materialized_run(path)
