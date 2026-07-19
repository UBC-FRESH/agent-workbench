"""Bounded, event-driven harness for one run-scoped supervision proof.

This is intentionally a caller-driven state machine.  It has no loop, clock
reads, host bridge, or agent invocation; callers provide events and call
``flush``/``close`` explicitly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any

from .p117_flush_policy import FlushDecision, choose_flush
from .p117_session_adapter import NativeSessionAdapter, SendReceipt, SessionBinding
from .supervision import RunLease, SupervisionJournal


@dataclass(frozen=True)
class DaemonResult:
    accepted: bool
    reason: str
    decision: FlushDecision | None = None


class BoundedSupervisionDaemon:
    """Drive at most one explicitly requested bundle for one leased run."""

    def __init__(
        self,
        *,
        lease: RunLease,
        journal: SupervisionJournal,
        adapter: NativeSessionAdapter,
        binding: SessionBinding,
    ) -> None:
        if binding.run_id != lease.run_id or binding.worker_id != lease.worker_id or binding.supervisor_id != lease.supervisor_id:
            raise ValueError("session binding does not match lease lineage")
        self.lease = lease
        self.journal = journal
        self.adapter = adapter
        self.binding = binding
        records = journal.records()
        for record in records:
            if record.get("run_id") != lease.run_id:
                raise ValueError("journal record does not match lease run")
        lineage = next((r for r in records if r.get("kind") == "lease"), None)
        if lineage is not None and lineage.get("lineage") != binding.__dict__:
            raise ValueError("journal lease lineage does not match session binding")
        if lineage is None:
            journal.append("lease", lease={"run_id": lease.run_id, "worker_id": lease.worker_id, "supervisor_id": lease.supervisor_id, "root": str(lease.root), "expires_at": lease.expires_at.isoformat()}, lineage=binding.__dict__)
        self._events = [r["event"] for r in records if r.get("kind") == "event"]
        self._acknowledged_sequence = max((r.get("cursor", 0) for r in records if r.get("kind") in {"cursor_receipt", "flush_receipt"}), default=0)
        self._flushed = any(
            r.get("kind") in {"cursor_receipt", "flush_receipt"}
            and r.get("adapter_state") in {"delivered", "already_applied"}
            for r in records
        )

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)

    def accept_event(self, event: dict[str, Any], *, now: datetime) -> bool:
        """Accept an event only while this lease is eligible."""
        if self.journal.state() == "closed":
            self.journal.append("rejection", operation="event", reason="closed", event=event)
            return False
        if self.journal.state() == "paused_reconciliation":
            self.journal.append("rejection", operation="event", reason="paused_reconciliation", event=event)
            return False
        if not self.lease.capture_eligible(run_id=event.get("run_id", self.lease.run_id), now=now):
            self.journal.append("rejection", operation="event", reason="lease_inactive", event=event)
            return False
        if self._flushed or any(item.get("sequence") == event.get("sequence") for item in self._events):
            return False
        self._events.append(dict(event))
        self._events.sort(key=lambda item: int(item["sequence"]))
        self.journal.append("event", event=dict(event))
        if self.journal.state() == "armed":
            self.journal.transition("capturing")
        return True

    def flush(self, *, now: datetime) -> DaemonResult:
        if self.journal.state() == "closed":
            self.journal.append("rejection", operation="flush", reason="closed")
            return DaemonResult(False, "closed")
        if self.journal.state() == "paused_reconciliation":
            return DaemonResult(False, "paused_reconciliation")
        if not self.lease.capture_eligible(run_id=self.lease.run_id, now=now):
            self.journal.append("rejection", operation="flush", reason="lease_inactive")
            return DaemonResult(False, "lease_inactive")
        if self._flushed:
            return DaemonResult(False, "bundle_already_selected")
        decision = choose_flush(self._events, acknowledged_sequence=self._acknowledged_sequence, now=now, lease=self.lease, run_id=self.lease.run_id, expected_root=self.lease.root)
        if not decision.flush:
            return DaemonResult(False, decision.reason, decision)
        message = json.dumps(list(decision.events), sort_keys=True, separators=(",", ":"))
        key = f"{self.lease.run_id}:{decision.start_sequence}-{decision.end_sequence}"
        self.journal.append(
            "flush_request",
            flush_start=decision.start_sequence,
            flush_end=decision.end_sequence,
            idempotency_key=key,
            message_fingerprint=sha256(message.encode("utf-8")).hexdigest(),
        )
        self.journal.append("delivery_intent", idempotency_key=key, flush_start=decision.start_sequence, flush_end=decision.end_sequence)
        prior = self.adapter.lookup(self.binding, idempotency_key=key)
        if prior.found:
            receipt = SendReceipt(self.binding, key, prior.state, "recorded")
        else:
            receipt = self.adapter.send(self.binding, message, idempotency_key=key)
        self.journal.append(
            "native_receipt",
            idempotency_key=key,
            adapter_state=receipt.state.value,
            message_fingerprint=receipt.message_fingerprint,
            reconciled=bool(prior.found),
        )
        self.journal.append("flush_receipt", cursor=decision.end_sequence, flush_start=decision.start_sequence, flush_end=decision.end_sequence, idempotency_key=key, lineage=self.binding.__dict__, adapter_state=receipt.state.value, message_fingerprint=receipt.message_fingerprint)
        if receipt.state.value == "paused_reconciliation":
            self.journal.transition("paused_reconciliation", delivery_uncertain=True)
            return DaemonResult(False, "paused_reconciliation", decision)
        self._acknowledged_sequence = decision.end_sequence or self._acknowledged_sequence
        self.journal.append("cursor_receipt", cursor=self._acknowledged_sequence, flush_start=decision.start_sequence, flush_end=decision.end_sequence, idempotency_key=key, adapter_state=receipt.state.value)
        self._flushed = True
        return DaemonResult(True, decision.reason, decision)

    def close(self) -> None:
        if self.journal.state() != "closed":
            self.journal.transition("closed")
            self.journal.append("closure", lineage=self.binding.__dict__)
        self.lease = self.lease.close()
