"""Summarize P57 packaged-launcher economics evidence.

This intentionally handles the mixed summary shapes produced during the P57
spike. It is not a general benchmark framework; it is a reproducible scoreboard
for deciding what the next local-supervisor experiment should optimize.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT = Path(
    "benchmarks/vscode_subagent_spike/p57_packaged_launcher_economics_comparison.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "planning/phase57_packaged_launcher_economics_decision_packet.md"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize P57 packaged-launcher economics evidence."
    )
    parser.add_argument(
        "--summary",
        action="append",
        type=Path,
        default=[],
        help="Summary JSON path. May be repeated.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def token_costs(data: dict[str, Any]) -> dict[str, Any]:
    token = data.get("token_costs")
    if isinstance(token, dict):
        return token
    return {
        "estimated_paid_cost_usd": data.get("estimated_paid_cost_usd"),
        "estimated_paid_cost_per_source_artifact_usd": data.get(
            "estimated_paid_cost_per_source_artifact_usd"
        ),
        "economics_usable": data.get("economics_usable"),
        "codex_total_token_delta": data.get("codex_total_token_delta"),
    }


def normalize(path: Path) -> dict[str, Any]:
    data = load_json(path)
    costs = token_costs(data)
    source_count = data.get("source_count")
    if not isinstance(source_count, int) or source_count <= 0:
        sources = data.get("source_artifacts", data.get("source_summaries", []))
        source_count = len(sources) if isinstance(sources, list) else None
    estimated_cost = number_or_none(costs.get("estimated_paid_cost_usd"))
    per_source = number_or_none(costs.get("estimated_paid_cost_per_source_artifact_usd"))
    if per_source is None and estimated_cost is not None and source_count:
        per_source = estimated_cost / source_count
    accepted = data.get("accepted_candidate")
    if accepted is None:
        status = str(data.get("status", ""))
        accepted = status.startswith("accepted") or status in {
            "completed",
            "completed_with_caveats",
        }
    economics_usable = costs.get("economics_usable")
    if economics_usable is None:
        economics_usable = bool(accepted and estimated_cost is not None)
    subagent = data.get("subagent_outcome", {})
    if not isinstance(subagent, dict):
        subagent = {}
    model_provenance = data.get("model_provenance", {})
    if not isinstance(model_provenance, dict):
        model_provenance = {}
    authoritative_model = str(
        model_provenance.get("authoritative_model") or data.get("model", "")
    )
    observed_model = str(model_provenance.get("observed_model") or authoritative_model)
    return {
        "summary_path": path.as_posix(),
        "record_label": path.stem,
        "summary_id": data.get("summary_id", path.stem),
        "status": data.get("status", ""),
        "accepted_candidate": bool(accepted),
        "model": authoritative_model,
        "model_provenance": {
            "expected_model": str(model_provenance.get("expected_model") or ""),
            "authoritative_model": authoritative_model,
            "observed_model": observed_model,
            "source": str(model_provenance.get("source") or "legacy_model_field"),
            "match_status": str(
                model_provenance.get("match_status") or "legacy_unavailable"
            ),
            "self_report_status": str(
                model_provenance.get("self_report_status") or "legacy_unavailable"
            ),
        },
        "source_count": source_count,
        "economics_usable": bool(economics_usable),
        "estimated_paid_cost_usd": round(estimated_cost, 6)
        if estimated_cost is not None
        else None,
        "estimated_paid_cost_per_source_artifact_usd": round(per_source, 6)
        if per_source is not None
        else None,
        "codex_total_token_delta": int(costs.get("codex_total_token_delta", 0) or 0),
        "measurement_boundary": costs.get("measurement_boundary", ""),
        "subagent_tool_observed": bool(data.get("subagent_tool_observed")),
        "subagent_status": subagent.get("audit_report_status", ""),
        "repair_required": subagent.get("repair_required"),
        "decision_breakdown": data.get("audit_decision_breakdown", {}),
        "validator_passed": all(
            bool(data.get(key))
            for key in (
                "authority_validation_passed",
                "document_audit_verifier_passed",
                "document_graph_report_verifier_passed",
            )
            if key in data
        ),
    }


def number_or_none(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return None


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [
        item
        for item in records
        if item["economics_usable"] and item["estimated_paid_cost_usd"] is not None
    ]
    accepted = [item for item in records if item["accepted_candidate"]]
    best = min(
        usable,
        key=lambda item: item["estimated_paid_cost_per_source_artifact_usd"]
        if item["estimated_paid_cost_per_source_artifact_usd"] is not None
        else item["estimated_paid_cost_usd"],
    ) if usable else None
    latest_external = next(
        (
            item
            for item in reversed(records)
            if item.get("measurement_boundary")
            in {"external_coordinator_span", "summed_external_coordinator_spans"}
        ),
        None,
    )
    external_usable = [
        item
        for item in usable
        if item.get("measurement_boundary")
        in {"external_coordinator_span", "summed_external_coordinator_spans"}
    ]
    best_external = min(
        external_usable,
        key=lambda item: item["estimated_paid_cost_per_source_artifact_usd"]
        if item["estimated_paid_cost_per_source_artifact_usd"] is not None
        else item["estimated_paid_cost_usd"],
    ) if external_usable else None
    return {
        "summary_id": "p57_packaged_launcher_economics_comparison",
        "scope": "P57 local Copilot supervisor packaged graph-run economics",
        "record_count": len(records),
        "accepted_count": len(accepted),
        "usable_economics_count": len(usable),
        "best_usable_cost_summary": best,
        "best_external_checkpoint_summary": best_external,
        "latest_external_checkpoint_summary": latest_external,
        "records": records,
        "interpretation": {
            "current_signal": (
                "The local Copilot supervisor can complete the five-artifact "
                "document-audit graph under deterministic validation. External "
                "coordinator checkpoints are required for credible paid-token "
                "economics."
            ),
            "next_optimization_target": (
                "Reduce coordinator overhead around packaged launch and result "
                "inspection while preserving accepted-candidate validation."
            ),
        },
    }


def render_markdown(summary: dict[str, Any]) -> str:
    best = summary.get("best_usable_cost_summary") or {}
    best_external = summary.get("best_external_checkpoint_summary") or {}
    latest_external = summary.get("latest_external_checkpoint_summary") or {}
    latest_model_provenance = latest_external.get("model_provenance", {})
    if not isinstance(latest_model_provenance, dict):
        latest_model_provenance = {}
    rows = [
        "| Record | Model | Accepted | Economics | Cost | Cost/source | Boundary | Subagent tool | Subagent status |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for record in summary.get("records", []):
        if not isinstance(record, dict):
            continue
        rows.append(
            "| {record} | `{model}` | {accepted} | {usable} | {cost} | {per_source} | {boundary} | {subagent_tool} | {subagent} |".format(
                record=record.get("record_label", ""),
                model=record.get("model", "") or "unknown",
                accepted=yes_no(record.get("accepted_candidate")),
                usable=yes_no(record.get("economics_usable")),
                cost=format_usd(record.get("estimated_paid_cost_usd")),
                per_source=format_usd(
                    record.get("estimated_paid_cost_per_source_artifact_usd")
                ),
                boundary=record.get("measurement_boundary", "") or "legacy",
                subagent_tool=yes_no(record.get("subagent_tool_observed")),
                subagent=record.get("subagent_status", "") or "n/a",
            )
        )

    return "\n".join(
        [
            "# P57 Packaged Launcher Economics Decision Packet",
            "",
            "## Decision Signal",
            "",
            "- Local Copilot supervision is working for this five-artifact graph audit task.",
            "- External coordinator checkpoints are required for credible packaged-run economics.",
            "- The latest external-checkpoint summary records expected model `{}` and observed model `{}` with match status `{}`.".format(
                latest_model_provenance.get("expected_model", "") or "n/a",
                latest_model_provenance.get("observed_model", "") or latest_external.get("model", "n/a"),
                latest_model_provenance.get("match_status", "") or "n/a",
            ),
            "- The cheapest accepted usable span is `{}` at `{}` total and `{}` per source artifact.".format(
                best.get("record_label", "n/a"),
                format_usd(best.get("estimated_paid_cost_usd")),
                format_usd(best.get("estimated_paid_cost_per_source_artifact_usd")),
            ),
            "- The cheapest usable external-checkpoint packaged span is `{}` at `{}` total and `{}` per source artifact.".format(
                best_external.get("record_label", "n/a"),
                format_usd(best_external.get("estimated_paid_cost_usd")),
                format_usd(
                    best_external.get(
                        "estimated_paid_cost_per_source_artifact_usd"
                    )
                ),
            ),
            "- The latest external-checkpoint packaged span is `{}` at `{}` total and `{}` per source artifact.".format(
                latest_external.get("record_label", "n/a"),
                format_usd(latest_external.get("estimated_paid_cost_usd")),
                format_usd(
                    latest_external.get(
                        "estimated_paid_cost_per_source_artifact_usd"
                    )
                ),
            ),
            "",
            "## Recommended Next Experiment",
            "",
            "Treat pre-materialized graph tickets and quiet runtime output as the default packaged-launcher path. Before another full-batch run, stabilize mechanical repair behavior by replacing ad hoc delete/recreate repair loops with generated overwrite-only repair helpers. After that, test one batch-level supervisor ticket with external-token accounting.",
            "",
            "Success criterion: accepted-candidate validation with external-checkpoint cost per source artifact at or below the quiet-output repeat band observed in v13-v14. Secondary criterion: document whether subagent repair frequency stays low as the work package grows.",
            "",
            "## Split 01 Scale Probe",
            "",
            "The expected-model gated split_01 v1 run matched `qwen3.6:35b-a3b-bf16` but stopped after the materializer command, leaving both required reports missing. The split_01 v2 retry used a stronger full-graph bridge prompt. That moved the local supervisor further: it invoked the subagent, wrote both runtime reports, and all deterministic validators passed. The bridge still rejected the run because the materializer command was executed twice, which remains a protocol deviation. The split_01 v3 pre-materialized retry fixed the materializer boundary but stopped after the first failed validator. The split_01 v4 pre-materialized retry accepted: model provenance matched, no materializer commands were run by Copilot, the subagent was invoked, both reports were written, all expected validators ran, and the bridge reported no deviations. The split_01 v5 external-checkpoint rerun accepted with usable economics and no Copilot-side materializer commands, but no subagent tool invocation was observed; the local supervisor appears to have completed the bounded repair/report task directly.",
            "",
            "Interpretation: coordinator-owned deterministic setup is the better boundary. The free local supervisor should receive a pre-materialized runtime ticket and own audit, repair, validation, and graph reporting. This removes a repeatable setup-command failure mode while preserving the useful local-supervisor/subagent behavior.",
            "",
            "## Multi-Split Scale Probe",
            "",
            "The split_01+split_02 v1 package ran two five-artifact pre-materialized child graph jobs under one external coordinator-token span. Both child runs accepted after deterministic verification, both matched the expected `qwen3.6:35b-a3b-bf16` model, both observed the subagent tool, and Copilot ran zero materializer commands across the package. The external span cost was `$0.109171` total, or `$0.010917` per source artifact, improving on the previous five-artifact v5 cost of `$0.013057` per source artifact.",
            "",
            "Interpretation: the coordinator-owned setup boundary amortizes in the expected direction as package size grows. The next question is whether the same pattern holds for full 14-artifact coverage or whether a single batch-level supervisor ticket reduces coordination overhead further.",
            "",
            "## Full 14-Artifact Coverage",
            "",
            "The full-coverage v1 aggregate combines the accepted split_01+split_02 package with accepted split_03 v1 for all fourteen source summaries in the batch manifest. All child packages matched expected model `qwen3.6:35b-a3b-bf16`, used pre-materialized audit tickets, observed subagent tool use, ran zero Copilot-side materializer commands, and passed deterministic validation. The summed external-span cost was `$0.190046` total, or `$0.013575` per source artifact.",
            "",
            "Interpretation: full coverage stayed accepted, but summed-span cost is higher than the 10-artifact package because split_03 was measured in a separate external span. The next optimization target is reducing span/session overhead, not changing the coordinator-owned setup boundary.",
            "",
            "## Failed Uninterrupted Full-Batch Retries",
            "",
            "Two uninterrupted full-batch retries failed before completing all splits. The first failed by emitting the final marker without creating reports or running validators. The second created valid reports but used a destructive `Remove-Item` repair loop against the assigned audit report, which the bridge correctly rejected. These failures indicate that the next optimization should harden mechanical repair tooling before a single batch-level supervisor ticket is treated as a reliable economics experiment.",
            "",
            "## Comparison Table",
            "",
            *rows,
            "",
        ]
    )


def yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def format_usd(value: Any) -> str:
    number = number_or_none(value)
    if number is None:
        return "n/a"
    return f"${number:.6f}"


def main() -> int:
    args = parse_args()
    if not args.summary:
        raise SystemExit("provide at least one --summary")
    records = [normalize(path) for path in args.summary]
    output = summarize(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(output), encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"wrote {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
