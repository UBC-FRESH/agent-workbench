from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_run_evidence_manifest import validate_manifest

def make_manifest(tmp_path: Path, config: str) -> Path:
    repo = tmp_path / "repo"; repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
    (repo / "tracked").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked"], cwd=repo, check=True); subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    roles = {"C0": ["coordinator", "advisor"], "C2": ["coordinator", "supervisor", "worker", "advisor"], "C3": ["coordinator", "supervisor", "worker", "advisor"], "C4": ["coordinator", "supervisor", "worker", "advisor"]}[config]
    parent = {"coordinator": None, "supervisor": "coordinator", "worker": ("coordinator" if config == "C2" else "supervisor"), "advisor": "coordinator"}
    sessions = []
    for role in roles:
        name = f"{role}.jsonl"; (tmp_path / name).write_text(role, encoding="utf-8")
        sessions.append({"role": role, "session_id": f"{role}-1", "parent_session_id": (None if parent[role] is None else f"{parent[role]}-1"), "provider": "fixture", "model_class": "fixture", "raw_session_path": name, "sha256": hashlib.sha256((tmp_path / name).read_bytes()).hexdigest(), "terminal_event": "completed"})
    pairs = {"C0": [("coordinator", "advisor")], "C2": [("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")], "C3": [("coordinator", "supervisor"), ("coordinator", "advisor"), ("supervisor", "worker")], "C4": [("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")]}[config]
    edges = []
    for p, c in pairs:
        source = tmp_path / f"edge-{p}-{c}.json"; source.write_text(f"{p}->{c}", encoding="utf-8")
        edges.append({"parent_session_id": f"{p}-1", "child_session_id": f"{c}-1", "parent_role": p, "child_role": c, "fork_context": False, "source_artifact_path": source.name, "source_artifact_sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    path = tmp_path / "manifest.json"; path.write_text(json.dumps({"schema_version": "p107_run_evidence_manifest_v1", "run_id": "run-1", "configuration_id": config, "repository_path": str(repo), "starting_commit": commit, "terminal_event": "completed", "raw_sessions": sessions, "spawn_edges": edges}), encoding="utf-8")
    return path

@pytest.mark.parametrize("config", ["C0", "C2", "C3"])
def test_valid_configurations(tmp_path: Path, config: str):
    assert validate_manifest(make_manifest(tmp_path, config)) == []

@pytest.mark.parametrize("mutation, expected", [
    (lambda d: d["raw_sessions"][0].update(raw_session_path="missing.jsonl"), "raw_session_path must be an existing regular file"),
    (lambda d: d["raw_sessions"][0].update(sha256="0" * 64), "raw_sessions[0] hash mismatch"),
    (lambda d: d["spawn_edges"][0].update(child_session_id="forged"), "references unknown session"),
    (lambda d: d["spawn_edges"][0].update(fork_context=True), "fork_context must be false"),
])
def test_rejects_adversarial_manifest(tmp_path: Path, mutation, expected):
    path = make_manifest(tmp_path, "C2"); doc = json.loads(path.read_text()); mutation(doc); path.write_text(json.dumps(doc))
    assert any(expected in error for error in validate_manifest(path))

def test_rejects_forbidden_nested_worker_and_dirty_repo(tmp_path: Path):
    for config in ("C2", "C4"):
        path = make_manifest(tmp_path / config, config); doc = json.loads(path.read_text()); doc["spawn_edges"].append({**doc["spawn_edges"][1], "parent_session_id": "supervisor-1", "parent_role": "supervisor"}); path.write_text(json.dumps(doc))
        assert "spawn topology is undeclared or forbidden" in validate_manifest(path)
    path = make_manifest(tmp_path / "dirty", "C2"); doc = json.loads(path.read_text())
    repo = Path(doc["repository_path"]); (repo / "dirty").write_text("x", encoding="utf-8")
    assert "repository worktree is dirty" in validate_manifest(path)

@pytest.mark.parametrize("mutation, expected", [
    (lambda d: d["raw_sessions"][2].update(parent_session_id="advisor-1"), "session parent does not match spawn edge"),
    (lambda d: d["spawn_edges"][1].update(child_session_id="advisor-1"), "spawn topology is undeclared or forbidden"),
    (lambda d: d["spawn_edges"].append(dict(d["spawn_edges"][0])), "duplicate spawn edge"),
    (lambda d: d.update(undeclared=True), "manifest contains undeclared properties"),
])
def test_rejects_forged_lineage_duplicate_edges_and_extra_properties(tmp_path: Path, mutation, expected):
    path = make_manifest(tmp_path, "C2"); doc = json.loads(path.read_text()); mutation(doc); path.write_text(json.dumps(doc))
    assert any(expected in error for error in validate_manifest(path))
