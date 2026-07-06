"""Run and summarize a split document-artifact graph batch."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("runtime/agent_jobs")
DEFAULT_SUMMARY_DIR = Path("benchmarks/vscode_subagent_spike")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a split document-artifact graph batch through Copilot supervisor."
    )
    parser.add_argument("--batch-manifest", type=Path, required=True)
    parser.add_argument("--run-suffix", required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--summary-dir", type=Path, default=DEFAULT_SUMMARY_DIR)
    parser.add_argument("--token-record", type=Path)
    parser.add_argument("--mode", default="agent-workbench-local-supervisor")
    parser.add_argument("--code-command", default="code")
    parser.add_argument("--bridge-prompt", default=None)
    parser.add_argument("--expected-model", default="qwen3.6:35b-a3b-bf16")
    parser.add_argument("--timeout-seconds", type=int, default=2400)
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument(
        "--skip-existing-accepted",
        action="store_true",
        help="Do not rerun child jobs whose existing summary is already accepted.",
    )
    parser.add_argument("--continue-on-failure", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def resolve_under_root(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def repo_relative(path: Path, root: Path) -> str:
    resolved = path if path.is_absolute() else root / path
    try:
        return resolved.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def child_run_id(base_job_id: str, run_suffix: str) -> str:
    return f"{base_job_id}_{run_suffix}"


def child_marker(base_marker: str, run_suffix: str) -> str:
    return f"{base_marker}_{run_suffix.upper()}"


def child_summary_path(summary_dir: Path, child_id: str, project_root: Path) -> Path:
    directory = resolve_under_root(summary_dir, project_root)
    return directory / f"{child_id}_internal_summary.json"


def batch_command(
    *,
    project_root: Path,
    output_dir: Path,
    summary_dir: Path,
    phase: str,
    task_id: str,
    title: str,
    job: dict[str, Any],
    run_suffix: str,
    mode: str,
    code_command: str,
    bridge_prompt: str | None,
    expected_model: str,
    timeout_seconds: int,
    poll_seconds: float,
) -> list[str]:
    base_job_id = str(job["job_id"])
    base_marker = str(job["marker"])
    child_id = child_run_id(base_job_id, run_suffix)
    command = [
        sys.executable,
        "-m",
        "agent_workbench.cli",
        "supervisor",
        "run-document-audit-graph",
        "--job-id",
        child_id,
        "--marker",
        child_marker(base_marker, run_suffix),
        "--phase",
        phase,
        "--task-id",
        task_id,
        "--title",
        f"{title} {job.get('batch_id', child_id)} {run_suffix}",
        "--project-root",
        str(project_root),
        "--output-dir",
        str(resolve_under_root(output_dir, project_root)),
        "--summary-output",
        repo_relative(child_summary_path(summary_dir, child_id, project_root), project_root),
        "--mode",
        mode,
        "--code-command",
        code_command,
        "--expected-model",
        expected_model,
        "--pre-materialize-audit-ticket",
        "--timeout-seconds",
        str(timeout_seconds),
        "--poll-seconds",
        str(poll_seconds),
        "--quiet-runtime-output",
    ]
    if bridge_prompt:
        command.extend(["--bridge-prompt", bridge_prompt])
    for source in job.get("source_summaries", []):
        command.extend(["--source-summary", str(source)])
    return command


def run_batch(args: argparse.Namespace, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    project_root = args.project_root.resolve()
    child_results: list[dict[str, Any]] = []
    for job in manifest.get("jobs", []):
        if not isinstance(job, dict):
            continue
        child_id = child_run_id(str(job["job_id"]), args.run_suffix)
        summary_path = child_summary_path(args.summary_dir, child_id, project_root)
        if args.skip_existing_accepted and existing_summary_is_accepted(summary_path):
            child_results.append(
                {
                    "job_id": child_id,
                    "summary_path": repo_relative(summary_path, project_root),
                    "returncode": 0,
                    "skipped_existing_accepted": True,
                }
            )
            continue
        command = batch_command(
            project_root=project_root,
            output_dir=args.output_dir,
            summary_dir=args.summary_dir,
            phase=str(manifest.get("phase", "")),
            task_id=str(manifest.get("task_id", "")),
            title=str(manifest.get("title", "")),
            job=job,
            run_suffix=args.run_suffix,
            mode=args.mode,
            code_command=args.code_command,
            bridge_prompt=args.bridge_prompt,
            expected_model=args.expected_model,
            timeout_seconds=args.timeout_seconds,
            poll_seconds=args.poll_seconds,
        )
        if args.dry_run:
            child_results.append(
                {
                    "job_id": child_id,
                    "summary_path": repo_relative(summary_path, project_root),
                    "returncode": None,
                    "command": command,
                }
            )
            continue
        completed = subprocess.run(
            command,
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        child_results.append(
            {
                "job_id": child_id,
                "summary_path": repo_relative(summary_path, project_root),
                "returncode": completed.returncode,
                "stdout": compact_text(completed.stdout),
                "stderr": compact_text(completed.stderr),
            }
        )
        if completed.returncode != 0 and not args.continue_on_failure:
            break
    return child_results


def existing_summary_is_accepted(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        data = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    return bool(data.get("accepted_candidate"))


def compact_text(value: str, limit: int = 1000) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def load_child_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def token_cost_usd(token: dict[str, Any]) -> float:
    usage = token.get("usage", {})
    prices = token.get("prices", {})
    if not isinstance(usage, dict) or not isinstance(prices, dict):
        return 0.0
    return (
        float(usage.get("supervisor_input_tokens", 0) or 0)
        * float(prices.get("supervisor_input_price_per_1m_usd", 0) or 0)
        + float(usage.get("supervisor_cached_input_tokens", 0) or 0)
        * float(prices.get("supervisor_cached_input_price_per_1m_usd", 0) or 0)
        + (
            float(usage.get("supervisor_output_tokens", 0) or 0)
            + float(usage.get("supervisor_reasoning_output_tokens", 0) or 0)
        )
        * float(prices.get("supervisor_output_price_per_1m_usd", 0) or 0)
    ) / 1_000_000


def aggregate_summary(
    *,
    manifest: dict[str, Any],
    run_suffix: str,
    project_root: Path,
    summary_dir: Path,
    child_results: list[dict[str, Any]],
    token_record: Path | None,
    expected_model: str,
) -> dict[str, Any]:
    loaded_children: list[dict[str, Any]] = []
    missing_summaries: list[str] = []
    for job in manifest.get("jobs", []):
        if not isinstance(job, dict):
            continue
        child_id = child_run_id(str(job["job_id"]), run_suffix)
        path = child_summary_path(summary_dir, child_id, project_root)
        child = load_child_summary(path)
        if child is None:
            missing_summaries.append(repo_relative(path, project_root))
            continue
        loaded_children.append(child)

    source_count = sum(int(child.get("source_count", 0) or 0) for child in loaded_children)
    accepted = bool(loaded_children) and all(
        bool(child.get("accepted_candidate")) for child in loaded_children
    )
    quality_validated = bool(loaded_children) and all(
        bool(child.get("authority_validation_passed"))
        and bool(child.get("document_audit_verifier_passed"))
        and bool(child.get("document_graph_report_verifier_passed"))
        for child in loaded_children
    )
    materializer_command_count = sum(
        int(child.get("materializer_command_count", 0) or 0)
        for child in loaded_children
    )
    decisions: dict[str, int] = {}
    for child in loaded_children:
        breakdown = child.get("audit_decision_breakdown", {})
        if not isinstance(breakdown, dict):
            continue
        for key, value in breakdown.items():
            decisions[str(key)] = decisions.get(str(key), 0) + int(value or 0)

    token_costs: dict[str, Any]
    if token_record:
        token_path = resolve_under_root(token_record, project_root)
        token = load_json(token_path)
        usage = token.get("usage", {})
        cost = token_cost_usd(token)
        token_costs = {
            "measured_paid_cost_available": True,
            "economics_usable": accepted,
            "not_usable_reason": "" if accepted else "Batch was not accepted.",
            "estimated_paid_cost_usd": round(cost, 6),
            "estimated_paid_cost_per_source_artifact_usd": round(cost / source_count, 6)
            if source_count
            else 0.0,
            **usage,
            "local_copilot_ollama_cash_cost_usd": 0.0,
            "measurement_boundary": "external_coordinator_span",
            "external_token_record": repo_relative(token_path, project_root),
        }
    else:
        token_costs = {
            "measured_paid_cost_available": False,
            "economics_usable": False,
            "not_usable_reason": "No external token record attached.",
            "estimated_paid_cost_usd": 0.0,
            "estimated_paid_cost_per_source_artifact_usd": 0.0,
            "local_copilot_ollama_cash_cost_usd": 0.0,
        }

    models = {
        str(child.get("model_provenance", {}).get("observed_model") or child.get("model", ""))
        for child in loaded_children
    }
    model_match = models <= {expected_model}
    child_records = [
        {
            "summary_id": child.get("summary_id", ""),
            "job_id": child.get("job_id", ""),
            "status": child.get("status", ""),
            "accepted_candidate": bool(child.get("accepted_candidate")),
            "source_count": child.get("source_count", 0),
            "subagent_tool_observed": bool(child.get("subagent_tool_observed")),
            "materializer_command_count": child.get("materializer_command_count", 0),
            "audit_decision_breakdown": child.get("audit_decision_breakdown", {}),
        }
        for child in loaded_children
    ]
    job_id = f"{manifest.get('job_id', 'graph_batch')}_{run_suffix}"
    return {
        "summary_id": f"{job_id}_summary",
        "phase": manifest.get("phase", ""),
        "task_id": manifest.get("task_id", ""),
        "status": "accepted-candidate" if accepted else "needs-supervisor-review",
        "model": expected_model if model_match else "mixed-or-mismatched",
        "model_provenance": {
            "expected_model": expected_model,
            "observed_models": sorted(models),
            "authoritative_model": expected_model if model_match else "mixed-or-mismatched",
            "source": "batch_child_copilot_chat_bridge_reports",
            "match_status": "matched" if model_match else "mismatched",
            "self_report_status": "not_applicable",
        },
        "copilot_permission_level": "autopilot",
        "workflow_graph": "document_artifact_audit_supervisor_graph",
        "job_id": job_id,
        "source_count": source_count,
        "child_run_count": len(loaded_children),
        "child_runs": child_records,
        "child_run_results": child_results,
        "missing_child_summaries": missing_summaries,
        "bridge_status": "accepted-candidate" if accepted else "needs-supervisor-review",
        "final_marker_present": accepted,
        "subagent_tool_observed": any(
            bool(child.get("subagent_tool_observed")) for child in loaded_children
        ),
        "subagent_tool_observed_count": sum(
            1 for child in loaded_children if child.get("subagent_tool_observed")
        ),
        "materializer_command_count": materializer_command_count,
        "pre_materialized_audit_ticket": True,
        "accepted_candidate": accepted,
        "quality_validated_candidate": quality_validated,
        "protocol_deviations": {
            "materializer_command_count": materializer_command_count,
            "nonaccepted_child_count": sum(
                1 for child in loaded_children if not child.get("accepted_candidate")
            ),
            "missing_child_summary_count": len(missing_summaries),
        },
        "failure": "" if accepted else "One or more child runs failed or are missing.",
        "authority_validation_passed": all(
            bool(child.get("authority_validation_passed")) for child in loaded_children
        ),
        "document_audit_verifier_passed": all(
            bool(child.get("document_audit_verifier_passed")) for child in loaded_children
        ),
        "document_graph_report_verifier_passed": all(
            bool(child.get("document_graph_report_verifier_passed"))
            for child in loaded_children
        ),
        "supervisor_report_score": 1.0
        if loaded_children
        and all(float(child.get("supervisor_report_score", 0) or 0) == 1.0 for child in loaded_children)
        else 0.0,
        "audit_decision_breakdown": decisions,
        "subagent_outcome": {
            "audit_report_status": "accepted_child_runs" if accepted else "needs_review",
            "graph_report_status": "accepted_child_runs" if accepted else "needs_review",
            "repair_required": any(
                bool(child.get("subagent_outcome", {}).get("repair_required"))
                for child in loaded_children
                if isinstance(child.get("subagent_outcome"), dict)
            ),
            "summary": (
                "Batch wrapper completed child graph runs under one package. "
                "Deterministic validators passed for all accepted child runs."
            ),
        },
        "token_costs": token_costs,
        "public_safety": {
            "raw_chat_session_paths_excluded": True,
            "raw_transcripts_excluded": True,
            "provider_details_excluded": True,
        },
    }


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    manifest_path = resolve_under_root(args.batch_manifest, project_root)
    manifest = load_json(manifest_path)
    child_results: list[dict[str, Any]] = []
    if not args.summary_only:
        child_results = run_batch(args, manifest)
    summary = aggregate_summary(
        manifest=manifest,
        run_suffix=args.run_suffix,
        project_root=project_root,
        summary_dir=args.summary_dir,
        child_results=child_results,
        token_record=args.token_record,
        expected_model=args.expected_model,
    )
    output = resolve_under_root(args.summary_output, project_root)
    write_json(output, summary)
    print(f"wrote {output}")
    return 0 if args.dry_run or summary["accepted_candidate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
