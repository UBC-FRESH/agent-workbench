"""Validate one offline, materialized P107 run-evidence document."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _obj(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{name} must be an object")
    return {}


def _sha(value: Any, name: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        errors.append(f"{name} must be a lowercase SHA-256")
        return False
    return True


def validate_materialized_run(path: str | Path) -> list[str]:
    """Return explicit errors; no providers, agents, or runtime state are read."""
    document_path = Path(path)
    try:
        document = json.loads(document_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read materialized run: {exc}"]
    if not isinstance(document, dict):
        return ["materialized run root must be an object"]

    errors: list[str] = []
    if document.get("schema_version") != "p107_materialized_run_v1":
        errors.append("schema_version must be p107_materialized_run_v1")
    run_id = document.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("run_id must be materialized")
    configuration = document.get("configuration_id")
    if configuration not in {"C0", "C1", "C2", "C3", "C4"}:
        errors.append("configuration_id must be one of C0, C1, C2, C3, C4")

    frozen = document.get("frozen_files")
    if not isinstance(frozen, list) or not frozen:
        errors.append("frozen_files must be a nonempty list")
    else:
        for index, item in enumerate(frozen):
            entry = _obj(item, f"frozen_files[{index}]", errors)
            raw = entry.get("path")
            if not isinstance(raw, str) or not raw.strip():
                errors.append(f"frozen_files[{index}].path must be materialized")
                continue
            if _sha(entry.get("sha256"), f"frozen_files[{index}].sha256", errors):
                target = Path(raw)
                if not target.is_absolute():
                    target = document_path.parent / target
                try:
                    actual = hashlib.sha256(target.read_bytes()).hexdigest()
                except OSError as exc:
                    errors.append(f"frozen_files[{index}] cannot read named file: {exc}")
                else:
                    if actual != entry["sha256"]:
                        errors.append(f"frozen_files[{index}] hash mismatch")

    topology = _obj(document.get("topology"), "topology", errors)
    children = topology.get("coordinator_children")
    if not isinstance(children, list):
        errors.append("topology.coordinator_children must be a list")
        children = []
    expected = {"C0": {"advisor"}, "C1": {"worker", "advisor"}, "C2": {"supervisor", "worker", "advisor"},
                "C3": {"supervisor", "advisor"}, "C4": {"supervisor", "worker", "advisor"}}.get(configuration, set())
    if set(children) != expected:
        errors.append("topology coordinator children mismatch")
    if configuration == "C2" and topology.get("supervisor_spawned") is True:
        errors.append("C2 Supervisor spawn is forbidden")
    if configuration in {"C1", "C4"}:
        edits = _obj(document.get("implementation_edits"), "implementation_edits", errors)
        paths = edits.get("coordinator_paths", [])
        if not isinstance(paths, list):
            errors.append("implementation_edits.coordinator_paths must be a list")
        elif paths:
            errors.append("Coordinator implementation edits are forbidden for C1/C4")

    sessions = document.get("sessions")
    ids: list[str] = []
    if not isinstance(sessions, list) or not sessions:
        errors.append("sessions must be a nonempty list")
    else:
        for index, item in enumerate(sessions):
            session = _obj(item, f"sessions[{index}]", errors)
            sid = session.get("session_id")
            if not isinstance(sid, str) or not sid.strip():
                errors.append(f"sessions[{index}].session_id must be materialized")
            else:
                ids.append(sid)
        if len(ids) != len(set(ids)):
            errors.append("duplicate session IDs")
    prior = document.get("prior_session_ids", [])
    if not isinstance(prior, list):
        errors.append("prior_session_ids must be a list")
    elif set(ids) & set(prior):
        errors.append("reused session ID")

    contamination = _obj(document.get("contamination"), "contamination", errors)
    if contamination.get("contaminated") is not False:
        errors.append("contamination must be false")

    advisor = _obj(document.get("advisor"), "advisor", errors)
    for key in ("bundle_path", "verdict_path", "lineage_id"):
        if not isinstance(advisor.get(key), str) or not advisor[key].strip():
            errors.append(f"advisor.{key} must be materialized")
    for key in ("bundle_sha256", "verdict_sha256"):
        _sha(advisor.get(key), f"advisor.{key}", errors)
    if advisor.get("run_id") != run_id or advisor.get("bundle_run_id") != run_id or advisor.get("verdict_run_id") != run_id:
        errors.append("Advisor bundle/verdict run binding mismatch")
    if advisor.get("bundle_lineage_id") != advisor.get("lineage_id") or advisor.get("verdict_lineage_id") != advisor.get("lineage_id"):
        errors.append("Advisor bundle/verdict lineage mismatch")
    if advisor.get("verdict") not in {"accepted", "defect_packet", "verified_blocker"}:
        errors.append("Advisor verdict is missing or invalid")
    if advisor.get("bundle_path") == advisor.get("verdict_path"):
        errors.append("Advisor bundle and verdict must be distinct files")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_p107_materialized_run.py <materialized-run.json>")
    problems = validate_materialized_run(sys.argv[1])
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("P107 materialized run is valid")
