"""Dossier manifest loading and artifact integrity verification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCHEMA_VERSION = "p107_run_evidence_dossier_v1"


class DossierManifestError(ValueError):
    """Stable manifest-validation failure."""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_path_format(art_path_str: str, art_path: Path) -> None:
    """Raise DossierManifestError on structural path violations."""

    if art_path.is_absolute():
        raise DossierManifestError("artifact_path_invalid: absolute paths are forbidden") from None

    # Reject ".." anywhere in the component list (not collapsed by Path).
    for part in art_path_str.split("/"):
        if part == "..":
            raise DossierManifestError(
                "artifact_path_invalid: path traversal (..) is forbidden"
            ) from None
        if part == "":
            raise DossierManifestError(
                "artifact_path_invalid: empty path segment detected"
            ) from None

    # Reject any individual component that looks absolute (e.g. "C:" on Windows).
    for part in art_path.parts:
        if Path(part).is_absolute():
            raise DossierManifestError(
                "artifact_path_invalid: path contains an absolute component"
            ) from None


def load_manifest(path: Path) -> dict[str, object]:
    """Load a valid manifest and verify every declared artifact digest."""

    # --- file read ---
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise DossierManifestError(f"manifest file not found: {path}") from None
    except OSError as exc:
        raise DossierManifestError(f"cannot read manifest: {exc}") from None

    # --- top-level shape ---
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        raise DossierManifestError("manifest_invalid: malformed JSON") from None

    if not isinstance(data, dict):
        raise DossierManifestError(
            "manifest_invalid: top-level value is not an object"
        ) from None

    # --- schema version ---
    if data.get("schema_version") != SCHEMA_VERSION:
        raise DossierManifestError(
            "manifest_invalid: schema version mismatch"
        ) from None

    # --- run_id ---
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise DossierManifestError(
            "manifest_invalid: run_id must be a non-empty string"
        )

    # --- artifacts list ---
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) == 0:
        raise DossierManifestError(
            "manifest_invalid: artifacts must be a non-empty list"
        )

    # --- validate each artifact ---
    seen_paths: set[str] = set()
    validated: list[dict[str, str]] = []

    for i, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise DossierManifestError(
                f"manifest_invalid: artifacts[{i}] is not an object"
            ) from None

        allowed_keys = {"path", "sha256"}
        allowed_keys_with_kind = {"kind", "path", "sha256"}
        if set(artifact.keys()) not in (allowed_keys, allowed_keys_with_kind):
            raise DossierManifestError(
                f"manifest_invalid: artifact has unexpected keys at index {i}"
            ) from None

        if "kind" in artifact and (
            not isinstance(artifact["kind"], str) or not artifact["kind"].strip()
        ):
            raise DossierManifestError(
                f"manifest_invalid: artifact kind must be a non-empty string at index {i}"
            ) from None

        art_path_str = artifact.get("path")
        digest = artifact.get("sha256")

        # --- path format ---
        if not isinstance(art_path_str, str) or art_path_str == "":
            raise DossierManifestError(
                "manifest_invalid: artifact path must be a non-empty string"
            ) from None

        _validate_path_format(art_path_str, Path(art_path_str))

        # --- digest format ---
        if not isinstance(digest, str):
            raise DossierManifestError(
                f"artifact_digest_invalid at index {i}: sha256 must be a string"
            ) from None

        if len(digest) != 64:
            raise DossierManifestError(
                f"artifact_digest_invalid at index {i}: sha256 length must be 64"
            ) from None

        if any(character not in "0123456789abcdef" for character in digest):
            raise DossierManifestError(
                f"artifact_digest_invalid at index {i}: sha256 must be lowercase hex"
            ) from None

        # --- resolve and check file existence / type ---
        resolved = (path.parent / art_path_str).resolve()

        if not resolved.exists():
            raise DossierManifestError(
                f"artifact_missing: file does not exist: {art_path_str}"
            ) from None

        if resolved.is_symlink():
            raise DossierManifestError(
                f"artifact_path_invalid: symlinks are forbidden: {art_path_str}"
            ) from None

        if not resolved.is_file():
            raise DossierManifestError(
                f"artifact_path_invalid: is not a regular file: {art_path_str}"
            ) from None

        # --- duplicate check ---
        if art_path_str in seen_paths:
            raise DossierManifestError(
                f"artifact_path_invalid: duplicate artifact path: {art_path_str}"
            ) from None
        seen_paths.add(art_path_str)

        # --- digest verification ---
        actual = _sha256_file(resolved)
        if actual != digest.lower():
            raise DossierManifestError(
                f"artifact_digest_mismatch at index {i}: expected {digest}, got {actual}"
            ) from None

        validated.append({
            "path": art_path_str,
            "sha256": digest.lower(),
        })

    # --- canonical form: deterministic lex ordering, filtered keys ---
    validated.sort(key=lambda a: a["path"])
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "artifacts": validated,
    }
