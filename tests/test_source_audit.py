from __future__ import annotations

import hashlib
import json
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
    value = {"document_id": "d1", "chunk_id": "c1", "object_type": "paragraph", "source_path": "doc.txt"}
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
