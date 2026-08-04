#!/usr/bin/env python3
"""Install Agent Workbench custom agents into the user Copilot profile."""

from __future__ import annotations

import argparse
import shutil
import sys
from importlib import resources
from pathlib import Path


def _packaged_profiles() -> Path:
    """Locate the packaged profile templates.

    Works both from a source checkout and from an installed wheel, so the
    Agent Hub can be installed without cloning this repository.
    """
    try:
        return Path(str(resources.files("agent_workbench.agent_hub") / "profiles"))
    except (ModuleNotFoundError, AttributeError):
        return (
            Path(__file__).resolve().parents[1]
            / "src"
            / "agent_workbench"
            / "agent_hub"
            / "profiles"
        )


DEFAULT_SOURCE = _packaged_profiles()
DEFAULT_DESTINATION = Path.home() / ".copilot" / "agents"
DEFAULT_CONTRACT_SOURCE = (
    Path(__file__).resolve().parents[1] / ".github" / "copilot-instructions.md"
)
DEFAULT_CONTRACT_DESTINATION = (
    Path.home() / ".copilot" / "instructions" / "agent-workbench.instructions.md"
)
CORE_PROFILE_FILES = (
    "agent-workbench-advisor.agent.md",
    "agent-workbench-coordinator.agent.md",
    "agent-workbench-supervisor.agent.md",
    "agent-workbench-worker.agent.md",
)


def profile_files(source: Path) -> list[Path]:
    """Return the four portable core role files in deterministic order."""
    files = [source / name for name in CORE_PROFILE_FILES if (source / name).exists()]
    if not files:
        raise FileNotFoundError(f"No core *.agent.md files found in {source}")
    return files


def overlay_files(source: Path) -> list[Path]:
    """Return portable overlay documents in deterministic order."""
    return sorted((source / "overlays").glob("*.md"))


def render_global_contract(source: Path) -> str:
    """Add user-instruction frontmatter to the canonical Agent Hub contract."""
    content = source.expanduser().resolve().read_text(encoding="utf-8")
    return (
        "---\n"
        "description: Agent Hub operating contract for target workspaces\n"
        "applyTo: \"**\"\n"
        "---\n\n"
        + content
    )


def install_profiles(
    source: Path,
    destination: Path,
    *,
    replace: bool = False,
    dry_run: bool = False,
) -> tuple[list[str], list[str], list[str]]:
    """Install profiles, returning installed, unchanged, and conflict names."""
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    files = [(path, path.name) for path in profile_files(source)]
    files.extend(
        (path, f"overlays/{path.name}") for path in overlay_files(source)
    )

    conflicts = [
        target_name
        for path, target_name in files
        if (destination / target_name).exists()
        and (destination / target_name).read_bytes() != path.read_bytes()
        and not replace
    ]
    if conflicts:
        return [], [], conflicts

    installed: list[str] = []
    unchanged: list[str] = []
    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)
    for path, target_name in files:
        target = destination / target_name
        if target.exists() and target.read_bytes() == path.read_bytes():
            unchanged.append(target_name)
            continue
        installed.append(target_name)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return installed, unchanged, []


def prune_destination(
    source: Path,
    destination: Path,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Remove installed profiles and overlays no longer provided by the package.

    Without this, deleting a profile from the package never reaches an
    existing installation: the stale file lives in the user profile forever
    and keeps appearing in the agent picker.
    """
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if not destination.is_dir():
        return []

    expected = {path.name for path in profile_files(source)}
    expected |= {f"overlays/{path.name}" for path in overlay_files(source)}

    stale: list[str] = []
    for path in sorted(destination.glob("*.agent.md")):
        if path.name not in expected:
            stale.append(path.name)
    overlay_dir = destination / "overlays"
    if overlay_dir.is_dir():
        for path in sorted(overlay_dir.glob("*.md")):
            if f"overlays/{path.name}" not in expected:
                stale.append(f"overlays/{path.name}")

    if not dry_run:
        for name in stale:
            (destination / name).unlink()
    return stale


def install_global_contract(
    source: Path,
    destination: Path,
    *,
    replace: bool = False,
    dry_run: bool = False,
) -> tuple[bool, bool, bool]:
    """Install the full Agent Hub contract into user-level instructions."""
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    rendered = render_global_contract(source)
    if destination.exists():
        current = destination.read_text(encoding="utf-8")
        if current == rendered:
            return False, True, False
        if not replace:
            return False, False, True
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    return True, False, False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install Agent Workbench custom agents for all Copilot workspaces."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Agent Workbench .agent.md directory",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help="User-level Copilot agents directory (default: ~/.copilot/agents)",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace conflicting destination files explicitly",
    )
    parser.add_argument(
        "--contract-source",
        type=Path,
        default=DEFAULT_CONTRACT_SOURCE,
        help="Canonical Agent Hub instruction file",
    )
    parser.add_argument(
        "--contract-destination",
        type=Path,
        default=DEFAULT_CONTRACT_DESTINATION,
        help="User-level Agent Hub instruction file",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether the destination is current without modifying it",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        installed, unchanged, conflicts = install_profiles(
            args.source,
            args.destination,
            replace=args.replace,
            dry_run=args.check,
        )
        contract_installed, contract_unchanged, contract_conflict = (
            install_global_contract(
                args.contract_source,
                args.contract_destination,
                replace=args.replace,
                dry_run=args.check,
            )
        )
    except (FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if conflicts or contract_conflict:
        print(
            "conflicting destination files; rerun with --replace to overwrite:",
            file=sys.stderr,
        )
        for name in conflicts:
            print(f"  {name}", file=sys.stderr)
        if contract_conflict:
            print(f"  {args.contract_destination}", file=sys.stderr)
        return 2

    action = "would install" if args.check else "installed"
    profile_count = sum(name.endswith(".agent.md") for name in installed)
    overlay_count = sum(name.startswith("overlays/") for name in installed)
    print(
        f"{action} {profile_count} core profile(s) and "
        f"{overlay_count} overlay(s) in {args.destination}"
    )
    stale = prune_destination(
        args.source, args.destination, dry_run=args.check
    )
    if stale:
        removed = "would remove" if args.check else "removed"
        print(f"{removed} {len(stale)} stale profile(s)/overlay(s):")
        for name in stale:
            print(f"  {name}")
    if unchanged:
        print(f"already current: {len(unchanged)} profile(s)")
    if args.check and not installed:
        print("destination is current")
    if contract_installed:
        print(f"{action} Agent Hub contract in {args.contract_destination}")
    elif contract_unchanged:
        print(f"Agent Hub contract already current in {args.contract_destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())