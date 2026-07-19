from __future__ import annotations

import json
import hashlib
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_evaluation_block import validate

TEMPLATE = ROOT / "templates" / "p107_evaluation_block_template.json"


def materialized(tmp_path: Path) -> dict[str, object]:
    block = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    block.update(block_id="p107-block-1", starting_commit="a" * 40, workload_id="source-audit-bundle", runtime_version="0.1.0", environment_epoch="2026-07-15", pricing_catalog_path="runtime/p107/pricing_catalog.json", model_catalog_path="runtime/p107/model_catalog.json", effective_config_path="runtime/p107/effective_config.toml")
    for field in ("ticket_sha256", "fixture_sha256", "rubric_sha256", "pricing_catalog_sha256", "model_catalog_sha256", "effective_config_sha256"):
        block[field] = "b" * 64
    inputs = []
    for name, source in (("c0_prompt", "c0"), ("c1_prompt", "c1"), ("c2_prompt", "c2"), ("c3_prompt", "c3"), ("c4_prompt", "c4"), ("advisor_rubric", "rubric")):
        file = tmp_path / f"{source}.txt"
        file.write_text(source, encoding="utf-8")
        inputs.append({"name": name, "path": file.name, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    block["required_inputs"] = inputs
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
