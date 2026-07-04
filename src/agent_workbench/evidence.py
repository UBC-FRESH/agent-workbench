"""Evidence summary validation and Markdown rendering."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "phase",
    "task",
    "evidence_id",
    "evidence_type",
    "generated_utc",
    "source_runtime_paths",
    "ticket_family",
    "models_or_agent_host",
    "bridge_or_harness",
    "allowed_authority",
    "forbidden_authority",
    "outcomes",
    "verification",
    "promotion_boundary",
    "supervisor_decision",
)

CLAIM_FIELDS = (
    "accepted_claims",
    "rejected_claims",
    "needs_evidence_claims",
)

SUSPICIOUS_PATTERNS = (
    re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+"),
    re.compile(r"gho_[A-Za-z0-9_]+"),
    re.compile(r"(?i)\b(token|secret|password|cookie)\b\s*[:=]"),
    re.compile(r"(?i)cf-access-(client-id|client-secret)"),
)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


def load_summary(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("summary must be a JSON object")
    return data


def validate_summary(data: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")

    source_paths = data.get("source_runtime_paths")
    if source_paths is not None:
        if not isinstance(source_paths, list) or not all(
            isinstance(path, str) for path in source_paths
        ):
            errors.append("source_runtime_paths must be a list of repo-relative strings")
        else:
            for path in source_paths:
                if Path(path).is_absolute() or re.match(r"^[A-Za-z]:", path):
                    errors.append(f"source_runtime_paths must be repo-relative: {path}")

    outcomes = data.get("outcomes")
    if outcomes is not None and not isinstance(outcomes, list):
        errors.append("outcomes must be a list")

    for field in CLAIM_FIELDS:
        claims = data.get(field)
        if claims is not None and not is_claim_list(claims):
            errors.append(
                f"{field} must be a list of strings or claim objects with a text field"
            )

    for finding in find_private_values(data):
        errors.append(f"private-looking value detected: {finding}")

    return ValidationResult(ok=not errors, errors=errors)


def is_claim_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    for item in value:
        if isinstance(item, str):
            continue
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            continue
        return False
    return True


def find_private_values(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            findings.extend(find_private_values(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_private_values(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(value):
                findings.append(path)
                break
    return findings


def render_markdown(data: dict[str, Any]) -> str:
    outcomes = data.get("outcomes", [])
    verification = data.get("verification", {})
    promotion = data.get("promotion_boundary", {})
    decision = data.get("supervisor_decision", {})

    lines = [
        "# Evidence Summary",
        "",
        "## Metadata",
        "",
        f"- phase: `{data.get('phase', '')}`",
        f"- task: `{data.get('task', '')}`",
        f"- evidence_id: `{data.get('evidence_id', '')}`",
        f"- evidence_type: `{data.get('evidence_type', '')}`",
        f"- generated_utc: `{data.get('generated_utc', '')}`",
        "",
        "## Scope",
        "",
        f"- ticket_family: `{data.get('ticket_family', '')}`",
        f"- models_or_agent_host: {format_value(data.get('models_or_agent_host', ''))}",
        f"- bridge_or_harness: `{data.get('bridge_or_harness', '')}`",
        f"- allowed_authority: {format_value(data.get('allowed_authority', ''))}",
        f"- forbidden_authority: {format_value(data.get('forbidden_authority', ''))}",
        "",
        "## Source Runtime Paths",
        "",
    ]
    for path in data.get("source_runtime_paths", []):
        lines.append(f"- `{path}`")

    lines.extend(["", "## Outcomes", "", "| Subject | Classification | Count | Notes |", "| --- | --- | ---: | --- |"])
    if isinstance(outcomes, list):
        for outcome in outcomes:
            if isinstance(outcome, dict):
                lines.append(
                    "| {subject} | `{classification}` | {count} | {notes} |".format(
                        subject=outcome.get("subject", ""),
                        classification=outcome.get("classification", ""),
                        count=outcome.get("count", ""),
                        notes=outcome.get("notes", outcome.get("note", "")),
                    )
                )

    lines.extend(render_claim_review(data))
    lines.extend(["", "## Verification", ""])
    if isinstance(verification, dict):
        for key, item in verification.items():
            lines.append(f"- {key}: {format_value(item)}")

    lines.extend(["", "## Promotion Boundary", ""])
    if isinstance(promotion, dict):
        for key, item in promotion.items():
            lines.append(f"- {key}: {format_value(item)}")

    lines.extend(["", "## Supervisor Decision", ""])
    if isinstance(decision, dict):
        lines.append(f"Decision: `{decision.get('decision', '')}`")
        lines.append("")
        lines.append(f"Rationale: {decision.get('rationale', '')}")
    else:
        lines.append(str(decision))

    lines.append("")
    return "\n".join(lines)


def render_claim_review(data: dict[str, Any]) -> list[str]:
    if not any(data.get(field) for field in CLAIM_FIELDS):
        return []
    lines = ["", "## Claim Review", ""]
    labels = {
        "accepted_claims": "Accepted Claims",
        "rejected_claims": "Rejected Claims",
        "needs_evidence_claims": "Needs Evidence Claims",
    }
    for field, label in labels.items():
        lines.extend([f"### {label}", ""])
        claims = data.get(field, [])
        if isinstance(claims, list) and claims:
            for claim in claims:
                lines.append(f"- {format_claim(claim)}")
        else:
            lines.append("- None recorded.")
        lines.append("")
    return lines


def format_claim(claim: Any) -> str:
    if isinstance(claim, str):
        return claim
    if isinstance(claim, dict):
        text = str(claim.get("text", ""))
        evidence = claim.get("evidence")
        if evidence:
            return f"{text} Evidence: `{evidence}`"
        return text
    return str(claim)


def synthesize_markdown(paths: list[Path]) -> str:
    summaries: list[tuple[Path, dict[str, Any]]] = []
    errors: list[str] = []
    for path in paths:
        try:
            data = load_summary(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        result = validate_summary(data)
        if not result.ok:
            errors.extend(f"{path}: {error}" for error in result.errors)
            continue
        summaries.append((path, data))

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"cannot synthesize invalid evidence summaries:\n{joined}")

    lines = [
        "# Supervisor Decision Packet",
        "",
        "This packet is synthesized from sanitized evidence summaries. Raw worker",
        "outputs remain in ignored runtime paths and must not be treated as",
        "verified facts without supervisor review.",
        "",
        "## Evidence Inputs",
        "",
    ]
    for path, data in summaries:
        lines.append(f"- `{path.as_posix()}`: `{data.get('evidence_id', '')}`")

    decision_counts: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    claim_counts = {field: 0 for field in CLAIM_FIELDS}
    lines.extend(["", "## Decision Summary", ""])
    for _path, data in summaries:
        decision = data.get("supervisor_decision", {})
        if isinstance(decision, dict):
            value = str(decision.get("decision", ""))
        else:
            value = str(decision)
        decision_counts[value] = decision_counts.get(value, 0) + 1

        outcomes = data.get("outcomes", [])
        if isinstance(outcomes, list):
            for outcome in outcomes:
                if isinstance(outcome, dict):
                    classification = str(outcome.get("classification", ""))
                    count = outcome.get("count", 1)
                    if isinstance(count, int):
                        classification_counts[classification] = (
                            classification_counts.get(classification, 0) + count
                        )
        for field in CLAIM_FIELDS:
            claims = data.get(field, [])
            if isinstance(claims, list):
                claim_counts[field] += len(claims)

    lines.append("### Supervisor Decisions")
    lines.append("")
    for decision, count in sorted(decision_counts.items()):
        lines.append(f"- `{decision}`: {count}")

    lines.extend(["", "### Outcome Classifications", ""])
    for classification, count in sorted(classification_counts.items()):
        lines.append(f"- `{classification}`: {count}")

    lines.extend(["", "### Claim Dispositions", ""])
    for field, count in claim_counts.items():
        lines.append(f"- `{field}`: {count}")

    lines.extend(
        [
            "",
            "## Evidence Table",
            "",
            "| Evidence | Task | Decision | Rationale |",
            "| --- | --- | --- | --- |",
        ]
    )
    for _path, data in summaries:
        decision = data.get("supervisor_decision", {})
        decision_value = ""
        rationale = ""
        if isinstance(decision, dict):
            decision_value = str(decision.get("decision", ""))
            rationale = str(decision.get("rationale", ""))
        lines.append(
            "| {evidence} | {task} | `{decision}` | {rationale} |".format(
                evidence=data.get("evidence_id", ""),
                task=data.get("task", ""),
                decision=decision_value,
                rationale=rationale.replace("|", "\\|"),
            )
        )

    lines.extend(["", "## Claims And Notes", ""])
    for _path, data in summaries:
        lines.append(f"### {data.get('evidence_id', '')}")
        lines.append("")
        outcomes = data.get("outcomes", [])
        if isinstance(outcomes, list):
            for outcome in outcomes:
                if isinstance(outcome, dict):
                    note = outcome.get("note", outcome.get("notes", ""))
                    lines.append(
                        "- `{classification}` x{count}: {note}".format(
                            classification=outcome.get("classification", ""),
                            count=outcome.get("count", ""),
                            note=str(note),
                        )
                    )
        lines.append("")

    lines.extend(["## Claim Review", ""])
    for _path, data in summaries:
        if not any(data.get(field) for field in CLAIM_FIELDS):
            continue
        lines.append(f"### {data.get('evidence_id', '')}")
        lines.append("")
        for field in CLAIM_FIELDS:
            lines.append(f"#### {field}")
            claims = data.get(field, [])
            if isinstance(claims, list) and claims:
                for claim in claims:
                    lines.append(f"- {format_claim(claim)}")
            else:
                lines.append("- None recorded.")
            lines.append("")

    lines.extend(["## Promotion Boundary", ""])
    for _path, data in summaries:
        boundary = data.get("promotion_boundary", {})
        if isinstance(boundary, dict):
            raw_path = boundary.get("raw_evidence_retained_under", "")
            private_excluded = boundary.get("private_values_excluded", "")
            lines.append(
                f"- `{data.get('evidence_id', '')}` raw evidence: `{raw_path}`; "
                f"private values excluded: `{private_excluded}`"
            )

    lines.append("")
    return "\n".join(lines)


def format_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(f"`{item}`" for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)
