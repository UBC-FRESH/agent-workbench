"""Validate one offline, materialized P107 run-evidence document."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from validate_p107_run_evidence_manifest import validate_manifest

from validate_p107_advisor_review import validate_review

SHA256 = re.compile(r"^[0-9a-f]{64}$")
ROLES = {
    "C0": ["coordinator", "advisor"],
    "C1": ["coordinator", "worker", "advisor"],
    "C2": ["coordinator", "supervisor", "worker", "advisor"],
    "C3": ["coordinator", "supervisor", "advisor", "worker"],
    "C4": ["coordinator", "supervisor", "worker", "advisor"],
}
CHILDREN = {
    "C0": ["advisor"],
    "C1": ["worker", "advisor"],
    "C2": ["supervisor", "worker", "advisor"],
    "C3": ["supervisor", "advisor"],
    "C4": ["supervisor", "worker", "advisor"],
}


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


def _artifact(raw: Any, label: str, root: Path, errors: list[str], *, json_only: bool = False) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        errors.append(f"{label} must be materialized")
        return None
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        errors.append(f"{label} must be beneath the materialized-run directory")
        return None
    target = (root / candidate).resolve(strict=False)
    try:
        target.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label} must be beneath the materialized-run directory")
        return None
    current = root.resolve()
    for part in candidate.parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"{label} must not be a symlink")
            return None
    if json_only and target.suffix.lower() != ".json":
        errors.append(f"{label} must be a JSON path")
    if not target.is_file():
        errors.append(f"{label} must be an existing file")
    return target


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
    manifest_path = document.get("evidence_manifest_path")
    manifest_sha = document.get("evidence_manifest_sha256")
    manifest = None
    if not isinstance(manifest_path, str) or not manifest_path.strip() or Path(manifest_path).is_absolute() or ".." in Path(manifest_path).parts:
        errors.append("evidence_manifest_path must be a canonical relative path")
    else:
        target = document_path.parent / manifest_path
        if not target.is_file(): errors.append("evidence manifest is missing")
        elif not isinstance(manifest_sha, str) or not SHA256.fullmatch(manifest_sha) or hashlib.sha256(target.read_bytes()).hexdigest() != manifest_sha:
            errors.append("evidence manifest hash mismatch")
        else:
            problems = validate_manifest(target)
            errors.extend(f"evidence manifest: {p}" for p in problems)
            if not problems:
                manifest = json.loads(target.read_text(encoding="utf-8"))
    if document.get("schema_version") != "p107_materialized_run_v1":
        errors.append("schema_version must be p107_materialized_run_v1")
    run_id = document.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("run_id must be materialized")
    configuration = document.get("configuration_id")
    if configuration not in {"C0", "C1", "C2", "C3", "C4"}:
        errors.append("configuration_id must be one of C0, C1, C2, C3, C4")
    if isinstance(manifest, dict):
        if document.get("run_id") != manifest.get("run_id"): errors.append("run_id does not match evidence manifest")
        if document.get("configuration_id") != manifest.get("configuration_id"): errors.append("configuration_id does not match evidence manifest")
        declared = {(s.get("role"), s.get("session_id")) for s in document.get("sessions", []) if isinstance(s, dict)}
        actual = {(s.get("role"), s.get("session_id")) for s in manifest.get("raw_sessions", []) if isinstance(s, dict)}
        if declared != actual: errors.append("sessions do not match evidence manifest")
        edge_roles = [(e.get("parent_role"), e.get("child_role")) for e in manifest.get("spawn_edges", []) if isinstance(e, dict)]
        expected_children = [c for p, c in edge_roles if p == "coordinator"]
        if document.get("topology", {}).get("coordinator_children") != expected_children: errors.append("topology contradicts evidence manifest")
        if document.get("repository_path") is not None and document.get("repository_path") != manifest.get("repository_path"): errors.append("repository_path does not match evidence manifest")
        if document.get("starting_commit") is not None and document.get("starting_commit") != manifest.get("starting_commit"): errors.append("starting_commit does not match evidence manifest")
        if document.get("terminal_event") is not None and document.get("terminal_event") != manifest.get("terminal_event"): errors.append("terminal_event does not match evidence manifest")

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
                target = _artifact(raw, f"frozen_files[{index}].path", document_path.parent, errors)
                if target is not None:
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
    expected = CHILDREN.get(configuration, [])
    if children != expected or len(children) != len(set(children)):
        errors.append("topology coordinator children mismatch")
    if configuration == "C3" and topology.get("nested_worker_spawned") is not True:
        errors.append("C3 nested Worker spawn is required")
    if configuration in {"C0", "C1", "C2", "C4"} and topology.get("nested_worker_spawned") is not False:
        errors.append(f"{configuration} nested Worker spawn must be explicitly false")
    if configuration in {"C0", "C1", "C2", "C4"} and topology.get("supervisor_spawned") is True:
        errors.append(f"{configuration} Supervisor spawn is forbidden")
    if configuration in {"C1", "C2", "C3", "C4"}:
        edits = _obj(document.get("implementation_edits"), "implementation_edits", errors)
        paths = edits.get("coordinator_paths", [])
        if not isinstance(paths, list):
            errors.append("implementation_edits.coordinator_paths must be a list")
        elif paths:
            errors.append("Coordinator implementation edits are forbidden for C1-C4")

    sessions = document.get("sessions")
    ids: list[str] = []
    roles: list[str] = []
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
            role = session.get("role")
            if role not in ROLES.get(configuration, []):
                errors.append(f"sessions[{index}].role is not active for configuration")
            else:
                roles.append(role)
            for field in ("provider", "model_class"):
                if not isinstance(session.get(field), str) or not session[field].strip():
                    errors.append(f"sessions[{index}].{field} must be declared")
        if len(ids) != len(set(ids)):
            errors.append("duplicate session IDs")
        expected_roles = set(ROLES.get(configuration, []))
        if len(roles) != len(set(roles)) or set(roles) != expected_roles:
            errors.append("sessions must contain each active role exactly once")
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
    bundle = _artifact(advisor.get("bundle_path"), "advisor.bundle_path", document_path.parent, errors, json_only=True)
    verdict = _artifact(advisor.get("verdict_path"), "advisor.verdict_path", document_path.parent, errors, json_only=True)
    if bundle is not None and verdict is not None and bundle == verdict:
        errors.append("Advisor bundle and verdict must be distinct files")
    for target, key in ((bundle, "bundle_sha256"), (verdict, "verdict_sha256")):
        if target is not None and _sha(advisor.get(key), f"advisor.{key}", errors):
            if hashlib.sha256(target.read_bytes()).hexdigest() != advisor[key]:
                errors.append(f"advisor.{key} hash mismatch")
    if bundle is not None and verdict is not None:
        review_errors = validate_review(bundle, verdict, prior_session_ids=set(prior) if isinstance(prior, list) else None)
        errors.extend(f"Advisor review: {problem}" for problem in review_errors)
        try:
            bundle_data = json.loads(bundle.read_text(encoding="utf-8"))
            verdict_data = json.loads(verdict.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            bundle_data = verdict_data = {}
        if verdict_data.get("verdict") != advisor.get("verdict"):
            errors.append("Advisor terminal outcome mismatch")
        if bundle_data.get("run_id") != run_id or verdict_data.get("run_id") != run_id:
            errors.append("Advisor review run binding mismatch")
        if advisor.get("lineage_id") not in {bundle_data.get("advisor_lineage_id"), verdict_data.get("advisor_lineage_id")}:
            errors.append("Advisor review lineage binding mismatch")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_p107_materialized_run.py <materialized-run.json>")
    problems = validate_materialized_run(sys.argv[1])
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("P107 materialized run is valid")
