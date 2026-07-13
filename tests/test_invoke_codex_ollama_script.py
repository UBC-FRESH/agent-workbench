from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ollama_bootstrap_writes_toml_without_a_bom() -> None:
    script = (ROOT / "scripts" / "invoke_codex_ollama.ps1").read_text(encoding="utf-8")

    assert "function Write-Utf8NoBom" in script
    assert "[Text.UTF8Encoding]::new($false)" in script
    assert "Set-Content -LiteralPath $configPath -Value $updatedConfig -Encoding utf8" not in script
    assert "Set-Content -LiteralPath (Join-Path $localAgents" not in script
