"""Bind the exact native Worker session to an inactive staged P116 run."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.supervision import validate_manifest
from agent_workbench.supervision_controller import load_manifest
from agent_workbench.native_session_events import initialize_session_cursor


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.bind.tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def bind(manifest_path: Path, worker_session_id: str, supervisor_session_id: str) -> None:
    manifest, root = load_manifest(manifest_path)
    activation_path = manifest_path.parent / "activation.json"
    if not activation_path.exists():
        raise ValueError("activation marker is missing")
    try:
        activation = json.loads(activation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("activation marker is malformed") from exc
    if not isinstance(activation, dict):
        raise ValueError("activation marker is malformed")
    if activation.get("active") is not False:
        raise ValueError("activation is already active")
    for field in ("run_id", "assigned_root", "supervision_dir"):
        if activation.get(field) != manifest.get(field):
            raise ValueError(f"activation {field} does not match manifest")
    for field in ("events_path", "packets_path", "actions_path", "cursor_path"):
        artifact = (root / manifest[field]).resolve()
        if not artifact.is_relative_to(root):
            raise ValueError("manifest artifact escapes assigned root")
        if artifact.exists() and (artifact.stat().st_size > 0 or artifact.is_file()):
            raise ValueError("run artifacts already exist")
    updated = dict(manifest)
    updated["worker_session_id"] = worker_session_id
    updated["supervisor_session_id"] = supervisor_session_id
    validation = validate_manifest(updated)
    if not validation.ok:
        raise ValueError("updated manifest is invalid")
    _atomic_json(manifest_path, updated)
    initialize_session_cursor(manifest=updated, root=root)
    activation["active"] = True
    activation["worker_session_id"] = worker_session_id
    _atomic_json(activation_path, activation)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--worker-session-id", required=True)
    parser.add_argument("--supervisor-session-id", required=True)
    args = parser.parse_args()
    try:
        bind(Path(args.manifest), args.worker_session_id, args.supervisor_session_id)
        print(json.dumps({"status": "bound", "manifest": "validated"}, separators=(",", ":")), file=sys.stderr)
        return 0
    except (OSError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "error", "code": "BIND_REFUSED"}, separators=(",", ":")), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
