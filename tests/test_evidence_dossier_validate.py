"""Tests for typed P107 dossier artifact validation."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from agent_workbench.cli import main
from agent_workbench.evidence_dossier import SCHEMA_VERSION
from agent_workbench.evidence_dossier_validate import (
    analyze_dossier_timeline,
    render_dossier_json,
    render_dossier_markdown,
    reconcile_dossier,
    validate_dossier_artifacts,
)


RUN_ID = "run-001"
FROZEN_FIXTURE_MANIFEST = (
    Path(__file__).parent / "fixtures" / "p107_run_evidence_dossier_v3" / "manifest.json"
)


def _write(path: Path, content: str) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _valid_documents() -> dict[str, str]:
    return {
        "heartbeat": json.dumps(
            {
                "timestamp": "2026-07-20T12:00:00Z",
                "checklist_item": "implement",
                "status": "completed",
                "action": "pytest",
                "artifact_path": "output.txt",
                "command_summary": "pytest -q",
                "next_intended_action": "report",
                "run_id": RUN_ID,
                "session_id": "worker-1",
            }
        )
        + "\n",
        "token_ledger": json.dumps(
            {
                "run_id": RUN_ID,
                "roles": [
                    {"role": "worker", "session_id": "worker-1"},
                    {"role": "advisor", "session_id": "advisor-1", "lineage_id": "lineage-1"},
                ],
            }
        ),
        "advisor_verdict": json.dumps(
            {
                "run_id": RUN_ID,
                "advisor_session_id": "advisor-1",
                "advisor_lineage_id": "lineage-1",
                "verdict": "accepted",
            }
        ),
        "archive_manifest": json.dumps(
            {"run_id": RUN_ID, "session_id": "worker-1", "model_ids_detected": ["worker-model"]}
        ),
        "worker_result": "# Worker Result\n\n## Final Status\n\n`accepted-candidate`\n",
    }


def _dossier(tmp_path: Path, documents: dict[str, str] | None = None) -> Path:
    documents = documents or _valid_documents()
    artifacts = []
    for kind, content in documents.items():
        suffix = ".md" if kind == "worker_result" else ".jsonl" if kind == "heartbeat" else ".json"
        artifact = _write(tmp_path / f"{kind}{suffix}", content)
        artifacts.append({"kind": kind, **artifact})
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "run_id": RUN_ID, "artifacts": artifacts}),
        encoding="utf-8",
    )
    return manifest


def _analysis_documents() -> dict[str, str]:
    documents = _valid_documents()
    first = json.loads(documents["heartbeat"])
    first.update(status="thinking", timestamp="2026-07-20T12:00:00Z")
    second = dict(first, status="completed", timestamp="2026-07-20T12:01:00Z")
    documents["heartbeat"] = json.dumps(first) + "\n" + json.dumps(second) + "\n"
    ledger = json.loads(documents["token_ledger"])
    ledger["roles"][0].update(closed=True, span_start="2026-07-20T11:59:00Z", span_end="2026-07-20T12:02:00Z")
    ledger["roles"][1].update(closed=True, span_start="2026-07-20T12:00:30Z", span_end="2026-07-20T12:02:30Z")
    documents["token_ledger"] = json.dumps(ledger)
    verdict = json.loads(documents["advisor_verdict"])
    verdict["timestamp"] = "2026-07-20T12:02:30Z"
    documents["advisor_verdict"] = json.dumps(verdict)
    archive = json.loads(documents["archive_manifest"])
    archive["captured_at"] = "2026-07-20T12:03:00Z"
    documents["archive_manifest"] = json.dumps(archive)
    return documents


def _copy_frozen_fixture(tmp_path: Path) -> Path:
    copied = tmp_path / "fixture"
    shutil.copytree(FROZEN_FIXTURE_MANIFEST.parent, copied)
    return copied / "manifest.json"


def _refresh_artifact_hash(manifest: Path, artifact_name: str) -> None:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    artifact_path = manifest.parent / artifact_name
    for artifact in data["artifacts"]:
        if artifact["path"] == artifact_name:
            artifact["sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            break
    else:
        raise AssertionError(f"fixture manifest has no {artifact_name}")
    manifest.write_text(json.dumps(data), encoding="utf-8")


def test_accepts_complete_typed_dossier(tmp_path: Path) -> None:
    result = validate_dossier_artifacts(_dossier(tmp_path))
    assert result.ok, result.errors


def test_rejects_missing_required_artifact_kind(tmp_path: Path) -> None:
    documents = _valid_documents()
    del documents["archive_manifest"]
    result = validate_dossier_artifacts(_dossier(tmp_path, documents))
    assert not result.ok
    assert "artifact_role_invalid: missing required kind archive_manifest" in result.errors


def test_rejects_unknown_artifact_kind(tmp_path: Path) -> None:
    manifest = _dossier(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["artifacts"][0]["kind"] = "unknown"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    result = validate_dossier_artifacts(manifest)
    assert not result.ok
    assert "artifact_role_invalid: unknown kind unknown" in result.errors


def test_rejects_heartbeat_without_session_id(tmp_path: Path) -> None:
    documents = _valid_documents()
    heartbeat = json.loads(documents["heartbeat"])
    del heartbeat["session_id"]
    documents["heartbeat"] = json.dumps(heartbeat) + "\n"
    result = validate_dossier_artifacts(_dossier(tmp_path, documents))
    assert not result.ok
    assert "artifact_schema_invalid: heartbeat record 1 session_id is required" in result.errors


def test_rejects_token_ledger_without_role_session_id(tmp_path: Path) -> None:
    documents = _valid_documents()
    documents["token_ledger"] = json.dumps({"run_id": RUN_ID, "roles": [{"role": "worker"}]})
    result = validate_dossier_artifacts(_dossier(tmp_path, documents))
    assert not result.ok
    assert "artifact_schema_invalid: token_ledger role 0.session_id must be a non-empty string" in result.errors


def test_rejects_advisor_verdict_with_invalid_outcome(tmp_path: Path) -> None:
    documents = _valid_documents()
    verdict = json.loads(documents["advisor_verdict"])
    verdict["verdict"] = "pending"
    documents["advisor_verdict"] = json.dumps(verdict)
    result = validate_dossier_artifacts(_dossier(tmp_path, documents))
    assert not result.ok
    assert "artifact_schema_invalid: advisor_verdict verdict is invalid" in result.errors


def test_rejects_archive_manifest_without_models(tmp_path: Path) -> None:
    documents = _valid_documents()
    documents["archive_manifest"] = json.dumps({"run_id": RUN_ID, "session_id": "worker-1", "model_ids_detected": []})
    result = validate_dossier_artifacts(_dossier(tmp_path, documents))
    assert not result.ok
    assert "artifact_schema_invalid: archive_manifest.model_ids_detected must be a non-empty string list" in result.errors


def test_rejects_worker_result_without_valid_final_status(tmp_path: Path) -> None:
    documents = _valid_documents()
    documents["worker_result"] = "# Worker Result\n\n## Final Status\n\n`finished`\n"
    result = validate_dossier_artifacts(_dossier(tmp_path, documents))
    assert not result.ok
    assert "artifact_schema_invalid: worker_result must contain one valid Final Status" in result.errors


def test_rejects_manifest_tampering_before_schema_validation(tmp_path: Path) -> None:
    manifest = _dossier(tmp_path)
    (tmp_path / "advisor_verdict.json").write_text("{}", encoding="utf-8")
    result = validate_dossier_artifacts(manifest)
    assert not result.ok
    assert any(error.startswith("artifact_digest_mismatch") for error in result.errors)


def test_reconciliation_accepts_consistent_typed_dossier(tmp_path: Path) -> None:
    result = reconcile_dossier(_dossier(tmp_path))
    assert result.ok, result.conflicts
    assert result.conflicts == []


def test_reconciliation_reports_worker_session_mismatch(tmp_path: Path) -> None:
    documents = _valid_documents()
    heartbeat = json.loads(documents["heartbeat"])
    heartbeat["session_id"] = "different-worker"
    documents["heartbeat"] = json.dumps(heartbeat) + "\n"
    result = reconcile_dossier(_dossier(tmp_path, documents))
    assert not result.ok
    assert result.conflicts == [
        {"code": "worker_session_mismatch", "artifact": "heartbeat", "field": "record:1"}
    ]


def test_reconciliation_reports_missing_worker_role(tmp_path: Path) -> None:
    documents = _valid_documents()
    documents["token_ledger"] = json.dumps(
        {
            "run_id": RUN_ID,
            "roles": [
                {"role": "coordinator", "session_id": "coordinator-1"},
                {"role": "advisor", "session_id": "advisor-1", "lineage_id": "lineage-1"},
            ],
        }
    )
    result = reconcile_dossier(_dossier(tmp_path, documents))
    assert not result.ok
    assert result.conflicts == [
        {"code": "worker_role_missing", "artifact": "token_ledger", "field": "roles"}
    ]


def test_reconciliation_reports_terminal_outcome_disagreement(tmp_path: Path) -> None:
    documents = _valid_documents()
    documents["worker_result"] = "# Worker Result\n\n## Final Status\n\n`blocked`\n"
    result = reconcile_dossier(_dossier(tmp_path, documents))
    assert not result.ok
    assert result.conflicts == [
        {"code": "terminal_outcome_mismatch", "artifact": "worker_result", "field": "final_status"}
    ]


def test_reconciliation_reports_advisor_session_and_lineage_mismatch(tmp_path: Path) -> None:
    documents = _valid_documents()
    ledger = json.loads(documents["token_ledger"])
    ledger["roles"][1].update(session_id="other-advisor", lineage_id="other-lineage")
    documents["token_ledger"] = json.dumps(ledger)
    result = reconcile_dossier(_dossier(tmp_path, documents))
    assert not result.ok
    assert result.conflicts == [
        {"code": "advisor_lineage_mismatch", "artifact": "advisor_verdict", "field": "advisor_lineage_id"},
        {"code": "advisor_session_mismatch", "artifact": "advisor_verdict", "field": "advisor_session_id"},
    ]


def test_reconciliation_reports_heartbeat_timestamp_regression(tmp_path: Path) -> None:
    documents = _valid_documents()
    first = json.loads(documents["heartbeat"])
    second = dict(first, timestamp="2026-07-20T11:59:00Z")
    documents["heartbeat"] = json.dumps(first) + "\n" + json.dumps(second) + "\n"
    result = reconcile_dossier(_dossier(tmp_path, documents))
    assert not result.ok
    assert result.conflicts == [
        {"code": "heartbeat_timestamp_regression", "artifact": "heartbeat", "field": "record:2"}
    ]


def test_reconciliation_returns_validation_failures_as_sorted_conflicts(tmp_path: Path) -> None:
    documents = _valid_documents()
    documents["worker_result"] = "# Worker Result\n\n## Final Status\n\n`finished`\n"
    result = reconcile_dossier(_dossier(tmp_path, documents))
    assert not result.ok
    assert result.conflicts == [
        {
            "code": "artifact_validation_failed",
            "detail": "artifact_schema_invalid: worker_result must contain one valid Final Status",
        }
    ]


def test_timeline_analysis_normalizes_consistent_lifecycle(tmp_path: Path) -> None:
    result = analyze_dossier_timeline(_dossier(tmp_path, _analysis_documents()))
    assert result.anomalies == []
    assert [event["stage"] for event in result.timeline] == [
        "token_span_start",
        "worker_heartbeat",
        "token_span_start",
        "worker_heartbeat",
        "token_span_end",
        "advisor_verdict",
        "token_span_end",
        "archive_captured",
    ]


def test_timeline_analysis_reports_stale_heartbeat(tmp_path: Path) -> None:
    documents = _analysis_documents()
    records = [json.loads(line) for line in documents["heartbeat"].splitlines()]
    records[1]["timestamp"] = "2026-07-20T12:30:00Z"
    documents["heartbeat"] = "\n".join(json.dumps(record) for record in records) + "\n"
    result = analyze_dossier_timeline(_dossier(tmp_path, documents), stale_after_seconds=600)
    assert {anomaly["code"] for anomaly in result.anomalies} == {"stale_heartbeat"}


def test_timeline_analysis_reports_missing_worker_start(tmp_path: Path) -> None:
    documents = _analysis_documents()
    records = [json.loads(line) for line in documents["heartbeat"].splitlines()]
    records[0]["status"] = "completed"
    documents["heartbeat"] = "\n".join(json.dumps(record) for record in records) + "\n"
    result = analyze_dossier_timeline(_dossier(tmp_path, documents))
    assert {anomaly["code"] for anomaly in result.anomalies} == {"missing_worker_start"}


def test_timeline_analysis_reports_missing_worker_terminal(tmp_path: Path) -> None:
    documents = _analysis_documents()
    records = [json.loads(line) for line in documents["heartbeat"].splitlines()]
    records[1]["status"] = "running_command"
    documents["heartbeat"] = "\n".join(json.dumps(record) for record in records) + "\n"
    result = analyze_dossier_timeline(_dossier(tmp_path, documents))
    assert {anomaly["code"] for anomaly in result.anomalies} == {"missing_worker_terminal"}


def test_timeline_analysis_reports_unclosed_role_and_token_span_gap(tmp_path: Path) -> None:
    documents = _analysis_documents()
    ledger = json.loads(documents["token_ledger"])
    ledger["roles"][0].pop("closed")
    ledger["roles"][0].pop("span_end")
    documents["token_ledger"] = json.dumps(ledger)
    result = analyze_dossier_timeline(_dossier(tmp_path, documents))
    assert {anomaly["code"] for anomaly in result.anomalies} == {"token_span_gap", "unclosed_role"}


def test_timeline_analysis_reports_result_advisor_disagreement(tmp_path: Path) -> None:
    documents = _analysis_documents()
    documents["worker_result"] = "# Worker Result\n\n## Final Status\n\n`blocked`\n"
    result = analyze_dossier_timeline(_dossier(tmp_path, documents))
    assert {anomaly["code"] for anomaly in result.anomalies} == {"result_advisor_disagreement"}


def test_dossier_renderers_are_deterministic_and_public_safe(tmp_path: Path) -> None:
    manifest = _dossier(tmp_path, _analysis_documents())
    first_json = render_dossier_json(manifest)
    assert first_json == render_dossier_json(manifest)
    report = json.loads(first_json)
    assert report["valid"] is True
    assert report["run_id"] == RUN_ID
    markdown = render_dossier_markdown(manifest)
    assert "# P107 Run Evidence Dossier" in markdown
    assert "No lifecycle anomalies." in markdown


def test_dossier_cli_validates_strictly_and_renders_both_formats(tmp_path: Path) -> None:
    manifest = _dossier(tmp_path, _analysis_documents())
    assert main(["dossier", "validate", "--manifest", str(manifest)]) == 0
    json_output = tmp_path / "report.json"
    markdown_output = tmp_path / "report.md"
    assert main(["dossier", "render", "--manifest", str(manifest), "--format", "json", "--output", str(json_output)]) == 0
    assert main(["dossier", "render", "--manifest", str(manifest), "--output", str(markdown_output)]) == 0
    assert json.loads(json_output.read_text(encoding="utf-8"))["valid"] is True
    assert markdown_output.read_text(encoding="utf-8") == render_dossier_markdown(manifest)

    documents = _analysis_documents()
    documents["worker_result"] = "# Worker Result\n\n## Final Status\n\n`blocked`\n"
    invalid_manifest = _dossier(tmp_path / "invalid", documents)
    assert main(["dossier", "validate", "--manifest", str(invalid_manifest)]) == 1


def test_frozen_v3_fixture_passes_module_and_cli_acceptance(tmp_path: Path) -> None:
    assert validate_dossier_artifacts(FROZEN_FIXTURE_MANIFEST).ok
    assert reconcile_dossier(FROZEN_FIXTURE_MANIFEST).ok
    analysis = analyze_dossier_timeline(FROZEN_FIXTURE_MANIFEST)
    assert analysis.anomalies == []
    assert main(["dossier", "validate", "--manifest", str(FROZEN_FIXTURE_MANIFEST)]) == 0
    output = tmp_path / "frozen-fixture-report.json"
    assert main(
        [
            "dossier",
            "render",
            "--manifest",
            str(FROZEN_FIXTURE_MANIFEST),
            "--format",
            "json",
            "--output",
            str(output),
        ]
    ) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["valid"] is True


@pytest.mark.parametrize(
    "artifact_name",
    [
        "advisor_verdict.json",
        "archive_manifest.json",
        "heartbeat.jsonl",
        "token_ledger.json",
        "worker_result.md",
    ],
)
def test_frozen_fixture_rejects_each_tampered_artifact(tmp_path: Path, artifact_name: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    artifact = manifest.parent / artifact_name
    artifact.write_text(artifact.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    result = validate_dossier_artifacts(manifest)
    assert not result.ok
    assert any(error.startswith("artifact_digest_mismatch") for error in result.errors)


@pytest.mark.parametrize(
    "kind",
    ["advisor_verdict", "archive_manifest", "heartbeat", "token_ledger", "worker_result"],
)
def test_frozen_fixture_requires_each_named_artifact_kind(tmp_path: Path, kind: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["artifacts"] = [artifact for artifact in data["artifacts"] if artifact["kind"] != kind]
    manifest.write_text(json.dumps(data), encoding="utf-8")
    result = validate_dossier_artifacts(manifest)
    assert not result.ok
    assert f"artifact_role_invalid: missing required kind {kind}" in result.errors


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("timestamp", "artifact_schema_invalid: heartbeat record 1: missing required field: timestamp"),
        ("checklist_item", "artifact_schema_invalid: heartbeat record 1: missing required field: checklist_item"),
        ("status", "artifact_schema_invalid: heartbeat record 1: missing required field: status"),
        ("action", "artifact_schema_invalid: heartbeat record 1: missing required field: action"),
        ("artifact_path", "artifact_schema_invalid: heartbeat record 1: missing required field: artifact_path"),
        ("command_summary", "artifact_schema_invalid: heartbeat record 1: missing required field: command_summary"),
        ("next_intended_action", "artifact_schema_invalid: heartbeat record 1: missing required field: next_intended_action"),
        ("run_id", "artifact_schema_invalid: heartbeat record 1 run_id mismatch"),
        ("session_id", "artifact_schema_invalid: heartbeat record 1 session_id is required"),
    ],
)
def test_frozen_fixture_heartbeat_schema_refusals(tmp_path: Path, field: str, expected: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    heartbeat = manifest.parent / "heartbeat.jsonl"
    records = [json.loads(line) for line in heartbeat.read_text(encoding="utf-8").splitlines()]
    if field in {"run_id", "session_id"}:
        records[0][field] = "wrong-run" if field == "run_id" else ""
    else:
        del records[0][field]
    heartbeat.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    _refresh_artifact_hash(manifest, "heartbeat.jsonl")
    assert expected in validate_dossier_artifacts(manifest).errors


@pytest.mark.parametrize(
    ("replacement", "expected"),
    [
        ({"roles": []}, "artifact_schema_invalid: token_ledger.run_id must be a non-empty string"),
        ({"run_id": "p107-dossier-fixture-001", "roles": []}, "artifact_schema_invalid: token_ledger.roles must be a non-empty list"),
        ({"run_id": "p107-dossier-fixture-001", "roles": {}}, "artifact_schema_invalid: token_ledger.roles must be a non-empty list"),
        ({"run_id": "p107-dossier-fixture-001", "roles": ["worker"]}, "artifact_schema_invalid: token_ledger role 0 must be an object"),
        ({"run_id": "p107-dossier-fixture-001", "roles": [{"session_id": "worker-fixture-001"}]}, "artifact_schema_invalid: token_ledger role 0.role must be a non-empty string"),
        ({"run_id": "p107-dossier-fixture-001", "roles": [{"role": "worker"}]}, "artifact_schema_invalid: token_ledger role 0.session_id must be a non-empty string"),
    ],
)
def test_frozen_fixture_token_ledger_schema_refusals(tmp_path: Path, replacement: dict, expected: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    ledger = manifest.parent / "token_ledger.json"
    ledger.write_text(json.dumps(replacement), encoding="utf-8")
    _refresh_artifact_hash(manifest, "token_ledger.json")
    assert expected in validate_dossier_artifacts(manifest).errors


@pytest.mark.parametrize(
    "kind",
    ["advisor_verdict", "archive_manifest", "heartbeat", "token_ledger", "worker_result"],
)
def test_frozen_fixture_rejects_each_duplicate_artifact_kind(tmp_path: Path, kind: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    source_kind = "advisor_verdict" if kind == "worker_result" else "worker_result"
    next(artifact for artifact in data["artifacts"] if artifact["kind"] == source_kind)["kind"] = kind
    manifest.write_text(json.dumps(data), encoding="utf-8")
    result = validate_dossier_artifacts(manifest)
    assert not result.ok
    assert f"artifact_role_invalid: duplicate kind {kind}" in result.errors


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("run_id", "", "artifact_schema_invalid: advisor_verdict.run_id must be a non-empty string"),
        ("advisor_session_id", "", "artifact_schema_invalid: advisor_verdict.advisor_session_id must be a non-empty string"),
        ("advisor_lineage_id", "", "artifact_schema_invalid: advisor_verdict.advisor_lineage_id must be a non-empty string"),
        ("verdict", "pending", "artifact_schema_invalid: advisor_verdict verdict is invalid"),
    ],
)
def test_frozen_fixture_advisor_verdict_schema_refusals(tmp_path: Path, field: str, value: str, expected: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    verdict = manifest.parent / "advisor_verdict.json"
    data = json.loads(verdict.read_text(encoding="utf-8"))
    data[field] = value
    verdict.write_text(json.dumps(data), encoding="utf-8")
    _refresh_artifact_hash(manifest, "advisor_verdict.json")
    assert expected in validate_dossier_artifacts(manifest).errors


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("run_id", "", "artifact_schema_invalid: archive_manifest.run_id must be a non-empty string"),
        ("session_id", "", "artifact_schema_invalid: archive_manifest.session_id must be a non-empty string"),
        ("model_ids_detected", [], "artifact_schema_invalid: archive_manifest.model_ids_detected must be a non-empty string list"),
        ("model_ids_detected", "worker-model", "artifact_schema_invalid: archive_manifest.model_ids_detected must be a non-empty string list"),
        ("model_ids_detected", [""], "artifact_schema_invalid: archive_manifest.model_ids_detected must be a non-empty string list"),
    ],
)
def test_frozen_fixture_archive_manifest_schema_refusals(tmp_path: Path, field: str, value: object, expected: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    archive = manifest.parent / "archive_manifest.json"
    data = json.loads(archive.read_text(encoding="utf-8"))
    data[field] = value
    archive.write_text(json.dumps(data), encoding="utf-8")
    _refresh_artifact_hash(manifest, "archive_manifest.json")
    assert expected in validate_dossier_artifacts(manifest).errors


@pytest.mark.parametrize(
    "content",
    [
        "# Worker Result\n",
        "# Worker Result\n\n## Final Status\n\n`finished`\n",
        "# Worker Result\n\n## Final Status\n\n`accepted-candidate`\n\n## Final Status\n\n`blocked`\n",
    ],
)
def test_frozen_fixture_worker_result_schema_refusals(tmp_path: Path, content: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    result_path = manifest.parent / "worker_result.md"
    result_path.write_text(content, encoding="utf-8")
    _refresh_artifact_hash(manifest, "worker_result.md")
    errors = validate_dossier_artifacts(manifest).errors
    assert "artifact_schema_invalid: worker_result must contain one valid Final Status" in errors


@pytest.mark.parametrize(
    ("artifact_name", "field", "value", "expected_artifact", "expected_field"),
    [
        ("heartbeat.jsonl", "session_id", "other-worker", "heartbeat", "record:1"),
        ("archive_manifest.json", "session_id", "other-worker", "archive_manifest", "session_id"),
    ],
)
def test_frozen_fixture_reconciliation_rejects_worker_session_mismatches(
    tmp_path: Path, artifact_name: str, field: str, value: str, expected_artifact: str, expected_field: str
) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    artifact = manifest.parent / artifact_name
    if artifact_name.endswith("jsonl"):
        records = [json.loads(line) for line in artifact.read_text(encoding="utf-8").splitlines()]
        records[0][field] = value
        artifact.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    else:
        data = json.loads(artifact.read_text(encoding="utf-8"))
        data[field] = value
        artifact.write_text(json.dumps(data), encoding="utf-8")
    _refresh_artifact_hash(manifest, artifact_name)
    assert {"code": "worker_session_mismatch", "artifact": expected_artifact, "field": expected_field} in reconcile_dossier(manifest).conflicts


@pytest.mark.parametrize(
    ("field", "value", "expected_field"),
    [
        ("session_id", "other-advisor", "advisor_session_id"),
        ("lineage_id", "other-lineage", "advisor_lineage_id"),
    ],
)
def test_frozen_fixture_reconciliation_rejects_advisor_identity_mismatches(
    tmp_path: Path, field: str, value: str, expected_field: str
) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    ledger = manifest.parent / "token_ledger.json"
    data = json.loads(ledger.read_text(encoding="utf-8"))
    next(role for role in data["roles"] if role["role"] == "advisor")[field] = value
    ledger.write_text(json.dumps(data), encoding="utf-8")
    _refresh_artifact_hash(manifest, "token_ledger.json")
    assert {"code": f"advisor_{field.replace('_id', '')}_mismatch", "artifact": "advisor_verdict", "field": expected_field} in reconcile_dossier(manifest).conflicts


@pytest.mark.parametrize("role_name", ["worker", "advisor"])
def test_frozen_fixture_reconciliation_requires_worker_and_advisor_roles(tmp_path: Path, role_name: str) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    ledger = manifest.parent / "token_ledger.json"
    data = json.loads(ledger.read_text(encoding="utf-8"))
    data["roles"] = [role for role in data["roles"] if role["role"] != role_name]
    ledger.write_text(json.dumps(data), encoding="utf-8")
    _refresh_artifact_hash(manifest, "token_ledger.json")
    expected = f"{role_name}_role_missing"
    assert any(conflict["code"] == expected for conflict in reconcile_dossier(manifest).conflicts)


@pytest.mark.parametrize(
    ("advisor_verdict", "worker_status"),
    [
        ("accepted", "blocked"),
        ("accepted", "needs-supervisor-review"),
        ("defect_packet", "accepted-candidate"),
        ("verified_blocker", "accepted-candidate"),
    ],
)
def test_frozen_fixture_reconciliation_rejects_terminal_outcome_pairs(
    tmp_path: Path, advisor_verdict: str, worker_status: str
) -> None:
    manifest = _copy_frozen_fixture(tmp_path)
    verdict = manifest.parent / "advisor_verdict.json"
    data = json.loads(verdict.read_text(encoding="utf-8"))
    data["verdict"] = advisor_verdict
    verdict.write_text(json.dumps(data), encoding="utf-8")
    _refresh_artifact_hash(manifest, "advisor_verdict.json")
    worker_result = manifest.parent / "worker_result.md"
    worker_result.write_text(f"# Worker Result\n\n## Final Status\n\n`{worker_status}`\n", encoding="utf-8")
    _refresh_artifact_hash(manifest, "worker_result.md")
    assert any(conflict["code"] == "terminal_outcome_mismatch" for conflict in reconcile_dossier(manifest).conflicts)
