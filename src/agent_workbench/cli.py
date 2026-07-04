"""Command-line entrypoint for Agent Workbench local supervisor tools."""

from __future__ import annotations

import argparse

from . import __version__


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
    parser.set_defaults(func=run_overview)
    return parser


def run_overview(_args: argparse.Namespace) -> int:
    parser = build_parser()
    parser.print_help()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
