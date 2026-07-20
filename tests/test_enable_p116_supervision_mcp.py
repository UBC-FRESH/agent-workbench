from pathlib import Path
import json
import shutil
import subprocess
import uuid

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "enable_p116_supervision_mcp.ps1"


def test_script_is_p116_scoped_and_reversible():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "supervision_wait_delta" in text
    assert "p116_supervision_mcp_server.py" in text
    assert "transaction_cli commit" in text and "transaction_cli restore" in text
    assert "enabled_tools = [\"supervision_wait_delta\"]" in text
    assert "provider" not in text.lower()


def test_script_requires_manifest_and_uses_unique_server_identity():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "supervision\\manifest.json" in text
    assert "p116_supervision_" in text
    assert "config.before.toml" in text
    assert "p116_staging_manifest.json" in text


def test_enable_disable_round_trip_uses_temporary_codex_home(tmp_path):
    repo = SCRIPT.parents[1]
    run_id = "p116_test_" + uuid.uuid4().hex
    run_dir = repo / "runtime" / "agent_jobs" / run_id
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    original = "model = \"test-model\"\n\n[profiles.default]\nname = \"test\"\n"
    config.write_bytes(original.encode("utf-8"))
    project_root = tmp_path / "project"
    hooks_dir = project_root / ".codex"
    hooks_dir.mkdir(parents=True)
    hooks = hooks_dir / "hooks.json"
    original_hooks = b'{"description":"temporary hooks"}\n'
    hooks.write_bytes(original_hooks)
    supervision = run_dir / "supervision"
    supervision.mkdir(parents=True)
    manifest = {
        "schema_version": "p116_supervision_v1", "run_id": run_id,
        "worker_session_id": "worker-test", "supervisor_session_id": "supervisor-test",
        "assigned_root": str(run_dir), "supervision_dir": str(supervision),
        "events_path": "supervision/events.jsonl", "cursor_path": "supervision/cursor.json",
        "packets_path": "supervision/packets.jsonl", "actions_path": "supervision/actions.jsonl",
    }
    (supervision / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    command = [
        "powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
        "-File", str(SCRIPT), "-Mode", "Enable", "-RunId", run_id,
        "-CodexHome", str(codex_home),
        "-ProjectRoot", str(project_root),
    ]
    try:
        enabled = subprocess.run(command, cwd=repo, capture_output=True, text=True, timeout=30)
        assert enabled.returncode == 0, enabled.stderr + enabled.stdout
        staged = config.read_text(encoding="utf-8")
        server = f"[mcp_servers.p116_supervision_{run_id}]"
        assert staged.count(server) == 1
        assert staged.count('enabled_tools = ["supervision_wait_delta"]') == 1
        assert "p116_supervision_mcp_server.py" in staged
        assert staged.count("[mcp_servers.") == 1
        staged_hooks = json.loads(hooks.read_text(encoding="utf-8"))
        assert set(staged_hooks["hooks"]) == {"PreToolUse", "PostToolUse"}
        assert all(entry["matcher"] == "^Bash$" for entries in staged_hooks["hooks"].values() for entry in entries)
        assert all("p116_capture_hook.py" in hook["command"] for entries in staged_hooks["hooks"].values() for entry in entries for hook in entry["hooks"])
        assert all(set(hook) == {"type", "command"} for entries in staged_hooks["hooks"].values() for entry in entries for hook in entry["hooks"])
        activation = json.loads((run_dir / "supervision" / "activation.json").read_text(encoding="utf-8"))
        assert activation["active"] is False and activation["run_id"] == run_id
        assert "worker_session_id" not in activation

        disabled = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(SCRIPT), "-Mode", "Disable", "-RunId", run_id,
             "-CodexHome", str(codex_home), "-ProjectRoot", str(project_root)],
            cwd=repo, capture_output=True, text=True, timeout=30,
        )
        assert disabled.returncode == 0, disabled.stderr + disabled.stdout
        assert config.read_bytes() == original.encode("utf-8")
        assert hooks.read_bytes() == original_hooks
        assert not (run_dir / "supervision" / "activation.json").exists()
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)
