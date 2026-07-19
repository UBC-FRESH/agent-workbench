"""Validate an immutable offline P107 Advisor review bundle and verdict."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERDICTS = {"accepted", "defect_packet", "verified_blocker"}
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _schema(data: Any, schema: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    if schema.get("type") == "object" and not isinstance(data, dict):
        return [f"{label} must be an object"]
    for key in schema.get("required", []):
        if key not in data:
            errors.append(f"missing {label}.{key}")
    for key, rule in schema.get("properties", {}).items():
        if key not in data:
            continue
        value = data[key]
        types = rule.get("type", [])
        if isinstance(types, str):
            types = [types]
        type_ok = any((t == "object" and isinstance(value, dict)) or
                      (t == "array" and isinstance(value, list)) or
                      (t == "string" and isinstance(value, str)) or
                      (t == "integer" and isinstance(value, int) and not isinstance(value, bool)) or
                      (t == "boolean" and isinstance(value, bool)) or
                      (t == "null" and value is None) for t in types)
        if types and not type_ok:
            errors.append(f"{label}.{key} has invalid type")
            continue
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{label}.{key} has invalid value")
        if "const" in rule and value != rule["const"]:
            errors.append(f"{label}.{key} must equal {rule['const']!r}")
        if isinstance(value, int) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]: errors.append(f"{label}.{key} is below minimum")
            if "maximum" in rule and value > rule["maximum"]: errors.append(f"{label}.{key} exceeds maximum")
        if isinstance(value, str) and "pattern" in rule and not re.fullmatch(rule["pattern"], value):
            errors.append(f"{label}.{key} has invalid format")
        if isinstance(value, list):
            if "minItems" in rule and len(value) < rule["minItems"]: errors.append(f"{label}.{key} has too few items")
            if "maxItems" in rule and len(value) > rule["maxItems"]: errors.append(f"{label}.{key} has too many items")
        if isinstance(value, list) and isinstance(rule.get("items"), dict):
            for i, item in enumerate(value):
                errors.extend(_schema(item, rule["items"], f"{label}.{key}[{i}]"))
    for clause in schema.get("allOf", []):
        condition = clause.get("if", {}).get("properties", {})
        matched = all(data.get(k) == v.get("const") for k, v in condition.items())
        if matched:
            errors.extend(_schema(data, clause.get("then", {}), label))
    return errors


def _read(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"cannot read {label}: {exc}"]
    return (value, []) if isinstance(value, dict) else (None, [f"{label} root must be an object"])


def _safe_path(path: Path, label: str, other: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file(): errors.append(f"{label} must be an existing file")
    # CLI inputs may be absolute; reject traversal components only for paths
    # supplied as relative artifact references.
    if not path.is_absolute() and ".." in path.parts: errors.append(f"{label} must be an immutable path")
    if path.suffix.lower() != ".json": errors.append(f"{label} must be a JSON path")
    if path == other: errors.append("bundle and verdict paths must be distinct")
    if path.is_symlink(): errors.append(f"{label} must not be a symlink")
    return errors


def validate_review(bundle_path: str | Path, verdict_path: str | Path, *, prior_session_ids: set[str] | None = None) -> list[str]:
    bundle_file, verdict_file = Path(bundle_path), Path(verdict_path)
    errors = _safe_path(bundle_file, "bundle path", verdict_file) + _safe_path(verdict_file, "verdict path", bundle_file)
    bundle, read_errors = _read(bundle_file, "bundle")
    errors += read_errors
    verdict, read_errors = _read(verdict_file, "verdict")
    errors += read_errors
    if bundle is None or verdict is None: return errors
    errors += _schema(bundle, json.loads((REPOSITORY_ROOT / "templates/p107_review_bundle.schema.json").read_text()), "bundle")
    errors += _schema(verdict, json.loads((REPOSITORY_ROOT / "templates/p107_advisor_verdict.schema.json").read_text()), "verdict")
    run_id = bundle.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip() or verdict.get("run_id") != run_id: errors.append("run ID mismatch")
    if verdict.get("review_number") != bundle.get("review_number"): errors.append("review number mismatch")
    review_number, kind = bundle.get("review_number"), bundle.get("packet_kind")
    if kind == "initial" and review_number != 1: errors.append("initial packet must be review 1")
    if kind == "repair_delta" and (not isinstance(review_number, int) or review_number not in (2, 3)): errors.append("repair packet must be review 2 through 3")
    declared = bundle.get("bundle_sha256")
    if not isinstance(declared, str) or not SHA256.fullmatch(declared): errors.append("bundle_sha256 must be lowercase SHA-256")
    else:
        unsigned = dict(bundle); unsigned["bundle_sha256"] = ""
        actual = hashlib.sha256((json.dumps(unsigned, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
        if declared != actual: errors.append("bundle hash mismatch")
    if verdict.get("bundle_sha256") != declared: errors.append("verdict is not bound to bundle hash")
    for document in (bundle, verdict):
        if not isinstance(document.get("advisor_session_id"), str) or not document["advisor_session_id"].strip(): errors.append("Advisor session identity is required")
        if not isinstance(document.get("advisor_lineage_id"), str) or not document["advisor_lineage_id"].strip(): errors.append("Advisor lineage identity is required")
    if bundle.get("advisor_session_id") != verdict.get("advisor_session_id") or bundle.get("advisor_lineage_id") != verdict.get("advisor_lineage_id"): errors.append("Advisor session/lineage mismatch")
    if prior_session_ids and bundle.get("advisor_session_id") in prior_session_ids: errors.append("Advisor session reused across a different run")
    if kind == "initial" and bundle.get("previous_defect_packet") is not None: errors.append("initial packet cannot have prior defect packet")
    if kind == "repair_delta":
        prior = bundle.get("previous_defect_packet")
        if not isinstance(prior, dict) or not prior.get("defect_id"): errors.append("repair packet requires prior defect lineage")
    if verdict.get("verdict") not in VERDICTS: errors.append("pending/silence is not a valid verdict")
    if verdict.get("verdict") == "defect_packet":
        packet = verdict.get("defect_packet")
        if not isinstance(packet, dict) or any(not isinstance(packet.get(k), str) or not packet[k].strip() for k in ("defect_id", "failed_evidence", "acceptance_condition")):
            errors.append("defect_packet requires defect_id, failed_evidence, and acceptance_condition")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 3: raise SystemExit("usage: validate_p107_advisor_review.py <bundle.json> <verdict.json>")
    problems = validate_review(sys.argv[1], sys.argv[2])
    if problems: print("\n".join(problems)); raise SystemExit(1)
    print("P107 Advisor review bundle/verdict is valid")
