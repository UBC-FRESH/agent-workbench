"""Materialize one immutable P114.5/P107 qualification worktree.

This command performs no model invocation and no Codex configuration change.
It creates a literal detached worktree from the frozen P107 baseline, copies
the independently frozen workload inputs into the paths named by that ticket,
and writes a manifest that later bridge staging must verify.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


BASELINE = "139e725ee069c27cf68c797dd66aa88b5bb2824d"
WORKLOAD_ID = "p107-provenance-audit-bundle-v1"
INPUTS = {
    "p107_suite_provenance_audit_bundle_ticket.md": "c4e264621ef541cad555319a7226383b0eb62366b3d4c3d6313e1c9415f78670",
    "p107_suite_provenance_audit_bundle_acceptance.py": "6999f38748d7babe62fc9cf1eaf0a97796fa0ea3ad6cbd773be5534a540ac099",
    "p107_suite_provenance_audit_bundle_workload_manifest.json": "8480c869bfd118e3cc7f4eebed2048d93b91abeffc31007c448e57d929d8bb4a",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(repo_root: Path, run_dir: Path, frozen_input_dir: Path, worktree: Path | None = None) -> Path:
    """Create one detached worktree and immutable copied input bundle."""

    repo_root = repo_root.resolve()
    run_dir = run_dir.resolve()
    frozen_input_dir = frozen_input_dir.resolve()
    if run_dir.exists():
        raise ValueError(f"run directory already exists: {run_dir}")
    if not frozen_input_dir.is_dir():
        raise ValueError(f"frozen input directory is missing: {frozen_input_dir}")
    for name, expected in INPUTS.items():
        source = frozen_input_dir / name
        if not source.is_file() or sha256(source) != expected:
            raise ValueError(f"frozen input hash mismatch: {name}")

    run_dir.mkdir(parents=True)
    worktree = (worktree or run_dir / "worktree").resolve()
    if worktree.exists():
        raise ValueError(f"worktree path already exists: {worktree}")
    subprocess.run(["git", "-C", str(repo_root), "worktree", "add", "--detach", str(worktree), BASELINE], check=True)
    try:
        destination = worktree / "runtime" / "agent_jobs"
        destination.mkdir(parents=True, exist_ok=True)
        copied: dict[str, str] = {}
        for name, expected in INPUTS.items():
            target = destination / name
            shutil.copyfile(frozen_input_dir / name, target)
            if sha256(target) != expected:
                raise ValueError(f"copied input hash mismatch: {name}")
            copied[str(target.relative_to(worktree).as_posix())] = expected
        manifest = {
            "schema_version": 1,
            "run_kind": "p114_c4_qualification_preparation",
            "workload_id": WORKLOAD_ID,
            "baseline_commit": BASELINE,
            "literal_worktree": str(worktree),
            "frozen_input_dir": str(frozen_input_dir),
            "materialized_inputs": copied,
            "worker_allowed_patch_paths": [
                "src/agent_workbench/source_audit.py",
                "src/agent_workbench/cli.py",
                "tests/test_source_audit.py",
                "README.md",
            ],
            "frozen_validation_commands": [
                "python -m pytest -q tests/test_source_audit.py",
                "python runtime/agent_jobs/p107_suite_provenance_audit_bundle_acceptance.py",
            ],
        }
        output = run_dir / "qualification_manifest.json"
        output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return output
    except Exception:
        subprocess.run(["git", "-C", str(repo_root), "worktree", "remove", "--force", str(worktree)], check=False)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--frozen-input-dir", type=Path, required=True)
    parser.add_argument("--worktree", type=Path, help="Optional short absolute detached-worktree path for Windows MAX_PATH safety.")
    args = parser.parse_args()
    print(prepare(args.repo_root, args.run_dir, args.frozen_input_dir, args.worktree))


if __name__ == "__main__":
    main()
