from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from agent_workbench.p117_daemon import BoundedSupervisionDaemon
from agent_workbench.p117_session_adapter import CallerDrivenNativeSessionAdapter, FakeNativeSessionAdapter, SessionBinding
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


def test_restart_reconciles_recorded_flush_without_resending(tmp_path: Path):
    daemon, adapter = make_daemon(tmp_path)
    assert daemon.accept_event(event(), now=NOW)
    assert daemon.flush(now=NOW).accepted
    restarted = BoundedSupervisionDaemon(
        lease=daemon.lease,
        journal=SupervisionJournal(tmp_path / "journal.jsonl", root=tmp_path, run_id="run-117"),
        adapter=FakeNativeSessionAdapter(daemon.binding),
        binding=daemon.binding,
    )
    assert restarted.flush(now=NOW).reason == "bundle_already_selected"
    assert len(adapter.messages) == 1


def test_restart_preserves_unknown_delivery_as_fail_closed(tmp_path: Path):
    daemon, _adapter = make_daemon(tmp_path)
    assert daemon.accept_event(event(), now=NOW)
    uncertain = FakeNativeSessionAdapter(daemon.binding, uncertain_delivery=True)
    paused = BoundedSupervisionDaemon(
        lease=daemon.lease,
        journal=SupervisionJournal(tmp_path / "journal.jsonl", root=tmp_path, run_id="run-117"),
        adapter=uncertain,
        binding=daemon.binding,
    )
    assert paused.flush(now=NOW).reason == "paused_reconciliation"
    restarted = BoundedSupervisionDaemon(
        lease=daemon.lease,
        journal=SupervisionJournal(tmp_path / "journal.jsonl", root=tmp_path, run_id="run-117"),
        adapter=FakeNativeSessionAdapter(daemon.binding),
        binding=daemon.binding,
    )
    assert restarted.flush(now=NOW).reason == "paused_reconciliation"
    kinds = [record["kind"] for record in restarted.journal.records()]
    assert "flush_request" in kinds and "delivery_intent" in kinds and "native_receipt" in kinds


def test_closed_run_writes_post_close_rejection_receipt(tmp_path: Path):
    daemon, _adapter = make_daemon(tmp_path)
    daemon.close()
    assert not daemon.accept_event(event(), now=NOW)
    assert not daemon.flush(now=NOW).accepted
    assert all(record.get("reason") == "closed" for record in daemon.journal.records() if record.get("kind") == "rejection")


def test_caller_driven_flush_prepare_and_submission(tmp_path: Path):
    daemon, _ = make_daemon(tmp_path)
    daemon.adapter = CallerDrivenNativeSessionAdapter(lambda *_: pytest.fail("daemon must not send"))
    daemon.delivery.adapter = daemon.adapter
    assert daemon.accept_event(event(), now=NOW)
    request = daemon.prepare_flush(now=NOW)
    assert request is not None
    assert request.target_worker_session_id == daemon.binding.session_id
    assert request.idempotency_key == "run-117:1-1"
    result = daemon.record_flush_submission(request, "sub-daemon-1")
    assert result.accepted
    assert [r["kind"] for r in daemon.journal.records() if r["kind"] in {"native_receipt", "flush_receipt", "cursor_receipt"}] == ["native_receipt", "flush_receipt", "cursor_receipt"]


def test_caller_driven_restart_completes_cursor_without_second_request(tmp_path: Path):
    daemon, _ = make_daemon(tmp_path)
    assert daemon.accept_event(event(), now=NOW)
    request = daemon.prepare_flush(now=NOW)
    assert request is not None
    daemon.delivery.record_submission(request, "sub-daemon-2")
    restarted, _ = make_daemon(tmp_path)
    reconciled = restarted.prepare_flush(now=NOW)
    assert reconciled is None
    assert restarted.journal.records()[-1]["kind"] == "cursor_receipt"
    assert restarted._acknowledged_sequence == 1
    records = restarted.journal.records()
    assert sum(r["kind"] == "flush_request" for r in records) == 1
    assert sum(r["kind"] == "delivery_intent" for r in records) == 1
    reconciled = [r for r in records if r["kind"] == "native_receipt_reconciled"]
    assert len(reconciled) == 1
    assert reconciled[0]["target_worker_session_id"] == daemon.binding.session_id
    assert reconciled[0]["submission_id"] == "sub-daemon-2"
    assert reconciled[0]["reconciled"] is True
