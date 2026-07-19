"""Caller-driven native delivery bridge for one run-scoped journal.

The bridge only coordinates persistence and an already-bound adapter.  It does
not create sessions, start watchers, wake agents, or select providers/models.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from .p117_session_adapter import (
    DeliveryState,
    NativeSessionAdapter,
    SendReceipt,
    SessionBinding,
)


class DeliveryJournal(Protocol):
    def append(self, kind: str, **fields: object) -> object: ...


@dataclass(frozen=True)
class DeliveryResult:
    receipt: SendReceipt
    reconciled: bool


@dataclass(frozen=True)
class NativeSendRequest:
    """Exact request for the coordinator's native ``send_input`` call."""

    target_worker_session_id: str
    message: str
    idempotency_key: str
    message_fingerprint: str
    lineage: dict[str, str]


@dataclass(frozen=True)
class PreparedDelivery:
    request: NativeSendRequest
    receipt: SendReceipt | None = None


class NativeDeliveryBridge:
    """Persist an intent, perform one native call, then persist its receipt."""

    def __init__(self, *, adapter: NativeSessionAdapter, journal: DeliveryJournal, binding: SessionBinding) -> None:
        self.adapter = adapter
        self.journal = journal
        self.binding = binding

    def prepare(self, message: str, *, idempotency_key: str) -> PreparedDelivery:
        """Persist intent and return a request; never invokes a host tool."""
        fingerprint = sha256(message.encode("utf-8")).hexdigest()
        lineage = self.binding.__dict__.copy()
        request = NativeSendRequest(self.binding.session_id, message, idempotency_key, fingerprint, lineage)
        prior = [r for r in self.journal.records()
                 if r.get("idempotency_key") == idempotency_key
                 and r.get("kind") in {"delivery_intent", "native_receipt", "native_receipt_reconciled"}]
        for record in prior:
            if (record.get("lineage") != lineage or
                    record.get("target_worker_session_id") != self.binding.session_id or
                    record.get("message_fingerprint") != fingerprint):
                raise ValueError("durable receipt identity mismatch")
        receipt_record = next((r for r in reversed(prior) if r.get("kind") == "native_receipt"), None)
        if receipt_record:
            receipt = SendReceipt(
                self.binding, idempotency_key, DeliveryState(receipt_record["adapter_state"]),
                fingerprint, submission_id=receipt_record["submission_id"])
            self.journal.append("native_receipt_reconciled", operation="multi_agent_v1__send_input",
                                target_worker_session_id=self.binding.session_id,
                                idempotency_key=idempotency_key, message_fingerprint=fingerprint,
                                submission_id=receipt.submission_id, adapter_state=receipt.state.value,
                                reconciled=True, lineage=lineage)
            return PreparedDelivery(request, receipt)
        if not any(r.get("kind") == "delivery_intent" for r in prior):
            self.journal.append("delivery_intent", operation="multi_agent_v1__send_input",
                                target_worker_session_id=self.binding.session_id,
                                idempotency_key=idempotency_key, message_fingerprint=fingerprint,
                                lineage=lineage)
        return PreparedDelivery(request)

    def record_submission(self, request: NativeSendRequest, submission_id: str) -> SendReceipt:
        """Record the ID returned by the coordinator's actual native tool call."""
        if not submission_id:
            raise ValueError("native submission_id is required")
        expected = self.prepare(request.message, idempotency_key=request.idempotency_key).request
        if expected != request:
            raise ValueError("native send request identity mismatch")
        receipt = SendReceipt(self.binding, request.idempotency_key, DeliveryState.DELIVERED,
                              request.message_fingerprint, submission_id=submission_id)
        self.journal.append("native_receipt", operation="multi_agent_v1__send_input",
                            target_worker_session_id=request.target_worker_session_id,
                            submission_id=submission_id, idempotency_key=request.idempotency_key,
                            adapter_state=receipt.state.value, message_fingerprint=request.message_fingerprint,
                            reconciled=False, lineage=request.lineage)
        return receipt

    def deliver(self, message: str, *, idempotency_key: str) -> DeliveryResult:
        fingerprint = sha256(message.encode("utf-8")).hexdigest()
        lineage = self.binding.__dict__.copy()
        prior_records = [r for r in self.journal.records()
                         if r.get("idempotency_key") == idempotency_key
                         and r.get("kind") in {"delivery_intent", "native_receipt", "native_receipt_reconciled"}]
        for prior in prior_records:
            if (prior.get("lineage") != lineage or
                    prior.get("target_worker_session_id") != self.binding.session_id or
                    prior.get("message_fingerprint") != fingerprint):
                raise ValueError("durable receipt identity mismatch")
        self.journal.append(
            "delivery_intent", operation="multi_agent_v1__send_input",
            target_worker_session_id=self.binding.session_id,
            idempotency_key=idempotency_key, message_fingerprint=fingerprint,
            lineage=lineage,
        )
        prior_receipt = next((r for r in reversed(prior_records) if r.get("kind") == "native_receipt"), None)
        if prior_receipt is not None:
            receipt = SendReceipt(self.binding, idempotency_key,
                                  DeliveryState(prior_receipt["adapter_state"]), fingerprint,
                                  submission_id=prior_receipt["submission_id"])
            self.journal.append("native_receipt_reconciled", operation="multi_agent_v1__send_input",
                                target_worker_session_id=self.binding.session_id, idempotency_key=idempotency_key,
                                message_fingerprint=fingerprint, submission_id=receipt.submission_id,
                                adapter_state=receipt.state.value, lineage=lineage)
            return DeliveryResult(receipt, True)
        prior = self.adapter.lookup(self.binding, idempotency_key=idempotency_key)
        if prior.found:
            receipt = SendReceipt(self.binding, idempotency_key, prior.state or DeliveryState.PAUSED_RECONCILIATION, fingerprint)
            reconciled = True
        else:
            receipt = self.adapter.send(self.binding, message, idempotency_key=idempotency_key)
            reconciled = False
        self.journal.append(
            "native_receipt",
            operation="multi_agent_v1__send_input",
            target_worker_session_id=self.binding.session_id,
            submission_id=receipt.submission_id,
            idempotency_key=idempotency_key,
            adapter_state=receipt.state.value,
            message_fingerprint=receipt.message_fingerprint,
            reconciled=reconciled,
            lineage=self.binding.__dict__,
        )
        return DeliveryResult(receipt, reconciled)
