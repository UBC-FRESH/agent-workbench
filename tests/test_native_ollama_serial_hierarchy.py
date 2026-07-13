from __future__ import annotations

from pathlib import Path


def test_serial_hierarchy_keeps_remote_model_turns_non_overlapping() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "run_native_ollama_serial_hierarchy.ps1").read_text(encoding="utf-8")

    assert "SUPERVISOR_MARKER`_DISPATCHED" not in text  # marker is runtime-interpolated
    assert "Supervisor dispatch acknowledgement" in text
    assert "run_native_ollama_worker.ps1" in text
    assert "Worker marker did not match" in text
    assert "Supervisor verification marker did not match" in text
    assert "model_provider=agent_workbench_ollama" in text
    assert "'read-only'" in text
    assert "approval_policy=\"never\"" in text
    assert "features.shell_tool=false" in text
    assert "Invoke-OllamaTurn -AllowTools" in text
    assert "function Remove-WorkerCodexHome" in text
    assert "Remove-WorkerCodexHome" in text
