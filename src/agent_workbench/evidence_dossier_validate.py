"""Schema validation for the public-safe artifacts in a P107 evidence dossier."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import timezone
from pathlib import Path
from typing import Any

from .evidence_dossier import DossierManifestError, load_manifest
from .heartbeat import load_heartbeat_jsonl, parse_timestamp, validate_heartbeat_records


REQUIRED_ARTIFACT_KINDS = frozenset(
    {
        "heartbeat",
        "token_ledger",
        "advisor_verdict",
        "archive_manifest",
        "worker_result",
    }
)
ALLOWED_ADVISOR_VERDICTS = frozenset({"accepted", "defect_packet", "verified_blocker"})
ALLOWED_WORKER_STATUSES = frozenset(
    {"accepted-candidate", "blocked", "needs-supervisor-review"}
)
_FINAL_STATUS = re.compile(r"^## Final Status\s*\n+[-*]?\s*`?([a-z-]+)`?\s*$", re.MULTILINE)


@dataclass(frozen=True)
class DossierArtifactValidation:
    """The deterministic validation result for one complete dossier."""

    ok: bool
    errors: list[str]


@dataclass(frozen=True)
class DossierReconciliation:
    """Deterministic cross-artifact conflicts for one typed dossier."""

    ok: bool
    conflicts: list[dict[str, str]]


@dataclass(frozen=True)
class DossierTimelineAnalysis:
    """Normalized timeline and deterministic anomalies for one dossier."""

    timeline: list[dict[str, str]]
    anomalies: list[dict[str, str]]


def validate_dossier_artifacts(manifest_path: Path) -> DossierArtifactValidation:
    """Validate the five typed artifacts referenced by an integrity-checked manifest."""

    try:
        canonical_manifest = load_manifest(manifest_path)
    except DossierManifestError as exc:
        return DossierArtifactValidation(False, [str(exc)])

    try:
        raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return DossierArtifactValidation(False, [f"artifact_schema_invalid: manifest read failed: {exc}"])

    raw_artifacts = raw_manifest.get("artifacts") if isinstance(raw_manifest, dict) else None
    if not isinstance(raw_artifacts, list):
        return DossierArtifactValidation(False, ["artifact_schema_invalid: manifest artifacts are unavailable"])

    errors: list[str] = []
    artifacts_by_kind: dict[str, Path] = {}
    canonical_paths = {artifact["path"] for artifact in canonical_manifest["artifacts"]}  # type: ignore[index]
    for index, artifact in enumerate(raw_artifacts):
        if not isinstance(artifact, dict):
            continue
        kind = artifact.get("kind")
        path = artifact.get("path")
        if not isinstance(kind, str) or not kind.strip():
            errors.append(f"artifact_role_invalid: artifact {index} is missing kind")
            continue
        if kind not in REQUIRED_ARTIFACT_KINDS:
            errors.append(f"artifact_role_invalid: unknown kind {kind}")
            continue
        if kind in artifacts_by_kind:
            errors.append(f"artifact_role_invalid: duplicate kind {kind}")
            continue
        if not isinstance(path, str) or path not in canonical_paths:
            errors.append(f"artifact_role_invalid: {kind} does not name an integrity-checked path")
            continue
        artifacts_by_kind[kind] = manifest_path.parent / path

    missing_kinds = REQUIRED_ARTIFACT_KINDS - artifacts_by_kind.keys()
    for kind in sorted(missing_kinds):
        errors.append(f"artifact_role_invalid: missing required kind {kind}")

    if errors:
        return DossierArtifactValidation(False, errors)

    run_id = canonical_manifest["run_id"]
    assert isinstance(run_id, str)
    errors.extend(_validate_heartbeat(artifacts_by_kind["heartbeat"], run_id))
    errors.extend(_validate_token_ledger(artifacts_by_kind["token_ledger"], run_id))
    errors.extend(_validate_advisor_verdict(artifacts_by_kind["advisor_verdict"], run_id))
    errors.extend(_validate_archive_manifest(artifacts_by_kind["archive_manifest"], run_id))
    errors.extend(_validate_worker_result(artifacts_by_kind["worker_result"]))
    return DossierArtifactValidation(not errors, errors)


def reconcile_dossier(manifest_path: Path) -> DossierReconciliation:
    """Reconcile run identity, Worker session identity, and terminal outcomes."""

    validation = validate_dossier_artifacts(manifest_path)
    if not validation.ok:
        return DossierReconciliation(
            False,
            [
                {"code": "artifact_validation_failed", "detail": error}
                for error in sorted(validation.errors)
            ],
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    assert isinstance(manifest, dict)
    run_id = manifest["run_id"]
    assert isinstance(run_id, str)
    paths = {
        artifact["kind"]: manifest_path.parent / artifact["path"]
        for artifact in manifest["artifacts"]
        if isinstance(artifact, dict)
    }

    heartbeat = load_heartbeat_jsonl(paths["heartbeat"])
    token_ledger = _load_json(paths["token_ledger"], "token_ledger")[0]
    advisor_verdict = _load_json(paths["advisor_verdict"], "advisor_verdict")[0]
    archive_manifest = _load_json(paths["archive_manifest"], "archive_manifest")[0]
    assert token_ledger is not None and advisor_verdict is not None and archive_manifest is not None

    conflicts: list[dict[str, str]] = []
    for index, record in enumerate(heartbeat, 1):
        if record.get("run_id") != run_id:
            conflicts.append(_conflict("run_id_mismatch", "heartbeat", f"record:{index}"))
        if index > 1 and parse_timestamp(record["timestamp"]) < parse_timestamp(heartbeat[index - 2]["timestamp"]):
            conflicts.append(_conflict("heartbeat_timestamp_regression", "heartbeat", f"record:{index}"))
    for kind, document in (
        ("token_ledger", token_ledger),
        ("advisor_verdict", advisor_verdict),
        ("archive_manifest", archive_manifest),
    ):
        if document.get("run_id") != run_id:
            conflicts.append(_conflict("run_id_mismatch", kind, "run_id"))

    worker_sessions = [
        role.get("session_id")
        for role in token_ledger["roles"]
        if isinstance(role, dict) and role.get("role") == "worker"
    ]
    if len(worker_sessions) == 0:
        conflicts.append(_conflict("worker_role_missing", "token_ledger", "roles"))
    elif len(worker_sessions) != 1:
        conflicts.append(_conflict("worker_role_ambiguous", "token_ledger", "roles"))
    else:
        worker_session = worker_sessions[0]
        for index, record in enumerate(heartbeat, 1):
            if record.get("session_id") != worker_session:
                conflicts.append(_conflict("worker_session_mismatch", "heartbeat", f"record:{index}"))
        if archive_manifest.get("session_id") != worker_session:
            conflicts.append(_conflict("worker_session_mismatch", "archive_manifest", "session_id"))

    advisor_roles = [
        role
        for role in token_ledger["roles"]
        if isinstance(role, dict) and role.get("role") == "advisor"
    ]
    if len(advisor_roles) == 0:
        conflicts.append(_conflict("advisor_role_missing", "token_ledger", "roles"))
    elif len(advisor_roles) != 1:
        conflicts.append(_conflict("advisor_role_ambiguous", "token_ledger", "roles"))
    else:
        advisor_role = advisor_roles[0]
        if advisor_role.get("session_id") != advisor_verdict.get("advisor_session_id"):
            conflicts.append(_conflict("advisor_session_mismatch", "advisor_verdict", "advisor_session_id"))
        if advisor_role.get("lineage_id") != advisor_verdict.get("advisor_lineage_id"):
            conflicts.append(_conflict("advisor_lineage_mismatch", "advisor_verdict", "advisor_lineage_id"))

    worker_status = _worker_status(paths["worker_result"])
    advisor_outcome = advisor_verdict.get("verdict")
    required_worker_status = {
        "accepted": "accepted-candidate",
        "defect_packet": "needs-supervisor-review",
        "verified_blocker": "blocked",
    }[advisor_outcome]
    if worker_status != required_worker_status:
        conflicts.append(_conflict("terminal_outcome_mismatch", "worker_result", "final_status"))

    conflicts.sort(key=lambda conflict: (conflict["code"], conflict["artifact"], conflict["field"]))
    return DossierReconciliation(not conflicts, conflicts)


def analyze_dossier_timeline(
    manifest_path: Path, *, stale_after_seconds: int = 600
) -> DossierTimelineAnalysis:
    """Build a safe ordered timeline and flag missing or contradictory lifecycle evidence."""

    validation = validate_dossier_artifacts(manifest_path)
    if not validation.ok:
        return DossierTimelineAnalysis(
            [],
            [
                {"code": "artifact_validation_failed", "artifact": "dossier", "field": error}
                for error in sorted(validation.errors)
            ],
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    assert isinstance(manifest, dict)
    paths = {
        artifact["kind"]: manifest_path.parent / artifact["path"]
        for artifact in manifest["artifacts"]
        if isinstance(artifact, dict)
    }
    heartbeat = load_heartbeat_jsonl(paths["heartbeat"])
    token_ledger = _load_json(paths["token_ledger"], "token_ledger")[0]
    advisor_verdict = _load_json(paths["advisor_verdict"], "advisor_verdict")[0]
    archive_manifest = _load_json(paths["archive_manifest"], "archive_manifest")[0]
    assert token_ledger is not None and advisor_verdict is not None and archive_manifest is not None

    timeline: list[dict[str, str]] = []
    anomalies: list[dict[str, str]] = []
    heartbeat_times = []
    for index, record in enumerate(heartbeat, 1):
        timestamp = parse_timestamp(record["timestamp"])
        heartbeat_times.append(timestamp)
        timeline.append(
            _timeline_event(timestamp, "heartbeat", "worker", "worker_heartbeat", str(record["status"]))
        )
        if index > 1 and (timestamp - heartbeat_times[index - 2]).total_seconds() > stale_after_seconds:
            anomalies.append(_anomaly("stale_heartbeat", "heartbeat", f"record:{index}"))

    statuses = {record["status"] for record in heartbeat}
    if not statuses.intersection({"thinking", "running_command"}):
        anomalies.append(_anomaly("missing_worker_start", "heartbeat", "status"))
    if not statuses.intersection({"completed", "blocked"}):
        anomalies.append(_anomaly("missing_worker_terminal", "heartbeat", "status"))

    for index, role in enumerate(token_ledger["roles"]):
        assert isinstance(role, dict)
        role_name = str(role["role"])
        if role.get("closed") is not True:
            anomalies.append(_anomaly("unclosed_role", "token_ledger", f"roles:{index}"))
        start = _optional_timestamp(role.get("span_start"))
        end = _optional_timestamp(role.get("span_end"))
        if start is None or end is None or end < start:
            anomalies.append(_anomaly("token_span_gap", "token_ledger", f"roles:{index}"))
            continue
        timeline.append(_timeline_event(start, "token_ledger", role_name, "token_span_start", "open"))
        timeline.append(_timeline_event(end, "token_ledger", role_name, "token_span_end", "closed"))

    advisor_time = _optional_timestamp(advisor_verdict.get("timestamp"))
    if advisor_time is None:
        anomalies.append(_anomaly("advisor_timestamp_missing", "advisor_verdict", "timestamp"))
    else:
        timeline.append(
            _timeline_event(advisor_time, "advisor_verdict", "advisor", "advisor_verdict", str(advisor_verdict["verdict"]))
        )
    archive_time = _optional_timestamp(archive_manifest.get("captured_at"))
    if archive_time is None:
        anomalies.append(_anomaly("archive_timestamp_missing", "archive_manifest", "captured_at"))
    else:
        timeline.append(_timeline_event(archive_time, "archive_manifest", "worker", "archive_captured", "captured"))

    for conflict in reconcile_dossier(manifest_path).conflicts:
        if conflict["code"] == "terminal_outcome_mismatch":
            anomalies.append(_anomaly("result_advisor_disagreement", "worker_result", "final_status"))

    timeline.sort(key=lambda event: (event["timestamp"], event["stage"], event["role"], event["source"]))
    anomalies.sort(key=lambda anomaly: (anomaly["code"], anomaly["artifact"], anomaly["field"]))
    return DossierTimelineAnalysis(timeline, anomalies)


def build_dossier_report(manifest_path: Path) -> dict[str, Any]:
    """Build the deterministic public-safe report used by the dossier CLI."""

    validation = validate_dossier_artifacts(manifest_path)
    try:
        manifest = load_manifest(manifest_path)
        run_id = manifest["run_id"]
    except DossierManifestError:
        run_id = ""
    reconciliation = reconcile_dossier(manifest_path)
    analysis = analyze_dossier_timeline(manifest_path)
    return {
        "schema_version": "p107_dossier_report_v1",
        "run_id": run_id,
        "artifact_validation": {"ok": validation.ok, "errors": sorted(validation.errors)},
        "reconciliation": {"ok": reconciliation.ok, "conflicts": reconciliation.conflicts},
        "timeline": analysis.timeline,
        "anomalies": analysis.anomalies,
        "valid": validation.ok and reconciliation.ok and not analysis.anomalies,
    }


def render_dossier_json(manifest_path: Path) -> str:
    """Render a deterministic JSON dossier report."""

    return json.dumps(build_dossier_report(manifest_path), indent=2, sort_keys=True) + "\n"


def render_dossier_markdown(manifest_path: Path) -> str:
    """Render a deterministic Markdown dossier report."""

    report = build_dossier_report(manifest_path)
    lines = [
        "# P107 Run Evidence Dossier",
        "",
        f"- run id: `{report['run_id']}`",
        f"- status: `{'valid' if report['valid'] else 'invalid'}`",
        "",
        "## Artifact Validation",
        "",
    ]
    lines.extend(_render_messages(report["artifact_validation"]["errors"], "No artifact validation errors."))
    lines.extend(["", "## Reconciliation", ""])
    lines.extend(_render_records(report["reconciliation"]["conflicts"], "No reconciliation conflicts."))
    lines.extend(["", "## Timeline", ""])
    if report["timeline"]:
        lines.extend(
            f"- `{event['timestamp']}` {event['role']} {event['stage']} ({event['status']})"
            for event in report["timeline"]
        )
    else:
        lines.append("No timeline events.")
    lines.extend(["", "## Anomalies", ""])
    lines.extend(_render_records(report["anomalies"], "No lifecycle anomalies."))
    return "\n".join(lines) + "\n"


def _load_json(path: Path, kind: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        document = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"artifact_schema_invalid: {kind} is not readable JSON: {exc}"]
    if not isinstance(document, dict):
        return None, [f"artifact_schema_invalid: {kind} must be a JSON object"]
    return document, []


def _require_nonempty_string(document: dict[str, Any], field: str, kind: str) -> list[str]:
    value = document.get(field)
    if not isinstance(value, str) or not value.strip():
        return [f"artifact_schema_invalid: {kind}.{field} must be a non-empty string"]
    return []


def _validate_heartbeat(path: Path, run_id: str) -> list[str]:
    try:
        records = load_heartbeat_jsonl(path)
    except (OSError, ValueError) as exc:
        return [f"artifact_schema_invalid: heartbeat is invalid JSONL: {exc}"]
    result = validate_heartbeat_records(records)
    errors = [f"artifact_schema_invalid: heartbeat {error}" for error in result.errors]
    for index, record in enumerate(records, 1):
        if record.get("run_id") != run_id:
            errors.append(f"artifact_schema_invalid: heartbeat record {index} run_id mismatch")
        if not isinstance(record.get("session_id"), str) or not record["session_id"].strip():
            errors.append(f"artifact_schema_invalid: heartbeat record {index} session_id is required")
    return errors


def _validate_token_ledger(path: Path, run_id: str) -> list[str]:
    document, errors = _load_json(path, "token_ledger")
    if document is None:
        return errors
    errors.extend(_require_nonempty_string(document, "run_id", "token_ledger"))
    if document.get("run_id") != run_id:
        errors.append("artifact_schema_invalid: token_ledger run_id mismatch")
    roles = document.get("roles")
    if not isinstance(roles, list) or not roles:
        return errors + ["artifact_schema_invalid: token_ledger.roles must be a non-empty list"]
    for index, role in enumerate(roles):
        if not isinstance(role, dict):
            errors.append(f"artifact_schema_invalid: token_ledger role {index} must be an object")
            continue
        errors.extend(_require_nonempty_string(role, "role", f"token_ledger role {index}"))
        errors.extend(_require_nonempty_string(role, "session_id", f"token_ledger role {index}"))
    return errors


def _validate_advisor_verdict(path: Path, run_id: str) -> list[str]:
    document, errors = _load_json(path, "advisor_verdict")
    if document is None:
        return errors
    for field in ("run_id", "advisor_session_id", "advisor_lineage_id"):
        errors.extend(_require_nonempty_string(document, field, "advisor_verdict"))
    if document.get("run_id") != run_id:
        errors.append("artifact_schema_invalid: advisor_verdict run_id mismatch")
    if document.get("verdict") not in ALLOWED_ADVISOR_VERDICTS:
        errors.append("artifact_schema_invalid: advisor_verdict verdict is invalid")
    return errors


def _validate_archive_manifest(path: Path, run_id: str) -> list[str]:
    document, errors = _load_json(path, "archive_manifest")
    if document is None:
        return errors
    for field in ("run_id", "session_id"):
        errors.extend(_require_nonempty_string(document, field, "archive_manifest"))
    if document.get("run_id") != run_id:
        errors.append("artifact_schema_invalid: archive_manifest run_id mismatch")
    models = document.get("model_ids_detected")
    if not isinstance(models, list) or not models or any(not isinstance(model, str) or not model.strip() for model in models):
        errors.append("artifact_schema_invalid: archive_manifest.model_ids_detected must be a non-empty string list")
    return errors


def _validate_worker_result(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return [f"artifact_schema_invalid: worker_result cannot be read: {exc}"]
    statuses = _FINAL_STATUS.findall(text)
    if len(statuses) != 1 or statuses[0] not in ALLOWED_WORKER_STATUSES:
        return ["artifact_schema_invalid: worker_result must contain one valid Final Status"]
    return []


def _worker_status(path: Path) -> str:
    return _FINAL_STATUS.findall(path.read_text(encoding="utf-8-sig"))[0]


def _conflict(code: str, artifact: str, field: str) -> dict[str, str]:
    return {"code": code, "artifact": artifact, "field": field}


def _anomaly(code: str, artifact: str, field: str) -> dict[str, str]:
    return {"code": code, "artifact": artifact, "field": field}


def _optional_timestamp(value: Any):
    if not isinstance(value, str):
        return None
    try:
        return parse_timestamp(value)
    except ValueError:
        return None


def _timeline_event(timestamp: Any, source: str, role: str, stage: str, status: str) -> dict[str, str]:
    normalized = timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return {"timestamp": normalized, "source": source, "role": role, "stage": stage, "status": status}


def _render_messages(messages: list[str], empty: str) -> list[str]:
    return [f"- {message}" for message in messages] if messages else [empty]


def _render_records(records: list[dict[str, str]], empty: str) -> list[str]:
    if not records:
        return [empty]
    return [
        "- " + ", ".join(f"{key}=`{value}`" for key, value in sorted(record.items()))
        for record in records
    ]
