"""Fail-closed offline validation for a materialized P107 accounting record."""
from __future__ import annotations

import json
import hashlib
import math
import sys
from pathlib import Path
from typing import Any

CONFIG_ROLES = {"C0": {"coordinator", "advisor"}, "C1": {"coordinator", "worker", "advisor"}, "C2": {"coordinator", "supervisor", "worker", "advisor"}, "C3": {"coordinator", "supervisor", "worker", "advisor"}, "C4": {"coordinator", "supervisor", "worker", "advisor"}}
TOKEN_CLASSES = ("uncached_input", "cached_input", "output", "reasoning")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _required_object(data: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _catalog_path(catalog: dict[str, Any]) -> Any:
    return catalog.get("path", catalog.get("catalog_path", catalog.get("artifact_path")))


def _catalog_hash(catalog: dict[str, Any]) -> Any:
    return catalog.get("sha256", catalog.get("content_hash"))


def _load_catalog(catalog: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    path_value = _catalog_path(catalog)
    if not _nonempty(path_value):
        errors.append("pricing_catalog materialized artifact path is required")
        return {}
    artifact = Path(path_value).expanduser()
    try:
        raw = artifact.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        expected = _catalog_hash(catalog)
        if not _nonempty(expected):
            errors.append("pricing_catalog content hash is required")
        elif expected.removeprefix("sha256:").lower() != actual:
            errors.append("pricing_catalog content hash does not match artifact")
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load pricing_catalog artifact: {exc}")
        return {}
    if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
        errors.append("pricing_catalog artifact must contain an entries list")
        return {}
    return value


def _canonical_artifact(root: Path, value: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts or Path(value).as_posix() != value:
        errors.append(f"{label} must be a canonical relative path")
        return None
    path = root / value
    if not path.is_file() or path.is_symlink():
        errors.append(f"{label} must be an existing regular file")
        return None
    return path


def validate_accounting_record(path: str | Path) -> list[str]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read accounting record: {exc}"]
    if not isinstance(data, dict):
        return ["accounting record root must be an object"]
    errors: list[str] = []
    if data.get("schema_version") != "p107_accounting_record_v1": errors.append("schema_version must be p107_accounting_record_v1")
    for key in ("evaluation_block_id", "run_id"):
        if not _nonempty(data.get(key)): errors.append(f"{key} must be materialized")
    config = data.get("configuration_id")
    if config not in CONFIG_ROLES: errors.append("configuration_id must be one of C0, C1, C2, C3, C4")

    binding = _required_object(data, "run_evidence_manifest", errors)
    manifest_path = _canonical_artifact(Path(path).parent, binding.get("path"), "run_evidence_manifest.path", errors) if binding else None
    manifest: dict[str, Any] = {}
    manifest_sessions: dict[str, dict[str, Any]] = {}
    if manifest_path:
        digest = binding.get("sha256")
        actual = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        if not isinstance(digest, str) or digest.removeprefix("sha256:") != actual:
            errors.append("run_evidence_manifest.sha256 does not match artifact")
        try:
            from validate_p107_run_evidence_manifest import validate_manifest
            errors.extend(f"run evidence manifest: {e}" for e in validate_manifest(manifest_path))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load run evidence manifest: {exc}")
    if manifest:
        if data.get("run_id") != manifest.get("run_id"): errors.append("run_id must match run evidence manifest")
        if data.get("configuration_id") != manifest.get("configuration_id"): errors.append("configuration_id must match run evidence manifest")
        manifest_sessions = {s.get("session_id"): s for s in manifest.get("raw_sessions", []) if isinstance(s, dict) and _nonempty(s.get("session_id"))}

    source = _required_object(data, "source_session_identity", errors)
    if source:
        if source.get("run_id") != data.get("run_id"): errors.append("source_session_identity.run_id must match run_id")
        ids = source.get("session_ids")
        if not isinstance(ids, list) or not ids or not all(_nonempty(x) for x in ids) or len(ids) != len(set(ids)):
            errors.append("source_session_identity.session_ids must be a nonempty unique list")
        if manifest_sessions and set(ids or []) != set(manifest_sessions): errors.append("source_session_identity.session_ids must match manifest sessions")

    catalog = _required_object(data, "pricing_catalog", errors)
    for key in ("catalog_id", "catalog_date", "provenance", "content_hash"):
        if not _nonempty(catalog.get(key)): errors.append(f"pricing_catalog.{key} is required")
    catalog_data = _load_catalog(catalog, errors)
    catalog_entries = {entry.get("model_id"): entry for entry in catalog_data.get("entries", []) if isinstance(entry, dict)}

    local = _required_object(data, "local_cost", errors)
    status = local.get("status")
    allowed = {"measured", "unknown"} if config == "C4" else {"measured", "unknown", "not_applicable"}
    if status not in allowed: errors.append("local_cost.status is invalid for configuration")
    amount = local.get("amount_usd")
    if isinstance(amount, (int, float)) and not _finite_number(amount): errors.append("local_cost.amount_usd must be finite")
    if status == "unknown" and amount == 0: errors.append("unknown local cost cannot be represented as zero")
    if status == "measured" and (isinstance(amount, bool) or not isinstance(amount, (int, float))): errors.append("measured local cost requires numeric amount_usd")
    if isinstance(amount, (int, float)) and amount < 0: errors.append("local_cost.amount_usd must be nonnegative")
    if status == "not_applicable" and (amount == 0 or amount is not None): errors.append("not_applicable local cost cannot be zero or carry an amount")

    run = _required_object(data, "run_accounting", errors)
    for key in ("adapter_identity", "active_time_seconds", "wait_time_seconds", "review_count", "repair_count", "transport_count", "maintainer_intervention", "invalid_run_spend_usd"):
        if key not in run: errors.append(f"run_accounting.{key} is required")
    if run.get("adapter_identity") is not None and not _nonempty(run.get("adapter_identity")): errors.append("run_accounting.adapter_identity is required")
    for key in ("active_time_seconds", "wait_time_seconds", "review_count", "repair_count", "transport_count"):
        value = run.get(key)
        if not _finite_number(value) or value < 0: errors.append(f"run_accounting.{key} must be a finite nonnegative number")
    if not isinstance(run.get("maintainer_intervention"), bool): errors.append("run_accounting.maintainer_intervention must be boolean")
    if not _finite_number(run.get("invalid_run_spend_usd")) or run.get("invalid_run_spend_usd") < 0: errors.append("run_accounting.invalid_run_spend_usd must be a finite nonnegative number")
    if status == "measured":
        if not _nonempty(run.get("adapter_identity")):
            errors.append("measured local cost requires run_accounting.adapter_identity")
        if not _nonempty(local.get("basis")) and not isinstance(local.get("metadata"), dict):
            errors.append("measured local cost requires basis or metadata")

    roles = data.get("roles")
    if not isinstance(roles, list): errors.append("roles must be a list"); roles = []
    seen_roles: set[str] = set(); seen_sessions: set[str] = set(); total_usd = 0.0
    for index, role in enumerate(roles):
        if not isinstance(role, dict): errors.append(f"roles[{index}] must be an object"); continue
        name, session = role.get("role"), role.get("session_id")
        if name in seen_roles: errors.append(f"duplicate role: {name}")
        seen_roles.add(name)
        if session in seen_sessions: errors.append(f"duplicate session_id: {session}")
        seen_sessions.add(session)
        for key in ("role", "session_id", "provider", "model"):
            if not _nonempty(role.get(key)): errors.append(f"roles[{index}].{key} is required")
        tokens = role.get("tokens"); prices = role.get("token_usd")
        if not isinstance(tokens, dict): errors.append(f"roles[{index}].tokens must be an object")
        if not isinstance(prices, dict): errors.append(f"roles[{index}].token_usd must be an object")
        role_total = 0.0
        entry = catalog_entries.get(role.get("model"))
        rates = entry.get("rates", {}) if entry else {}
        rate_map = {"uncached_input": rates.get("input_per_1m_usd"), "cached_input": rates.get("cached_input_read_per_1m_usd"), "output": rates.get("output_per_1m_usd"), "reasoning": rates.get("output_per_1m_usd")}
        if not entry: errors.append(f"roles[{index}].model is absent from pricing catalog")
        for key in TOKEN_CLASSES:
            value = tokens.get(key) if isinstance(tokens, dict) else None
            if isinstance(value, bool) or not isinstance(value, int) or value < 0: errors.append(f"roles[{index}].tokens.{key} must be a nonnegative integer")
            usd = prices.get(key) if isinstance(prices, dict) else None
            if not _finite_number(usd) or usd < 0: errors.append(f"roles[{index}].token_usd.{key} must be a finite nonnegative number")
            rate = rate_map[key]
            if not _finite_number(rate) or rate < 0:
                errors.append(f"pricing catalog rate for {role.get('model')}.{key} is invalid")
            elif isinstance(value, int) and not isinstance(value, bool):
                derived = value * rate / 1_000_000
                if isinstance(usd, (int, float)) and not math.isclose(usd, derived, rel_tol=0, abs_tol=1e-12):
                    errors.append(f"roles[{index}].token_usd.{key} must equal catalog-derived USD")
                role_total += derived
        if not _finite_number(role.get("total_usd")) or role.get("total_usd") != role_total: errors.append(f"roles[{index}].total_usd must equal derived token USD total")
        total_usd += role_total
        checkpoints = role.get("checkpoints")
        if not isinstance(checkpoints, dict):
            errors.append(f"roles[{index}].checkpoints must have start and end")
        else:
            for point in ("start", "end"):
                checkpoint = checkpoints.get(point)
                if not isinstance(checkpoint, dict):
                    errors.append(f"roles[{index}].checkpoints.{point} must identify a hashed raw-session snapshot")
                    continue
                if checkpoint.get("session_id") != session or checkpoint.get("session_id") not in manifest_sessions:
                    errors.append(f"roles[{index}].checkpoints.{point}.session_id must match a manifest session")
                snapshot = _canonical_artifact(manifest_path.parent if manifest_path else Path(path).parent, checkpoint.get("snapshot_path"), f"roles[{index}].checkpoints.{point}.snapshot_path", errors)
                expected = manifest_sessions.get(checkpoint.get("session_id"), {}).get("raw_session_path")
                if snapshot and snapshot.as_posix() != (manifest_path.parent / expected).as_posix(): errors.append(f"roles[{index}].checkpoints.{point}.snapshot_path must match manifest raw session")
                if snapshot and checkpoint.get("snapshot_sha256") != hashlib.sha256(snapshot.read_bytes()).hexdigest(): errors.append(f"roles[{index}].checkpoints.{point}.snapshot_sha256 does not match snapshot")
        if role.get("confidence") not in {"high", "medium", "low"}: errors.append(f"roles[{index}].confidence must be high, medium, or low")
    if not _finite_number(data.get("total_paid_usd")) or data.get("total_paid_usd") != total_usd: errors.append("total_paid_usd must equal derived role total")
    if config in CONFIG_ROLES and seen_roles != CONFIG_ROLES[config]: errors.append("roles must contain exactly the required paid roles for configuration_id")
    if isinstance(source.get("session_ids"), list) and set(source["session_ids"]) != seen_sessions: errors.append("source_session_identity.session_ids must contain exactly all role session IDs")
    configured = source.get("role_sessions")
    if isinstance(configured, dict) and any(configured.get(role) != next((r.get("session_id") for r in roles if isinstance(r, dict) and r.get("role") == role), None) for role in configured):
        errors.append("source_session_identity.role_sessions must match configured role sessions")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("usage: validate_p107_accounting_record.py <record.json>")
    problems = validate_accounting_record(sys.argv[1])
    if problems: print("\n".join(problems)); raise SystemExit(1)
    print("P107 accounting record is structurally valid")
