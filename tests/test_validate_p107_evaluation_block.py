from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_evaluation_block import validate

TEMPLATE = ROOT / "templates" / "p107_evaluation_block_template.json"


def materialized() -> dict[str, object]:
    block = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    block.update(block_id="p107-block-1", starting_commit="a" * 40, workload_id="source-audit-bundle", runtime_version="0.1.0", environment_epoch="2026-07-15", pricing_catalog_path="runtime/p107/pricing_catalog.json", model_catalog_path="runtime/p107/model_catalog.json", effective_config_path="runtime/p107/effective_config.toml")
    for field in ("ticket_sha256", "fixture_sha256", "rubric_sha256", "pricing_catalog_sha256", "model_catalog_sha256", "effective_config_sha256"):
        block[field] = "b" * 64
    return block


def test_materialized_block_is_valid(tmp_path: Path) -> None:
    path = tmp_path / "block.json"
    path.write_text(json.dumps(materialized()), encoding="utf-8")
    assert validate(path) == []


def test_rejects_unpinned_model_catalog_or_memories(tmp_path: Path) -> None:
    block = materialized()
    block["model_catalog_sha256"] = "not-a-hash"
    block["ambient_memories_enabled"] = True
    path = tmp_path / "block.json"
    path.write_text(json.dumps(block), encoding="utf-8")
    errors = validate(path)
    assert "model_catalog_sha256 must be a lowercase SHA-256" in errors
    assert "ambient_memories_enabled must be false" in errors
