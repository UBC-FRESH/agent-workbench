"""Command-line entrypoint for Agent Workbench local supervisor tools."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .accounting import (
    load_accounting_record,
    render_accounting_markdown,
    synthesize_accounting_markdown,
    validate_accounting_record,
)
from .authority import (
    load_authority_record,
    render_supervisor_job_contract,
    render_supervisor_report,
    validate_supervisor_job_contract,
    validate_supervisor_report,
)
from .benchmark import (
    load_benchmark_record,
    prepare_benchmark_worktrees,
    render_benchmark_markdown,
    validate_benchmark_record,
)
from .behavior_analytics import (
    analyze_archive_manifest,
    load_archive_manifest,
    render_behavior_markdown,
    synthesize_behavior_summaries,
)
from .budget import (
    load_budget_declaration,
    render_budget_validation,
    validate_budget_declaration,
)
from .comparison import render_eval_comparison
from .copilot_archive import CopilotArchiveConfig, archive_copilot_session
from .copilot_agent_profiles import (
    render_agent_profiles_markdown,
    render_profile_catalog_markdown,
    resolve_agent_profiles,
    validate_standard_profile_catalog,
)
from .copilot_health_gate import (
    build_health_gate_report,
    health_gate_report_to_jsonable,
    render_health_gate_markdown,
)
from .copilot_profile_runs import (
    render_profile_run_evidence_markdown,
    summarize_profile_run,
)
from .copilot_task_controller import (
    generate_prompt_file,
    load_run_manifest,
    render_review_packet,
    validate_run_manifest,
)
from .copilot_sdk_bridge import (
    SdkTurnConfig,
    load_sdk_session_manifest,
    monitor_sdk_session,
    render_sdk_compact_transcript_from_manifest,
    render_sdk_monitor_markdown,
    render_sdk_transcript_from_manifest,
    run_live_sdk_turn,
    validate_sdk_session_manifest,
)
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
from .eval_batch import BatchEvalConfig, run_eval_batch
from .experiments import (
    load_experiment_record,
    render_experiment_markdown,
    synthesize_experiment_markdown,
    validate_experiment_record,
)
from .foundry_profile_optimization import (
    build_profile_evaluation_aggregate,
    build_profile_evaluation_dataset,
    build_profile_contract_repair_plan,
    build_profile_optimization_plan,
    load_profile_evaluation_aggregate_json,
    load_profile_evaluation_dataset_jsonl,
    render_profile_evaluation_aggregate_json,
    render_profile_evaluation_aggregate_markdown,
    render_profile_evaluation_dataset_jsonl,
    render_profile_evaluation_dataset_markdown,
    render_profile_contract_repair_plan_json,
    render_profile_contract_repair_plan_markdown,
    render_profile_optimization_plan_markdown,
)
from .graph import (
    FreshForgeGraphUnavailable,
    load_graph_document,
    render_graph_decisions_markdown,
    render_graph_markdown,
    render_graph_validation,
    validate_graph_document,
)
from .heartbeat import (
    load_heartbeat_jsonl,
    render_heartbeat_summary,
    suggest_nudge,
    summarize_heartbeat_records,
    validate_heartbeat_records,
)
from .pilot import (
    PilotPackScaffoldConfig,
    PilotPackTask,
    PilotScaffoldConfig,
    scaffold_pilot,
    scaffold_pilot_pack,
)
from .policy import tune_policy
from .profile_evidence_review import (
    build_profile_evidence_review_contract,
    render_profile_evidence_review_contract_json,
    render_profile_evidence_review_ticket,
)
from .roles import (
    load_role_record,
    render_role_markdown,
    validate_role_record,
)
from .supervisor_graph_run import (
    DocumentAuditGraphRunConfig,
    run_document_audit_graph,
    summarize_existing_document_audit_graph,
)
from .supervisor_tokens import (
    latest_snapshot,
    span_record_from_checkpoints,
    synthesize_supervisor_token_spans,
    write_checkpoint,
)
from .tokens import (
    load_token_record,
    synthesize_graph_token_markdown,
    render_token_markdown,
    synthesize_token_markdown,
    validate_token_record,
)
from .workflow import (
    load_workflow_step,
    render_workflow_markdown,
    validate_workflow_step,
)


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def add_codex_session_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--session-jsonl",
        type=Path,
        default=None,
        help="Explicit Codex session JSONL path. Fails closed if no token_count events exist.",
    )
    parser.add_argument(
        "--session-root",
        type=Path,
        default=None,
        help="Codex sessions root to search when --session-jsonl is omitted.",
    )


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

    copilot_parser = subparsers.add_parser(
        "copilot",
        help="Archive and summarize local VS Code Copilot Chat evidence.",
    )
    copilot_subparsers = copilot_parser.add_subparsers(
        dest="copilot_command",
        required=True,
    )
    copilot_archive_parser = copilot_subparsers.add_parser(
        "archive",
        help="Copy raw Copilot session logs to runtime storage and write a sanitized manifest.",
    )
    copilot_archive_parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path("."),
        help="Workspace root whose VS Code workspaceStorage should be searched.",
    )
    copilot_archive_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Ignored runtime directory for raw session copies and manifest.",
    )
    copilot_archive_parser.add_argument(
        "--code-user-dir",
        type=Path,
        default=None,
        help="VS Code User directory. Defaults to APPDATA/Code/User or ~/.config/Code/User.",
    )
    copilot_archive_parser.add_argument(
        "--run-id",
        default=None,
        help="Optional run id expected to appear in the chat session.",
    )
    copilot_archive_parser.add_argument(
        "--session-id",
        default=None,
        help="Optional exact Copilot/VS Code chat session id.",
    )
    copilot_archive_parser.add_argument(
        "--prompt-marker",
        default=None,
        help="Optional prompt marker expected to appear in the chat session.",
    )
    copilot_archive_parser.add_argument(
        "--max-snippet-chars",
        type=int,
        default=240,
        help="Maximum characters retained per sanitized snippet.",
    )
    copilot_archive_parser.add_argument(
        "--max-snippets",
        type=int,
        default=20,
        help="Maximum sanitized snippets retained per message/tool category.",
    )
    copilot_archive_parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Do not copy raw logs; write only the sanitized manifest.",
    )
    copilot_archive_parser.set_defaults(func=run_copilot_archive)

    copilot_task_validate_parser = copilot_subparsers.add_parser(
        "task-validate",
        help="Validate a Copilot child-task run manifest.",
    )
    copilot_task_validate_parser.add_argument("--manifest", type=Path, required=True)
    copilot_task_validate_parser.set_defaults(func=run_copilot_task_validate)

    copilot_task_prompt_parser = copilot_subparsers.add_parser(
        "task-prompt",
        help="Render the executable prompt for a Copilot child-task run.",
    )
    copilot_task_prompt_parser.add_argument("--manifest", type=Path, required=True)
    copilot_task_prompt_parser.add_argument("--output", type=Path, required=True)
    copilot_task_prompt_parser.set_defaults(func=run_copilot_task_prompt)

    copilot_task_review_parser = copilot_subparsers.add_parser(
        "task-review",
        help="Render a coordinator review packet for one Copilot child-task run.",
    )
    copilot_task_review_parser.add_argument("--manifest", type=Path, required=True)
    copilot_task_review_parser.add_argument("--output", type=Path, required=True)
    copilot_task_review_parser.add_argument("--json-output", type=Path, default=None)
    copilot_task_review_parser.set_defaults(func=run_copilot_task_review)

    copilot_sdk_parser = subparsers.add_parser(
        "copilot-sdk",
        help="Create, resume, send, and validate SDK-owned Copilot sessions.",
    )
    copilot_sdk_subparsers = copilot_sdk_parser.add_subparsers(
        dest="copilot_sdk_command",
        required=True,
    )

    copilot_sdk_validate_parser = copilot_sdk_subparsers.add_parser(
        "validate",
        help="Validate a Copilot SDK session manifest.",
    )
    copilot_sdk_validate_parser.add_argument("--manifest", type=Path, required=True)
    copilot_sdk_validate_parser.add_argument(
        "--allow-missing-ticket",
        action="store_true",
        help="Do not require paths.ticket to exist.",
    )
    copilot_sdk_validate_parser.add_argument(
        "--allow-missing-workspace",
        action="store_true",
        help="Do not require workspace_root to exist.",
    )
    copilot_sdk_validate_parser.set_defaults(func=run_copilot_sdk_validate)

    copilot_sdk_start_parser = copilot_sdk_subparsers.add_parser(
        "start",
        help="Create an SDK-owned session, send the prompt, and record events.",
    )
    add_copilot_sdk_turn_args(copilot_sdk_start_parser)
    copilot_sdk_start_parser.set_defaults(func=run_copilot_sdk_start)

    copilot_sdk_resume_parser = copilot_sdk_subparsers.add_parser(
        "resume-send",
        help="Resume an SDK-owned session, send the prompt, and record events.",
    )
    add_copilot_sdk_turn_args(copilot_sdk_resume_parser)
    copilot_sdk_resume_parser.set_defaults(func=run_copilot_sdk_resume_send)

    copilot_sdk_nudge_parser = copilot_sdk_subparsers.add_parser(
        "nudge",
        help="Resume an SDK-owned session, send a nudge, and record nudge evidence.",
    )
    add_copilot_sdk_turn_args(copilot_sdk_nudge_parser)
    copilot_sdk_nudge_parser.add_argument("--nudge-text", required=True)
    copilot_sdk_nudge_parser.set_defaults(func=run_copilot_sdk_nudge)

    copilot_sdk_monitor_parser = copilot_sdk_subparsers.add_parser(
        "monitor",
        help="Summarize SDK event/nudge logs and classify current session state.",
    )
    copilot_sdk_monitor_parser.add_argument("--manifest", type=Path, required=True)
    copilot_sdk_monitor_parser.add_argument("--output", type=Path, default=None)
    copilot_sdk_monitor_parser.add_argument(
        "--markdown-output", type=Path, default=None
    )
    copilot_sdk_monitor_parser.set_defaults(func=run_copilot_sdk_monitor)

    copilot_sdk_nudge_plan_parser = copilot_sdk_subparsers.add_parser(
        "nudge-plan",
        help="Render the recommended nudge text from the current SDK monitor state.",
    )
    copilot_sdk_nudge_plan_parser.add_argument("--manifest", type=Path, required=True)
    copilot_sdk_nudge_plan_parser.add_argument("--output", type=Path, required=True)
    copilot_sdk_nudge_plan_parser.set_defaults(func=run_copilot_sdk_nudge_plan)

    copilot_sdk_transcript_parser = copilot_sdk_subparsers.add_parser(
        "transcript",
        help="Render a human-readable transcript from an SDK event log.",
    )
    copilot_sdk_transcript_parser.add_argument("--manifest", type=Path, required=True)
    copilot_sdk_transcript_parser.add_argument("--output", type=Path, required=True)
    copilot_sdk_transcript_parser.add_argument(
        "--compact-output",
        type=Path,
        default=None,
        help="Optional second Markdown transcript with compact chat-pane-style summaries.",
    )
    copilot_sdk_transcript_parser.add_argument(
        "--include-system",
        action="store_true",
        help="Include raw system.message events in the transcript.",
    )
    copilot_sdk_transcript_parser.add_argument(
        "--exclude-tools",
        action="store_true",
        help="Omit tool and permission events; render only chat messages.",
    )
    copilot_sdk_transcript_parser.add_argument(
        "--max-text-chars",
        type=int,
        default=4000,
        help="Maximum characters retained per transcript entry; 0 disables truncation.",
    )
    copilot_sdk_transcript_parser.set_defaults(func=run_copilot_sdk_transcript)

    copilot_sdk_profile_validate_parser = copilot_sdk_subparsers.add_parser(
        "profile-validate",
        help="Validate Copilot SDK custom agent profiles declared by a manifest.",
    )
    copilot_sdk_profile_validate_parser.add_argument(
        "--manifest", type=Path, required=True
    )
    copilot_sdk_profile_validate_parser.set_defaults(
        func=run_copilot_sdk_profile_validate
    )

    copilot_sdk_profile_render_parser = copilot_sdk_subparsers.add_parser(
        "profile-render",
        help="Write a public-safe resolved custom agent profile preview.",
    )
    copilot_sdk_profile_render_parser.add_argument(
        "--manifest", type=Path, required=True
    )
    copilot_sdk_profile_render_parser.add_argument("--output", type=Path, required=True)
    copilot_sdk_profile_render_parser.set_defaults(func=run_copilot_sdk_profile_render)

    copilot_sdk_catalog_validate_parser = copilot_sdk_subparsers.add_parser(
        "catalog-validate",
        help="Validate and preview the standard Agent Workbench profile catalog.",
    )
    copilot_sdk_catalog_validate_parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root containing .github/agents. Defaults to auto-detect.",
    )
    copilot_sdk_catalog_validate_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional Markdown preview output path.",
    )
    copilot_sdk_catalog_validate_parser.set_defaults(
        func=run_copilot_sdk_catalog_validate
    )

    copilot_sdk_profile_run_parser = copilot_sdk_subparsers.add_parser(
        "profile-run-summary",
        help="Summarize profile-selected SDK run evidence from a manifest.",
    )
    copilot_sdk_profile_run_parser.add_argument("--manifest", type=Path, required=True)
    copilot_sdk_profile_run_parser.add_argument("--output", type=Path, required=True)
    copilot_sdk_profile_run_parser.set_defaults(func=run_copilot_sdk_profile_run)

    copilot_sdk_health_gate_parser = copilot_sdk_subparsers.add_parser(
        "health-gate",
        help="Render a controller/session health go/no-go report from SDK manifests.",
    )
    copilot_sdk_health_gate_parser.add_argument(
        "--manifest",
        type=Path,
        action="append",
        required=True,
        help="SDK session manifest path. May be repeated.",
    )
    copilot_sdk_health_gate_parser.add_argument(
        "--required-count",
        type=int,
        default=None,
        help="Optional minimum manifest count required for a go decision.",
    )
    copilot_sdk_health_gate_parser.add_argument(
        "--json-output",
        type=Path,
        required=True,
    )
    copilot_sdk_health_gate_parser.add_argument(
        "--markdown-output",
        type=Path,
        required=True,
    )
    copilot_sdk_health_gate_parser.set_defaults(func=run_copilot_sdk_health_gate)

    foundrytk_parser = subparsers.add_parser(
        "foundrytk",
        help="Plan FoundryTK-style profile optimization experiments.",
    )
    foundrytk_subparsers = foundrytk_parser.add_subparsers(
        dest="foundrytk_command",
        required=True,
    )
    foundrytk_profile_plan_parser = foundrytk_subparsers.add_parser(
        "profile-optimization-plan",
        help="Render a public-safe profile optimization plan from SDK manifests.",
    )
    foundrytk_profile_plan_parser.add_argument(
        "--manifest",
        type=Path,
        action="append",
        required=True,
        help="SDK session manifest path. May be repeated.",
    )
    foundrytk_profile_plan_parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root for resolving standard Agent Workbench profiles and overlays.",
    )
    foundrytk_profile_plan_parser.add_argument("--output", type=Path, required=True)
    foundrytk_profile_plan_parser.set_defaults(
        func=run_foundrytk_profile_optimization_plan
    )

    foundrytk_dataset_parser = foundrytk_subparsers.add_parser(
        "profile-evaluation-dataset",
        help="Render public-safe profile evaluation dataset rows from SDK manifests.",
    )
    foundrytk_dataset_parser.add_argument(
        "--manifest",
        type=Path,
        action="append",
        required=True,
        help="SDK session manifest path. May be repeated.",
    )
    foundrytk_dataset_parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root for resolving standard Agent Workbench profiles and overlays.",
    )
    foundrytk_dataset_parser.add_argument("--jsonl-output", type=Path, required=True)
    foundrytk_dataset_parser.add_argument(
        "--markdown-output",
        type=Path,
        required=True,
    )
    foundrytk_dataset_parser.set_defaults(func=run_foundrytk_profile_dataset)

    foundrytk_aggregate_parser = foundrytk_subparsers.add_parser(
        "profile-evaluation-aggregate",
        help="Aggregate public-safe profile evaluation JSONL rows.",
    )
    foundrytk_aggregate_parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Profile evaluation JSONL dataset path.",
    )
    foundrytk_aggregate_parser.add_argument("--json-output", type=Path, required=True)
    foundrytk_aggregate_parser.add_argument(
        "--markdown-output",
        type=Path,
        required=True,
    )
    foundrytk_aggregate_parser.set_defaults(func=run_foundrytk_profile_aggregate)

    foundrytk_repair_plan_parser = foundrytk_subparsers.add_parser(
        "profile-contract-repair-plan",
        help="Render a repair plan from public-safe profile aggregate JSON.",
    )
    foundrytk_repair_plan_parser.add_argument(
        "--aggregate",
        type=Path,
        required=True,
        help="Profile evaluation aggregate JSON summary path.",
    )
    foundrytk_repair_plan_parser.add_argument("--json-output", type=Path, required=True)
    foundrytk_repair_plan_parser.add_argument(
        "--markdown-output",
        type=Path,
        required=True,
    )
    foundrytk_repair_plan_parser.set_defaults(
        func=run_foundrytk_profile_contract_repair_plan
    )

    foundrytk_evidence_ticket_parser = foundrytk_subparsers.add_parser(
        "profile-evidence-review-ticket",
        help="Render a repaired profile-evidence-review ticket from an SDK manifest.",
    )
    foundrytk_evidence_ticket_parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="SDK manifest with a pre-existing review subject path.",
    )
    foundrytk_evidence_ticket_parser.add_argument(
        "--ticket-output",
        type=Path,
        required=True,
    )
    foundrytk_evidence_ticket_parser.add_argument(
        "--json-output",
        type=Path,
        required=True,
    )
    foundrytk_evidence_ticket_parser.add_argument(
        "--allow-missing-subject",
        action="store_true",
        help="Render even when the declared review subject does not exist.",
    )
    foundrytk_evidence_ticket_parser.set_defaults(
        func=run_foundrytk_profile_evidence_review_ticket
    )

    heartbeat_parser = subparsers.add_parser(
        "heartbeat",
        help="Validate and summarize delegated-run heartbeat JSONL files.",
    )
    heartbeat_subparsers = heartbeat_parser.add_subparsers(
        dest="heartbeat_command",
        required=True,
    )
    heartbeat_validate_parser = heartbeat_subparsers.add_parser(
        "validate",
        help="Validate a delegated-run heartbeat JSONL file.",
    )
    heartbeat_validate_parser.add_argument("--input", type=Path, required=True)
    heartbeat_validate_parser.set_defaults(func=run_heartbeat_validate)

    heartbeat_summarize_parser = heartbeat_subparsers.add_parser(
        "summarize",
        help="Summarize heartbeat freshness and nudge state.",
    )
    heartbeat_summarize_parser.add_argument("--input", type=Path, required=True)
    heartbeat_summarize_parser.add_argument("--output", type=Path, required=True)
    heartbeat_summarize_parser.add_argument(
        "--markdown-output",
        type=Path,
        default=None,
        help="Optional Markdown summary path.",
    )
    heartbeat_summarize_parser.add_argument(
        "--stale-after-seconds",
        type=int,
        default=900,
    )
    heartbeat_summarize_parser.set_defaults(func=run_heartbeat_summarize)

    nudge_parser = subparsers.add_parser(
        "nudge",
        help="Render a targeted nudge from a heartbeat summary JSON file.",
    )
    nudge_subparsers = nudge_parser.add_subparsers(
        dest="nudge_command",
        required=True,
    )
    nudge_suggest_parser = nudge_subparsers.add_parser(
        "suggest",
        help="Render the recommended delegated-run nudge message.",
    )
    nudge_suggest_parser.add_argument("--summary", type=Path, required=True)
    nudge_suggest_parser.add_argument("--output", type=Path, required=True)
    nudge_suggest_parser.set_defaults(func=run_nudge_suggest)

    behavior_parser = subparsers.add_parser(
        "behavior",
        help="Analyze sanitized Copilot archive manifests for delegation behavior.",
    )
    behavior_subparsers = behavior_parser.add_subparsers(
        dest="behavior_command",
        required=True,
    )
    behavior_analyze_parser = behavior_subparsers.add_parser(
        "analyze",
        help="Analyze one sanitized Copilot archive manifest.",
    )
    behavior_analyze_parser.add_argument("--input", type=Path, required=True)
    behavior_analyze_parser.add_argument("--output", type=Path, required=True)
    behavior_analyze_parser.add_argument("--markdown-output", type=Path, required=True)
    behavior_analyze_parser.set_defaults(func=run_behavior_analyze)

    behavior_synthesize_parser = behavior_subparsers.add_parser(
        "synthesize",
        help="Synthesize multiple behavior summary JSON files.",
    )
    behavior_synthesize_parser.add_argument(
        "--input",
        type=Path,
        action="append",
        default=[],
    )
    behavior_synthesize_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing *.behavior.json files.",
    )
    behavior_synthesize_parser.add_argument("--output", type=Path, required=True)
    behavior_synthesize_parser.add_argument("--json-output", type=Path, required=True)
    behavior_synthesize_parser.set_defaults(func=run_behavior_synthesize)

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

    eval_batch_parser = subparsers.add_parser(
        "eval-batch",
        help="Quietly run or summarize a directory of SDK eval manifests.",
    )
    eval_batch_parser.add_argument("--manifest-dir", type=Path, required=True)
    eval_batch_parser.add_argument("--pattern", default="**/*.manifest.json")
    eval_batch_parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Optional target project root used for cross-project manifests.",
    )
    eval_batch_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Ignored directory for compact batch logs and summaries.",
    )
    eval_batch_parser.add_argument("--dry-run", action="store_true")
    eval_batch_parser.add_argument("--summary-only", action="store_true")
    eval_batch_parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue running remaining manifests after a nonzero eval exit.",
    )
    eval_batch_parser.set_defaults(func=run_eval_batch_command)

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

    accounting_parser = subparsers.add_parser(
        "accounting",
        help="Validate, render, or synthesize pilot accounting records.",
    )
    accounting_subparsers = accounting_parser.add_subparsers(
        dest="accounting_command",
        required=True,
    )

    accounting_validate_parser = accounting_subparsers.add_parser(
        "validate",
        help="Validate a sanitized pilot accounting JSON record.",
    )
    accounting_validate_parser.add_argument("--input", type=Path, required=True)
    accounting_validate_parser.set_defaults(func=run_accounting_validate)

    accounting_render_parser = accounting_subparsers.add_parser(
        "render",
        help="Render a pilot accounting JSON record to Markdown.",
    )
    accounting_render_parser.add_argument("--input", type=Path, required=True)
    accounting_render_parser.add_argument("--output", type=Path, required=True)
    accounting_render_parser.set_defaults(func=run_accounting_render)

    accounting_synthesize_parser = accounting_subparsers.add_parser(
        "synthesize",
        help="Synthesize multiple pilot accounting records into one report.",
    )
    accounting_synthesize_parser.add_argument(
        "--input", type=Path, action="append", default=[]
    )
    accounting_synthesize_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing *.accounting.json files.",
    )
    accounting_synthesize_parser.add_argument("--output", type=Path, required=True)
    accounting_synthesize_parser.set_defaults(func=run_accounting_synthesize)

    policy_parser = subparsers.add_parser(
        "policy",
        help="Tune delegation policy from pilot accounting records.",
    )
    policy_subparsers = policy_parser.add_subparsers(
        dest="policy_command",
        required=True,
    )

    policy_tune_parser = policy_subparsers.add_parser(
        "tune",
        help="Render transparent policy tuning guidance from accounting records.",
    )
    policy_tune_parser.add_argument("--input", type=Path, action="append", default=[])
    policy_tune_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing *.accounting.json files.",
    )
    policy_tune_parser.add_argument("--output", type=Path, required=True)
    policy_tune_parser.set_defaults(func=run_policy_tune)

    authority_parser = subparsers.add_parser(
        "authority",
        help="Validate or render supervisor job contracts and reports.",
    )
    authority_subparsers = authority_parser.add_subparsers(
        dest="authority_command",
        required=True,
    )

    authority_validate_parser = authority_subparsers.add_parser(
        "validate",
        help="Validate an authority hierarchy contract or supervisor report.",
    )
    authority_validate_parser.add_argument(
        "--kind",
        choices=("contract", "report"),
        required=True,
    )
    authority_validate_parser.add_argument("--input", type=Path, required=True)
    authority_validate_parser.set_defaults(func=run_authority_validate)

    authority_render_parser = authority_subparsers.add_parser(
        "render",
        help="Render an authority hierarchy contract or supervisor report.",
    )
    authority_render_parser.add_argument(
        "--kind",
        choices=("contract", "report"),
        required=True,
    )
    authority_render_parser.add_argument("--input", type=Path, required=True)
    authority_render_parser.add_argument("--output", type=Path, required=True)
    authority_render_parser.set_defaults(func=run_authority_render)

    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Validate or render artifact-first workflow step records.",
    )
    workflow_subparsers = workflow_parser.add_subparsers(
        dest="workflow_command",
        required=True,
    )

    workflow_validate_parser = workflow_subparsers.add_parser(
        "validate",
        help="Validate a workflow step JSON record.",
    )
    workflow_validate_parser.add_argument("--input", type=Path, required=True)
    workflow_validate_parser.set_defaults(func=run_workflow_validate)

    workflow_render_parser = workflow_subparsers.add_parser(
        "render",
        help="Render a workflow step JSON record to Markdown.",
    )
    workflow_render_parser.add_argument("--input", type=Path, required=True)
    workflow_render_parser.add_argument("--output", type=Path, required=True)
    workflow_render_parser.set_defaults(func=run_workflow_render)

    roles_parser = subparsers.add_parser(
        "roles",
        help="Validate or render role/capability/implementation records.",
    )
    roles_subparsers = roles_parser.add_subparsers(
        dest="roles_command",
        required=True,
    )

    roles_validate_parser = roles_subparsers.add_parser(
        "validate",
        help="Validate a role/capability/implementation JSON record.",
    )
    roles_validate_parser.add_argument("--input", type=Path, required=True)
    roles_validate_parser.set_defaults(func=run_roles_validate)

    roles_render_parser = roles_subparsers.add_parser(
        "render",
        help="Render a role/capability/implementation JSON record to Markdown.",
    )
    roles_render_parser.add_argument("--input", type=Path, required=True)
    roles_render_parser.add_argument("--output", type=Path, required=True)
    roles_render_parser.set_defaults(func=run_roles_render)

    tokens_parser = subparsers.add_parser(
        "tokens",
        help="Validate, render, or synthesize sanitized token/cost records.",
    )
    tokens_subparsers = tokens_parser.add_subparsers(
        dest="tokens_command",
        required=True,
    )

    tokens_validate_parser = tokens_subparsers.add_parser(
        "validate",
        help="Validate a sanitized token/cost JSON record.",
    )
    tokens_validate_parser.add_argument("--input", type=Path, required=True)
    tokens_validate_parser.set_defaults(func=run_tokens_validate)

    tokens_render_parser = tokens_subparsers.add_parser(
        "render",
        help="Render a sanitized token/cost JSON record to Markdown.",
    )
    tokens_render_parser.add_argument("--input", type=Path, required=True)
    tokens_render_parser.add_argument("--output", type=Path, required=True)
    tokens_render_parser.set_defaults(func=run_tokens_render)

    tokens_synthesize_parser = tokens_subparsers.add_parser(
        "synthesize",
        help="Synthesize sanitized token/cost records.",
    )
    tokens_synthesize_parser.add_argument(
        "--input", type=Path, action="append", default=[]
    )
    tokens_synthesize_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing *.tokens.json files.",
    )
    tokens_synthesize_parser.add_argument("--output", type=Path, required=True)
    tokens_synthesize_parser.set_defaults(func=run_tokens_synthesize)

    tokens_graph_synthesize_parser = tokens_subparsers.add_parser(
        "graph-synthesize",
        help="Synthesize sanitized token/cost records by graph node.",
    )
    tokens_graph_synthesize_parser.add_argument(
        "--input", type=Path, action="append", default=[]
    )
    tokens_graph_synthesize_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing *.tokens.json files.",
    )
    tokens_graph_synthesize_parser.add_argument("--output", type=Path, required=True)
    tokens_graph_synthesize_parser.set_defaults(func=run_tokens_graph_synthesize)

    supervisor_tokens_parser = subparsers.add_parser(
        "supervisor-tokens",
        help="Capture Codex supervisor-token checkpoints and span records.",
    )
    supervisor_tokens_subparsers = supervisor_tokens_parser.add_subparsers(
        dest="supervisor_tokens_command",
        required=True,
    )

    supervisor_tokens_latest_parser = supervisor_tokens_subparsers.add_parser(
        "latest",
        help="Print the latest Codex token_count snapshot.",
    )
    add_codex_session_args(supervisor_tokens_latest_parser)
    supervisor_tokens_latest_parser.set_defaults(func=run_supervisor_tokens_latest)

    supervisor_tokens_checkpoint_parser = supervisor_tokens_subparsers.add_parser(
        "checkpoint",
        help="Write a start/end checkpoint from the latest Codex token_count event.",
    )
    supervisor_tokens_checkpoint_parser.add_argument("--span", required=True)
    supervisor_tokens_checkpoint_parser.add_argument(
        "--event",
        choices=("start", "end"),
        required=True,
    )
    supervisor_tokens_checkpoint_parser.add_argument(
        "--output", type=Path, required=True
    )
    add_codex_session_args(supervisor_tokens_checkpoint_parser)
    supervisor_tokens_checkpoint_parser.set_defaults(
        func=run_supervisor_tokens_checkpoint
    )

    supervisor_tokens_span_parser = supervisor_tokens_subparsers.add_parser(
        "span",
        help="Convert start/end checkpoints into a sanitized token/cost record.",
    )
    supervisor_tokens_span_parser.add_argument("--start", type=Path, required=True)
    supervisor_tokens_span_parser.add_argument("--end", type=Path, required=True)
    supervisor_tokens_span_parser.add_argument("--output", type=Path, required=True)
    supervisor_tokens_span_parser.add_argument("--project", default="agent-workbench")
    supervisor_tokens_span_parser.add_argument("--phase", default="")
    supervisor_tokens_span_parser.add_argument("--task-id", default="")
    supervisor_tokens_span_parser.add_argument("--span-kind", default="")
    supervisor_tokens_span_parser.add_argument(
        "--supervisor-input-price-per-1m-usd",
        type=float,
        default=1.75,
    )
    supervisor_tokens_span_parser.add_argument(
        "--supervisor-cached-input-price-per-1m-usd",
        type=float,
        default=0.175,
    )
    supervisor_tokens_span_parser.add_argument(
        "--supervisor-output-price-per-1m-usd",
        type=float,
        default=14.0,
    )
    supervisor_tokens_span_parser.set_defaults(func=run_supervisor_tokens_span)

    supervisor_tokens_synthesize_parser = supervisor_tokens_subparsers.add_parser(
        "synthesize",
        help="Synthesize supervisor-token span records in a runtime ledger directory.",
    )
    supervisor_tokens_synthesize_parser.add_argument(
        "--input-dir", type=Path, required=True
    )
    supervisor_tokens_synthesize_parser.add_argument(
        "--output", type=Path, required=True
    )
    supervisor_tokens_synthesize_parser.set_defaults(
        func=run_supervisor_tokens_synthesize
    )

    supervisor_parser = subparsers.add_parser(
        "supervisor",
        help="Run packaged local-supervisor workflows.",
    )
    supervisor_subparsers = supervisor_parser.add_subparsers(
        dest="supervisor_command",
        required=True,
    )

    supervisor_budget_parser = supervisor_subparsers.add_parser(
        "budget",
        help="Validate paid-supervisor benchmark budget declarations.",
    )
    supervisor_budget_subparsers = supervisor_budget_parser.add_subparsers(
        dest="supervisor_budget_command",
        required=True,
    )
    supervisor_budget_validate_parser = supervisor_budget_subparsers.add_parser(
        "validate",
        help="Validate a benchmark budget declaration.",
    )
    supervisor_budget_validate_parser.add_argument("--input", type=Path, required=True)
    supervisor_budget_validate_parser.add_argument("--output", type=Path, default=None)
    supervisor_budget_validate_parser.set_defaults(func=run_supervisor_budget_validate)

    supervisor_document_audit_parser = supervisor_subparsers.add_parser(
        "run-document-audit-graph",
        help="Run a packaged document-artifact audit graph through Copilot supervisor.",
    )
    supervisor_document_audit_parser.add_argument("--job-id", required=True)
    supervisor_document_audit_parser.add_argument("--marker", required=True)
    supervisor_document_audit_parser.add_argument("--phase", default="P57")
    supervisor_document_audit_parser.add_argument("--task-id", default="P57.4")
    supervisor_document_audit_parser.add_argument("--title", required=True)
    supervisor_document_audit_parser.add_argument(
        "--source-summary",
        action="append",
        required=True,
        help="Source summary JSON path. May be repeated.",
    )
    supervisor_document_audit_parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
    )
    supervisor_document_audit_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runtime/agent_jobs"),
    )
    supervisor_document_audit_parser.add_argument(
        "--token-dir",
        type=Path,
        default=None,
        help="Runtime token ledger directory. Defaults under runtime/supervisor_tokens.",
    )
    supervisor_document_audit_parser.add_argument(
        "--budget-record",
        type=Path,
        default=None,
        help=(
            "Required for live runs. Valid benchmark budget declaration used to "
            "gate paid-supervisor economics evidence."
        ),
    )
    supervisor_document_audit_parser.add_argument(
        "--summary-output",
        type=Path,
        required=True,
        help="Sanitized summary JSON output path.",
    )
    supervisor_document_audit_parser.add_argument(
        "--mode",
        default="agent-workbench-local-supervisor",
    )
    supervisor_document_audit_parser.add_argument("--code-command", default="code")
    supervisor_document_audit_parser.add_argument(
        "--bridge-prompt",
        default=None,
        help="Override the one-line prompt passed to code chat.",
    )
    supervisor_document_audit_parser.add_argument(
        "--expected-model",
        default=None,
        help="Require the Copilot bridge to observe this resolved model.",
    )
    supervisor_document_audit_parser.add_argument(
        "--pre-materialize-audit-ticket",
        action="store_true",
        default=True,
        help=(
            "Coordinator-materialize the lower-level audit ticket before launching "
            "Copilot, so the local supervisor starts at audit/report/repair nodes."
        ),
    )
    supervisor_document_audit_parser.add_argument(
        "--no-pre-materialize-audit-ticket",
        action="store_false",
        dest="pre_materialize_audit_ticket",
        help=(
            "Legacy/debug mode: expose setup/materializer work to the local "
            "supervisor ticket."
        ),
    )
    supervisor_document_audit_parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=1800,
    )
    supervisor_document_audit_parser.add_argument(
        "--poll-seconds",
        type=float,
        default=10.0,
    )
    supervisor_document_audit_parser.add_argument("--dry-run", action="store_true")
    supervisor_document_audit_parser.add_argument(
        "--bridge-no-launch",
        action="store_true",
        help="Parse an existing Copilot session instead of launching a new one.",
    )
    supervisor_document_audit_parser.add_argument(
        "--quiet-runtime-output",
        action="store_true",
        default=True,
        help=(
            "Capture materializer and bridge stdout/stderr instead of printing "
            "large runtime reports into the coordinator shell."
        ),
    )
    supervisor_document_audit_parser.add_argument(
        "--loud-runtime-output",
        action="store_false",
        dest="quiet_runtime_output",
        help="Legacy/debug mode: stream materializer and bridge output.",
    )
    supervisor_document_audit_parser.set_defaults(
        func=run_supervisor_document_audit_graph
    )

    supervisor_document_audit_summary_parser = supervisor_subparsers.add_parser(
        "summarize-document-audit-graph",
        help=(
            "Validate and summarize an existing document-artifact audit graph "
            "run, optionally using an externally captured token record."
        ),
    )
    supervisor_document_audit_summary_parser.add_argument("--job-id", required=True)
    supervisor_document_audit_summary_parser.add_argument("--marker", required=True)
    supervisor_document_audit_summary_parser.add_argument("--phase", default="P57")
    supervisor_document_audit_summary_parser.add_argument("--task-id", default="P57.4")
    supervisor_document_audit_summary_parser.add_argument("--title", required=True)
    supervisor_document_audit_summary_parser.add_argument(
        "--source-summary",
        action="append",
        required=True,
        help="Source summary JSON path. May be repeated.",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runtime/agent_jobs"),
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--token-dir",
        type=Path,
        default=None,
        help="Runtime token ledger directory. Defaults under runtime/supervisor_tokens.",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--token-record",
        type=Path,
        default=None,
        help=(
            "Optional externally captured token record to use instead of the "
            "launcher-contained token record."
        ),
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--budget-record",
        type=Path,
        default=None,
        help=(
            "Required to summarize graph runs as economics evidence. Valid "
            "benchmark budget declaration for this run."
        ),
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--summary-output",
        type=Path,
        required=True,
        help="Sanitized summary JSON output path.",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--mode",
        default="agent-workbench-local-supervisor",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--code-command", default="code"
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--bridge-prompt",
        default=None,
        help="Recorded prompt override for run-plan reconstruction.",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--expected-model",
        default=None,
        help="Expected bridge-observed model used for provenance reporting.",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--pre-materialize-audit-ticket",
        action="store_true",
        default=True,
        help="Reconstruct the plan as a pre-materialized-audit-ticket run.",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--no-pre-materialize-audit-ticket",
        action="store_false",
        dest="pre_materialize_audit_ticket",
        help="Reconstruct the plan as a legacy self-materialized run.",
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=1800,
    )
    supervisor_document_audit_summary_parser.add_argument(
        "--poll-seconds",
        type=float,
        default=10.0,
    )
    supervisor_document_audit_summary_parser.set_defaults(
        func=run_supervisor_document_audit_graph_summary
    )

    experiments_parser = subparsers.add_parser(
        "experiments",
        help="Validate, render, or synthesize delegation experiment records.",
    )
    experiments_subparsers = experiments_parser.add_subparsers(
        dest="experiments_command",
        required=True,
    )

    experiments_validate_parser = experiments_subparsers.add_parser(
        "validate",
        help="Validate a sanitized delegation experiment JSON record.",
    )
    experiments_validate_parser.add_argument("--input", type=Path, required=True)
    experiments_validate_parser.set_defaults(func=run_experiments_validate)

    experiments_render_parser = experiments_subparsers.add_parser(
        "render",
        help="Render a delegation experiment JSON record to Markdown.",
    )
    experiments_render_parser.add_argument("--input", type=Path, required=True)
    experiments_render_parser.add_argument("--output", type=Path, required=True)
    experiments_render_parser.set_defaults(func=run_experiments_render)

    experiments_synthesize_parser = experiments_subparsers.add_parser(
        "synthesize",
        help="Synthesize multiple delegation experiment records.",
    )
    experiments_synthesize_parser.add_argument(
        "--input", type=Path, action="append", default=[]
    )
    experiments_synthesize_parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing *.experiment.json files.",
    )
    experiments_synthesize_parser.add_argument("--output", type=Path, required=True)
    experiments_synthesize_parser.set_defaults(func=run_experiments_synthesize)

    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Validate or render phase-scale A/B benchmark records.",
    )
    benchmark_subparsers = benchmark_parser.add_subparsers(
        dest="benchmark_command",
        required=True,
    )

    benchmark_validate_parser = benchmark_subparsers.add_parser(
        "validate",
        help="Validate a phase-scale A/B benchmark JSON record.",
    )
    benchmark_validate_parser.add_argument("--input", type=Path, required=True)
    benchmark_validate_parser.set_defaults(func=run_benchmark_validate)

    benchmark_render_parser = benchmark_subparsers.add_parser(
        "render",
        help="Render a phase-scale A/B benchmark JSON record to Markdown.",
    )
    benchmark_render_parser.add_argument("--input", type=Path, required=True)
    benchmark_render_parser.add_argument("--output", type=Path, required=True)
    benchmark_render_parser.set_defaults(func=run_benchmark_render)

    benchmark_prepare_parser = benchmark_subparsers.add_parser(
        "prepare-worktrees",
        help="Prepare benchmark lane worktrees in a target project checkout.",
    )
    benchmark_prepare_parser.add_argument("--input", type=Path, required=True)
    benchmark_prepare_parser.add_argument(
        "--project-root",
        type=Path,
        required=True,
        help="Target project checkout where benchmark lanes will be prepared.",
    )
    benchmark_prepare_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional Markdown report path.",
    )
    benchmark_prepare_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the worktree commands without running them.",
    )
    benchmark_prepare_parser.set_defaults(func=run_benchmark_prepare_worktrees)

    graph_parser = subparsers.add_parser(
        "graph",
        help="Validate FreshForge-compatible agentic workflow graphs.",
    )
    graph_subparsers = graph_parser.add_subparsers(
        dest="graph_command",
        required=True,
    )

    graph_validate_parser = graph_subparsers.add_parser(
        "validate",
        help="Validate graph structure without executing workflow nodes.",
    )
    graph_validate_parser.add_argument("--input", type=Path, required=True)
    graph_validate_parser.add_argument(
        "--agent-metadata",
        action="store_true",
        help="Also validate Agent Workbench metadata convention fields.",
    )
    graph_validate_parser.set_defaults(func=run_graph_validate)

    graph_render_parser = graph_subparsers.add_parser(
        "render",
        help="Render a graph document to a supervisor-readable Markdown summary.",
    )
    graph_render_parser.add_argument("--input", type=Path, required=True)
    graph_render_parser.add_argument("--output", type=Path, required=True)
    graph_render_parser.add_argument(
        "--agent-metadata",
        action="store_true",
        help="Validate Agent Workbench metadata before rendering.",
    )
    graph_render_parser.set_defaults(func=run_graph_render)

    graph_decide_parser = graph_subparsers.add_parser(
        "decide",
        help="Render graph-node delegation recommendations.",
    )
    graph_decide_parser.add_argument("--input", type=Path, required=True)
    graph_decide_parser.add_argument("--output", type=Path, required=True)
    graph_decide_parser.add_argument(
        "--agent-metadata",
        action="store_true",
        help="Validate Agent Workbench metadata before deciding.",
    )
    graph_decide_parser.set_defaults(func=run_graph_decide)

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
    evidence_subparsers = evidence_parser.add_subparsers(
        dest="evidence_command", required=True
    )

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


def add_copilot_sdk_turn_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", type=Path, required=True)
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument("--prompt", default=None)
    prompt_group.add_argument("--prompt-file", type=Path, default=None)
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=None,
        help="Override manifest control.stall_seconds for this turn.",
    )
    parser.add_argument(
        "--no-update-manifest",
        action="store_true",
        help="Write event/status outputs without updating the manifest state.",
    )


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


def run_copilot_archive(args: argparse.Namespace) -> int:
    config = CopilotArchiveConfig(
        workspace_root=args.workspace_root,
        output_dir=args.output_dir,
        code_user_dir=args.code_user_dir,
        run_id=args.run_id,
        session_id=args.session_id,
        prompt_marker=args.prompt_marker,
        max_snippet_chars=args.max_snippet_chars,
        max_snippets=args.max_snippets,
        copy_raw=not args.manifest_only,
    )
    try:
        manifest = archive_copilot_session(config)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    manifest_path = args.output_dir / str(manifest.get("manifest_path", ""))
    print(f"manifest: {manifest_path}")
    for raw_file in manifest.get("raw_files", []):
        print(f"raw: {args.output_dir / str(raw_file)}")
    print(
        "session_id={session_id} user_messages={user_messages} "
        "assistant_messages={assistant_messages} tool_requests={tool_requests}".format(
            session_id=manifest.get("session_id", ""),
            user_messages=manifest.get("user_message_count", 0),
            assistant_messages=manifest.get("assistant_message_count_with_text", 0),
            tool_requests=manifest.get("tool_request_count", 0),
        )
    )
    return 0


def run_copilot_task_validate(args: argparse.Namespace) -> int:
    try:
        data = load_run_manifest(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_run_manifest(data, manifest_path=args.manifest)
    if result.ok:
        print(f"valid Copilot task manifest: {args.manifest}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_copilot_task_prompt(args: argparse.Namespace) -> int:
    try:
        result = generate_prompt_file(args.manifest, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {args.output}")
    print(f"launch_command: {result.get('launch_command', '')}")
    return 0


def run_copilot_task_review(args: argparse.Namespace) -> int:
    try:
        packet = render_review_packet(args.manifest, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {args.output}")
    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(packet, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.json_output}")
    return 0


def run_copilot_sdk_validate(args: argparse.Namespace) -> int:
    try:
        data = load_sdk_session_manifest(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_sdk_session_manifest(
        data,
        manifest_path=args.manifest,
        require_existing_ticket=not args.allow_missing_ticket,
        require_existing_workspace=not args.allow_missing_workspace,
    )
    if result.ok:
        print(f"valid Copilot SDK session manifest: {args.manifest}")
        for warning in result.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_copilot_sdk_start(args: argparse.Namespace) -> int:
    return run_copilot_sdk_turn(args, resume=False, nudge_text=None)


def run_copilot_sdk_resume_send(args: argparse.Namespace) -> int:
    return run_copilot_sdk_turn(args, resume=True, nudge_text=None)


def run_copilot_sdk_nudge(args: argparse.Namespace) -> int:
    return run_copilot_sdk_turn(args, resume=True, nudge_text=args.nudge_text)


def run_copilot_sdk_turn(
    args: argparse.Namespace,
    *,
    resume: bool,
    nudge_text: str | None,
) -> int:
    config = SdkTurnConfig(
        manifest_path=args.manifest,
        prompt_text=nudge_text or args.prompt,
        prompt_path=args.prompt_file,
        resume=resume,
        nudge_text=nudge_text,
        timeout_seconds=args.timeout_seconds,
        update_manifest=not args.no_update_manifest,
    )
    try:
        summary = asyncio.run(run_live_sdk_turn(config))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        "session_id={session_id} status={status} events={events}".format(
            session_id=summary.get("session_id", ""),
            status=summary.get("latest_status", ""),
            events=summary.get("event_count", 0),
        )
    )
    if summary.get("blocker"):
        print(f"blocker={summary['blocker']}")
        return 2
    return 0


def run_copilot_sdk_monitor(args: argparse.Namespace) -> int:
    try:
        summary = monitor_sdk_session(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    if args.markdown_output is not None:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(
            render_sdk_monitor_markdown(summary), encoding="utf-8"
        )
        print(f"wrote {args.markdown_output}")
    print(
        "session_id={session_id} status={status} action={action}".format(
            session_id=summary.get("session_id", ""),
            status=summary.get("latest_status", ""),
            action=summary.get("recommended_coordinator_action", ""),
        )
    )
    return 2 if summary.get("stop_rule_triggered") else 0


def run_copilot_sdk_nudge_plan(args: argparse.Namespace) -> int:
    try:
        summary = monitor_sdk_session(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        str(summary.get("recommended_nudge", "")) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.output}")
    return 2 if summary.get("stop_rule_triggered") else 0


def run_copilot_sdk_transcript(args: argparse.Namespace) -> int:
    try:
        transcript, summary = render_sdk_transcript_from_manifest(
            args.manifest,
            include_system=args.include_system,
            include_tools=not args.exclude_tools,
            max_text_chars=args.max_text_chars,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(transcript, encoding="utf-8")
    print(f"wrote {args.output}")
    if args.compact_output is not None:
        try:
            compact_transcript, compact_summary = (
                render_sdk_compact_transcript_from_manifest(
                    args.manifest,
                    include_system=args.include_system,
                    include_tools=not args.exclude_tools,
                    max_text_chars=args.max_text_chars,
                )
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        args.compact_output.parent.mkdir(parents=True, exist_ok=True)
        args.compact_output.write_text(compact_transcript, encoding="utf-8")
        print(
            "wrote {path} compact_entries={entries}".format(
                path=args.compact_output,
                entries=compact_summary.entry_count,
            )
        )
    print(
        "session_id={session_id} entries={entries} user_messages={users} "
        "assistant_messages={assistants} tool_events={tools}".format(
            session_id=summary.session_id,
            entries=summary.entry_count,
            users=summary.user_message_count,
            assistants=summary.assistant_message_count,
            tools=summary.tool_event_count,
        )
    )
    return 0


def run_copilot_sdk_profile_validate(args: argparse.Namespace) -> int:
    try:
        manifest = load_sdk_session_manifest(args.manifest)
        resolved = resolve_agent_profiles(manifest, manifest_path=args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for warning in resolved.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in resolved.errors:
        print(f"error: {error}", file=sys.stderr)
    print(
        "profiles={profiles} selected={selected} custom_tools={tools} "
        "task_overlays={overlays} warnings={warnings} errors={errors}".format(
            profiles=len(resolved.custom_agents),
            selected=resolved.selected_agent or "",
            tools=len(resolved.custom_tool_names),
            overlays=",".join(resolved.task_overlay_names) or "",
            warnings=len(resolved.warnings),
            errors=len(resolved.errors),
        )
    )
    return 0 if resolved.ok else 1


def run_copilot_sdk_profile_render(args: argparse.Namespace) -> int:
    try:
        manifest = load_sdk_session_manifest(args.manifest)
        resolved = resolve_agent_profiles(manifest, manifest_path=args.manifest)
        preview = render_agent_profiles_markdown(resolved)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(preview, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0 if resolved.ok else 1


def run_copilot_sdk_catalog_validate(args: argparse.Namespace) -> int:
    try:
        validation = validate_standard_profile_catalog(repo_root=args.repo_root)
        preview = render_profile_catalog_markdown(validation)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for warning in validation.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in validation.errors:
        print(f"error: {error}", file=sys.stderr)
    print(
        "profiles={profiles} overlays={overlays} warnings={warnings} errors={errors}".format(
            profiles=len(validation.profiles),
            overlays=len(validation.overlays),
            warnings=len(validation.warnings),
            errors=len(validation.errors),
        )
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(preview, encoding="utf-8")
        print(f"wrote {args.output}")
    return 0 if validation.ok else 1


def run_copilot_sdk_profile_run(args: argparse.Namespace) -> int:
    try:
        evidence = summarize_profile_run(args.manifest)
        preview = render_profile_run_evidence_markdown(evidence)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for warning in evidence.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in evidence.errors:
        print(f"error: {error}", file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(preview, encoding="utf-8")
    print(
        "selected={selected} overlays={overlays} controller_health={health} "
        "result_status={result_status} events={events}".format(
            selected=evidence.selected_agent,
            overlays=",".join(evidence.task_overlays),
            health=evidence.controller_health,
            result_status=evidence.result_status,
            events=evidence.event_count,
        )
    )
    print(f"wrote {args.output}")
    return 0 if evidence.ok else 1


def run_copilot_sdk_health_gate(args: argparse.Namespace) -> int:
    try:
        report = build_health_gate_report(
            args.manifest,
            required_count=args.required_count,
        )
        json_payload = health_gate_report_to_jsonable(report)
        markdown = render_health_gate_markdown(report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(json_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown, encoding="utf-8")
    print(
        "decision={decision} manifests={manifests} controller_health={health} "
        "repeated_errors={errors}".format(
            decision=report.decision,
            manifests=len(report.rows),
            health=report.controller_health,
            errors=report.repeated_error_signatures,
        )
    )
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    return 0 if report.go else 2


def run_foundrytk_profile_optimization_plan(args: argparse.Namespace) -> int:
    try:
        plan = build_profile_optimization_plan(
            args.manifest,
            repo_root=args.repo_root,
        )
        preview = render_profile_optimization_plan_markdown(plan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(preview, encoding="utf-8")
    print(
        "runs={runs} valid={valid} recommendation={recommendation}".format(
            runs=len(plan.runs),
            valid=plan.ok,
            recommendation=plan.recommendation,
        )
    )
    print(f"wrote {args.output}")
    return 0 if plan.ok else 1


def run_foundrytk_profile_dataset(args: argparse.Namespace) -> int:
    try:
        dataset = build_profile_evaluation_dataset(
            args.manifest,
            repo_root=args.repo_root,
        )
        jsonl = render_profile_evaluation_dataset_jsonl(dataset)
        markdown = render_profile_evaluation_dataset_markdown(dataset)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.jsonl_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.jsonl_output.write_text(jsonl, encoding="utf-8")
    args.markdown_output.write_text(markdown, encoding="utf-8")
    print(
        "rows={rows} valid={valid} jsonl={jsonl} markdown={markdown}".format(
            rows=len(dataset.rows),
            valid=dataset.ok,
            jsonl=args.jsonl_output,
            markdown=args.markdown_output,
        )
    )
    return 0 if dataset.ok else 1


def run_foundrytk_profile_aggregate(args: argparse.Namespace) -> int:
    try:
        dataset = load_profile_evaluation_dataset_jsonl(args.dataset)
        aggregate = build_profile_evaluation_aggregate(dataset)
        json_text = render_profile_evaluation_aggregate_json(aggregate)
        markdown = render_profile_evaluation_aggregate_markdown(aggregate)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json_text, encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown, encoding="utf-8")
    print(
        "rows={rows} valid={valid} recommendation={recommendation}".format(
            rows=aggregate.summary.get("row_count", 0),
            valid=aggregate.ok,
            recommendation=aggregate.summary.get("recommendation", ""),
        )
    )
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    return 0 if aggregate.ok else 1


def run_foundrytk_profile_contract_repair_plan(args: argparse.Namespace) -> int:
    try:
        aggregate_summary = load_profile_evaluation_aggregate_json(args.aggregate)
        plan = build_profile_contract_repair_plan(aggregate_summary)
        json_text = render_profile_contract_repair_plan_json(plan)
        markdown = render_profile_contract_repair_plan_markdown(plan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json_text, encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown, encoding="utf-8")
    print(
        "rows={rows} valid={valid} weak_cells={weak_cells} recommendation={recommendation}".format(
            rows=plan.summary.get("row_count", 0),
            valid=plan.ok,
            weak_cells=len(plan.summary.get("weak_treatment_cells", [])),
            recommendation=plan.summary.get("recommendation", ""),
        )
    )
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    return 0 if plan.ok else 1


def run_foundrytk_profile_evidence_review_ticket(args: argparse.Namespace) -> int:
    try:
        manifest = load_sdk_session_manifest(args.manifest)
        contract = build_profile_evidence_review_contract(
            manifest,
            manifest_path=args.manifest,
            require_existing_subject=not args.allow_missing_subject,
        )
        json_text = render_profile_evidence_review_contract_json(contract)
        ticket = render_profile_evidence_review_ticket(contract)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json_text, encoding="utf-8")
    args.ticket_output.parent.mkdir(parents=True, exist_ok=True)
    args.ticket_output.write_text(ticket, encoding="utf-8")
    print(
        "valid={valid} task_family={task_family} review_subject={review_subject}".format(
            valid=contract.ok,
            task_family=contract.task_family,
            review_subject=contract.review_subject_path,
        )
    )
    print(f"wrote {args.json_output}")
    print(f"wrote {args.ticket_output}")
    return 0 if contract.ok else 1


def run_heartbeat_validate(args: argparse.Namespace) -> int:
    try:
        records = load_heartbeat_jsonl(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_heartbeat_records(records)
    if result.ok:
        print(f"valid heartbeat: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_heartbeat_summarize(args: argparse.Namespace) -> int:
    try:
        records = load_heartbeat_jsonl(args.input)
        summary = summarize_heartbeat_records(
            records,
            stale_after_seconds=args.stale_after_seconds,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    if args.markdown_output is not None:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(
            render_heartbeat_summary(summary),
            encoding="utf-8",
        )
        print(f"wrote {args.markdown_output}")
    return 0 if summary.get("validation_ok") else 1


def run_nudge_suggest(args: argparse.Namespace) -> int:
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not isinstance(summary, dict):
        print("error: heartbeat summary must be a JSON object", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(suggest_nudge(summary) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_behavior_analyze(args: argparse.Namespace) -> int:
    try:
        data = load_archive_manifest(args.input)
        metrics = analyze_archive_manifest(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_behavior_markdown(metrics), encoding="utf-8")
    print(f"wrote {args.markdown_output}")
    return 0


def run_behavior_synthesize(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("*.behavior.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        synthesis, markdown = synthesize_behavior_summaries(paths)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"wrote {args.output}")
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(synthesis, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.json_output}")
    return 0


def load_optional_json(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def run_eval(args: argparse.Namespace) -> int:
    script = script_path(args.repo_root, "sdk_same_ticket_eval.py")
    cwd = (
        args.project_root.resolve() if args.project_root is not None else args.repo_root
    )
    manifest = (
        materialize_cross_project_manifest(args) if args.project_root else args.manifest
    )
    command = [sys.executable, str(script), "--manifest", str(manifest)]
    if args.dry_run:
        command.append("--dry-run")
    if args.summary_only:
        command.append("--summary-only")
    return run_command(command, cwd)


def run_eval_batch_command(args: argparse.Namespace) -> int:
    project_root = args.project_root.resolve() if args.project_root else None
    manifest_dir = (
        args.manifest_dir
        if args.manifest_dir.is_absolute()
        else (project_root / args.manifest_dir if project_root else args.manifest_dir)
    )
    output_dir = (
        args.output_dir
        if args.output_dir.is_absolute()
        else (project_root / args.output_dir if project_root else args.output_dir)
    )
    try:
        report = run_eval_batch(
            BatchEvalConfig(
                repo_root=args.repo_root.resolve(),
                manifest_dir=manifest_dir.resolve(),
                project_root=project_root,
                pattern=args.pattern,
                dry_run=args.dry_run,
                summary_only=args.summary_only,
                continue_on_failure=args.continue_on_failure,
                output_dir=output_dir.resolve(),
            )
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {output_dir / 'batch_summary.json'}")
    print(f"wrote {output_dir / 'batch_summary.md'}")
    return 1 if report["failed_manifests"] and not args.continue_on_failure else 0


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


def run_accounting_validate(args: argparse.Namespace) -> int:
    try:
        data = load_accounting_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_accounting_record(data)
    if result.ok:
        print(f"valid pilot accounting record: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_accounting_render(args: argparse.Namespace) -> int:
    try:
        data = load_accounting_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_accounting_record(data)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_accounting_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_accounting_synthesize(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("*.accounting.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        report = synthesize_accounting_markdown(paths)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_policy_tune(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("*.accounting.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        report = tune_policy(paths)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_authority_validate(args: argparse.Namespace) -> int:
    try:
        data = load_authority_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.kind == "contract":
        result = validate_supervisor_job_contract(data)
        label = "supervisor job contract"
    else:
        result = validate_supervisor_report(data)
        label = "supervisor report"
    if result.ok:
        print(f"valid {label}: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_authority_render(args: argparse.Namespace) -> int:
    try:
        data = load_authority_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.kind == "contract":
        result = validate_supervisor_job_contract(data)
        renderer = render_supervisor_job_contract
    else:
        result = validate_supervisor_report(data)
        renderer = render_supervisor_report
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(renderer(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_workflow_validate(args: argparse.Namespace) -> int:
    try:
        data = load_workflow_step(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_workflow_step(data)
    if result.ok:
        print(f"valid workflow step record: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_workflow_render(args: argparse.Namespace) -> int:
    try:
        data = load_workflow_step(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_workflow_step(data)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_workflow_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_roles_validate(args: argparse.Namespace) -> int:
    try:
        data = load_role_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_role_record(data)
    if result.ok:
        print(f"valid role/capability/implementation record: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_roles_render(args: argparse.Namespace) -> int:
    try:
        data = load_role_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_role_record(data)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_role_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_tokens_validate(args: argparse.Namespace) -> int:
    try:
        data = load_token_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_token_record(data)
    if result.ok:
        print(f"valid token/cost record: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_tokens_render(args: argparse.Namespace) -> int:
    try:
        data = load_token_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_token_record(data)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_token_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_tokens_synthesize(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("*.tokens.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        report = synthesize_token_markdown(paths)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_tokens_graph_synthesize(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("*.tokens.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        report = synthesize_graph_token_markdown(paths)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_supervisor_tokens_latest(args: argparse.Namespace) -> int:
    try:
        snapshot = latest_snapshot(
            session_jsonl=args.session_jsonl,
            session_root=args.session_root,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    payload = {
        "timestamp": snapshot.timestamp,
        "source_session_path": str(snapshot.source_session_path),
        "source_session_file": snapshot.source_session_file,
        "usage": snapshot.usage,
        "last_usage": snapshot.last_usage,
        "model_context_window": snapshot.model_context_window,
    }
    print(json.dumps(payload, indent=2))
    return 0


def run_supervisor_tokens_checkpoint(args: argparse.Namespace) -> int:
    try:
        checkpoint = write_checkpoint(
            span_id=args.span,
            event=args.event,
            output=args.output,
            session_jsonl=args.session_jsonl,
            session_root=args.session_root,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {args.output}")
    usage = checkpoint.get("usage", {})
    if isinstance(usage, dict):
        print(
            "snapshot total_tokens={total} input_tokens={input} "
            "cached_input_tokens={cached} output_tokens={output} "
            "reasoning_output_tokens={reasoning}".format(
                total=usage.get("total_tokens", 0),
                input=usage.get("input_tokens", 0),
                cached=usage.get("cached_input_tokens", 0),
                output=usage.get("output_tokens", 0),
                reasoning=usage.get("reasoning_output_tokens", 0),
            )
        )
    return 0


def run_supervisor_tokens_span(args: argparse.Namespace) -> int:
    try:
        span_record_from_checkpoints(
            start_path=args.start,
            end_path=args.end,
            output=args.output,
            project=args.project,
            phase=args.phase,
            task_id=args.task_id,
            span_kind=args.span_kind,
            supervisor_input_price_per_1m_usd=args.supervisor_input_price_per_1m_usd,
            supervisor_cached_input_price_per_1m_usd=(
                args.supervisor_cached_input_price_per_1m_usd
            ),
            supervisor_output_price_per_1m_usd=args.supervisor_output_price_per_1m_usd,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {args.output}")
    return 0


def run_supervisor_tokens_synthesize(args: argparse.Namespace) -> int:
    try:
        synthesize_supervisor_token_spans(args.input_dir, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {args.output}")
    return 0


def run_supervisor_budget_validate(args: argparse.Namespace) -> int:
    try:
        data = load_budget_declaration(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_budget_declaration(data)
    rendered = render_budget_validation(data, result)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(rendered, end="")
    return 0 if result.ok else 1


def require_valid_budget_record(path: Path | None) -> bool:
    if path is None:
        print(
            "error: --budget-record is required for live/economics supervisor runs",
            file=sys.stderr,
        )
        return False
    try:
        data = load_budget_declaration(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: invalid --budget-record: {exc}", file=sys.stderr)
        return False
    result = validate_budget_declaration(data)
    if result.ok:
        return True
    for error in result.errors:
        print(f"error: budget-record: {error}", file=sys.stderr)
    return False


def run_supervisor_document_audit_graph(args: argparse.Namespace) -> int:
    if not args.dry_run and not require_valid_budget_record(args.budget_record):
        return 1
    project_root = args.project_root.resolve()
    token_dir = args.token_dir
    if token_dir is None:
        token_dir = Path("runtime/supervisor_tokens") / args.job_id
    config = DocumentAuditGraphRunConfig(
        project_root=project_root,
        repo_root=args.repo_root.resolve(),
        job_id=args.job_id,
        marker=args.marker,
        phase=args.phase,
        task_id=args.task_id,
        title=args.title,
        source_summaries=tuple(Path(value) for value in args.source_summary),
        output_dir=args.output_dir,
        summary_output=args.summary_output,
        token_dir=token_dir,
        mode=args.mode,
        code_command=args.code_command,
        expected_model=args.expected_model,
        bridge_prompt=args.bridge_prompt,
        pre_materialize_audit_ticket=args.pre_materialize_audit_ticket,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
        dry_run=args.dry_run,
        bridge_no_launch=args.bridge_no_launch,
        quiet_runtime_output=args.quiet_runtime_output,
    )
    try:
        result = run_document_audit_graph(config)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(json.dumps(result, indent=2))
    else:
        print(f"wrote {args.summary_output}")
    if isinstance(result, dict) and result.get("accepted_candidate") is False:
        return 1
    return 0


def run_supervisor_document_audit_graph_summary(args: argparse.Namespace) -> int:
    if not require_valid_budget_record(args.budget_record):
        return 1
    project_root = args.project_root.resolve()
    token_dir = args.token_dir
    if token_dir is None:
        token_dir = Path("runtime/supervisor_tokens") / args.job_id
    config = DocumentAuditGraphRunConfig(
        project_root=project_root,
        repo_root=args.repo_root.resolve(),
        job_id=args.job_id,
        marker=args.marker,
        phase=args.phase,
        task_id=args.task_id,
        title=args.title,
        source_summaries=tuple(Path(value) for value in args.source_summary),
        output_dir=args.output_dir,
        summary_output=args.summary_output,
        token_dir=token_dir,
        mode=args.mode,
        code_command=args.code_command,
        expected_model=args.expected_model,
        bridge_prompt=args.bridge_prompt,
        pre_materialize_audit_ticket=args.pre_materialize_audit_ticket,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    try:
        result = summarize_existing_document_audit_graph(
            config,
            token_record=args.token_record,
        )
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {args.summary_output}")
    if isinstance(result, dict) and result.get("accepted_candidate") is False:
        return 1
    return 0


def run_experiments_validate(args: argparse.Namespace) -> int:
    try:
        data = load_experiment_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_experiment_record(data)
    if result.ok:
        print(f"valid delegation experiment record: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_experiments_render(args: argparse.Namespace) -> int:
    try:
        data = load_experiment_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_experiment_record(data)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_experiment_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_experiments_synthesize(args: argparse.Namespace) -> int:
    paths = list(args.input)
    if args.input_dir is not None:
        paths.extend(sorted(args.input_dir.glob("*.experiment.json")))
    if not paths:
        print("error: provide --input or --input-dir", file=sys.stderr)
        return 1
    try:
        report = synthesize_experiment_markdown(paths)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_benchmark_validate(args: argparse.Namespace) -> int:
    try:
        data = load_benchmark_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_benchmark_record(data)
    if result.ok:
        print(f"valid benchmark record: {args.input}")
        return 0
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def run_benchmark_render(args: argparse.Namespace) -> int:
    try:
        data = load_benchmark_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result = validate_benchmark_record(data)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_benchmark_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_benchmark_prepare_worktrees(args: argparse.Namespace) -> int:
    try:
        data = load_benchmark_record(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    validation = validate_benchmark_record(data)
    if not validation.ok:
        for error in validation.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    result = prepare_benchmark_worktrees(
        data,
        args.project_root,
        dry_run=args.dry_run,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result.report, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(result.report)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


def run_graph_validate(args: argparse.Namespace) -> int:
    try:
        data = load_graph_document(args.input)
        result = validate_graph_document(
            data,
            source_path=args.input,
            agent_metadata=args.agent_metadata,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FreshForgeGraphUnavailable as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = render_graph_validation(result)
    if result.ok:
        print(report)
        return 0
    print(report, file=sys.stderr)
    return 1


def run_graph_render(args: argparse.Namespace) -> int:
    try:
        data = load_graph_document(args.input)
        result = validate_graph_document(
            data,
            source_path=args.input,
            agent_metadata=args.agent_metadata,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FreshForgeGraphUnavailable as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not result.ok:
        print(render_graph_validation(result), file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_graph_markdown(data), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def run_graph_decide(args: argparse.Namespace) -> int:
    try:
        data = load_graph_document(args.input)
        result = validate_graph_document(
            data,
            source_path=args.input,
            agent_metadata=args.agent_metadata,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FreshForgeGraphUnavailable as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not result.ok:
        print(render_graph_validation(result), file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_graph_decisions_markdown(data), encoding="utf-8")
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


def resolve_decision_paths(
    data: dict[str, object], input_path: Path, repo_root: Path
) -> None:
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
