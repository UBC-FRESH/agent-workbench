from __future__ import annotations

from pathlib import Path


def test_serial_supervisor_worker_is_explicitly_coordinator_relayed() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "run_ollama_serial_supervisor_worker.py").read_text(encoding="utf-8")

    assert "The Coordinator owns transport between serial turns" in text
    assert 'base_url + "/responses"' in text
    assert "P102_SERIAL_SUPERVISOR_DISPATCH" in text
    assert "P102_SERIAL_WORKER_RESULT" in text
    assert "P102_SERIAL_SUPERVISOR_VERIFIED" in text
    assert '"stream": False' in text
