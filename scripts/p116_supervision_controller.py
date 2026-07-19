"""Render or acknowledge one P116 supervision review delta."""

from __future__ import annotations

import argparse
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
    args = parser.parse_args()
    try:
        delta, maximum = prepare_review_delta(manifest_path=args.manifest)
        if args.ack:
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
