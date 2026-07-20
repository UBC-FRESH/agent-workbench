"""CLI wrapper for agent bridge config transactions."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from agent_workbench.agent_bridge.transaction import BridgeConfigTransaction, ConfigTarget


def _target(value: str) -> tuple[ConfigTarget, Path | None]:
    parts = value.split("|")
    if len(parts) not in {3, 4}:
        raise argparse.ArgumentTypeError("target must be kind|path|backup or kind|path|backup|staged")
    kind, path, backup = parts[:3]
    if kind not in {"config", "agent_role", "hooks"}:
        raise argparse.ArgumentTypeError("target kind must be config, agent_role, or hooks")
    staged = Path(parts[3]) if len(parts) == 4 else None
    return ConfigTarget(path=Path(path), backup_path=Path(backup), kind=kind), staged


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an Agent Workbench bridge file transaction.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("commit", "restore"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--run-id", required=True)
        sub.add_argument("--journal", type=Path, required=True)
        sub.add_argument("--lock", type=Path, required=True)
        sub.add_argument("--target", action="append", type=_target, required=True, help="kind|path|backup for restore, kind|path|backup|staged for commit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    targets = tuple(target for target, _staged in args.target)
    transaction = BridgeConfigTransaction(run_id=args.run_id, targets=targets, journal_path=args.journal, lock_path=args.lock)
    if args.command == "restore":
        transaction.restore_existing()
        print(f"restored {len(targets)} target(s)")
        return 0
    with transaction:
        for target, staged in args.target:
            if staged is None:
                raise SystemExit("commit targets require staged content paths")
            transaction.stage(target.path, staged.read_text(encoding="utf-8"))
        transaction.commit()
    print(f"committed {len(targets)} target(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

