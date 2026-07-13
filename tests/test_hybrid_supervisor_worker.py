from __future__ import annotations

from pathlib import Path


def test_hybrid_proof_uses_restricted_supervisor_ticket_authorship() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "run_hybrid_supervisor_worker.py").read_text(encoding="utf-8")

    assert "Supervisor-owned ticket authorship" in text
    assert '"type": "workspaceWrite"' in text
    assert '"writableRoots": [str(run_dir)]' in text
    assert '"type": "readOnly"' in text
    assert '"approvalPolicy": "never"' in text
    assert "supervisor_evidence.json" in text
