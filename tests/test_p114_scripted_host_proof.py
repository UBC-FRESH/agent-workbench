from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_p114_scripted_host_proof.ps1"


def test_host_proof_bypasses_known_broken_windows_sandbox_by_default() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "[switch]$UseBrokenWindowsSandbox" in text
    assert "'--dangerously-bypass-approvals-and-sandbox'" in text
    assert "if ($UseBrokenWindowsSandbox)" in text


def test_host_proof_preserves_prompt_as_one_process_argument_and_refreshes_exit_code() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "$codexArguments += ('\"' + $prompt.Replace('\"', '\\\"') + '\"')" in text
    assert "$codexProcess.Refresh()" in text
    assert "Wait-Process -Id $codexProcess.Id -Timeout 45" in text
