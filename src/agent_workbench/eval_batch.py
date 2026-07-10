"""Quiet batch orchestration for SDK eval manifests."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BatchEvalConfig:
    repo_root: Path
    manifest_dir: Path
    project_root: Path | None
    pattern: str
    dry_run: bool
    summary_only: bool
    continue_on_failure: bool
    output_dir: Path


def run_eval_batch(config: BatchEvalConfig) -> dict[str, Any]:
    manifests = sorted(config.manifest_dir.glob(config.pattern))
    config.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for manifest in manifests:
        row = run_one_manifest(config, manifest)
        rows.append(row)
        print(
            "BATCH {manifest} exit={exit_code} rows={row_count} status={status}".format(
                manifest=manifest,
                exit_code=row["exit_code"],
                row_count=row["worker_row_count"],
                status=row["status"],
            )
        )
        if row["exit_code"] != 0 and not config.continue_on_failure:
            break
    report = {
        "schema_version": 1,
        "generated_utc": now_utc(),
        "manifest_dir": str(config.manifest_dir),
        "project_root": str(config.project_root) if config.project_root else "",
        "pattern": config.pattern,
        "dry_run": config.dry_run,
        "summary_only": config.summary_only,
        "continue_on_failure": config.continue_on_failure,
        "manifests_discovered": len(manifests),
        "manifests_run": len(rows),
        "failed_manifests": sum(1 for row in rows if row["exit_code"] != 0),
        "rows": rows,
    }
    (config.output_dir / "batch_summary.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (config.output_dir / "batch_summary.md").write_text(
        render_batch_markdown(report),
        encoding="utf-8",
    )
    return report


def run_one_manifest(config: BatchEvalConfig, manifest: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "agent_workbench",
        "--repo-root",
        str(config.repo_root),
        "eval",
        "--manifest",
        str(manifest),
    ]
    if config.project_root is not None:
        command.extend(["--project-root", str(config.project_root)])
    if config.dry_run:
        command.append("--dry-run")
    if config.summary_only:
        command.append("--summary-only")

    log_path = config.output_dir / f"{manifest.stem}.log"
    completed = subprocess.run(
        command,
        cwd=config.project_root or config.repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    log_path.write_text(
        "\n".join(
            [
                "$ " + " ".join(command),
                "",
                "## stdout",
                "",
                completed.stdout,
                "",
                "## stderr",
                "",
                completed.stderr,
                "",
            ]
        ),
        encoding="utf-8",
    )
    summary_path = eval_summary_path(manifest, config.project_root)
    summary = load_json_if_exists(summary_path)
    worker_rows = summary.get("rows", []) if isinstance(summary, dict) else []
    classifications = classification_counts(worker_rows)
    return {
        "manifest": str(manifest),
        "exit_code": int(completed.returncode),
        "status": status_label(completed.returncode, worker_rows),
        "summary_json": str(summary_path),
        "log_path": str(log_path),
        "worker_row_count": len(worker_rows),
        "classification_counts": classifications,
        "failed_worker_rows": failed_worker_rows(worker_rows),
    }


def eval_summary_path(manifest: Path, project_root: Path | None) -> Path:
    data = load_json_if_exists(manifest)
    output_dir_text = (
        str(data.get("output_dir", "")).strip() if isinstance(data, dict) else ""
    )
    if not output_dir_text:
        return manifest.parent / "eval" / "summary.json"
    output_dir = Path(output_dir_text)
    if output_dir.is_absolute():
        return output_dir / "summary.json"
    if project_root is not None:
        return project_root / output_dir / "summary.json"
    return output_dir / "summary.json"


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def classification_counts(rows: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = str(row.get("classification", row.get("status", "unknown")))
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def failed_worker_rows(rows: list[Any]) -> int:
    failures = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("status") != "completed":
            failures += 1
    return failures


def status_label(exit_code: int, rows: list[Any]) -> str:
    if exit_code != 0:
        return "nonzero-exit"
    if not rows:
        return "no-summary-rows"
    if failed_worker_rows(rows):
        return "completed-with-worker-failures"
    return "completed"


def render_batch_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Eval Batch Summary",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- manifest_dir: `{report['manifest_dir']}`",
        f"- manifests_discovered: {report['manifests_discovered']}",
        f"- manifests_run: {report['manifests_run']}",
        f"- failed_manifests: {report['failed_manifests']}",
        "",
        "| Manifest | Exit | Status | Worker Rows | Worker Failures | Classifications |",
        "| --- | ---: | --- | ---: | ---: | --- |",
    ]
    for row in report["rows"]:
        lines.append(
            "| {manifest} | {exit_code} | `{status}` | {worker_row_count} | "
            "{failed_worker_rows} | {classifications} |".format(
                manifest=row["manifest"],
                exit_code=row["exit_code"],
                status=row["status"],
                worker_row_count=row["worker_row_count"],
                failed_worker_rows=row["failed_worker_rows"],
                classifications=format_counts(row["classification_counts"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return ""
    return ", ".join(f"`{key}`: {value}" for key, value in counts.items())


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
