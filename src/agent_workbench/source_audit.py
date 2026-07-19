"""Deterministic, offline provenance audit for source-anchored JSONL records."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

REQUIRED = ("document_id", "chunk_id", "object_type")

def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()

def _error(code: str, **details: Any) -> dict[str, Any]:
    return {"code": code, **details}

def _rooted(root: Path, value: Any, *, kind: str = "source") -> tuple[Path | None, dict[str, Any] | None]:
    if not isinstance(value, str) or not value.strip():
        return None, _error("invalid_source_path", reason="path must be a non-empty string", field=kind)
    p = Path(value)
    if p.is_absolute():
        return None, _error("path_escape", reason="absolute path is forbidden", path=value)
    root = root.resolve()
    resolved = (root / p).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, _error("path_escape", reason="path escapes manifest root", path=value)
    if not resolved.exists() or not resolved.is_file():
        return None, _error("source_missing", path=value)
    return resolved, None

def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(str(exc)) from exc

def _record_rows(root: Path, records: Path, documents: dict[str, tuple[Path, str]], relaxed: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    try:
        raw = records.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [], [_error("input_read_error", path=str(records), message=str(exc))]
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line.strip(): continue
        try: item = json.loads(line)
        except json.JSONDecodeError as exc:
            rows.append({"line": line_no, "status": "invalid", "errors": [_error("malformed_json", message=str(exc))]}); continue
        row_errors: list[dict[str, Any]] = []
        if not isinstance(item, dict):
            rows.append({"line": line_no, "status": "invalid", "errors": [_error("schema_error", field="record")]}); continue
        for field in (("document_id", "chunk_id") if relaxed else REQUIRED):
            if not isinstance(item.get(field), str) or not item[field].strip(): row_errors.append(_error("invalid_field", field=field))
        doc_id = item.get("document_id")
        ref = documents.get(doc_id) if isinstance(doc_id, str) else None
        if ref is None and isinstance(doc_id, str) and doc_id: row_errors.append(_error("unknown_document_id", document_id=doc_id))
        if not relaxed and (not isinstance(item.get("source_path"), str) or not item.get("source_path", "").strip()): row_errors.append(_error("invalid_field", field="source_path"))
        if ref and isinstance(item.get("source_path"), str):
            resolved, pe = _rooted(root, item["source_path"])
            if pe or resolved != ref[0]:
                row_errors.append(pe or _error("provenance_conflict", field="source_path"))
                if pe: row_errors.append(_error("provenance_conflict", field="source_path"))
        if ref:
            for field in ("source_sha256", "source_hash"):
                if field in item and not isinstance(item[field], str): row_errors.append(_error("invalid_field", field=field))
            supplied = item.get("source_sha256", item.get("source_hash"))
            if supplied is not None and (not isinstance(supplied, str) or supplied != ref[1]): row_errors.append(_error("provenance_conflict", field="source_sha256"))
            quote = item.get("source_quote")
            if not isinstance(quote, str) or not quote.strip(): row_errors.append(_error("invalid_field", field="source_quote"))
            else:
                try: source_text = ref[0].read_text(encoding="utf-8")
                except (OSError, UnicodeError) as exc: row_errors.append(_error("input_read_error", message=str(exc)))
                else:
                    if _normalise(quote) not in _normalise(source_text): row_errors.append(_error("source_quote_mismatch", field="source_quote"))
        rows.append({"line": line_no, "status": "accepted" if not row_errors else "invalid", "record": item, "errors": row_errors})
    if not rows: errors.append(_error("empty_jsonl"))
    return rows, errors

def _one(root: Path, source_value: Any, records_value: Any, input_id: str | None = None) -> dict[str, Any]:
    source, pe = _rooted(root, source_value)
    records, re_ = _rooted(root, records_value, kind="records")
    findings = [e for e in (pe, re_) if e]
    digest = None
    documents: dict[str, tuple[Path, str]] = {}
    if source:
        try: digest = hashlib.sha256(source.read_bytes()).hexdigest()
        except (OSError, UnicodeError) as exc: findings.append(_error("input_read_error", message=str(exc)))
        if digest: documents["document-1"] = (source, digest)
    rows: list[dict[str, Any]] = []
    if records and not findings: rows, row_errors = _record_rows(root, records, documents, relaxed=True); findings.extend(row_errors)
    synthetic_invalid = 1 if findings and not rows else 0
    valid_count = sum(r["status"] == "accepted" for r in rows)
    invalid_count = sum(r["status"] != "accepted" for r in rows) + synthetic_invalid
    result: dict[str, Any] = {"input_id": input_id, "source_sha256": digest, "record_count": valid_count + invalid_count, "valid_record_count": valid_count, "invalid_record_count": invalid_count, "provenance_status": "accepted" if not findings and invalid_count == 0 else "invalid", "findings": findings, "records": rows}
    return result

def audit(manifest_path: Path, records_path: Path | None = None) -> dict[str, Any]:
    manifest_path = Path(manifest_path); root = manifest_path.parent
    try: data = _json(manifest_path)
    except ValueError as exc: return {"schema_version": "p107_source_audit_v1", "status": "error", "errors": [_error("invalid_manifest", message=str(exc))], "records": []}
    if isinstance(data, dict) and data.get("schema_version") == "provenance_audit_batch_v1":
        inputs = data.get("inputs")
        if not isinstance(inputs, list) or not inputs or any(not isinstance(x, dict) for x in inputs): raise ValueError("invalid batch manifest inputs")
        ids = [x.get("input_id") for x in inputs]
        if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids): raise ValueError("invalid or duplicate input_id")
        for item in inputs:
            for field in ("source", "records"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    raise ValueError(f"invalid batch manifest {field}")
        results = [_one(root, x.get("source"), x.get("records"), x["input_id"]) for x in inputs]
        results.sort(key=lambda x: x["input_id"])
        return {"schema_version": data["schema_version"], "input_count": len(results), "record_count": sum(x["record_count"] for x in results), "valid_input_count": sum(x["provenance_status"] == "accepted" for x in results), "invalid_input_count": sum(x["provenance_status"] != "accepted" for x in results), "valid_record_count": sum(x["valid_record_count"] for x in results), "invalid_record_count": sum(x["invalid_record_count"] for x in results), "results": results}
    entries = data.get("documents") if isinstance(data, dict) else None
    if not isinstance(entries, list): return {"schema_version": "p107_source_audit_v1", "status": "error", "errors": [_error("invalid_manifest", message="expected a documents list")], "records": []}
    documents: dict[str, tuple[Path, str]] = {}; errors: list[dict[str, Any]] = []
    for i, item in enumerate(entries):
        if not isinstance(item, dict): errors.append(_error("invalid_document", index=i)); continue
        doc = item.get("document_id")
        if not isinstance(doc, str) or not doc: errors.append(_error("invalid_document_id", index=i)); continue
        path, pe = _rooted(root, item.get("path", item.get("source_path")))
        if pe: errors.append({**pe, "index": i, "document_id": doc}); continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not isinstance(item.get("source_sha256", item.get("source_hash")), str) or item.get("source_sha256", item.get("source_hash")).lower() != digest: errors.append(_error("source_hash_mismatch", index=i, document_id=doc, expected=digest, supplied=item.get("source_sha256", item.get("source_hash"))))
        if doc in documents: errors.append(_error("duplicate_document_id", document_id=doc))
        documents[doc] = (path, digest)
    if records_path is None: records_path = Path(data.get("records", data.get("records_path", "")))
    if not records_path.is_absolute(): records_path = root / records_path
    records, row_errors = _record_rows(root, records_path.resolve(strict=False), documents)
    errors.extend(row_errors)
    return {"schema_version": "p107_source_audit_v1", "status": "accepted" if not errors and records and all(r["status"] == "accepted" for r in records) else "invalid", "errors": errors, "records": records}

def audit_files(manifest: Path, records: Path | None = None, output: Path | None = None) -> dict[str, Any]:
    result = audit(manifest, records)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return result
