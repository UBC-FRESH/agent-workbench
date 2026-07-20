from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pytest

from agent_workbench.supervision import SCHEMA_VERSION
from agent_workbench.supervision_runtime import CoordinatorAssessment, ControllerRuntime, SessionLineage


BOUNDARY = "Edit only src/example.py and run the declared unit test."


def event(sequence: int, *, kind: str = "tool_failed", stage: str = "validation") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "sequence": sequence,
        "event_id": f"event-{sequence}", "timestamp": "2026-07-20T00:00:00Z",
        "kind": kind, "stage": stage, "outcome": "failed" if kind == "tool_failed" else "succeeded",
        "redaction_applied": True, "run_id": "run-116", "hook_event": "host",
        "tool_name": "apply_patch", "root_match": True,
    }


def manifest_path(tmp_path: Path) -> Path:
    root = tmp_path / "run"
    supervision = root / "supervision"
    supervision.mkdir(parents=True)
    value = {
        "schema_version": SCHEMA_VERSION, "run_id": "run-116",
        "worker_session_id": "worker-116", "supervisor_session_id": "supervisor-116",
        "coordinator_session_id": "coordinator-116",
        "assigned_root": str(root), "supervision_dir": str(supervision),
        "events_path": "supervision/events.jsonl", "cursor_path": "supervision/cursor.json",
        "packets_path": "supervision/packets.jsonl", "actions_path": "supervision/actions.jsonl",
    }
    path = supervision / "manifest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class FakeHost:
    def __init__(self, *, worker: str = "worker-116") -> None:
        self.worker = worker
        self.callback: Callable[[dict[str, Any]], None] | None = None
        self.requests: list[dict[str, Any]] = []
        self.deliveries: list[tuple[str, str, str]] = []
        self.resumed: list[str] = []

    def start_run(self, _manifest: dict[str, Any]) -> SessionLineage:
        return SessionLineage(self.worker, "supervisor-116", "coordinator-116")

    def subscribe_worker(self, worker: str, callback: Callable[[dict[str, Any]], None]) -> None:
        assert worker == self.worker
        self.callback = callback

    def resume_session(self, session_id: str) -> None:
        self.resumed.append(session_id)

    def invoke_supervisor(self, _session: str, request: dict[str, Any]) -> str:
        self.requests.append(request)
        return "The validation failure needs one bounded repair cue."

    def invoke_coordinator(
        self, _session: str, advisory: str, delta: dict[str, Any], _boundary: str
    ) -> CoordinatorAssessment:
        assert advisory == "The validation failure needs one bounded repair cue."
        packet = {
            "schema_version": SCHEMA_VERSION, "run_id": "run-116",
            "event_start_sequence": delta["cursor_start_sequence"] + 1,
            "event_end_sequence": delta["cursor_end_sequence"],
            "classification": "material_repeat", "recommended_action": "nudge",
            "confidence": "medium",
            "evidence_citation": f"events:{delta['cursor_start_sequence'] + 1}-{delta['cursor_end_sequence']}",
            "evidence_summary": "The validation failure requires a bounded repair cue.",
            "nudge": {
                "observed_fact": "The declared validation failed.",
                "relevant_feedback": "The new event reports a failed validation stage.",
                "validation_seam": "The declared unit test remains the validation seam.",
                "ticket_boundary": BOUNDARY,
            },
        }
        return CoordinatorAssessment(packet=packet, decision="nudge")

    def send_worker(self, worker: str, message: str, *, idempotency_key: str) -> str:
        self.deliveries.append((worker, message, idempotency_key))
        return "receipt-116"

    def close_run(self) -> None:
        return None


def test_event_driven_nudge_reaches_exact_worker_and_acknowledges_cursor(tmp_path: Path) -> None:
    host = FakeHost()
    runtime = ControllerRuntime(manifest_path=manifest_path(tmp_path), host=host, ticket_boundary=BOUNDARY)
    runtime.start()
    assert host.callback is not None
    host.callback(event(1))
    assert len(host.requests) == 1
    assert len(host.deliveries) == 1
    assert host.resumed == ["supervisor-116", "worker-116"]
    worker, message, key = host.deliveries[0]
    assert worker == "worker-116" and key == "run-116:1-1"
    assert "The declared validation failed." in message
    action = json.loads((tmp_path / "run/supervision/actions.jsonl").read_text())
    assert action["decision"] == "nudge" and action["delivery_receipt"] == "receipt-116"
    assert json.loads((tmp_path / "run/supervision/cursor.json").read_text())["last_sequence"] == 1


def test_routine_progress_does_not_spend_a_supervisor_turn(tmp_path: Path) -> None:
    host = FakeHost()
    runtime = ControllerRuntime(manifest_path=manifest_path(tmp_path), host=host, ticket_boundary=BOUNDARY)
    runtime.start()
    assert host.callback is not None
    host.callback(event(1, kind="tool_completed", stage="implementation"))
    assert host.requests == [] and host.deliveries == []


def test_runtime_rejects_host_with_the_wrong_worker_identity(tmp_path: Path) -> None:
    runtime = ControllerRuntime(manifest_path=manifest_path(tmp_path), host=FakeHost(worker="other"), ticket_boundary=BOUNDARY)
    with pytest.raises(ValueError, match="Worker session"):
        runtime.start()


def test_delivery_failure_does_not_acknowledge_the_cursor(tmp_path: Path) -> None:
    class FailingHost(FakeHost):
        def send_worker(self, worker: str, message: str, *, idempotency_key: str) -> str:
            raise RuntimeError("delivery unavailable")

    host = FailingHost()
    runtime = ControllerRuntime(manifest_path=manifest_path(tmp_path), host=host, ticket_boundary=BOUNDARY)
    runtime.start()
    assert host.callback is not None
    with pytest.raises(RuntimeError, match="delivery unavailable"):
        host.callback(event(1))
    assert not (tmp_path / "run/supervision/cursor.json").exists()


def test_runtime_resumes_supervisor_before_review_even_when_no_nudge_is_sent(tmp_path: Path) -> None:
    class ContinueHost(FakeHost):
        def invoke_coordinator(
            self, _session: str, advisory: str, delta: dict[str, Any], boundary: str
        ) -> CoordinatorAssessment:
            assessment = super().invoke_coordinator(_session, advisory, delta, boundary)
            return CoordinatorAssessment(packet=assessment.packet, decision="continue")

    host = ContinueHost()
    runtime = ControllerRuntime(manifest_path=manifest_path(tmp_path), host=host, ticket_boundary=BOUNDARY)
    runtime.start()
    assert host.callback is not None
    host.callback(event(1))
    assert host.resumed == ["supervisor-116"]
