import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "bind_p116_worker.py"


def setup_run(tmp_path: Path, *, active=False):
    root = tmp_path / "run"; supervision = root / "supervision"; supervision.mkdir(parents=True)
    manifest = {"schema_version": "p116_supervision_v1", "run_id": "run-bind", "worker_session_id": "worker-placeholder", "supervisor_session_id": "supervisor-placeholder", "assigned_root": str(root), "supervision_dir": str(supervision), "events_path": "supervision/events.jsonl", "cursor_path": "supervision/cursor.json", "packets_path": "supervision/packets.jsonl", "actions_path": "supervision/actions.jsonl"}
    path = supervision / "manifest.json"; path.write_text(json.dumps(manifest), encoding="utf-8")
    (supervision / "activation.json").write_text(json.dumps({"active": active, "run_id": "run-bind", "assigned_root": str(root), "supervision_dir": str(supervision)}), encoding="utf-8")
    sessions = tmp_path / ".codex" / "sessions"; sessions.mkdir(parents=True)
    (sessions / "worker-native.jsonl").write_text('{"type":"thread.started"}\n', encoding="utf-8")
    return path, manifest


def run(manifest, worker="worker-native", supervisor="supervisor-native", home=None):
    env = None if home is None else {**__import__("os").environ, "HOME": str(home), "USERPROFILE": str(home)}
    return subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(manifest), "--worker-session-id", worker, "--supervisor-session-id", supervisor], capture_output=True, text=True, env=env)


def test_success_binds_manifest_then_activation(tmp_path):
    path, _ = setup_run(tmp_path); result = run(path, home=tmp_path)
    assert result.returncode == 0 and json.loads(result.stderr)["status"] == "bound"
    manifest = json.loads(path.read_text()); activation = json.loads(path.parent.joinpath("activation.json").read_text())
    assert manifest["worker_session_id"] == "worker-native" and manifest["supervisor_session_id"] == "supervisor-native"
    assert activation["active"] is True and activation["worker_session_id"] == "worker-native"


def test_active_refusal(tmp_path):
    path, _ = setup_run(tmp_path, active=True); result = run(path, home=tmp_path)
    assert result.returncode != 0 and json.loads(result.stderr)["code"] == "BIND_REFUSED"


def test_artifact_refusal(tmp_path):
    path, _ = setup_run(tmp_path); (path.parent / "events.jsonl").write_text("not empty\n")
    result = run(path, home=tmp_path)
    assert result.returncode != 0 and json.loads(result.stderr)["code"] == "BIND_REFUSED"


@pytest.mark.parametrize("activation", ["not-json", {"active": False, "run_id": "wrong", "assigned_root": "x", "supervision_dir": "y"}])
def test_malformed_or_mismatched_activation_refusal(tmp_path, activation):
    path, _ = setup_run(tmp_path); (path.parent / "activation.json").write_text(activation if isinstance(activation, str) else json.dumps(activation))
    result = run(path, home=tmp_path)
    assert result.returncode != 0 and json.loads(result.stderr)["code"] == "BIND_REFUSED"
