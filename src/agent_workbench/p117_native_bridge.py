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


class NativeDeliveryBridge:
    """Persist an intent, perform one native call, then persist its receipt."""

    def __init__(self, *, adapter: NativeSessionAdapter, journal: DeliveryJournal, binding: SessionBinding) -> None:
        self.adapter = adapter
        self.journal = journal
        self.binding = binding

    def deliver(self, message: str, *, idempotency_key: str) -> DeliveryResult:
        fingerprint = sha256(message.encode("utf-8")).hexdigest()
        self.journal.append("delivery_intent", idempotency_key=idempotency_key, message_fingerprint=fingerprint, lineage=self.binding.__dict__)
        prior = self.adapter.lookup(self.binding, idempotency_key=idempotency_key)
        if prior.found:
            receipt = SendReceipt(self.binding, idempotency_key, prior.state or DeliveryState.PAUSED_RECONCILIATION, fingerprint)
            reconciled = True
        else:
            receipt = self.adapter.send(self.binding, message, idempotency_key=idempotency_key)
            reconciled = False
        self.journal.append(
            "native_receipt",
            idempotency_key=idempotency_key,
            adapter_state=receipt.state.value,
            message_fingerprint=receipt.message_fingerprint,
            reconciled=reconciled,
            lineage=self.binding.__dict__,
        )
        return DeliveryResult(receipt, reconciled)
