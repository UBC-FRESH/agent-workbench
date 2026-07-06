"""Reusable local-supervisor graph run orchestration helpers."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .supervisor_tokens import span_record_from_checkpoints, write_checkpoint


@dataclass(frozen=True)
class DocumentAuditGraphRunConfig:
    project_root: Path
    repo_root: Path
    job_id: str
    marker: str
    phase: str
    task_id: str
    title: str
    source_summaries: tuple[Path, ...]
    output_dir: Path
    summary_output: Path
    token_dir: Path
    mode: str = "agent-workbench-local-supervisor"
    code_command: str = "code"
    expected_model: str | None = None
    bridge_prompt: str | None = None
    pre_materialize_audit_ticket: bool = False
    timeout_seconds: int = 1800
    poll_seconds: float = 10.0
    dry_run: bool = False
    bridge_no_launch: bool = False
    quiet_runtime_output: bool = False


def build_run_plan(config: DocumentAuditGraphRunConfig) -> dict[str, Any]:
    project_root = config.project_root.resolve()
    repo_root = config.repo_root.resolve()
    output_dir = resolve_under_root(config.output_dir, project_root)
    token_dir = resolve_under_root(config.token_dir, project_root)
    summary_output = resolve_under_root(config.summary_output, project_root)

    ticket_path = output_dir / f"{config.job_id}_ticket.md"
    bridge_report_path = output_dir / f"{config.job_id}_bridge_report.md"
    audit_report_path = output_dir / f"{config.job_id}_audit_report.json"
    graph_report_path = output_dir / f"{config.job_id}_graph_report.json"
    start_path = token_dir / "start.json"
    end_path = token_dir / "end.json"
    token_record_path = token_dir / f"{slug(config.job_id)}.tokens.json"

    materialize_command = [
        sys.executable,
        str(repo_root / "scripts" / "materialize_document_artifact_graph_job.py"),
        "--project-root",
        str(project_root),
        "--job-id",
        config.job_id,
        "--marker",
        config.marker,
        "--phase",
        config.phase,
        "--task-id",
        config.task_id,
        "--title",
        config.title,
        "--output-dir",
        str(output_dir),
    ]
    for source in config.source_summaries:
        materialize_command.extend(["--source-summary", repo_relative(source, project_root)])
    if config.pre_materialize_audit_ticket:
        materialize_command.append("--pre-materialize-audit-ticket")

    bridge_command = [
        sys.executable,
        str(repo_root / "scripts" / "copilot_chat_bridge.py"),
        "--ticket",
        repo_relative(ticket_path, project_root),
        "--marker",
        config.marker,
        "--workspace-root",
        str(project_root),
        "--report",
        repo_relative(bridge_report_path, project_root),
        "--timeout-seconds",
        str(config.timeout_seconds),
        "--poll-seconds",
        str(config.poll_seconds),
        "--mode",
        config.mode,
        "--code-command",
        config.code_command,
    ]
    if config.bridge_prompt:
        bridge_command.extend(["--prompt", config.bridge_prompt])
    if config.expected_model:
        bridge_command.extend(["--expected-model", config.expected_model])
    if config.bridge_no_launch:
        bridge_command.append("--no-launch")

    authority_validate_command = [
        sys.executable,
        "-m",
        "agent_workbench.cli",
        "authority",
        "validate",
        "--kind",
        "report",
        "--input",
        repo_relative(audit_report_path, project_root),
    ]
    document_audit_verifier_command = [
        sys.executable,
        str(repo_root / "scripts" / "verify_document_artifact_audit_report.py"),
        "--project-root",
        str(project_root),
        "--report",
        repo_relative(audit_report_path, project_root),
    ]
    for source in config.source_summaries:
        document_audit_verifier_command.extend(
            ["--source-summary", repo_relative(source, project_root)]
        )
    graph_report_verifier_command = [
        sys.executable,
        str(repo_root / "scripts" / "verify_document_artifact_graph_report.py"),
        "--project-root",
        str(project_root),
        "--graph-report",
        repo_relative(graph_report_path, project_root),
        "--audit-report",
        repo_relative(audit_report_path, project_root),
    ]

    return {
        "job_id": config.job_id,
        "marker": config.marker,
        "project_root": str(project_root),
        "repo_root": str(repo_root),
        "paths": {
            "ticket": repo_relative(ticket_path, project_root),
            "bridge_report": repo_relative(bridge_report_path, project_root),
            "audit_report": repo_relative(audit_report_path, project_root),
            "graph_report": repo_relative(graph_report_path, project_root),
            "token_start": repo_relative(start_path, project_root),
            "token_end": repo_relative(end_path, project_root),
            "token_record": repo_relative(token_record_path, project_root),
            "summary_output": repo_relative(summary_output, project_root),
        },
        "commands": {
            "materialize": materialize_command,
            "bridge": bridge_command,
            "authority_validate": authority_validate_command,
            "document_audit_verify": document_audit_verifier_command,
            "graph_report_verify": graph_report_verifier_command,
        },
        "source_summaries": [
            repo_relative(path, project_root) for path in config.source_summaries
        ],
        "pre_materialized_audit_ticket": config.pre_materialize_audit_ticket,
        "runtime_only": {
            "raw_chat_session_paths_excluded": True,
            "raw_transcripts_excluded": True,
            "provider_details_excluded": True,
        },
    }


def run_document_audit_graph(config: DocumentAuditGraphRunConfig) -> dict[str, Any]:
    plan = build_run_plan(config)
    if config.dry_run:
        return plan

    project_root = config.project_root.resolve()
    token_dir = resolve_under_root(config.token_dir, project_root)
    start_path = token_dir / "start.json"
    end_path = token_dir / "end.json"
    token_record_path = token_dir / f"{slug(config.job_id)}.tokens.json"

    validation_results: dict[str, Any] = {}
    failure: str | None = None
    write_checkpoint(span_id=slug(config.job_id), event="start", output=start_path)
    try:
        run_checked(
            plan["commands"]["materialize"],
            project_root,
            quiet=config.quiet_runtime_output,
        )
        run_checked(
            plan["commands"]["bridge"],
            project_root,
            quiet=config.quiet_runtime_output,
        )
    finally:
        write_checkpoint(span_id=slug(config.job_id), event="end", output=end_path)
        span_record_from_checkpoints(
            start_path=start_path,
            end_path=end_path,
            output=token_record_path,
            project="agent-workbench",
            phase=config.phase,
            task_id=config.task_id,
            span_kind="copilot-supervisor-graph-run",
        )

    for name, command in (
        ("authority_validation", plan["commands"]["authority_validate"]),
        ("document_audit_verifier", plan["commands"]["document_audit_verify"]),
        ("graph_report_verifier", plan["commands"]["graph_report_verify"]),
    ):
        result = run_captured(command, project_root)
        validation_results[name] = result
        if result["returncode"] != 0 and failure is None:
            failure = f"{name} failed"

    summary = summarize_document_audit_graph_run(
        job_id=config.job_id,
        phase=config.phase,
        task_id=config.task_id,
        plan=plan,
        bridge_report=project_root / plan["paths"]["bridge_report"],
        audit_report=project_root / plan["paths"]["audit_report"],
        graph_report=project_root / plan["paths"]["graph_report"],
        token_record=project_root / plan["paths"]["token_record"],
        validation_results=validation_results,
        failure=failure,
    )
    output = resolve_under_root(config.summary_output, project_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def summarize_existing_document_audit_graph(
    config: DocumentAuditGraphRunConfig,
    *,
    token_record: Path | None = None,
) -> dict[str, Any]:
    """Validate and summarize an already-run document-audit graph job.

    This supports externally measured coordinator-token spans: run the graph
    launcher between separate start/end checkpoints, convert those checkpoints
    into a token record, then summarize existing runtime artifacts against that
    external token record.
    """

    plan = build_run_plan(config)
    project_root = config.project_root.resolve()
    validation_results: dict[str, Any] = {}
    failure: str | None = None
    for name, command in (
        ("authority_validation", plan["commands"]["authority_validate"]),
        ("document_audit_verifier", plan["commands"]["document_audit_verify"]),
        ("graph_report_verifier", plan["commands"]["graph_report_verify"]),
    ):
        result = run_captured(command, project_root)
        validation_results[name] = result
        if result["returncode"] != 0 and failure is None:
            failure = f"{name} failed"

    token_record_path = (
        resolve_under_root(token_record, project_root)
        if token_record is not None
        else project_root / plan["paths"]["token_record"]
    )
    summary = summarize_document_audit_graph_run(
        job_id=config.job_id,
        phase=config.phase,
        task_id=config.task_id,
        plan=plan,
        bridge_report=project_root / plan["paths"]["bridge_report"],
        audit_report=project_root / plan["paths"]["audit_report"],
        graph_report=project_root / plan["paths"]["graph_report"],
        token_record=token_record_path,
        validation_results=validation_results,
        failure=failure,
    )
    if token_record is not None:
        summary["token_costs"]["measurement_boundary"] = "external_coordinator_span"
        summary["token_costs"]["external_token_record"] = repo_relative(
            token_record_path,
            project_root,
        )
    output = resolve_under_root(config.summary_output, project_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def summarize_document_audit_graph_run(
    *,
    job_id: str,
    phase: str,
    task_id: str,
    plan: dict[str, Any],
    bridge_report: Path,
    audit_report: Path,
    graph_report: Path,
    token_record: Path,
    validation_results: dict[str, Any] | None = None,
    failure: str | None = None,
) -> dict[str, Any]:
    bridge = parse_bridge_report(bridge_report)
    audit = load_json_optional(audit_report)
    graph = load_json_optional(graph_report)
    token = load_json(token_record)
    verification = audit.get("verification", {})
    audit_items = verification.get("audit_items", [])
    if not isinstance(audit_items, list):
        audit_items = []
    decisions: dict[str, int] = {}
    for item in audit_items:
        if isinstance(item, dict):
            decision = str(item.get("auditor_decision", ""))
            decisions[decision] = decisions.get(decision, 0) + 1
    usage = token.get("usage", {})
    prices = token.get("prices", {})
    paid_cost = token_cost_usd(usage, prices)
    total_delta = 0
    if isinstance(usage, dict):
        total_delta = int(usage.get("codex_total_token_delta", 0) or 0)
    source_count = len(plan.get("source_summaries", []))
    validation_results = sanitize_validation_results(validation_results or {})
    accepted = (
        bridge.get("status") == "accepted-candidate"
        and all(
            result.get("returncode") == 0
            for result in validation_results.values()
            if isinstance(result, dict)
        )
    )
    status = "accepted-candidate" if accepted else bridge.get("status", "unknown")
    if failure and status == "accepted-candidate":
        status = "validation_failed"
    model_provenance = bridge_model_provenance(
        bridge,
        expected_model=expected_model_from_plan(plan),
    )
    pre_materialized_audit_ticket = bool(plan.get("pre_materialized_audit_ticket"))
    return {
        "summary_id": f"{job_id}_summary",
        "phase": phase,
        "task_id": task_id,
        "status": status,
        "model": model_provenance["authoritative_model"],
        "model_provenance": model_provenance,
        "copilot_permission_level": bridge.get("permission_levels", "unknown"),
        "workflow_graph": graph.get("graph_id", ""),
        "job_id": job_id,
        "source_artifacts": plan.get("source_summaries", []),
        "source_count": source_count,
        "bridge_status": bridge.get("status", "unknown"),
        "final_marker_present": bridge.get("final_marker_present") == "true",
        "subagent_tool_observed": "runSubagent" in bridge.get("tool_names", []),
        "materializer_command_count": bridge.get("observed_commands", "").count(
            "materialize_document_artifact_audit.py"
        ),
        "pre_materialized_audit_ticket": pre_materialized_audit_ticket,
        "accepted_candidate": accepted,
        "failure": failure or "",
        "authority_validation_passed": validation_passed(
            validation_results, "authority_validation"
        ),
        "document_audit_verifier_passed": validation_passed(
            validation_results, "document_audit_verifier"
        ),
        "document_graph_report_verifier_passed": validation_passed(
            validation_results, "graph_report_verifier"
        ),
        "validation_results": validation_results,
        "all_decisions_consistent_with_gate": verification.get(
            "all_decisions_consistent_with_gate"
        ),
        "supervisor_report_score": verification.get("score"),
        "subagent_outcome": {
            "audit_report_status": verification.get("subagent_result_status"),
            "graph_report_status": graph.get("subagent_result", {}).get("status")
            if isinstance(graph.get("subagent_result"), dict)
            else "",
            "repair_required": graph.get("subagent_result", {}).get("repair_required")
            if isinstance(graph.get("subagent_result"), dict)
            else None,
            "summary": graph.get("subagent_result", {}).get("summary", "")
            if isinstance(graph.get("subagent_result"), dict)
            else "",
        },
        "audit_decision_breakdown": decisions,
        "token_costs": {
            "measured_paid_cost_available": True,
            "economics_usable": accepted and total_delta > 0,
            "not_usable_reason": ""
            if accepted and total_delta > 0
            else (
                "Token delta is zero or the run was not accepted; this span is "
                "not usable as paid coordinator economics evidence."
            ),
            "estimated_paid_cost_usd": round(paid_cost, 6),
            "estimated_paid_cost_per_source_artifact_usd": round(
                paid_cost / source_count, 6
            )
            if source_count
            else 0.0,
            **usage,
            "local_copilot_ollama_cash_cost_usd": 0.0,
        },
        "public_safety": {
            "raw_chat_session_paths_excluded": True,
            "raw_transcripts_excluded": True,
            "provider_details_excluded": True,
        },
    }


def parse_bridge_report(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    result: dict[str, Any] = {
        "observed_commands": section_text(text, "Observed Commands"),
        "tool_names": [
            line.removeprefix("- `").removesuffix("`")
            for line in section_text(text, "Tool Names").splitlines()
            if line.startswith("- `")
        ],
    }
    for line in text.splitlines():
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        if key in {
            "status",
            "expected_model",
            "resolved_model",
            "model_match",
            "permission_levels",
            "completed",
            "final_marker_present",
        }:
            result[key] = value.strip()
    return result


def bridge_model_provenance(
    bridge: dict[str, Any],
    *,
    expected_model: str = "",
) -> dict[str, Any]:
    observed = str(bridge.get("resolved_model", "unknown") or "unknown")
    expected = str(bridge.get("expected_model", "") or expected_model or "")
    model_match = str(bridge.get("model_match", "") or "")
    if not model_match and expected:
        model_match = str(model_label_matches(expected, observed)).lower()
    return {
        "expected_model": expected,
        "observed_model": observed,
        "authoritative_model": observed,
        "source": "copilot_chat_bridge_report",
        "match_status": "matched"
        if model_match == "true"
        else ("mismatched" if model_match == "false" else "not_checked"),
        "self_reported_model": "",
        "self_report_status": "not_applicable",
    }


def expected_model_from_plan(plan: dict[str, Any]) -> str:
    commands = plan.get("commands", {})
    if not isinstance(commands, dict):
        return ""
    bridge_command = commands.get("bridge", [])
    if not isinstance(bridge_command, list):
        return ""
    for index, value in enumerate(bridge_command):
        if value == "--expected-model" and index + 1 < len(bridge_command):
            return str(bridge_command[index + 1])
    return ""


def model_label_matches(expected: str, observed: str) -> bool:
    return normalize_model_label(expected) == normalize_model_label(observed)


def normalize_model_label(value: str) -> str:
    return (
        value.strip()
        .removeprefix("ollama-models/Ollama/")
        .removesuffix(":latest")
        .casefold()
    )


def section_text(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    start = text.find("\n", start)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + 1)
    if next_heading < 0:
        return text[start + 1 :]
    return text[start + 1 : next_heading]


def token_cost_usd(usage: Any, prices: Any) -> float:
    if not isinstance(usage, dict) or not isinstance(prices, dict):
        return 0.0
    fresh_input = float(usage.get("supervisor_input_tokens", 0) or 0)
    cached_input = float(usage.get("supervisor_cached_input_tokens", 0) or 0)
    output = float(usage.get("supervisor_output_tokens", 0) or 0)
    reasoning = float(usage.get("supervisor_reasoning_output_tokens", 0) or 0)
    return (
        fresh_input * float(prices.get("supervisor_input_price_per_1m_usd", 0) or 0)
        + cached_input
        * float(prices.get("supervisor_cached_input_price_per_1m_usd", 0) or 0)
        + (output + reasoning)
        * float(prices.get("supervisor_output_price_per_1m_usd", 0) or 0)
    ) / 1_000_000


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_json_optional(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_json(path)


def run_checked(command: list[str], cwd: Path, *, quiet: bool = False) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=command_env(),
        text=True if quiet else None,
        capture_output=quiet,
        check=False,
    )
    if completed.returncode != 0:
        detail = ""
        if quiet:
            stdout = compact_text(completed.stdout or "", limit=800)
            stderr = compact_text(completed.stderr or "", limit=800)
            detail = f"\nstdout: {stdout}\nstderr: {stderr}"
        raise RuntimeError(
            f"command failed with exit code {completed.returncode}: {command}{detail}"
        )


def run_captured(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=command_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": compact_text(completed.stdout),
        "stderr": compact_text(completed.stderr),
    }


def command_env() -> dict[str, str]:
    env = os.environ.copy()
    src_path = str(Path(__file__).resolve().parents[1])
    existing = env.get("PYTHONPATH", "")
    values = [value for value in existing.split(os.pathsep) if value]
    if src_path not in values:
        values.insert(0, src_path)
    env["PYTHONPATH"] = os.pathsep.join(values)
    return env


def validation_passed(results: dict[str, Any], key: str) -> bool:
    result = results.get(key)
    return isinstance(result, dict) and result.get("returncode") == 0


def sanitize_validation_results(results: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in results.items():
        if not isinstance(value, dict):
            continue
        sanitized[key] = {
            item_key: compact_text(item_value) if isinstance(item_value, str) else item_value
            for item_key, item_value in value.items()
        }
    return sanitized


def compact_text(value: str, limit: int = 1000) -> str:
    text = redact_private_paths(value.strip())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def redact_private_paths(value: str) -> str:
    redacted = re.sub(
        r"[A-Za-z]:\\Users\\[^\\\s]+\\Projects\\agent-workbench",
        "<agent-workbench-root>",
        value,
    )
    redacted = re.sub(r"[A-Za-z]:\\Users\\[^\\\s]+", "<user-home>", redacted)
    local_app_data = "App" + "Data"
    redacted = redacted.replace(f"<user-home>\\{local_app_data}", "<local-app-data>")
    redacted = redacted.replace(f"<user-home>/{local_app_data}", "<local-app-data>")
    return redacted


def resolve_under_root(path: Path, root: Path) -> Path:
    if path.is_absolute():
        return path
    return root / path


def repo_relative(path: Path, root: Path) -> str:
    resolved = path if path.is_absolute() else root / path
    try:
        return resolved.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def slug(value: str) -> str:
    return value.replace("_", "-")
