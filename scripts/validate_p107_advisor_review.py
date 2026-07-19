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


def _safe_path(path: Path, label: str, other: Path, *, root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file(): errors.append(f"{label} must be an existing file")
    # CLI inputs may be absolute; reject traversal components only for paths
    # supplied as relative artifact references.
    if not path.is_absolute() and ".." in path.parts: errors.append(f"{label} must be an immutable path")
    if path.suffix.lower() != ".json": errors.append(f"{label} must be a JSON path")
    if path == other: errors.append("bundle and verdict paths must be distinct")
    if path.is_symlink(): errors.append(f"{label} must not be a symlink")
    if root is not None:
        try:
            path.resolve(strict=False).relative_to(root.resolve())
        except ValueError:
            errors.append(f"{label} must remain under the history manifest root")
    return errors


def _validate_single(bundle_path: str | Path, verdict_path: str | Path, *, prior_session_ids: set[str] | None = None) -> list[str]:
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
    if verdict.get("verdict") == "verified_blocker":
        evidence = verdict.get("critical_defects")
        if not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
            errors.append("verified_blocker requires explicit blocker evidence in critical_defects")
    return errors


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_history(history_path: Path, bundle_path: Path, verdict_path: Path) -> list[str]:
    errors: list[str] = []
    errors += _safe_path(history_path, "review history path", history_path.parent / "__review_artifact__.json")
    history, read_errors = _read(history_path, "review history")
    errors += read_errors
    if history is None:
        return errors
    schema_path = REPOSITORY_ROOT / "templates/p107_advisor_review_history.schema.json"
    errors += _schema(history, json.loads(schema_path.read_text(encoding="utf-8")), "review history")
    entries = history.get("entries")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 3:
        return errors + ["review history entries must contain 1 through 3 reviews"]
    root = history_path.parent
    expected_identity: tuple[str, str] | None = None
    prior_verdict_hash: str | None = None
    for index, entry in enumerate(entries):
        label = f"review history entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        number = entry.get("review_number")
        if number != index + 1:
            errors.append("review history review numbers must be contiguous from 1")
        bundle_ref, verdict_ref = entry.get("bundle_path"), entry.get("verdict_path")
        if not isinstance(bundle_ref, str) or not isinstance(verdict_ref, str):
            errors.append(f"{label} must name bundle_path and verdict_path")
            continue
        bp, vp = root / bundle_ref, root / verdict_ref
        errors += _safe_path(bp, f"{label}.bundle_path", vp, root=root)
        errors += _safe_path(vp, f"{label}.verdict_path", bp, root=root)
        if not bp.is_file() or not vp.is_file():
            continue
        for key, path in (("bundle_sha256", bp), ("verdict_sha256", vp)):
            declared = entry.get(key)
            if not isinstance(declared, str) or not SHA256.fullmatch(declared):
                errors.append(f"{label}.{key} must be lowercase SHA-256")
            elif _sha256(path) != declared:
                errors.append(f"{label} {key} mismatch")
        errors += _validate_single(bp, vp)
        bundle, _ = _read(bp, "history bundle")
        verdict, _ = _read(vp, "history verdict")
        if bundle is None or verdict is None:
            continue
        identity = (bundle.get("advisor_lineage_id"), bundle.get("advisor_session_id"))
        if expected_identity is None:
            expected_identity = identity
        elif identity != expected_identity:
            errors.append("Advisor identity changed across review history")
        if entry.get("advisor_lineage_id") != identity[0] or entry.get("advisor_session_id") != identity[1]:
            errors.append(f"{label} Advisor identity mismatch")
        if index == 0:
            if bundle.get("review_number") != 1:
                errors.append("review history must begin with review 1")
            if entry.get("prior_verdict_sha256") is not None:
                errors.append("review 1 cannot have a prior verdict hash")
        elif entry.get("prior_verdict_sha256") != prior_verdict_hash:
            errors.append(f"{label} does not chain to the prior verdict hash")
        prior_verdict_hash = entry.get("verdict_sha256")
    final = entries[-1] if isinstance(entries[-1], dict) else {}
    if final.get("review_number") != len(entries):
        errors.append("final history entry must be the terminal review")
    if root / final.get("bundle_path", "") != bundle_path or root / final.get("verdict_path", "") != verdict_path:
        errors.append("terminal verdict must be the final history entry")
    return errors


def validate_review(bundle_path: str | Path, verdict_path: str | Path, *, prior_session_ids: set[str] | None = None, history_path: str | Path | None = None) -> list[str]:
    errors = _validate_single(bundle_path, verdict_path, prior_session_ids=prior_session_ids)
    bundle, _ = _read(Path(bundle_path), "bundle")
    review_number = bundle.get("review_number") if bundle else None
    if isinstance(review_number, int) and review_number > 1:
        if history_path is None:
            errors.append("review history is required for review 2 through 3")
        else:
            errors += _validate_history(Path(history_path), Path(bundle_path), Path(verdict_path))
    elif history_path is not None:
        errors += _validate_history(Path(history_path), Path(bundle_path), Path(verdict_path))
    return errors


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4): raise SystemExit("usage: validate_p107_advisor_review.py <bundle.json> <verdict.json> [history.json]")
    problems = validate_review(sys.argv[1], sys.argv[2], history_path=sys.argv[3] if len(sys.argv) == 4 else None)
    if problems: print("\n".join(problems)); raise SystemExit(1)
    print("P107 Advisor review bundle/verdict is valid")
