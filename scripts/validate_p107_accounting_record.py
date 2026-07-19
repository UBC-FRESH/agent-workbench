"""Fail-closed offline validation for a materialized P107 accounting record."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

CONFIG_ROLES = {
    "C0": {"coordinator", "advisor"},
    "C1": {"coordinator", "worker", "advisor"},
    "C2": {"coordinator", "supervisor", "worker", "advisor"},
    "C3": {"coordinator", "supervisor", "worker", "advisor"},
    "C4": {"coordinator", "supervisor", "worker", "advisor"},
}
TOKEN_CLASSES = ("uncached_input", "cached_input", "output", "reasoning")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_accounting_record(path: str | Path) -> list[str]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read accounting record: {exc}"]
    if not isinstance(data, dict):
        return ["accounting record root must be an object"]
    errors: list[str] = []
    if data.get("schema_version") != "p107_accounting_record_v1":
        errors.append("schema_version must be p107_accounting_record_v1")
    for key in ("evaluation_block_id", "run_id"):
        if not _nonempty(data.get(key)):
            errors.append(f"{key} must be materialized")
    config = data.get("configuration_id")
    if config not in CONFIG_ROLES:
        errors.append("configuration_id must be one of C0, C1, C2, C3, C4")

    source = data.get("source_session_identity")
    if not isinstance(source, dict):
        errors.append("source_session_identity must be an object")
    else:
        if source.get("run_id") != data.get("run_id"):
            errors.append("source_session_identity.run_id must match run_id")
        ids = source.get("session_ids")
        if not isinstance(ids, list) or not ids or not all(_nonempty(x) for x in ids):
            errors.append("source_session_identity.session_ids must be a nonempty list")

    catalog = data.get("pricing_catalog")
    if not isinstance(catalog, dict):
        errors.append("pricing_catalog must be an object")
    else:
        for key in ("catalog_id", "catalog_date", "provenance"):
            if not _nonempty(catalog.get(key)):
                errors.append(f"pricing_catalog.{key} is required")

    local = data.get("local_cost")
    if not isinstance(local, dict):
        errors.append("local_cost must be an object")
    else:
        if local.get("status") not in {"measured", "unknown", "not_applicable"}:
            errors.append("local_cost.status must be measured, unknown, or not_applicable")
        if local.get("status") == "unknown" and local.get("amount_usd") == 0:
            errors.append("unknown local cost cannot be represented as zero")
        if local.get("status") == "measured" and not isinstance(local.get("amount_usd"), (int, float)):
            errors.append("measured local cost requires numeric amount_usd")
        if isinstance(local.get("amount_usd"), (int, float)) and local["amount_usd"] < 0:
            errors.append("local_cost.amount_usd must be nonnegative")

    roles = data.get("roles")
    if not isinstance(roles, list):
        errors.append("roles must be a list")
        roles = []
    seen: set[str] = set()
    for index, role in enumerate(roles):
        if not isinstance(role, dict):
            errors.append(f"roles[{index}] must be an object"); continue
        name = role.get("role")
        if name in seen: errors.append(f"duplicate role: {name}")
        seen.add(name)
        for key in ("role", "session_id", "provider", "model"):
            if not _nonempty(role.get(key)): errors.append(f"roles[{index}].{key} is required")
        tokens = role.get("tokens")
        if not isinstance(tokens, dict): errors.append(f"roles[{index}].tokens must be an object")
        else:
            for key in TOKEN_CLASSES:
                value = tokens.get(key)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                    errors.append(f"roles[{index}].tokens.{key} must be nonnegative")
        checkpoints = role.get("checkpoints")
        if not isinstance(checkpoints, dict) or not _nonempty(checkpoints.get("start")) or not _nonempty(checkpoints.get("end")):
            errors.append(f"roles[{index}].checkpoints must have start and end")
        if role.get("confidence") not in {"high", "medium", "low"}:
            errors.append(f"roles[{index}].confidence must be high, medium, or low")
    if config in CONFIG_ROLES and seen != CONFIG_ROLES[config]:
        errors.append("roles must contain exactly the required paid roles for configuration_id")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("usage: validate_p107_accounting_record.py <record.json>")
    problems = validate_accounting_record(sys.argv[1])
    if problems: print("\n".join(problems)); raise SystemExit(1)
    print("P107 accounting record is valid; comparison eligible")
