from __future__ import annotations

from pathlib import Path


def test_sandbox_helper_requires_explicit_setup() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "native_codex_app_server_sandbox.py").read_text(encoding="utf-8")

    assert '"windowsSandbox/readiness"' in text
    assert '"windowsSandbox/setupStart"' in text
    assert 'action="store_true"' in text
    assert "if args.setup and before" in text
    assert '"codex",' in text
    assert '"app-server",' in text
    assert '"--stdio",' in text
    assert 'default_permissions="agent_workbench_ollama_readonly"' in text
