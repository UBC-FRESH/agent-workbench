"""Render or acknowledge one P116 supervision review delta."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.supervision_controller import acknowledge_cursor, prepare_review_delta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--action", type=Path)
    parser.add_argument("--ack", action="store_true")
    parser.add_argument("--record-nudge", action="store_true")
    parser.add_argument("--delivery-submission-id")
    parser.add_argument("--worker-session-id")
    parser.add_argument("--supervisor-session-id")
    args = parser.parse_args()
    try:
        delta, maximum = prepare_review_delta(manifest_path=args.manifest)
        if args.record_nudge:
            if not args.packet or not all((args.delivery_submission_id, args.worker_session_id, args.supervisor_session_id)):
                raise ValueError("--record-nudge requires --packet, --delivery-submission-id, --worker-session-id, and --supervisor-session-id")
            packet = json.loads(args.packet.read_text(encoding="utf-8"))
            action = {
                "schema_version": packet.get("schema_version"),
                "run_id": packet.get("run_id"),
                "packet_sha256": hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                "decision": "nudge",
                "worker_session_id": args.worker_session_id,
                "supervisor_session_id": args.supervisor_session_id,
                "delivery_submission_id": args.delivery_submission_id,
            }
            acknowledge_cursor(
                manifest_path=args.manifest,
                last_sequence=maximum,
                packet=packet,
                action=action,
            )
            delta["acknowledged_through_sequence"] = maximum
        elif args.ack:
            if not args.packet or not args.action:
                raise ValueError("--ack requires --packet and --action")
            packet = json.loads(args.packet.read_text(encoding="utf-8"))
            action = json.loads(args.action.read_text(encoding="utf-8"))
            acknowledge_cursor(
                manifest_path=args.manifest,
                last_sequence=maximum,
                packet=packet,
                action=action,
            )
            delta["acknowledged_through_sequence"] = maximum
        print(json.dumps(delta, indent=2, sort_keys=True))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
