"""Command-line entrypoint for Agent Workbench local supervisor tools."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .evidence import load_summary, render_markdown, validate_summary
from .pilot import PilotScaffoldConfig, scaffold_pilot


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
        "--project-root",
        type=Path,
        default=None,
        help=(
            "Optional target project root used to resolve manifest-relative "
            "ticket, output, provider, and evidence paths."
        ),
    )
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

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Validate or render sanitized evidence summaries.",
    )
    evidence_subparsers = evidence_parser.add_subparsers(dest="evidence_command", required=True)

    validate_parser = evidence_subparsers.add_parser(
        "validate",
        help="Validate a JSON evidence summary.",
    )
    validate_parser.add_argument("--input", type=Path, required=True)
    validate_parser.set_defaults(func=run_evidence_validate)

    render_parser = evidence_subparsers.add_parser(
        "render",
        help="Render a JSON evidence summary to Markdown.",
    )
    render_parser.add_argument("--input", type=Path, required=True)
    render_parser.add_argument("--output", type=Path, required=True)
    render_parser.set_defaults(func=run_evidence_render)

    pilot_parser = subparsers.add_parser(
        "pilot",
        help="Create real-project pilot scaffolds.",
    )
    pilot_subparsers = pilot_parser.add_subparsers(dest="pilot_command", required=True)

    scaffold_parser = pilot_subparsers.add_parser(
        "scaffold",
        help="Create a bounded ticket, eval manifest, and evidence stub.",
    )
    scaffold_parser.add_argument("--project-root", type=Path, required=True)
    scaffold_parser.add_argument("--task-id", required=True)
    scaffold_parser.add_argument("--title", required=True)
    scaffold_parser.add_argument(
        "--mode",
        choices=("marker", "proposal"),
        default="marker",
    )
    scaffold_parser.add_argument("--model", default="qwen3-coder:latest")
    scaffold_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runtime/agent_workbench/pilots"),
    )
    scaffold_parser.add_argument("--marker", default="")
    scaffold_parser.add_argument("--repeats", type=int, default=1)
    scaffold_parser.add_argument("--timeout-seconds", type=int, default=120)
    scaffold_parser.add_argument(
        "--base-url-file",
        default="runtime/ollama_openai_base_url.txt",
    )
    scaffold_parser.add_argument(
        "--provider-headers-file",
        default="runtime/local_provider_headers.json",
    )
    scaffold_parser.add_argument("--force", action="store_true")
    scaffold_parser.set_defaults(func=run_pilot_scaffold)

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
    cwd = args.project_root.resolve() if args.project_root is not None else args.repo_root
    manifest = materialize_cross_project_manifest(args) if args.project_root else args.manifest
    command = [sys.executable, str(script), "--manifest", str(manifest)]
    if args.dry_run:
        command.append("--dry-run")
    if args.summary_only:
        command.append("--summary-only")
    return run_command(command, cwd)


def materialize_cross_project_manifest(args: argparse.Namespace) -> Path:
    project_root = args.project_root.resolve()
    manifest_path = resolve_manifest_path(args.manifest, project_root)
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))

    probe_script = Path(str(data.get("probe_script", "")))
    if not probe_script.is_absolute():
        data["probe_script"] = str(script_path(args.repo_root, probe_script.name))

    python_executable = Path(str(data.get("python_executable", "")))
    if not str(python_executable) or not python_executable.is_absolute():
        data["python_executable"] = sys.executable

    materialized_dir = manifest_path.parent / "materialized_manifests"
    materialized_dir.mkdir(parents=True, exist_ok=True)
    materialized = materialized_dir / f"{manifest_path.stem}.agent-workbench.json"
    materialized.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return materialized


def resolve_manifest_path(manifest: Path, project_root: Path) -> Path:
    if manifest.is_absolute():
        return manifest
    return project_root / manifest


def run_evidence_validate(args: argparse.Namespace) -> int:
    data = load_summary(args.input)
    result = validate_summary(data)
    if result.ok:
        print(f"valid evidence summary: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_evidence_render(args: argparse.Namespace) -> int:
    data = load_summary(args.input)
    result = validate_summary(data)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_pilot_scaffold(args: argparse.Namespace) -> int:
    marker = args.marker.strip() or f"{args.task_id.upper().replace('-', '_')} done"
    config = PilotScaffoldConfig(
        project_root=args.project_root,
        task_id=args.task_id,
        title=args.title,
        mode=args.mode,
        model=args.model,
        output_dir=args.output_dir,
        marker=marker,
        repeats=args.repeats,
        timeout_seconds=args.timeout_seconds,
        base_url_file=args.base_url_file,
        provider_headers_file=args.provider_headers_file,
        force=args.force,
    )
    result = scaffold_pilot(config)
    print(f"ticket: {result.ticket_path}")
    print(f"manifest: {result.manifest_path}")
    print(f"evidence: {result.evidence_path}")
    return 0


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
