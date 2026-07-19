from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import pytest
from pathlib import Path

from agent_workbench.source_audit import audit_files


def setup(tmp_path: Path, records: list[object], **doc) -> tuple[Path, Path]:
    source = tmp_path / "doc.txt"
    source.write_text("héllo source\n", encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"documents": [{"document_id": "d1", "path": "doc.txt", "source_sha256": doc.get("hash", digest)}]}), encoding="utf-8")
    data = tmp_path / "records.jsonl"
    data.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records), encoding="utf-8")
    return manifest, data


def record(**kw):
    value = {"document_id": "d1", "chunk_id": "c1", "object_type": "paragraph", "source_path": "doc.txt", "source_quote": "héllo source"}
    value.update(kw)
    return value


def test_valid_digest_unicode_and_repeat_determinism(tmp_path):
    manifest, records = setup(tmp_path, [record()])
    one = audit_files(manifest, records, tmp_path / "one.json")
    two = audit_files(manifest, records, tmp_path / "two.json")
    assert one["status"] == "accepted"
    assert (tmp_path / "one.json").read_bytes() == (tmp_path / "two.json").read_bytes()


def test_hash_mismatch_traversal_and_schema_errors(tmp_path):
    manifest, records = setup(tmp_path, [record(chunk_id=""), record(source_path="../doc.txt")], hash="0" * 64)
    result = audit_files(manifest, records)
    codes = {error["code"] for error in result["errors"]}
    row_codes = {error["code"] for row in result["records"] for error in row["errors"]}
    assert "source_hash_mismatch" in codes
    assert "invalid_field" in row_codes
    assert "path_escape" in row_codes


def test_malformed_empty_duplicate_and_conflicting_provenance(tmp_path):
    source = tmp_path / "doc.txt"
    source.write_text("x", encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"documents": [{"document_id": "d1", "path": "doc.txt", "source_sha256": digest}, {"document_id": "d1", "path": "doc.txt", "source_sha256": digest}]}), encoding="utf-8")
    records = tmp_path / "records.jsonl"
    records.write_text(json.dumps(record(source_path="other.txt")) + "\nnot json\n", encoding="utf-8")
    result = audit_files(manifest, records)
    assert any(e["code"] == "duplicate_document_id" for e in result["errors"])
    assert any(e["code"] == "provenance_conflict" for e in result["records"][0]["errors"])
    assert result["records"][1]["errors"][0]["code"] == "malformed_json"


def test_empty_input_is_structured(tmp_path):
    manifest, records = setup(tmp_path, [])
    result = audit_files(manifest, records)
    assert result["status"] == "invalid"
    assert result["errors"] == [{"code": "empty_jsonl"}]


def cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    return subprocess.run(
        [sys.executable, "-m", "agent_workbench.cli", *args],
        cwd=tmp_path, env=env, text=True, capture_output=True, check=False,
    )


def test_cli_help_and_source_records_entrypoint(tmp_path):
    manifest, records = setup(tmp_path, [record()])
    help_result = cli(tmp_path, "source-audit", "--help")
    assert help_result.returncode == 0
    assert all(flag in help_result.stdout for flag in ("--manifest", "--source", "--records"))
    result = cli(tmp_path, "source-audit", "--manifest", str(manifest), "--records", str(records))
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "accepted"


def test_cli_manifest_only_and_exit_statuses(tmp_path):
    manifest, records = setup(tmp_path, [record()])
    manifest.write_text(json.dumps({"documents": [{"document_id": "d1", "path": "doc.txt", "source_sha256": hashlib.sha256((tmp_path / "doc.txt").read_bytes()).hexdigest()}], "records": records.name}), encoding="utf-8")
    assert cli(tmp_path, "source-audit", "--manifest", str(manifest)).returncode == 0
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps(record(source_quote="missing")) + "\n", encoding="utf-8")
    assert cli(tmp_path, "source-audit", "--manifest", str(manifest), "--records", str(bad)).returncode == 1
    assert cli(tmp_path, "source-audit", "--source", str(tmp_path / "doc.txt")).returncode == 2
    assert cli(tmp_path, "source-audit", "--manifest", str(tmp_path / "missing.json")).returncode == 2


def test_audit_rejects_nonstring_provenance_and_duplicate_ids_deterministically(tmp_path):
    manifest, records = setup(tmp_path, [record(source_path=3, source_quote="hÃ©llo source"), record(document_id="d1")])
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["documents"].append(data["documents"][0])
    manifest.write_text(json.dumps(data), encoding="utf-8")
    first = audit_files(manifest, records)
    second = audit_files(manifest, records)
    assert first == second
    assert any(error["code"] == "duplicate_document_id" for error in first["errors"])
    assert any(error["code"] == "invalid_field" for error in first["records"][0]["errors"])


