"""Validate that a P107 evaluation block seals every cost-relevant input."""

from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
from pathlib import Path

SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_INPUTS = ("c0_prompt", "c1_prompt", "c2_prompt", "c3_prompt", "c4_prompt", "advisor_rubric")
SEALED_ARTIFACTS = {
    "ticket_path": "ticket_sha256",
    "fixture_path": "fixture_sha256",
    "pricing_catalog_path": "pricing_catalog_sha256",
    "model_catalog_path": "model_catalog_sha256",
    "effective_config_path": "effective_config_sha256",
}


def _safe_path(root: Path, value: object, label: str, *, file: bool) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value.strip() or "REPLACE_WITH" in value:
        return None, f"{label} must be materialized"
    candidate = Path(value)
    if candidate.is_absolute() or any(part == ".." for part in candidate.parts):
        return None, f"{label} must stay relative to the block"
    current = root
    try:
        for part in candidate.parts:
            current = current / part
            if current.is_symlink():
                return None, f"{label} must not use symlinks"
        if not current.is_file() if file else not current.is_dir():
            return None, f"{label} must name a regular file" if file else f"{label} must name a directory"
        return current, None
    except OSError:
        return None, f"{label} is missing or inaccessible"


def validate(path: str | Path) -> list[str]:
    try:
        block = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read evaluation block: {exc}"]
    if not isinstance(block, dict):
        return ["evaluation block root must be an object"]
    errors: list[str] = []
    if block.get("schema_version") != "p107_evaluation_block_v1":
        errors.append("schema_version must be p107_evaluation_block_v1")
    if not isinstance(block.get("starting_commit"), str) or not COMMIT.fullmatch(block["starting_commit"]):
        errors.append("starting_commit must be a 40-character lowercase commit")
    for field in ("ticket_sha256", "fixture_sha256", "rubric_sha256", "pricing_catalog_sha256", "model_catalog_sha256", "effective_config_sha256"):
        if not isinstance(block.get(field), str) or not SHA256.fullmatch(block[field]):
            errors.append(f"{field} must be a lowercase SHA-256")
    for field in ("block_id", "workload_id", "runtime_version", "environment_epoch", "repository_root", "ticket_path", "fixture_path", "pricing_catalog_path", "model_catalog_path", "effective_config_path"):
        value = block.get(field)
        if not isinstance(value, str) or not value.strip() or "REPLACE_WITH" in value:
            errors.append(f"{field} must be materialized")
    if block.get("ambient_memories_enabled") is not False:
        errors.append("ambient_memories_enabled must be false")
    inputs = block.get("required_inputs")
    if not isinstance(inputs, list):
        return errors + ["required_inputs must list every C0-C4 prompt and Advisor rubric"]
    by_name = {}
    paths = set()
    block_path = Path(path).resolve()
    root, root_error = _safe_path(block_path.parent, block.get("repository_root"), "repository_root", file=False)
    if root_error:
        errors.append(root_error)
    elif not COMMIT.fullmatch(block["starting_commit"]):
        pass
    else:
        try:
            result = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{block['starting_commit']}^{{commit}}"], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                errors.append("starting_commit must be a resolvable local Git commit")
        except OSError:
            errors.append("starting_commit must be a resolvable local Git commit")
    for path_field, hash_field in SEALED_ARTIFACTS.items():
        target, path_error = _safe_path(block_path.parent, block.get(path_field), path_field, file=True)
        if path_error:
            errors.append(path_error)
        elif not SHA256.fullmatch(str(block.get(hash_field, ""))):
            pass
        else:
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual != block[hash_field]:
                errors.append(f"{hash_field} does not match file")
    for item in inputs:
        if not isinstance(item, dict):
            errors.append("required input must be an object")
            continue
        name, rel, digest = item.get("name"), item.get("path"), item.get("sha256")
        if isinstance(name, str):
            if name in by_name:
                errors.append(f"duplicate required input: {name}")
            by_name[name] = item
        if not isinstance(rel, str) or not rel.strip() or "REPLACE_WITH" in rel:
            errors.append(f"{name or 'required input'} path must be materialized")
            continue
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            errors.append(f"{name or 'required input'} sha256 must be a lowercase SHA-256")
        candidate = Path(rel)
        if candidate.is_absolute() or any(part == ".." for part in candidate.parts):
            errors.append(f"{name or 'required input'} path must stay relative to the block")
            continue
        target = block_path.parent / candidate
        try:
            current = block_path.parent
            components = []
            for part in candidate.parts:
                current = current / part
                components.append(current)
            if any(part.is_symlink() for part in components):
                errors.append(f"{name or 'required input'} path must not use symlinks")
                continue
            resolved = target.resolve(strict=True)
            if resolved != target.resolve() or not resolved.is_file():
                errors.append(f"{name or 'required input'} path must name a regular file")
                continue
            if rel in paths:
                errors.append(f"duplicate required input path: {rel}")
            paths.add(rel)
            actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
            if isinstance(digest, str) and SHA256.fullmatch(digest) and actual != digest:
                errors.append(f"{name or 'required input'} sha256 does not match file")
        except (OSError, RuntimeError):
            errors.append(f"{name or 'required input'} file is missing or inaccessible")
    for name in REQUIRED_INPUTS:
        if name not in by_name:
            errors.append(f"missing required input: {name}")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_p107_evaluation_block.py <evaluation-block.json>")
    errors = validate(sys.argv[1])
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("P107 evaluation block is valid")
