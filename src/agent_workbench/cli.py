"""Command-line entrypoint for Agent Workbench local supervisor tools."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-workbench",
        description="Local supervisor tooling for Agent Workbench workflows.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"agent-workbench {__version__}",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo_root(),
        help="Agent Workbench checkout root. Defaults to the installed editable checkout.",
    )
    subparsers = parser.add_subparsers(dest="command")

    smoke_parser = subparsers.add_parser(
        "smoke",
        help="Run local command-surface smoke checks.",
    )
    smoke_parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional ignored Markdown report path.",
    )
    smoke_parser.set_defaults(func=run_smoke)

    eval_parser = subparsers.add_parser(
        "eval",
        help="Run or plan an SDK same-ticket evaluation manifest.",
    )
    eval_parser.add_argument("--manifest", type=Path, required=True)
    eval_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan runs without contacting the model provider.",
    )
    eval_parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Summarize existing result files without running probes.",
    )
    eval_parser.set_defaults(func=run_eval)

    parser.set_defaults(func=run_overview)
    return parser


def run_overview(_args: argparse.Namespace) -> int:
    parser = build_parser()
    parser.print_help()
    return 0


def run_smoke(args: argparse.Namespace) -> int:
    script = script_path(args.repo_root, "check_command_surfaces.py")
    command = [sys.executable, str(script)]
    if args.report is not None:
        command.extend(["--report", str(args.report)])
    return run_command(command, args.repo_root)


def run_eval(args: argparse.Namespace) -> int:
    script = script_path(args.repo_root, "sdk_same_ticket_eval.py")
    command = [sys.executable, str(script), "--manifest", str(args.manifest)]
    if args.dry_run:
        command.append("--dry-run")
    if args.summary_only:
        command.append("--summary-only")
    return run_command(command, args.repo_root)


def script_path(repo_root: Path, script_name: str) -> Path:
    path = repo_root / "scripts" / script_name
    if not path.exists():
        raise SystemExit(f"script not found: {path}")
    return path


def run_command(command: list[str], repo_root: Path) -> int:
    completed = subprocess.run(command, cwd=repo_root, check=False)
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