def test_audit_malformed_and_empty_manifest_are_structured(tmp_path):
    records = tmp_path / "records.jsonl"
    records.write_text("{}\n", encoding="utf-8")
    malformed = tmp_path / "malformed.json"
    malformed.write_text("not json", encoding="utf-8")
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"documents": []}), encoding="utf-8")
    for path in (malformed, empty):
        result = audit_files(path, records)
        assert result["status"] in {"error", "invalid"}
        assert result["errors"] or any(row["errors"] for row in result["records"])

def test_batch_duplicate_id_is_configuration_error(tmp_path):
    p = tmp_path / "m.json"; p.write_text(json.dumps({"schema_version":"provenance_audit_batch_v1","inputs":[{"input_id":"x"},{"input_id":"x"}]}))
    with pytest.raises(ValueError): audit_files(p)

def test_batch_wrong_schema_is_not_accepted(tmp_path):
    p = tmp_path / "m.json"; p.write_text(json.dumps({"schema_version":"wrong","inputs":[]}))
    assert audit_files(p)["status"] == "error"

def test_batch_empty_inputs_is_configuration_error(tmp_path):
    p = tmp_path / "m.json"; p.write_text(json.dumps({"schema_version":"provenance_audit_batch_v1","inputs":[]}))
    with pytest.raises(ValueError): audit_files(p)

def test_list_document_id_does_not_raise(tmp_path):
    m, r = setup(tmp_path, [record(document_id=[])])
    assert audit_files(m, r)["status"] == "invalid"

def test_non_utf8_records_is_structured(tmp_path):
    m, r = setup(tmp_path, [record()]); r.write_bytes(b"\xff")
    result = audit_files(m, r)
    assert result["errors"][0]["code"] == "input_read_error"

def test_relative_source_is_contained(tmp_path):
    m, r = setup(tmp_path, [record(source_path="../outside")])
    assert any(e["code"] == "path_escape" for e in audit_files(m, r)["records"][0]["errors"])

def test_batch_results_are_lexical(tmp_path):
    for name in ("a", "b"):
        (tmp_path / f"{name}.txt").write_text(name); (tmp_path / f"{name}.jsonl").write_text("{}\n")
    m = tmp_path / "m.json"; m.write_text(json.dumps({"schema_version":"provenance_audit_batch_v1","inputs":[{"input_id":"b","source":"b.txt","records":"b.jsonl"},{"input_id":"a","source":"a.txt","records":"a.jsonl"}]}))
    assert [x["input_id"] for x in audit_files(m)["results"]] == ["a", "b"]

def test_batch_output_is_deterministic(tmp_path):
    m, r = setup(tmp_path, [record()]); data=json.loads(m.read_text()); data={"schema_version":"provenance_audit_batch_v1","inputs":[{"input_id":"a","source":"doc.txt","records":"records.jsonl"}]}; r.rename(tmp_path/"records.jsonl"); m.write_text(json.dumps(data))
    assert audit_files(m) == audit_files(m)

def test_batch_missing_required_fields_is_configuration_error(tmp_path):
    m = tmp_path / "m.json"
    m.write_text(json.dumps({"schema_version": "provenance_audit_batch_v1", "inputs": [{"input_id": "x", "source": ""}]}))
    with pytest.raises(ValueError): audit_files(m)

def test_batch_failed_inputs_preserve_aggregate_invariants(tmp_path):
    source = tmp_path / "source.txt"; source.write_text("text")
    records = tmp_path / "records.jsonl"; records.write_text("{}\n")
    m = tmp_path / "m.json"
    m.write_text(json.dumps({"schema_version": "provenance_audit_batch_v1", "inputs": [
        {"input_id": "bad", "source": "missing.txt", "records": "records.jsonl"},
        {"input_id": "good", "source": "source.txt", "records": "records.jsonl"},
    ]}))
    result = audit_files(m)
    assert result["record_count"] == result["valid_record_count"] + result["invalid_record_count"]
    assert result["invalid_input_count"] == 2
    assert all(item["provenance_status"] != "accepted" for item in result["results"])

def test_batch_symlink_escape_is_invalid_input(tmp_path):
    outside = tmp_path.parent / "outside-source.txt"; outside.write_text("outside")
    link = tmp_path / "source.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    records = tmp_path / "records.jsonl"; records.write_text("{}\n")
    m = tmp_path / "m.json"; m.write_text(json.dumps({"schema_version": "provenance_audit_batch_v1", "inputs": [{"input_id": "x", "source": "source.txt", "records": "records.jsonl"}]}))
    result = audit_files(m)
    assert result["results"][0]["findings"][0]["code"] == "path_escape"
