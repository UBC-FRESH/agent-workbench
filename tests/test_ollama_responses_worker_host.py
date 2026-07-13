from __future__ import annotations

from pathlib import Path


def test_responses_worker_host_is_runtime_only_and_non_streaming() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "ollama_responses_worker_host.py").read_text(encoding="utf-8")

    assert 'base_url + "/responses"' in text
    assert '"stream": False' in text
    assert 'root = (repo_root / "runtime" / "agent_jobs").resolve()' in text
    assert '"event": "worker_request_started"' in text
    assert 'parser.add_argument("--serve"' in text
    assert "fresh01x.01101.dev" not in text
