import pytest

from agent_workbench.p117_session_adapter import (
    DeliveryState,
    FakeNativeSessionAdapter,
    SessionBinding,
)
from agent_workbench.p117_native_bridge import NativeDeliveryBridge
from agent_workbench.supervision import SupervisionJournal


@pytest.fixture
def binding() -> SessionBinding:
    return SessionBinding("run-117", "worker-1", "supervisor-1", "native-session-1")


def test_inspect_resume_send_lookup_are_bound_and_typed(binding):
    adapter = FakeNativeSessionAdapter(binding)
    assert adapter.inspect(binding, idempotency_key="inspect-1").cursor == "cursor-0"
    assert adapter.resume(binding, idempotency_key="resume-1").status == "resumed"
    sent = adapter.send(binding, "continue", idempotency_key="send-1")
    assert sent.state is DeliveryState.DELIVERED
    found = adapter.lookup(binding, idempotency_key="send-1")
    assert found.found and found.state is DeliveryState.DELIVERED


def test_binding_mismatch_fails_closed(binding):
    adapter = FakeNativeSessionAdapter(binding)
    other = SessionBinding("other-run", binding.worker_id, binding.supervisor_id, binding.session_id)
    with pytest.raises(ValueError, match="binding"):
        adapter.send(other, "continue", idempotency_key="send-1")


def test_send_idempotency_does_not_duplicate_message(binding):
    adapter = FakeNativeSessionAdapter(binding)
    first = adapter.send(binding, "continue", idempotency_key="same-key")
    second = adapter.send(binding, "continue", idempotency_key="same-key")
    assert first == second
    assert adapter.messages == ["continue"]


def test_uncertain_delivery_pauses_reconciliation_and_is_lookupable(binding):
    adapter = FakeNativeSessionAdapter(binding, uncertain_delivery=True)
    receipt = adapter.send(binding, "nudge", idempotency_key="uncertain-1")
    assert receipt.state is DeliveryState.PAUSED_RECONCILIATION
    assert adapter.messages == []
    assert adapter.lookup(binding, idempotency_key="uncertain-1").state is DeliveryState.PAUSED_RECONCILIATION


def test_native_bridge_persists_intent_before_send_and_receipt_after(tmp_path, binding):
    journal = SupervisionJournal(tmp_path / "journal.jsonl", root=tmp_path, run_id=binding.run_id)
    adapter = FakeNativeSessionAdapter(binding)
    bridge = NativeDeliveryBridge(adapter=adapter, journal=journal, binding=binding)

    result = bridge.deliver("continue", idempotency_key="delivery-1")

    assert result.receipt.state is DeliveryState.DELIVERED
    assert not result.reconciled
    assert [record["kind"] for record in journal.records()] == ["delivery_intent", "native_receipt"]
    assert journal.records()[0]["message_fingerprint"] == journal.records()[1]["message_fingerprint"]


def test_native_bridge_reconciles_persisted_intent_without_duplicate_send(tmp_path, binding):
    journal = SupervisionJournal(tmp_path / "journal.jsonl", root=tmp_path, run_id=binding.run_id)
    adapter = FakeNativeSessionAdapter(binding)
    first = NativeDeliveryBridge(adapter=adapter, journal=journal, binding=binding)
    first.deliver("continue", idempotency_key="delivery-1")
    second = NativeDeliveryBridge(adapter=adapter, journal=journal, binding=binding)

    result = second.deliver("continue", idempotency_key="delivery-1")

    assert result.reconciled
    assert adapter.messages == ["continue"]
