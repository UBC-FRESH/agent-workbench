from __future__ import annotations

from pathlib import Path


def test_local_launcher_keeps_private_values_out_of_tracked_source() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "invoke_codex_ollama.ps1").read_text(encoding="utf-8")

    assert "AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL" in text
    assert "AGENT_WORKBENCH_PROVIDER_HEADERS_FILE" in text
    assert "agent_workbench_ollama" in text
    assert "CodexArgsBase64" in text
    assert "config.toml" in text
    assert "agent_workbench_ollama_" in text
    assert "config_file" in text
    assert "fresh01x" not in text
    assert "AW_CF_CLIENT_SECRET" in text
