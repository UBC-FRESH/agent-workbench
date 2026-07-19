"""Run-scoped protocol for the proven native inspect/resume/send surface.

This module is deliberately an adapter boundary: it does not start hosts,
watch for events, invoke agents, or select providers/models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Callable, Protocol


class DeliveryState(StrEnum):
    DELIVERED = "delivered"
    ALREADY_APPLIED = "already_applied"
    PAUSED_RECONCILIATION = "paused_reconciliation"


@dataclass(frozen=True)
class SessionBinding:
    run_id: str
    worker_id: str
    supervisor_id: str
    session_id: str


@dataclass(frozen=True)
class InspectReceipt:
    binding: SessionBinding
    idempotency_key: str
    status: str
    cursor: str | None


@dataclass(frozen=True)
class ResumeReceipt:
    binding: SessionBinding
    idempotency_key: str
    status: str


@dataclass(frozen=True)
class SendReceipt:
    binding: SessionBinding
    idempotency_key: str
    state: DeliveryState
    message_fingerprint: str
    operation: str = "multi_agent_v1__send_input"
    submission_id: str = ""


@dataclass(frozen=True)
class LookupReceipt:
    binding: SessionBinding
    idempotency_key: str
    found: bool
    state: DeliveryState | None


class NativeSessionAdapter(Protocol):
    """Permitted operations against one already-bound native session."""

    def inspect(self, binding: SessionBinding, *, idempotency_key: str) -> InspectReceipt: ...

    def resume(self, binding: SessionBinding, *, idempotency_key: str) -> ResumeReceipt: ...

    def send(self, binding: SessionBinding, message: str, *, idempotency_key: str) -> SendReceipt: ...

    def lookup(self, binding: SessionBinding, *, idempotency_key: str) -> LookupReceipt: ...


class CallerDrivenNativeSessionAdapter:
    """Production boundary: the caller supplies the already-bound native tool call.

    Python does not discover or invoke host tools.  ``send_tool`` must be the
    coordinator's call to ``multi_agent_v1__send_input`` and return its literal
    submission identifier (or a mapping containing ``submission_id``).
    """

    def __init__(self, send_tool: Callable[[str, str, str], object]) -> None:
        self._send_tool = send_tool

    def inspect(self, binding: SessionBinding, *, idempotency_key: str) -> InspectReceipt:
        raise RuntimeError("caller must provide native inspect receipt")

    def resume(self, binding: SessionBinding, *, idempotency_key: str) -> ResumeReceipt:
        raise RuntimeError("caller must provide native resume receipt")

    def send(self, binding: SessionBinding, message: str, *, idempotency_key: str) -> SendReceipt:
        result = self._send_tool(binding.session_id, message, idempotency_key)
        submission_id = result.get("submission_id") if isinstance(result, dict) else str(result)
        if not submission_id:
            raise ValueError("multi_agent_v1__send_input returned no submission_id")
        return SendReceipt(
            binding, idempotency_key, DeliveryState.DELIVERED,
            sha256(message.encode("utf-8")).hexdigest(),
            submission_id=submission_id,
        )

    def lookup(self, binding: SessionBinding, *, idempotency_key: str) -> LookupReceipt:
        return LookupReceipt(binding, idempotency_key, False, None)


class FakeNativeSessionAdapter:
    """Test-only deterministic adapter; never use for native production delivery."""

    def __init__(self, binding: SessionBinding, *, uncertain_delivery: bool = False) -> None:
        self.binding = binding
        self.uncertain_delivery = uncertain_delivery
        self._receipts: dict[str, SendReceipt] = {}
        self.messages: list[str] = []
        self.resumed = False

    def _check(self, binding: SessionBinding) -> None:
        if binding != self.binding:
            raise ValueError("session binding does not match run/Worker/Supervisor lineage")

    def inspect(self, binding: SessionBinding, *, idempotency_key: str) -> InspectReceipt:
        self._check(binding)
        return InspectReceipt(binding, idempotency_key, "observed", "cursor-0")

    def resume(self, binding: SessionBinding, *, idempotency_key: str) -> ResumeReceipt:
        self._check(binding)
        self.resumed = True
        return ResumeReceipt(binding, idempotency_key, "resumed")

    def send(self, binding: SessionBinding, message: str, *, idempotency_key: str) -> SendReceipt:
        self._check(binding)
        prior = self._receipts.get(idempotency_key)
        if prior is not None:
            return prior
        if self.uncertain_delivery:
            receipt = SendReceipt(binding, idempotency_key, DeliveryState.PAUSED_RECONCILIATION, "unknown")
        else:
            self.messages.append(message)
            fingerprint = sha256(message.encode("utf-8")).hexdigest()
            receipt = SendReceipt(binding, idempotency_key, DeliveryState.DELIVERED, fingerprint)
        self._receipts[idempotency_key] = receipt
        return receipt

    def lookup(self, binding: SessionBinding, *, idempotency_key: str) -> LookupReceipt:
        self._check(binding)
        receipt = self._receipts.get(idempotency_key)
        return LookupReceipt(binding, idempotency_key, receipt is not None, receipt.state if receipt else None)
