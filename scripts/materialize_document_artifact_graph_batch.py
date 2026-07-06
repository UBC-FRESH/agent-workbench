"""Materialize split-batch document-artifact graph jobs.

The local Copilot supervisor handled five-artifact mixed-schema graph jobs but
failed a single fourteen-artifact audit node. This script makes that split
policy explicit and reproducible by generating one graph-derived job ticket per
batch plus an aggregate manifest for coordinator review.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("runtime/agent_jobs")
DEFAULT_BATCH_SIZE = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize split-batch graph-derived document-artifact jobs."
    )
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--marker", required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--phase", default="P57")
    parser.add_argument("--task-id", default="P57.4")
    parser.add_argument("--title", default="Split-batch document artifact audit")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--source-summary",
        action="append",
        required=True,
        help="Source summary JSON path. May be repeated.",
    )
    return parser.parse_args()


def resolve_under_root(path: Path, project_root: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root / path


def display_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def batched(values: list[str], size: int) -> list[list[str]]:
    if size < 1:
        raise SystemExit("--batch-size must be >= 1")
    return [values[index : index + size] for index in range(0, len(values), size)]


def run_child_materializer(
    *,
    project_root: Path,
    output_dir: Path,
    job_id: str,
    marker: str,
    phase: str,
    task_id: str,
    title: str,
    sources: list[str],
) -> None:
    script = project_root / "scripts" / "materialize_document_artifact_graph_job.py"
    command = [
        sys.executable,
        str(script),
        "--project-root",
        str(project_root),
        "--output-dir",
        str(output_dir),
        "--job-id",
        job_id,
        "--marker",
        marker,
        "--phase",
        phase,
        "--task-id",
        task_id,
        "--title",
        title,
    ]
    for source in sources:
        command.extend(["--source-summary", source])
    completed = subprocess.run(command, cwd=project_root, text=True, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"child materializer failed for {job_id}: {completed.returncode}")


def load_child_manifest(output_dir: Path, job_id: str) -> dict[str, Any]:
    path = output_dir / f"{job_id}_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def manifest_for_batch(
    *,
    project_root: Path,
    output_dir: Path,
    parent_job_id: str,
    parent_marker: str,
    phase: str,
    task_id: str,
    title: str,
    batch_size: int,
    source_batches: list[list[str]],
) -> dict[str, Any]:
    jobs: list[dict[str, Any]] = []
    for index, sources in enumerate(source_batches, start=1):
        suffix = f"split_{index:02d}"
        child_job_id = f"{parent_job_id}_{suffix}"
        child_marker = f"{parent_marker}_{suffix.upper()}"
        child_title = f"{title} {suffix}"
        run_child_materializer(
            project_root=project_root,
            output_dir=output_dir,
            job_id=child_job_id,
            marker=child_marker,
            phase=phase,
            task_id=task_id,
            title=child_title,
            sources=sources,
        )
        child_manifest = load_child_manifest(output_dir, child_job_id)
        jobs.append(
            {
                "batch_id": suffix,
                "job_id": child_job_id,
                "marker": child_marker,
                "source_count": len(sources),
                "source_summaries": sources,
                "ticket_path": child_manifest["ticket_path"],
                "audit_report_path": child_manifest["audit_report_path"],
                "graph_report_path": child_manifest["graph_report_path"],
                "manifest_path": display_path(
                    output_dir / f"{child_job_id}_manifest.json",
                    project_root,
                ),
            }
        )
    return {
        "job_id": parent_job_id,
        "marker": parent_marker,
        "phase": phase,
        "task_id": task_id,
        "title": title,
        "batch_policy": {
            "strategy": "preserve_order_fixed_size",
            "max_source_summaries_per_graph_job": batch_size,
            "reason": (
                "P57 evidence showed one large mixed audit node failed early, "
                "while five-artifact split batches completed under verifier control."
            ),
        },
        "source_count": sum(len(batch) for batch in source_batches),
        "batch_count": len(source_batches),
        "jobs": jobs,
        "runtime_only": True,
    }


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_dir = resolve_under_root(args.output_dir, project_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    sources = [
        display_path(resolve_under_root(Path(source), project_root), project_root)
        for source in args.source_summary
    ]
    source_batches = batched(sources, args.batch_size)
    manifest = manifest_for_batch(
        project_root=project_root,
        output_dir=output_dir,
        parent_job_id=args.job_id,
        parent_marker=args.marker,
        phase=args.phase,
        task_id=args.task_id,
        title=args.title,
        batch_size=args.batch_size,
        source_batches=source_batches,
    )
    manifest_path = output_dir / f"{args.job_id}_batch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"batch_manifest: {manifest_path}")
    print(f"batch_count: {manifest['batch_count']}")
    print(f"source_count: {manifest['source_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
