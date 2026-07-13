from __future__ import annotations

from pathlib import Path


def test_hierarchy_launcher_uses_the_protected_worker_boundary() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "run_native_ollama_hierarchy.ps1").read_text(encoding="utf-8")

    assert "run_native_ollama_worker.ps1" in text
    assert "model_provider=agent_workbench_ollama" in text
    assert "$workerCodexHome = Join-Path $runDir 'codex_home'" in text
    assert "Copy-Item -LiteralPath (Join-Path $operatorCodexHome 'config.toml')" in text
    assert "timeout_ms set to 120000" in text
    assert "-Output $relativeWorkerOutput" in text
    assert "$supervisorEvents = Join-Path $runDir 'supervisor_events.jsonl'" in text
    assert "Tee-Object -LiteralPath $supervisorEvents" in text
    assert "Use the actual shell" in text
    assert "tool provided by Codex" in text
    assert "qwen3-coder:latest" in text
    assert "runtime\\agent_jobs" in text
    assert "local_provider_headers.json" not in text
