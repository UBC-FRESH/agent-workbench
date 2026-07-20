"""Validate one bounded P116 structured supervision review packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.supervision_review import (
    build_packet_repair_request,
    build_supervisor_review_request,
    validate_delta_review_packet,
)


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: unable to read JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}: JSON value must be an object")
    return value


def _read_packet(path: Path) -> dict[str, Any]:
    if str(path) == "-":
        try:
            value = json.loads(sys.stdin.read())
        except json.JSONDecodeError as exc:
            raise ValueError("packet: unable to read JSON from stdin: invalid JSON") from exc
        if not isinstance(value, dict):
            raise ValueError("packet: JSON value must be an object")
        return value
    return _read_object(path, "packet")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a P116 supervision review packet.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--delta", type=Path, required=True)
    parser.add_argument("--ticket-boundary", required=True)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--render-request", action="store_true")
    parser.add_argument("--repair-errors", type=Path)
    args = parser.parse_args(argv)

    try:
        manifest = _read_object(args.manifest, "manifest")
        delta = _read_object(args.delta, "delta")
        if args.render_request:
            if args.packet:
                raise ValueError("--render-request does not accept --packet")
            print(json.dumps(build_supervisor_review_request(
                delta, ticket_boundary=args.ticket_boundary, manifest=manifest
            ), sort_keys=True))
            return 0
        if args.repair_errors:
            if args.packet:
                raise ValueError("--repair-errors does not accept --packet")
            try:
                errors = json.loads(args.repair_errors.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                detail = "invalid JSON" if isinstance(exc, json.JSONDecodeError) else str(exc)
                raise ValueError(f"repair-errors: unable to read JSON: {detail}") from exc
            if not isinstance(errors, list):
                raise ValueError("repair errors must be a JSON list")
            print(json.dumps(build_packet_repair_request(
                delta, ticket_boundary=args.ticket_boundary, manifest=manifest, errors=errors
            ), sort_keys=True))
            return 0
        if not args.packet:
            raise ValueError("--packet is required unless --render-request is used")
        packet = _read_packet(args.packet)
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
