from __future__ import annotations

from pathlib import Path


def test_persistent_worker_host_is_runtime_only_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "native_codex_app_server_worker.py").read_text(encoding="utf-8")

    assert '"windowsSandbox/readiness"' in text
    assert '"approvalPolicy": "never"' in text
    assert '"sandbox": "read-only"' in text
    assert 'root = (repo_root / "runtime" / "agent_jobs").resolve()' in text
    assert 'parser.add_argument("--serve"' in text
    assert 'parser.add_argument("--stream-events"' in text
    assert "idle_timeout_seconds" in text
    assert "server.next_message(timeout_seconds=idle_timeout_seconds)" in text
    assert "output_path.write_text" in text
