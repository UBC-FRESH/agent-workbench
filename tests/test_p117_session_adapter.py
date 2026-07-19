import pytest

from agent_workbench.p117_session_adapter import (
    DeliveryState,
    FakeNativeSessionAdapter,
    SessionBinding,
)


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
