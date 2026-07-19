from __future__ import annotations

import hashlib
import json
import sys
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_materialized_run import validate_materialized_run


def make_run(tmp_path: Path, configuration: str = "C1") -> Path:
    repo = tmp_path / "worktree"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
    (repo / "tracked.txt").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    frozen = tmp_path / "frozen.txt"
    frozen.write_text("public fixture\n", encoding="utf-8")
    digest = hashlib.sha256(frozen.read_bytes()).hexdigest()
    bundle = tmp_path / "bundle.json"
    bundle_data = {"bundle_sha256": "", "run_id": "run-1", "review_number": 1, "packet_kind": "initial", "packet_bytes": 1, "estimated_input_tokens": 1, "acceptance_output": "ok", "scope_report": "ok", "changed_files": [], "contamination_status": "clean", "advisor_session_id": "advisor-1", "advisor_lineage_id": "line-1", "previous_defect_packet": None}
    bundle_data["bundle_sha256"] = hashlib.sha256((json.dumps(bundle_data, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    bundle.write_text(json.dumps(bundle_data), encoding="utf-8")
    verdict = tmp_path / "verdict.json"
    verdict_data = {"review_number": 1, "verdict": "accepted", "deterministic_acceptance": True, "correctness": 4, "score": 10, "critical_defects": [], "defect_packet": None, "run_id": "run-1", "bundle_sha256": bundle_data["bundle_sha256"], "advisor_session_id": "advisor-1", "advisor_lineage_id": "line-1"}
    verdict.write_text(json.dumps(verdict_data), encoding="utf-8")
    active = {"C0": ["coordinator", "advisor"], "C1": ["coordinator", "worker", "advisor"], "C2": ["coordinator", "supervisor", "worker", "advisor"], "C3": ["coordinator", "supervisor", "advisor", "worker"], "C4": ["coordinator", "supervisor", "worker", "advisor"]}[configuration]
    edges = {"C0": [("coordinator", "advisor")], "C1": [("coordinator", "worker"), ("coordinator", "advisor")], "C2": [("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")], "C3": [("coordinator", "supervisor"), ("coordinator", "advisor"), ("supervisor", "worker")], "C4": [("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")]}[configuration]
    sessions = []
    for role in active:
        parent = None if role == "coordinator" else next(p for p, c in edges if c == role)
        raw = tmp_path / f"{role}.jsonl"; raw.write_text(json.dumps({"session_id": f"{role}-1", "role": role}) + "\n", encoding="utf-8")
        sessions.append({"session_id": f"{role}-1", "role": role, "provider": "fixture", "model_class": "fixture", "parent_session_id": None if parent is None else f"{parent}-1", "raw_session_path": raw.name, "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "terminal_event": "completed"})
    spawn_artifacts = []
    spawn_edges = []
    for parent, child in edges:
        artifact = tmp_path / f"spawn_{parent}_{child}.json"; artifact.write_text(json.dumps({"parent": parent, "child": child}), encoding="utf-8")
        spawn_artifacts.append(artifact)
        spawn_edges.append({"parent_session_id": f"{parent}-1", "child_session_id": f"{child}-1", "parent_role": parent, "child_role": child, "fork_context": False, "source_artifact_path": artifact.name, "source_artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()})
    manifest = {"schema_version": "p107_run_evidence_manifest_v1", "run_id": "run-1", "configuration_id": configuration, "repository_path": str(repo), "starting_commit": commit, "terminal_event": "completed", "raw_sessions": sessions, "spawn_edges": spawn_edges}
    manifest_path = tmp_path / "evidence-manifest.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    document = {
        "schema_version": "p107_materialized_run_v1", "run_id": "run-1", "configuration_id": configuration,
        "evidence_manifest_path": manifest_path.name, "evidence_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(), "repository_path": str(repo), "starting_commit": commit, "terminal_event": "completed",
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


@pytest.mark.parametrize("configuration", ["C2", "C4"])
def test_rejects_nested_worker_spawn_in_flat_configurations(tmp_path: Path, configuration: str) -> None:
    path = make_run(tmp_path, configuration)
    doc = json.loads(path.read_text()); doc["topology"]["nested_worker_spawned"] = True
    path.write_text(json.dumps(doc))
    assert f"{configuration} nested Worker spawn must be explicitly false" in validate_materialized_run(path)


def test_rejects_empty_advisor_artifacts(tmp_path: Path) -> None:
    path = make_run(tmp_path)
    for name in ("bundle.json", "verdict.json"):
        (tmp_path / name).write_text("{}", encoding="utf-8")
    assert any("Advisor review:" in error for error in validate_materialized_run(path))


def test_rejects_cross_artifact_identity_mismatch(tmp_path: Path) -> None:
    path = make_run(tmp_path)
    verdict = tmp_path / "verdict.json"
    data = json.loads(verdict.read_text()); data["advisor_lineage_id"] = "other"
    verdict.write_text(json.dumps(data), encoding="utf-8")
    assert "Advisor review: Advisor session/lineage mismatch" in validate_materialized_run(path)
