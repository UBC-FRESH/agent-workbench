"""Verify a document-artifact audit supervisor report against source summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify document-artifact audit report source facts and decisions."
    )
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--source-summary", action="append", required=True)
    return parser.parse_args()


def resolve_under_root(path: Path, project_root: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root / path


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def source_fact(path: Path, project_root: Path, index: int) -> dict[str, Any]:
    data = load_json(path)
    totals = data.get("totals", {})
    if not isinstance(totals, dict):
        totals = {}
    return {
        "item_id": f"source_summary_{index}",
        "source_path": display_path(path, project_root),
        "source_summary_id": str(data.get("summary_id", "")),
        "source_document_id": str(data.get("document_id", "")),
        "source_gate_result": str(data.get("gate_result", "")),
        "source_recommended_next_move": str(data.get("recommended_next_move", "")),
        "source_needs_supervisor_fields": int(
            totals.get("needs_supervisor_fields", 0) or 0
        ),
        "source_quote_over_limit_fields": int(
            totals.get("quote_over_limit_fields", 0) or 0
        ),
        "source_resolved_fields": int(totals.get("resolved_fields", 0) or 0),
    }


def display_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def expected_decision(gate_result: str, recommended_next_move: str) -> str:
    gate = gate_result.casefold()
    next_move = recommended_next_move.casefold()
    if not gate.strip():
        return "needs_coordinator_review"
    if "quote-repair-needed" in gate or "quote-limit-failed" in gate:
        return "quote_repair_required"
    if any(value in gate for value in ("parse-failed", "failed", "blocked", "unreadable")):
        return "needs_coordinator_review"
    if (
        "ready-for-supervisor-audit" in gate
        or "paid supervisor audit" in next_move
        or "send only unresolved verifier fields to paid supervisor audit" in next_move
    ):
        return "paid_supervisor_audit_required"
    if any(value in gate for value in ("ready-to-scale", "ready_to_scale", "ready-for-scale")):
        return "ready_to_scale"
    return "needs_coordinator_review"


def verify(report: dict[str, Any], expected_facts: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    verification = report.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    audit_items = verification.get("audit_items")
    if not isinstance(audit_items, list):
        return ["verification.audit_items must be a list"]
    if len(audit_items) != len(expected_facts):
        errors.append(
            f"verification.audit_items length {len(audit_items)} != "
            f"expected {len(expected_facts)}"
        )
    field = verification.get("all_decisions_consistent_with_gate")
    if not isinstance(field, bool):
        errors.append("verification.all_decisions_consistent_with_gate must be boolean")
    score = verification.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        errors.append("verification.score must be numeric")

    all_decisions_ok = True
    all_source_facts_ok = True
    for index, expected in enumerate(expected_facts):
        if index >= len(audit_items):
            break
        item = audit_items[index]
        if not isinstance(item, dict):
            errors.append(f"verification.audit_items[{index}] must be an object")
            all_decisions_ok = False
            all_source_facts_ok = False
            continue
        source_fact_ok = True
        for key, value in expected.items():
            if item.get(key) != value:
                errors.append(
                    f"{expected['item_id']}.{key} mismatch: "
                    f"expected {value!r}, observed {item.get(key)!r}"
                )
                source_fact_ok = False
        expected_auditor_decision = expected_decision(
            expected["source_gate_result"],
            expected["source_recommended_next_move"],
        )
        observed_decision = item.get("auditor_decision")
        decision_ok = observed_decision == expected_auditor_decision
        if not decision_ok:
            errors.append(
                f"{expected['item_id']}.auditor_decision mismatch: "
                f"expected {expected_auditor_decision!r}, observed {observed_decision!r}"
            )
        if item.get("decision_consistent_with_gate") is not decision_ok:
            errors.append(
                f"{expected['item_id']}.decision_consistent_with_gate should be "
                f"{decision_ok}"
            )
        if item.get("source_fact_copy_ok") is not source_fact_ok:
            errors.append(
                f"{expected['item_id']}.source_fact_copy_ok should be {source_fact_ok}"
            )
        if source_fact_ok is not True:
            errors.append(f"{expected['item_id']}.source_fact_copy_ok must be true")
        all_decisions_ok = all_decisions_ok and decision_ok
        all_source_facts_ok = all_source_facts_ok and source_fact_ok

    if isinstance(field, bool) and field is not all_decisions_ok:
        errors.append(
            "verification.all_decisions_consistent_with_gate does not match "
            "per-item decisions"
        )
    if isinstance(score, (int, float)) and not isinstance(score, bool):
        expected_score = 1.0 if all_decisions_ok and all_source_facts_ok else 0.0
        if float(score) != expected_score:
            errors.append(
                f"verification.score should be {expected_score} for deterministic "
                "document-audit validation"
            )
    return errors


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    report_path = resolve_under_root(args.report, project_root)
    source_paths = [
        resolve_under_root(Path(value), project_root) for value in args.source_summary
    ]
    report = load_json(report_path)
    expected_facts = [
        source_fact(path, project_root, index)
        for index, path in enumerate(source_paths, start=1)
    ]
    errors = verify(report, expected_facts)
    if errors:
        print("invalid document artifact audit report")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"valid document artifact audit report: {display_path(report_path, project_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
