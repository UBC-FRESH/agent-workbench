"""Run-scoped blocking broker for sanitized P116 event deltas."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .supervision_controller import load_manifest, prepare_review_delta
from .native_session_events import ingest_worker_session


class SupervisionEventBroker:
    def __init__(self, manifest_path: Path, *, poll_interval: float = 0.05) -> None:
        self.manifest_path = manifest_path
        self.poll_interval = poll_interval
        self.manifest, self.root = load_manifest(manifest_path)

    def wait_for_trigger(self, *, timeout: float) -> dict[str, Any]:
        """Block until an unacknowledged meaningful delta exists or timeout expires."""
        if timeout < 0:
            raise ValueError("timeout must be non-negative")
        # The MCP server starts before the fresh Coordinator binds native IDs.
        # Reload so this wait uses the validated bound Worker identity.
        self.manifest, self.root = load_manifest(self.manifest_path)
        deadline = time.monotonic() + timeout
        while True:
            events = ingest_worker_session(manifest=self.manifest, root=self.root)
            if events:
                events_path = self.root / self.manifest["events_path"]
                with events_path.open("a", encoding="utf-8", newline="\n") as stream:
                    for event in events:
                        stream.write(__import__("json").dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
            delta, _ = prepare_review_delta(manifest_path=self.manifest_path)
            if _meaningful(delta):
                return delta
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("no meaningful unacknowledged supervision delta before timeout")
            time.sleep(min(self.poll_interval, remaining))


def _meaningful(delta: dict[str, Any]) -> bool:
    """Return fresh, sanitized Worker evidence to the in-session Coordinator.

    Native Codex hook capture intentionally projects successful tools to the
    generic ``tool_completed`` event.  Treating that projection as routine
    forever leaves a Coordinator asleep while the Worker is actively making
    progress, even though the new evidence is available for review.
    """
    return any(
        event.get("kind") in {"tool_completed", "tool_failed", "workspace_mismatch", "terminal"}
        or event.get("kind") == "stage_transition" and event.get("stage") == "validation"
        for event in delta.get("events", [])
    )
