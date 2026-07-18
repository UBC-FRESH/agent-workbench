from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_p114_multiagent_host_registration.py"
SPEC = importlib.util.spec_from_file_location("p114_host_registration", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_probe_reports_registration_gap_when_only_direct_host_has_patch_vocabulary(tmp_path: Path) -> None:
    direct = tmp_path / "direct.exe"
    child = tmp_path / "child.exe"
    direct.write_text("apply_patch_tool_type custom_tool_call unsupported custom tool call", encoding="utf-8")
    child.write_text("shell_command", encoding="utf-8")

    report = MODULE.inspect(direct, child)

    assert report["direct_supports_patch_dispatch"] is True
    assert report["child_supports_patch_dispatch"] is False
    assert report["verdict"] == "host_registration_gap"


def test_probe_is_inconclusive_when_both_hosts_expose_patch_vocabulary(tmp_path: Path) -> None:
    direct = tmp_path / "direct.exe"
    child = tmp_path / "child.exe"
    content = "apply_patch_tool_type custom_tool_call unsupported custom tool call"
    direct.write_text(content, encoding="utf-8")
    child.write_text(content, encoding="utf-8")

    assert MODULE.inspect(direct, child)["verdict"] == "inconclusive"
