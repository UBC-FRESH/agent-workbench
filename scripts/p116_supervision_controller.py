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
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--cursor", type=Path, required=True)
    parser.add_argument("--assigned-root", type=Path, required=True)
    parser.add_argument("--ack", action="store_true")
    args = parser.parse_args()
    try:
        delta, maximum = prepare_review_delta(
            events_path=args.events,
            cursor_path=args.cursor,
            assigned_root=args.assigned_root,
        )
        if args.ack:
            acknowledge_cursor(
                args.cursor,
                last_sequence=maximum,
                assigned_root=args.assigned_root,
            )
            delta["acknowledged_through_sequence"] = maximum
        print(json.dumps(delta, indent=2, sort_keys=True))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
