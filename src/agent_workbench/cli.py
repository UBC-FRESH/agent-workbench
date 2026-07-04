"""Command-line entrypoint for Agent Workbench local supervisor tools."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .comparison import render_eval_comparison
from .decision import (
    DecisionInputError,
    decide_task,
    load_decision_input,
    render_markdown_report,
    result_to_jsonable,
)
from .evidence import (
    load_summary,
    render_markdown,
    synthesize_markdown,
    validate_summary,
)
from .pilot import (
    PilotPackScaffoldConfig,
    PilotPackTask,
    PilotScaffoldConfig,
    scaffold_pilot,
    scaffold_pilot_pack,
)


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

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare existing worker evaluation summaries.",
    )
    compare_subparsers = compare_parser.add_subparsers(
        dest="compare_command",
        required=True,
    )

    eval_compare_parser = compare_subparsers.add_parser(
        "eval",
        help="Render a model/repeat comparison report for eval summary JSON.",
    )
    eval_compare_parser.add_argument("--input", type=Path, action="append", default=[])
    eval_compare_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing eval summary JSON files.",
    )
    eval_compare_parser.add_argument("--output", type=Path, required=True)
    eval_compare_parser.set_defaults(func=run_compare_eval)

    decide_parser = subparsers.add_parser(
        "decide",
        help="Render transparent delegation recommendations.",
    )
    decide_subparsers = decide_parser.add_subparsers(
        dest="decide_command",
        required=True,
    )

    decide_task_parser = decide_subparsers.add_parser(
        "task",
        help="Evaluate one candidate task-bundle decision input.",
    )
    decide_task_parser.add_argument("--input", type=Path, required=True)
    decide_task_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional Markdown report path. Prints to stdout when omitted.",
    )
    decide_task_parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="Optional JSON result path.",
    )
    decide_task_parser.set_defaults(func=run_decide_task)

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

    synthesize_parser = evidence_subparsers.add_parser(
        "synthesize",
        help="Render multiple evidence summaries into one supervisor decision packet.",
    )
    synthesize_parser.add_argument("--input", type=Path, action="append", default=[])
    synthesize_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing *.evidence.json files.",
    )
    synthesize_parser.add_argument("--output", type=Path, required=True)
    synthesize_parser.set_defaults(func=run_evidence_synthesize)

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

    pack_parser = pilot_subparsers.add_parser(
        "pack-scaffold",
        help="Create multiple isolated pilot tickets, manifests, and evidence stubs.",
    )
    pack_parser.add_argument("--project-root", type=Path, required=True)
    pack_parser.add_argument(
        "--task",
        action="append",
        required=True,
        help="Task spec as task-id=Title text. Repeat once per worker ticket.",
    )
    pack_parser.add_argument(
        "--mode",
        choices=("marker", "proposal"),
        default="proposal",
    )
    pack_parser.add_argument("--model", default="qwen3-coder:latest")
    pack_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runtime/agent_workbench/pilots"),
    )
    pack_parser.add_argument("--repeats", type=int, default=1)
    pack_parser.add_argument("--timeout-seconds", type=int, default=120)
    pack_parser.add_argument(
        "--base-url-file",
        default="runtime/ollama_openai_base_url.txt",
    )
    pack_parser.add_argument(
        "--provider-headers-file",
        default="runtime/local_provider_headers.json",
    )
    pack_parser.add_argument("--force", action="store_true")
    pack_parser.set_defaults(func=run_pilot_pack_scaffold)

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


def run_compare_eval(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("summary.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        report = render_eval_comparison(paths)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_decide_task(args: argparse.Namespace) -> int:
    try:
        data = load_decision_input(args.input)
        resolve_decision_paths(data, args.input, args.repo_root)
        result = decide_task(data)
    except (OSError, json.JSONDecodeError, DecisionInputError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = render_markdown_report(result)
    if args.output is None:
        print(report)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote {args.output}")

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(result_to_jsonable(result), indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.json_output}")
    return 0


def resolve_decision_paths(data: dict[str, object], input_path: Path, repo_root: Path) -> None:
    profile_path = data.get("model_profile_path")
    if profile_path is None:
        return
    path = Path(str(profile_path))
    if path.is_absolute() or path.exists():
        return
    for base in (input_path.parent, repo_root):
        candidate = base / path
        if candidate.exists():
            data["model_profile_path"] = str(candidate)
            return


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


def run_evidence_synthesize(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("*.evidence.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        packet = synthesize_markdown(paths)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(packet, encoding="utf-8")
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


def run_pilot_pack_scaffold(args: argparse.Namespace) -> int:
    tasks = tuple(parse_pack_task(task) for task in args.task)
    config = PilotPackScaffoldConfig(
        project_root=args.project_root,
        tasks=tasks,
        mode=args.mode,
        model=args.model,
        output_dir=args.output_dir,
        repeats=args.repeats,
        timeout_seconds=args.timeout_seconds,
        base_url_file=args.base_url_file,
        provider_headers_file=args.provider_headers_file,
        force=args.force,
    )
    result = scaffold_pilot_pack(config)
    for item in result.results:
        print(f"ticket: {item.ticket_path}")
        print(f"manifest: {item.manifest_path}")
        print(f"evidence: {item.evidence_path}")
    return 0


def parse_pack_task(value: str) -> PilotPackTask:
    if "=" not in value:
        raise SystemExit("pack task must use task-id=Title text")
    task_id, title = value.split("=", 1)
    task_id = task_id.strip()
    title = title.strip()
    if not task_id or not title:
        raise SystemExit("pack task must include both task id and title")
    return PilotPackTask(task_id=task_id, title=title)


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


if __name__ == "__main__":
    raise SystemExit(main())
