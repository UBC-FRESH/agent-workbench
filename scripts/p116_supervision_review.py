"""Validate one bounded P116 structured supervision review packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.supervision_review import validate_delta_review_packet


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: unable to read JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}: JSON value must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a P116 supervision review packet.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--delta", type=Path, required=True)
    parser.add_argument("--ticket-boundary", required=True)
    parser.add_argument("--packet", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        manifest = _read_object(args.manifest, "manifest")
        delta = _read_object(args.delta, "delta")
        packet = _read_object(args.packet, "packet")
        result = validate_delta_review_packet(
            packet,
            delta=delta,
            ticket_boundary=args.ticket_boundary,
            manifest=manifest,
        )
        print(json.dumps({"ok": result.ok, "errors": result.errors}, sort_keys=True))
        return 0 if result.ok else 1
    except ValueError as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
