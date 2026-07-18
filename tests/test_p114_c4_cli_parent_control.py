from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_p114_c4_cli_parent_control.ps1"
VERIFIER = ROOT / "scripts" / "verify_p114_c4_capability_battery.py"
PACKAGE_VERIFIER = ROOT / "scripts" / "verify_p114_package_mcp_battery.py"


def test_cli_parent_control_preserves_the_single_native_worker_boundary() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "multi_agent_v1 spawn tool exactly once" in text
    assert "agent_type: ollama_qwen_coder_worker" in text
    assert "fork_context: false" in text
    assert "no model, reasoning, or service-tier override" in text
    assert "--dangerously-bypass-approvals-and-sandbox" in text
    assert "$parentTicket | & codex @codexArgs" in text
    assert "'--json', '-o', $final, '-'" in text
    assert "-StripInclude" in text
    assert "[switch]$Battery" in text
    assert "[switch]$PackageMcpBattery" in text
    assert "-StripInclude -Battery" in text
    assert "-PackageMcpBattery" in text
    assert "AGENT_WORKBENCH_PROVIDER_HEADERS_FILE" in text
    assert "'AW_CF_CLIENT_ID' = $headers.'CF-Access-Client-Id'" in text
    assert "'AW_CF_CLIENT_SECRET' = $headers.'CF-Access-Client-Secret'" in text
    assert "[Environment]::SetEnvironmentVariable($name, $value, 'Process')" in text
    assert "-Mode Disable -RunId $RunId -AdapterPort $AdapterPort" in text


def test_c4_battery_verifier_requires_raw_child_sequence_and_three_rows() -> None:
    text = VERIFIER.read_text(encoding="utf-8")
    assert '["shell_command", "apply_patch", "shell_command", "apply_patch", "shell_command"]' in text
    assert 'exit_codes != [0, 17, 0]' in text
    assert 'terminal_text != "P114_C4_BATTERY_DONE"' in text
    assert "len(rows) == 3" in text


def test_package_mcp_battery_verifier_requires_namespaced_calls_and_restoration() -> None:
    text = PACKAGE_VERIFIER.read_text(encoding="utf-8")
    assert 'EXPECTED_CALLS = ["tool_search", "exec", "apply_patch", "exec", "apply_patch", "exec"]' in text
    assert 'EXPECTED_MCP_TOOLS = ["exec", "apply_patch", "exec", "apply_patch", "exec"]' in text
    assert 'TERMINAL_MARKER = "P114_C4_PACKAGE_MCP_BATTERY_DONE"' in text
    assert 'exit_codes != [0, 17, 0]' in text
    assert 'errors.append("byte_restore")' in text
    assert "len(rows) == 3" in text
