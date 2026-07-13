from __future__ import annotations

from pathlib import Path


def test_worker_launcher_has_no_provider_header_file_access() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "run_native_ollama_worker.ps1").read_text(encoding="utf-8")

    assert "model_provider=agent_workbench_ollama" in text
    assert "CODEX_HOME" in text
    assert "Split-Path -Parent $ticketPath" in text
    assert "Worker Codex home is missing its prepared config" in text
    assert "-s read-only --add-dir $env:CODEX_HOME" in text
    assert "approval_policy=\"never\"" in text
    assert "[switch]$Background" in text
    assert "Start-Process" in text
    assert "worker_process.stderr.log" in text
    assert "qwen3-coder:latest" in text
    assert "runtime/agent_jobs" in text
    assert "local_provider_headers.json" not in text
    assert ".agent-workbench-env.txt" not in text
