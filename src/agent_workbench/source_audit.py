"""Deterministic, offline provenance audit for source-anchored JSONL records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED = ("document_id", "chunk_id", "object_type")


def _error(code: str, **details: Any) -> dict[str, Any]:
    return {"code": code, **details}


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid manifest: {exc}") from exc


def _manifest_entries(data: Any) -> list[dict[str, Any]]:
    entries = data.get("documents") if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise ValueError("invalid manifest: expected a documents list")
    if any(not isinstance(item, dict) for item in entries):
        raise ValueError("invalid manifest: each document must be an object")
    return entries


def _resolve(root: Path, value: Any) -> tuple[Path | None, dict[str, Any] | None]:
    if not isinstance(value, str) or not value.strip():
        return None, _error("invalid_source_path", reason="path must be a non-empty string")
    candidate = Path(value)
    if candidate.is_absolute():
        return None, _error("path_escape", reason="absolute path is forbidden", path=value)
    root = root.resolve()
    path = (root / candidate).resolve(strict=False)
    try:
        path.relative_to(root)
    except ValueError:
        return None, _error("path_escape", reason="path escapes manifest root", path=value)
    if not path.exists() or not path.is_file():
        return None, _error("source_missing", path=value)
    return path, None


def audit(manifest_path: Path, records_path: Path) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    root = manifest_path.parent
    try:
        entries = _manifest_entries(_load(manifest_path))
    except ValueError as exc:
        return {"schema_version": "p107_source_audit_v1", "status": "error", "errors": [_error("invalid_manifest", message=str(exc))], "records": []}

    documents: dict[str, tuple[Path, str]] = {}
    errors: list[dict[str, Any]] = []
    for index, item in enumerate(entries):
        doc_id = item.get("document_id")
        if not isinstance(doc_id, str) or not doc_id:
            errors.append(_error("invalid_document_id", index=index))
            continue
        path, path_error = _resolve(root, item.get("path", item.get("source_path")))
        if path_error:
            errors.append({**path_error, "index": index, "document_id": doc_id})
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        supplied = item.get("source_sha256", item.get("source_hash"))
        if not isinstance(supplied, str) or supplied.lower() != digest:
            errors.append(_error("source_hash_mismatch", index=index, document_id=doc_id, expected=digest, supplied=supplied))
        if doc_id in documents:
            errors.append(_error("duplicate_document_id", document_id=doc_id))
        documents[doc_id] = (path, digest)

    rows: list[dict[str, Any]] = []
    try:
        raw = records_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return {"schema_version": "p107_source_audit_v1", "status": "error", "errors": errors + [_error("invalid_jsonl", message=str(exc))], "records": []}
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            rows.append({"line": line_no, "status": "invalid", "errors": [_error("malformed_json", message=str(exc))]})
            continue
        if not isinstance(item, dict):
            rows.append({"line": line_no, "status": "invalid", "errors": [_error("schema_error", field="record") ]})
            continue
        row_errors: list[dict[str, Any]] = []
        for field in REQUIRED:
            if not isinstance(item.get(field), str) or not item[field].strip():
                row_errors.append(_error("invalid_field", field=field))
        doc_id = item.get("document_id")
        ref = documents.get(doc_id)
        if ref is None and doc_id:
            row_errors.append(_error("unknown_document_id", document_id=doc_id))
        if ref and isinstance(item.get("source_path"), str):
            resolved, path_error = _resolve(root, item["source_path"])
            if path_error or resolved != ref[0]:
                row_errors.append(path_error or _error("provenance_conflict", field="source_path"))
                if path_error:
                    row_errors.append(_error("provenance_conflict", field="source_path"))
        if ref and item.get("source_sha256", item.get("source_hash")) not in (None, ref[1]):
            row_errors.append(_error("provenance_conflict", field="source_sha256"))
        rows.append({"line": line_no, "status": "accepted" if not row_errors else "invalid", "record": item, "errors": row_errors})
    if not rows:
        errors.append(_error("empty_jsonl"))
    status = "accepted" if not errors and rows and all(r["status"] == "accepted" for r in rows) else "invalid"
    return {"schema_version": "p107_source_audit_v1", "status": status, "errors": errors, "records": rows}


def audit_files(manifest: Path, records: Path, output: Path | None = None) -> dict[str, Any]:
    result = audit(manifest, records)
    text = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    return result
