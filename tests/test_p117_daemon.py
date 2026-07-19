from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_workbench.p117_daemon import BoundedSupervisionDaemon
from agent_workbench.p117_session_adapter import FakeNativeSessionAdapter, SessionBinding
from agent_workbench.supervision import SupervisionJournal, create_run_lease


NOW = datetime(2026, 7, 18, 12, tzinfo=timezone.utc)


def make_daemon(tmp_path: Path):
    lease = create_run_lease(run_id="run-117", worker_id="worker-117", supervisor_id="supervisor-117", root=tmp_path, expires_at=NOW + timedelta(minutes=1))
    binding = SessionBinding("run-117", "worker-117", "supervisor-117", "session-117")
    adapter = FakeNativeSessionAdapter(binding)
    daemon = BoundedSupervisionDaemon(lease=lease, journal=SupervisionJournal(tmp_path / "journal.jsonl", root=tmp_path, run_id="run-117"), adapter=adapter, binding=binding)
    return daemon, adapter


def event(sequence=1, *, run_id="run-117", kind="terminal", outcome="terminal"):
    return {"run_id": run_id, "sequence": sequence, "timestamp": NOW.isoformat(), "kind": kind, "outcome": outcome, "stage": "proof"}


def test_accepts_eligible_event_selects_one_bundle_and_closes(tmp_path: Path):
    daemon, adapter = make_daemon(tmp_path)
    assert daemon.accept_event(event(), now=NOW)
    result = daemon.flush(now=NOW)
    assert result.accepted and result.decision is not None
    assert len(adapter.messages) == 1
    assert not daemon.flush(now=NOW).accepted
    daemon.close()
    assert daemon.journal.state() == "closed"
    assert not daemon.accept_event(event(2), now=NOW)


def test_rejects_wrong_run_and_expired_events(tmp_path: Path):
    daemon, _adapter = make_daemon(tmp_path)
    assert not daemon.accept_event(event(run_id="other-run"), now=NOW)
    assert not daemon.accept_event(event(), now=NOW + timedelta(minutes=2))

