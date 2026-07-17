"""Validate that a P107 evaluation block seals every cost-relevant input."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def validate(path: str | Path) -> list[str]:
    try:
        block = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read evaluation block: {exc}"]
    if not isinstance(block, dict):
        return ["evaluation block root must be an object"]
    errors: list[str] = []
    if block.get("schema_version") != "p107_evaluation_block_v1":
        errors.append("schema_version must be p107_evaluation_block_v1")
    if not isinstance(block.get("starting_commit"), str) or not COMMIT.fullmatch(block["starting_commit"]):
        errors.append("starting_commit must be a 40-character lowercase commit")
    for field in ("ticket_sha256", "fixture_sha256", "rubric_sha256", "pricing_catalog_sha256", "model_catalog_sha256", "effective_config_sha256"):
        if not isinstance(block.get(field), str) or not SHA256.fullmatch(block[field]):
            errors.append(f"{field} must be a lowercase SHA-256")
    for field in ("block_id", "workload_id", "runtime_version", "environment_epoch", "pricing_catalog_path", "model_catalog_path", "effective_config_path"):
        value = block.get(field)
        if not isinstance(value, str) or not value.strip() or "REPLACE_WITH" in value:
            errors.append(f"{field} must be materialized")
    if block.get("ambient_memories_enabled") is not False:
        errors.append("ambient_memories_enabled must be false")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_p107_evaluation_block.py <evaluation-block.json>")
    errors = validate(sys.argv[1])
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("P107 evaluation block is valid")
