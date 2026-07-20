import json
import subprocess
import uuid
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "enable_p116_vscode_in_session.ps1"


def test_install_round_trip_adds_native_ui_tools_without_overwriting_existing_hooks(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex"
    codex_home.mkdir()
    (codex_home / "config.toml").write_text('model = "test"\n', encoding="utf-8")
    (codex_home / "hooks.json").write_text(json.dumps({"description": "existing", "hooks": {"Stop": [{"matcher": ".*", "hooks": []}]}}), encoding="utf-8")
    install_id = "p116_ui_" + uuid.uuid4().hex
    enable = subprocess.run([
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
        "-Mode", "Enable", "-InstallId", install_id, "-CodexHome", str(codex_home),
    ], capture_output=True, text=True)
    assert enable.returncode == 0, enable.stderr + enable.stdout
    config = (codex_home / "config.toml").read_text(encoding="utf-8")
    hooks = json.loads((codex_home / "hooks.json").read_text(encoding="utf-8"))
    assert "[mcp_servers.p116_in_session_supervision]" in config
    assert "supervision_start_run" in config
    assert set(hooks["hooks"]) == {"Stop", "PreToolUse", "PostToolUse"}
    disable = subprocess.run([
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
        "-Mode", "Disable", "-InstallId", install_id, "-CodexHome", str(codex_home),
    ], capture_output=True, text=True)
    assert disable.returncode == 0, disable.stderr + disable.stdout
    assert (codex_home / "config.toml").read_text(encoding="utf-8") == 'model = "test"\n'
    assert json.loads((codex_home / "hooks.json").read_text(encoding="utf-8"))["hooks"] == {"Stop": [{"matcher": ".*", "hooks": []}]}
