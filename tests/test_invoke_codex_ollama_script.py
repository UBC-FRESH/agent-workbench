from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_local_launcher_keeps_private_values_out_of_tracked_source() -> None:
    text = (ROOT / "scripts" / "invoke_codex_ollama.ps1").read_text(encoding="utf-8")

    assert "AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL" in text
    assert "AGENT_WORKBENCH_PROVIDER_HEADERS_FILE" in text
    assert "agent_workbench_ollama" in text
    assert "CodexArgsBase64" in text
    assert "config.toml" in text
    assert "agent_workbench_ollama_" in text
    assert "config_file" in text
    assert "env_http_headers" in text
    assert '[model_providers.agent_workbench_ollama.http_headers]' not in text
    assert "fresh01x" not in text
    assert "AW_CF_CLIENT_SECRET" in text


def test_ollama_bootstrap_writes_toml_without_a_bom() -> None:
    text = (ROOT / "scripts" / "invoke_codex_ollama.ps1").read_text(encoding="utf-8")

    assert "function Write-Utf8NoBom" in text
    assert "[Text.UTF8Encoding]::new($false)" in text
    assert "Set-Content -LiteralPath $configPath -Value $updatedConfig -Encoding utf8" not in text
    assert "Set-Content -LiteralPath (Join-Path $localAgents" not in text
