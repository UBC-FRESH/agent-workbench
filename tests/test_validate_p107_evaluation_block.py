from __future__ import annotations

import json
import hashlib
import pytest
import shutil
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_evaluation_block import validate

TEMPLATE = ROOT / "templates" / "p107_evaluation_block_template.json"


def materialized(tmp_path: Path) -> dict[str, object]:
    block = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "seed").write_text("seed", encoding="utf-8")
    subprocess.run(["git", "add", "seed"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=test@example.com", "-c", "user.name=Test", "commit", "-qm", "seed"], cwd=repo, check=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    block.update(block_id="p107-block-1", starting_commit=commit, repository_root="repo", workload_id="source-audit-bundle", runtime_version="0.1.0", environment_epoch="2026-07-15", ticket_path="ticket.md", fixture_path="fixture-manifest.json", pricing_catalog_path="pricing_catalog.json", model_catalog_path="model_catalog.json", effective_config_path="effective_config.toml")
    for field in ("ticket_sha256", "fixture_sha256", "rubric_sha256", "pricing_catalog_sha256", "model_catalog_sha256", "effective_config_sha256"):
        block[field] = "b" * 64
    for name, content in (("ticket.md", "ticket"), ("fixture-manifest.json", '{"files":[]}'), ("pricing_catalog.json", "pricing"), ("model_catalog.json", "models"), ("effective_config.toml", "config")):
        file = tmp_path / name
        file.write_text(content, encoding="utf-8")
        field = {"ticket.md": "ticket_sha256", "fixture-manifest.json": "fixture_sha256", "pricing_catalog.json": "pricing_catalog_sha256", "model_catalog.json": "model_catalog_sha256", "effective_config.toml": "effective_config_sha256"}[name]
        block[field] = hashlib.sha256(file.read_bytes()).hexdigest()
    inputs = []
    for name, source in (("c0_prompt", "c0"), ("c1_prompt", "c1"), ("c2_prompt", "c2"), ("c3_prompt", "c3"), ("c4_prompt", "c4"), ("advisor_rubric", "rubric")):
        file = tmp_path / f"{source}.txt"
        file.write_text(source, encoding="utf-8")
        inputs.append({"name": name, "path": file.name, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    block["required_inputs"] = inputs
    block["rubric_sha256"] = inputs[-1]["sha256"]
    return block


def test_materialized_block_is_valid(tmp_path: Path) -> None:
    path = tmp_path / "block.json"
    path.write_text(json.dumps(materialized(tmp_path)), encoding="utf-8")
    assert validate(path) == []


def test_rejects_unpinned_model_catalog_or_memories(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    block["model_catalog_sha256"] = "not-a-hash"
    block["ambient_memories_enabled"] = True
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    errors = validate(path)
    assert "model_catalog_sha256 must be a lowercase SHA-256" in errors
    assert "ambient_memories_enabled must be false" in errors


def test_rejects_missing_duplicate_traversal_and_hash_drift(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    block["required_inputs"] = block["required_inputs"][:-1]
    block["required_inputs"][0]["path"] = "../outside.txt"
    block["required_inputs"][1]["path"] = block["required_inputs"][2]["path"]
    block["required_inputs"][2]["sha256"] = "0" * 64
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    errors = validate(path)
    assert "c0_prompt path must stay relative to the block" in errors
    assert "duplicate required input path: c2.txt" in errors
    assert "c2_prompt sha256 does not match file" in errors
    assert "missing required input: advisor_rubric" in errors


def test_rejects_symlink_input(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(tmp_path / "c0.txt")
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")
    block["required_inputs"][0]["path"] = link.name
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert "c0_prompt path must not use symlinks" in validate(path)


@pytest.mark.parametrize("field", ["ticket_path", "fixture_path", "pricing_catalog_path", "model_catalog_path", "effective_config_path"])
def test_rejects_fabricated_sealed_artifact(tmp_path: Path, field: str) -> None:
    block = materialized(tmp_path)
    block[field] = "missing-file"
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert any(field in error for error in validate(path))


def test_rejects_sealed_artifact_hash_drift(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    (tmp_path / "ticket.md").write_text("changed", encoding="utf-8")
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert "ticket_sha256 does not match file" in validate(path)


def test_rejects_sealed_artifact_traversal_and_symlink(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    block["fixture_path"] = "../fixture-manifest.json"
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert "fixture_path must stay relative to the block" in validate(path)
    link = tmp_path / "linked-ticket.md"
    try:
        link.symlink_to(tmp_path / "ticket.md")
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")
    block["fixture_path"] = "fixture-manifest.json"
    block["ticket_path"] = link.name
    path.write_text(json.dumps(block), encoding="utf-8")
    assert "ticket_path must not use symlinks" in validate(path)


def test_rejects_invalid_starting_commit(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    block["starting_commit"] = "0" * 40
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert "starting_commit must be a resolvable local Git commit" in validate(path)


def test_rejects_mismatched_rubric_hash(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    block["rubric_sha256"] = "0" * 64
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert "rubric_sha256 does not match advisor_rubric sha256" in validate(path)


def test_rejects_worktree_checked_out_at_different_commit(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    repo = tmp_path / "repo"
    (repo / "later").write_text("later", encoding="utf-8")
    subprocess.run(["git", "add", "later"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=test@example.com", "-c", "user.name=Test", "commit", "-qm", "later"], cwd=repo, check=True)
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert "repository_root must be checked out at starting_commit" in validate(path)


def test_preflight_override_validates_runtime_block_against_external_checkout(tmp_path: Path) -> None:
    block = materialized(tmp_path)
    freeze = tmp_path / "runtime" / "p107-freeze"
    freeze.mkdir(parents=True)
    for name in (
        "ticket.md",
        "fixture-manifest.json",
        "pricing_catalog.json",
        "model_catalog.json",
        "effective_config.toml",
        "c0.txt",
        "c1.txt",
        "c2.txt",
        "c3.txt",
        "c4.txt",
        "rubric.txt",
    ):
        shutil.copy2(tmp_path / name, freeze / name)
    block["repository_root"] = "."
    path = freeze / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    assert validate(path, repository_root=tmp_path / "repo") == []
