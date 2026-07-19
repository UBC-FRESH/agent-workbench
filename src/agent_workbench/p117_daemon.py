"""Bounded, event-driven harness for one run-scoped supervision proof.

This is intentionally a caller-driven state machine.  It has no loop, clock
reads, host bridge, or agent invocation; callers provide events and call
``flush``/``close`` explicitly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .p117_flush_policy import FlushDecision, choose_flush
from .p117_session_adapter import NativeSessionAdapter, SessionBinding
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
        self._events: list[dict[str, Any]] = []
        self._acknowledged_sequence = 0
        self._flushed = False

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)

    def accept_event(self, event: dict[str, Any], *, now: datetime) -> bool:
        """Accept an event only while this lease is eligible."""
        if not self.lease.capture_eligible(run_id=event.get("run_id", self.lease.run_id), now=now):
            return False
        if self._flushed or any(item.get("sequence") == event.get("sequence") for item in self._events):
            return False
        self._events.append(dict(event))
        self._events.sort(key=lambda item: int(item["sequence"]))
        if self.journal.state() == "armed":
            self.journal.transition("capturing")
        return True

    def flush(self, *, now: datetime) -> DaemonResult:
        if not self.lease.capture_eligible(run_id=self.lease.run_id, now=now):
            return DaemonResult(False, "lease_inactive")
        if self._flushed:
            return DaemonResult(False, "bundle_already_selected")
        decision = choose_flush(self._events, acknowledged_sequence=self._acknowledged_sequence, now=now, lease=self.lease, run_id=self.lease.run_id, expected_root=self.lease.root)
        if not decision.flush:
            return DaemonResult(False, decision.reason, decision)
        message = json.dumps(list(decision.events), sort_keys=True, separators=(",", ":"))
        receipt = self.adapter.send(self.binding, message, idempotency_key=f"{self.lease.run_id}:{decision.start_sequence}-{decision.end_sequence}")
        if receipt.state.value == "paused_reconciliation":
            self.journal.transition("paused_reconciliation", delivery_uncertain=True)
            return DaemonResult(False, "paused_reconciliation", decision)
        self._acknowledged_sequence = decision.end_sequence or self._acknowledged_sequence
        self._flushed = True
        return DaemonResult(True, decision.reason, decision)

    def close(self) -> None:
        if self.journal.state() != "closed":
            self.journal.transition("closed")
        self.lease = self.lease.close()

