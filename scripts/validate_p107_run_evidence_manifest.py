"""Deterministically validate an offline P107 run evidence manifest."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any

ROLES = {"coordinator", "supervisor", "worker", "advisor"}
EXPECTED = {
    "C0": {("coordinator", "advisor")},
    "C1": {("coordinator", "worker"), ("coordinator", "advisor")},
    "C2": {("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")},
    "C3": {("coordinator", "supervisor"), ("coordinator", "advisor"), ("supervisor", "worker")},
    "C4": {("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")},
}
ACTIVE = {"C0": {"coordinator", "advisor"}, "C1": {"coordinator", "worker", "advisor"},
          "C2": {"coordinator", "supervisor", "worker", "advisor"}, "C3": {"coordinator", "supervisor", "worker", "advisor"},
          "C4": {"coordinator", "supervisor", "worker", "advisor"}}
TOP_LEVEL_KEYS = {"schema_version", "run_id", "configuration_id", "repository_path", "starting_commit", "terminal_event", "raw_sessions", "spawn_edges"}
SESSION_KEYS = {"schema_version", "role", "session_id", "parent_session_id", "provider", "model_class", "raw_session_path", "sha256", "terminal_event", "event_type"}
EDGE_KEYS = {"schema_version", "parent_session_id", "child_session_id", "parent_role", "child_role", "fork_context", "source_artifact_path", "source_artifact_sha256", "terminal_event", "observed_event"}
RAW_ARTIFACT_KEYS = {"schema_version", "session_id", "parent_session_id", "role", "provider", "model_class", "terminal_event", "event_type"}
SPAWN_ARTIFACT_KEYS = {"schema_version", "parent_session_id", "child_session_id", "parent_role", "child_role", "fork_context", "terminal_event", "observed_event"}

def _file(root: Path, value: Any, label: str, errors: list[str]) -> Path | None:
    candidate = Path(value) if isinstance(value, str) else Path(".")
    if not isinstance(value, str) or not value or candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != value:
        errors.append(f"{label} must be a canonical relative path"); return None
    p = root / value
    current = root
    for part in candidate.parts:
        current /= part
        if current.is_symlink(): errors.append(f"{label} must not be a symlink"); return None
    if not p.is_file() or p.is_symlink(): errors.append(f"{label} must be an existing regular file") ; return None
    return p

def _json_record(file: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        record = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label} must contain a canonical JSON object: {exc}"); return None
    if not isinstance(record, dict): errors.append(f"{label} must contain a JSON object"); return None
    return record

def _compare_record(record: dict[str, Any], declaration: dict[str, Any], keys: set[str], label: str, errors: list[str]) -> None:
    if set(record) - keys: errors.append(f"{label} contains undeclared properties")
    required = keys - {"event_type", "observed_event"}
    if not required.issubset(record): errors.append(f"{label} is missing canonical properties")
    for key in keys:
        if key in record and key in declaration and record[key] != declaration[key]:
            errors.append(f"{label} {key} does not match manifest")

def validate_manifest(path: str | Path) -> list[str]:
    path = Path(path); errors: list[str] = []
    try: doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: return [f"cannot read manifest: {exc}"]
    if not isinstance(doc, dict): return ["manifest root must be an object"]
    extra = set(doc) - TOP_LEVEL_KEYS
    if extra: errors.append("manifest contains undeclared properties")
    if doc.get("schema_version") != "p107_run_evidence_manifest_v1": errors.append("invalid schema_version")
    run_id, config = doc.get("run_id"), doc.get("configuration_id")
    if not isinstance(run_id, str) or not run_id: errors.append("run_id must be declared")
    if config not in EXPECTED: errors.append("configuration_id must be C0-C4")
    if not isinstance(doc.get("terminal_event"), str) or not doc.get("terminal_event"): errors.append("terminal_event must be declared")
    commit = doc.get("starting_commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit): errors.append("starting_commit must be a full lowercase commit")
    repo = doc.get("repository_path")
    if not isinstance(repo, str) or not repo: errors.append("repository_path must be declared")
    else:
        try:
            clean = subprocess.run(["git", "-C", repo, "status", "--porcelain"], capture_output=True, text=True, check=True)
            head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            if clean.stdout: errors.append("repository worktree is dirty")
            if isinstance(commit, str) and head != commit: errors.append("repository is not at starting_commit")
        except (OSError, subprocess.CalledProcessError) as exc: errors.append(f"repository_path is not a git repository: {exc}")
    sessions = doc.get("raw_sessions")
    if not isinstance(sessions, list) or not sessions: errors.append("raw_sessions must be nonempty") ; sessions = []
    ids: dict[str, dict[str, Any]] = {}
    for i, s in enumerate(sessions):
        if not isinstance(s, dict): errors.append(f"raw_sessions[{i}] must be an object"); continue
        if set(s) - SESSION_KEYS: errors.append(f"raw_sessions[{i}] contains undeclared properties")
        sid, role = s.get("session_id"), s.get("role")
        if not isinstance(sid, str) or not sid: errors.append(f"raw_sessions[{i}] session_id missing")
        elif sid in ids: errors.append("duplicate session IDs")
        else: ids[sid] = s
        if role not in ROLES: errors.append(f"raw_sessions[{i}] unknown role")
        if role == "coordinator" and s.get("parent_session_id") is not None: errors.append("root coordinator parent must be null")
        if role != "coordinator" and not isinstance(s.get("parent_session_id"), str): errors.append("non-root parent_session_id required")
        for field in ("provider", "model_class", "terminal_event"):
            if not isinstance(s.get(field), str) or not s.get(field): errors.append(f"raw_sessions[{i}] {field} must be declared")
        raw = _file(path.parent, s.get("raw_session_path"), f"raw_sessions[{i}].raw_session_path", errors)
        digest = s.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest): errors.append(f"raw_sessions[{i}] invalid SHA-256")
        elif raw and hashlib.sha256(raw.read_bytes()).hexdigest() != digest: errors.append(f"raw_sessions[{i}] hash mismatch")
        if raw:
            record = _json_record(raw, f"raw_sessions[{i}].raw_session_path", errors)
            if record is not None:
                _compare_record(record, s, RAW_ARTIFACT_KEYS, f"raw_sessions[{i}] raw artifact", errors)
    if config in ACTIVE and (set(s.get("role") for s in sessions if isinstance(s, dict)) != ACTIVE[config] or len(ids) != len(ACTIVE[config])): errors.append("raw session roles do not match configuration")
    edges = doc.get("spawn_edges")
    if not isinstance(edges, list): errors.append("spawn_edges must be a list"); edges = []
    actual: set[tuple[str, str]] = set()
    edge_ids: set[tuple[str, str]] = set()
    expected_edge_count = len(EXPECTED.get(config, set()))
    if len(edges) != expected_edge_count: errors.append("spawn edge count does not match configuration")
    for i, e in enumerate(edges):
        if not isinstance(e, dict): errors.append(f"spawn_edges[{i}] must be an object"); continue
        if set(e) - EDGE_KEYS: errors.append(f"spawn_edges[{i}] contains undeclared properties")
        parent, child = e.get("parent_session_id"), e.get("child_session_id")
        if parent not in ids or child not in ids: errors.append(f"spawn_edges[{i}] references unknown session")
        else:
            edge_id = (parent, child)
            if edge_id in edge_ids: errors.append("duplicate spawn edge")
            edge_ids.add(edge_id)
            pair = (ids[parent].get("role"), ids[child].get("role")); actual.add(pair)
            if e.get("parent_role") != pair[0] or e.get("child_role") != pair[1]: errors.append(f"spawn_edges[{i}] role binding mismatch")
            if ids[child].get("role") == "coordinator": errors.append("coordinator must not be a spawn edge child")
            if ids[child].get("role") != "coordinator" and ids[child].get("parent_session_id") != parent: errors.append("session parent does not match spawn edge")
        if e.get("fork_context") is not False: errors.append(f"spawn_edges[{i}] fork_context must be false")
        for field in ("parent_session_id", "child_session_id", "parent_role", "child_role", "source_artifact_path"):
            if not isinstance(e.get(field), str) or not e.get(field): errors.append(f"spawn_edges[{i}] {field} must be declared")
        source_hash = e.get("source_artifact_sha256")
        if not isinstance(source_hash, str) or len(source_hash) != 64 or any(c not in "0123456789abcdef" for c in source_hash): errors.append(f"spawn_edges[{i}] invalid source artifact SHA-256")
        art = _file(path.parent, e.get("source_artifact_path"), f"spawn_edges[{i}].source_artifact_path", errors)
        if art and hashlib.sha256(art.read_bytes()).hexdigest() != source_hash: errors.append(f"spawn_edges[{i}] source artifact hash mismatch")
        if art:
            record = _json_record(art, f"spawn_edges[{i}].source_artifact_path", errors)
            if record is not None:
                _compare_record(record, e, SPAWN_ARTIFACT_KEYS, f"spawn_edges[{i}] source artifact", errors)
    if actual != EXPECTED.get(config, set()): errors.append("spawn topology is undeclared or forbidden")
    for sid, session in ids.items():
        if session.get("role") != "coordinator":
            matches = [edge for edge in edges if isinstance(edge, dict) and edge.get("child_session_id") == sid and edge.get("parent_session_id") == session.get("parent_session_id")]
            if len(matches) != 1: errors.append("non-coordinator session must have exactly one matching spawn edge")
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("usage: validate_p107_run_evidence_manifest.py <manifest.json>")
    problems = validate_manifest(sys.argv[1])
    if problems: print("\n".join(problems)); raise SystemExit(1)
    print("P107 run evidence manifest is valid")
