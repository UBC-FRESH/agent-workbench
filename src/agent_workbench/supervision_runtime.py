"""Event-driven P116 controller for one host-owned Agent Hub run.

The runtime contains no provider calls.  A concrete host adapter must own the
three live session handles, push sanitized Worker events through the supplied
callback, re-invoke the Supervisor and Coordinator, and return a durable
receipt when it sends a message to the Worker.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

from .supervision import SCHEMA_VERSION, validate_events
from .supervision_controller import acknowledge_cursor, load_manifest, prepare_review_delta
from .supervision_review import build_supervisor_review_request, validate_delta_review_packet


@dataclass(frozen=True)
class SessionLineage:
    """The three exact sessions the host owns for one controller run."""

    worker_session_id: str
    supervisor_session_id: str
    coordinator_session_id: str


@dataclass(frozen=True)
class CoordinatorAssessment:
    """Coordinator-owned normalized recommendation for one Supervisor advisory."""

    packet: dict[str, Any]
    decision: str


class HostAdapter(Protocol):
    """Live host boundary; implementations must push events rather than poll."""

    def start_run(self, manifest: dict[str, Any]) -> SessionLineage: ...

    def subscribe_worker(
        self, worker_session_id: str, on_event: Callable[[dict[str, Any]], None]
    ) -> None: ...

    def resume_session(self, session_id: str) -> None: ...

    def invoke_supervisor(self, supervisor_session_id: str, request: dict[str, Any]) -> str: ...

    def invoke_coordinator(
        self, coordinator_session_id: str, advisory: str, delta: dict[str, Any], ticket_boundary: str
    ) -> CoordinatorAssessment: ...

    def send_worker(self, worker_session_id: str, message: str, *, idempotency_key: str) -> str: ...

    def close_run(self) -> None: ...


class ControllerRuntime:
    """One bounded event-to-action loop bound to one manifest and host lineage."""

    def __init__(self, *, manifest_path: Path, host: HostAdapter, ticket_boundary: str) -> None:
        self.manifest_path = manifest_path
        self.host = host
        self.ticket_boundary = ticket_boundary
        self.manifest, self.root = load_manifest(manifest_path)
        for field in ("worker_session_id", "supervisor_session_id", "coordinator_session_id"):
            if not self.manifest.get(field):
                raise ValueError("manifest must be persisted with all session IDs before starting")
        self.lineage: SessionLineage | None = None

    @classmethod
    def bootstrap(cls, *, manifest_path: Path, host: HostAdapter, ticket_boundary: str) -> "ControllerRuntime":
        """Create host threads, persist exact IDs, then load the runtime."""
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        lineage = host.start_run(manifest)
        fields = {"worker_session_id": lineage.worker_session_id, "supervisor_session_id": lineage.supervisor_session_id, "coordinator_session_id": lineage.coordinator_session_id}
        for field, value in fields.items():
            if manifest.get(field) and manifest[field] != value:
                raise ValueError(f"manifest {field} conflicts with host-created thread")
        manifest.update(fields)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return cls(manifest_path=manifest_path, host=host, ticket_boundary=ticket_boundary)

    def start(self) -> SessionLineage:
        if self.lineage is not None:
            return self.lineage
        lineage = self.host.start_run(self.manifest)
        if lineage.worker_session_id != self.manifest["worker_session_id"]:
            raise ValueError("host Worker session does not match manifest")
        if lineage.supervisor_session_id != self.manifest["supervisor_session_id"]:
            raise ValueError("host Supervisor session does not match manifest")
        if not lineage.coordinator_session_id:
            raise ValueError("host must provide a Coordinator session")
        self.host.subscribe_worker(lineage.worker_session_id, self.on_worker_event)
        self.lineage = lineage
        return lineage

    def on_worker_event(self, event: dict[str, Any]) -> None:
        """Accept one already-sanitized host event and act only on meaningful deltas."""
        if self.lineage is None:
            raise RuntimeError("controller must be started before it receives Worker events")
        if event.get("run_id") != self.manifest["run_id"]:
            raise ValueError("Worker event run_id does not match manifest")
        self._append_event(event)
        delta, _maximum = prepare_review_delta(manifest_path=self.manifest_path)
        if not delta["event_count"] or not _requires_review(delta):
            return
        request = build_supervisor_review_request(
            delta, ticket_boundary=self.ticket_boundary, manifest=self.manifest
        )
        self.host.resume_session(self.lineage.supervisor_session_id)
        advisory = self.host.invoke_supervisor(self.lineage.supervisor_session_id, request)
        if not isinstance(advisory, str) or not advisory.strip():
            raise ValueError("Supervisor returned no advisory assessment")
        assessment = self.host.invoke_coordinator(
            self.lineage.coordinator_session_id, advisory, delta, self.ticket_boundary
        )
        if not isinstance(assessment, CoordinatorAssessment):
            raise ValueError("Coordinator returned no normalized assessment")
        packet, decision = assessment.packet, assessment.decision
        packet_result = validate_delta_review_packet(
            packet, delta=delta, ticket_boundary=self.ticket_boundary, manifest=self.manifest
        )
        if not packet_result.ok:
            raise ValueError("invalid Coordinator packet: " + "; ".join(packet_result.errors))
        if decision not in {"continue", "nudge", "escalate", "terminal"}:
            raise ValueError("Coordinator returned an unsupported decision")
        if decision == "nudge" and packet.get("nudge") is None:
            raise ValueError("Coordinator nudge requires a validated Supervisor nudge")
        action: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.manifest["run_id"],
            "packet_sha256": _packet_digest(packet),
            "decision": decision,
        }
        if decision == "nudge":
            key = f"{self.manifest['run_id']}:{packet['event_start_sequence']}-{packet['event_end_sequence']}"
            self.host.resume_session(self.lineage.worker_session_id)
            receipt = self.host.send_worker(
                self.lineage.worker_session_id, _render_nudge(packet["nudge"]), idempotency_key=key
            )
            if not receipt:
                raise RuntimeError("Worker delivery returned no receipt")
            action["worker_session_id"] = self.lineage.worker_session_id
            action["delivery_receipt"] = receipt
        acknowledge_cursor(
            manifest_path=self.manifest_path,
            last_sequence=int(packet["event_end_sequence"]),
            packet=packet,
            action=action,
        )

    def close(self) -> None:
        self.host.close_run()
        self.lineage = None

    def _append_event(self, event: dict[str, Any]) -> None:
        events_path = self.root / self.manifest["events_path"]
        existing = _read_events(events_path)
        result = validate_events([*existing, event], assigned_root=self.root)
        if not result.ok:
            raise ValueError("invalid Worker event: " + "; ".join(result.errors))
        events_path.parent.mkdir(parents=True, exist_ok=True)
        with events_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def _requires_review(delta: dict[str, Any]) -> bool:
    return any(
        event.get("kind") in {"tool_failed", "workspace_mismatch", "terminal"}
        or event.get("kind") == "stage_transition" and event.get("stage") == "validation"
        for event in delta["events"]
    )


def _render_nudge(nudge: dict[str, Any]) -> str:
    return "\n".join(
        str(nudge[field])
        for field in ("observed_fact", "relevant_feedback", "validation_seam", "ticket_boundary")
    )


def _packet_digest(packet: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
