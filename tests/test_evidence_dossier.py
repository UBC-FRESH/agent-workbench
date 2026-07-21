"""Tests for dossier manifest loading and artifact integrity verification."""

from __future__ import annotations

import hashlib
import os
import json
from pathlib import Path

import pytest

from agent_workbench.evidence_dossier import (
    SCHEMA_VERSION,
    DossierManifestError,
    load_manifest,
)


# ── helpers that place fixtures inside tmp_path ──────────────────────────


def _make_file(tmp_path: Path, rel: str, content: str) -> dict:
    """Write *content* at ``tmp_path/rel`` and return a valid artifact dict."""
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    sha = hashlib.sha256(target.read_bytes()).hexdigest()
    return {"path": rel, "sha256": sha}


def _write_manifest(tmp_path: Path, artifacts: list[dict]) -> Path:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": "test-run-001",
        "artifacts": artifacts,
    }
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(manifest), encoding="utf-8")
    return p


# ── valid manifest tests ────────────────────────────────────────────────


def test_load_valid_manifest_single_artifact(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "hello")
    p = _write_manifest(tmp_path, [art])
    result = load_manifest(p)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["run_id"] == "test-run-001"
    assert len(result["artifacts"]) == 1
    assert result["artifacts"][0]["path"] == "a.txt"


def test_load_valid_manifest_multiple_artifacts(tmp_path: Path):
    arts = [
        _make_file(tmp_path, "z.txt", "zzz"),
        _make_file(tmp_path, "a.txt", "aaa"),
        _make_file(tmp_path, "m.txt", "mmm"),
    ]
    p = _write_manifest(tmp_path, arts)
    result = load_manifest(p)
    assert len(result["artifacts"]) == 3
    paths = [a["path"] for a in result["artifacts"]]
    assert paths == ["a.txt", "m.txt", "z.txt"]


def test_canonical_form_has_only_three_keys(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    p = _write_manifest(tmp_path, [art])
    result = load_manifest(p)
    assert set(result.keys()) == {"schema_version", "run_id", "artifacts"}


def test_canonical_artifact_has_only_two_keys(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    p = _write_manifest(tmp_path, [art])
    result = load_manifest(p)
    for a in result["artifacts"]:
        assert set(a.keys()) == {"path", "sha256"}


def test_typed_artifact_preserves_canonical_integrity_projection(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    p = tmp_path / "manifest.json"
    p.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": "test-run-001",
                "artifacts": [{"kind": "heartbeat", **art}],
            }
        ),
        encoding="utf-8",
    )
    result = load_manifest(p)
    assert result["artifacts"] == [art]


# ── manifest_invalid errors ─────────────────────────────────────────────


def test_rejects_wrong_schema_version(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    doc = {
        "schema_version": "wrong_v2",
        "run_id": "x",
        "artifacts": [art],
    }
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


def test_rejects_missing_run_id(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    doc = {"schema_version": SCHEMA_VERSION, "artifacts": [art]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


def test_rejects_empty_run_id(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "", "artifacts": [art]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


def test_rejects_non_string_run_id(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    doc = {"schema_version": SCHEMA_VERSION, "run_id": 123, "artifacts": [art]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


def test_rejects_empty_artifacts_list(tmp_path: Path):
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": []}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


def test_rejects_malformed_json(tmp_path: Path):
    p = tmp_path / "m.json"
    p.write_text("{ broken json }", encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


def test_rejects_top_level_array(tmp_path: Path):
    p = tmp_path / "m.json"
    p.write_text("[]", encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


def test_rejects_extra_artifact_keys(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    extra_art = {
        "path": "a.txt",
        "sha256": art["sha256"],
        "extra": True,
    }
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [extra_art]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="manifest_invalid"):
        load_manifest(p)


# ── artifact_path_invalid errors ────────────────────────────────────────


def test_rejects_absolute_path(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    abs_path = str(tmp_path / "a.txt")
    bad_art = {"path": abs_path, "sha256": art["sha256"]}
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [bad_art]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_path_invalid"):
        load_manifest(p)


def test_rejects_path_traversal(tmp_path: Path):
    _make_file(tmp_path, "a.txt", "data")
    doc = {
        "schema_version": SCHEMA_VERSION,
        "run_id": "x",
        "artifacts": [{"path": "../other/a.txt", "sha256": "0" * 64}],
    }
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_path_invalid"):
        load_manifest(p)


def test_rejects_empty_path_segment(tmp_path: Path):
    _make_file(tmp_path, "a.txt", "data")
    doc = {
        "schema_version": SCHEMA_VERSION,
        "run_id": "x",
        "artifacts": [{"path": "a//b.txt", "sha256": "0" * 64}],
    }
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_path_invalid"):
        load_manifest(p)


def test_rejects_symlink(tmp_path: Path):
    target = tmp_path / "target.txt"
    target.write_text("real data", encoding="utf-8")
    link = tmp_path / "link.txt"
    if link.exists() or link.is_symlink():
        link.unlink()
    try:
        os.symlink(target, link)
    except OSError:
        pytest.skip("symlinks not supported on this platform")
    art = {"path": "link.txt", "sha256": "0" * 64}
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [art]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_path_invalid"):
        load_manifest(p)


def test_rejects_duplicate_paths(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [art, art]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_path_invalid"):
        load_manifest(p)


def test_rejects_non_file_entry(tmp_path: Path):
    d = tmp_path / "adir"
    d.mkdir(exist_ok=True)
    doc = {
        "schema_version": SCHEMA_VERSION,
        "run_id": "x",
        "artifacts": [{"path": "adir", "sha256": "0" * 64}],
    }
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_path_invalid"):
        load_manifest(p)


# ── artifact_digest_mismatch errors ─────────────────────────────────────


def test_rejects_bad_sha256_length(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    bad = {"path": "a.txt", "sha256": "short"}
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [bad]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_digest_invalid"):
        load_manifest(p)


def test_rejects_non_hex_sha256(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    bad = {"path": "a.txt", "sha256": "g" * 64}
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [bad]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_digest_invalid"):
        load_manifest(p)


def test_rejects_uppercase_sha256(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    bad = {"path": "a.txt", "sha256": art["sha256"].upper()}
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [bad]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_digest_invalid"):
        load_manifest(p)


def test_rejects_digest_mismatch(tmp_path: Path):
    art = _make_file(tmp_path, "a.txt", "data")
    bad = {"path": "a.txt", "sha256": "0" * 64}
    doc = {"schema_version": SCHEMA_VERSION, "run_id": "x", "artifacts": [bad]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(DossierManifestError, match="artifact_digest_mismatch"):
        load_manifest(p)


def test_rejects_missing_manifest_file():
    p = Path("/this/does/not/exist/manifest.json")
    with pytest.raises(DossierManifestError):
        load_manifest(p)
