from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_p107_2_ab_run_packet import validate_run_packet


TEMPLATE = ROOT / "templates" / "p107_2_ab_run_packet_template.json"


def materialized_packet(tmp_path: Path) -> dict[str, object]:
    document = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    document["run_id"] = "p107-2-pilot"
    repos = []
    retail_repo = tmp_path / "retail-worktree"
    retail_repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(retail_repo)], check=True)
    (retail_repo / "README.md").write_text("baseline", encoding="utf-8")
    subprocess.run(["git", "-C", str(retail_repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(retail_repo), "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline"], check=True)
    repos = [retail_repo]
    for lane in ("workbench",):
        repo = tmp_path / f"{lane}-worktree"
        subprocess.run(["git", "clone", "-q", str(retail_repo), str(repo)], check=True)
        repos.append(repo)
    document["baseline_commit"] = subprocess.run(["git", "-C", str(repos[0]), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    for lane, repo in zip(("retail", "workbench"), repos):
        document["lanes"][lane]["worktree"] = str(repo.resolve())
    for name in ("ticket", "acceptance_fixture", "usability_rubric"):
        artifact = tmp_path / f"{name}.json"
        artifact.write_text(name, encoding="utf-8")
        document[name]["path"] = str(artifact.resolve())
        document[name]["sha256"] = hashlib.sha256(name.encode()).hexdigest()
    document["acceptance_fixture"]["command"] = "python -m pytest acceptance -q"
    document["implementation_scope"]["allowed_paths"] = ["src/example.py"]
    for lane in ("retail", "workbench"):
        manifest = tmp_path / f"{lane}-manifest.json"
        manifest.write_text("{}", encoding="utf-8")
        document["lanes"][lane]["manifest"] = {"path": str(manifest.resolve()), "sha256": hashlib.sha256(b"{}").hexdigest()}
    accounting = tmp_path / "accounting.json"
    accounting.write_text("{}", encoding="utf-8")
    document["accounting"]["record_path"] = str(accounting.resolve())
    document["accounting"]["sha256"] = hashlib.sha256(b"{}").hexdigest()
    return document


def write_packet(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_template_is_deliberately_not_materialized() -> None:
    assert validate_run_packet(TEMPLATE)


def test_materialized_packet_is_valid(tmp_path: Path) -> None:
    assert validate_run_packet(write_packet(tmp_path, materialized_packet(tmp_path))) == []


def test_closeout_rejects_dirty_worktree(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    (Path(document["lanes"]["retail"]["worktree"]) / "dirty.txt").write_text("dirty", encoding="utf-8")
    errors = validate_run_packet(write_packet(tmp_path, document), closeout=True)
    assert any("must be clean at closeout" in error for error in errors)


def test_closeout_rejects_missing_accounting(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    document["accounting"]["record_path"] = str((tmp_path / "missing-accounting.json").resolve())
    errors = validate_run_packet(write_packet(tmp_path, document), closeout=True)
    assert any("accounting.path must be an existing file" in error for error in errors)


def test_closeout_rejects_unsafe_allowed_paths(tmp_path: Path) -> None:
    for index, value in enumerate(("../../outside", "C:/Windows/System32", 7)):
        document = materialized_packet(tmp_path / str(index))
        document["implementation_scope"]["allowed_paths"] = [value]
        errors = validate_run_packet(write_packet(tmp_path / str(index), document), closeout=True)
        assert any("allowed_paths[0]" in error for error in errors)


def test_rejects_nonexistent_worktree(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    document["lanes"]["retail"]["worktree"] = str(tmp_path / "missing")
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert any("existing non-symlink directory" in error for error in errors)


def test_rejects_fabricated_artifact_path_and_hash(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    document["ticket"]["path"] = str((tmp_path / "missing-ticket").resolve())
    document["ticket"]["sha256"] = "b" * 64
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert any("existing file under the run root" in error for error in errors)


def test_rejects_same_worktree_for_both_lanes(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    document["lanes"]["workbench"]["worktree"] = document["lanes"]["retail"]["worktree"]
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert "lanes.retail.worktree and lanes.workbench.worktree must be distinct" in errors


def test_rejects_non_neutral_reviewer_and_missing_restart_policy(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    document["review_policy"]["reviewer_lane_neutral"] = False
    document["contamination_policy"]["restart_affected_lane_required"] = False

    errors = validate_run_packet(write_packet(tmp_path, document))

    assert "review_policy.reviewer_lane_neutral must be True" in errors
    assert "contamination_policy.restart_affected_lane_required must be true" in errors


def test_rejects_soft_review_cap(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    document["review_policy"]["review_cap_kind"] = "soft_measured_stop_condition"
    document["review_policy"]["max_completed_reviews_per_lane"] = 8
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert any("exactly 3" in error for error in errors)
    assert any("exact_three_review_cap" in error for error in errors)


def test_rejects_nudge_and_forbidden_wait_action(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    for action in ("nudge", "timeout", "silence_inference", "repair", "implementation_spawn", "accept", "reject", "lane_end"):
        document["liveness"]["missed_interval_action"] = f"wait_then_{action}"
        errors = validate_run_packet(write_packet(tmp_path, document))
        assert any("metadata-only hard wait" in error for error in errors)
    document["liveness"]["missed_interval_action"] = "inspect_metadata_only_until_schema_valid_verdict"
    document["liveness"]["forbidden_wait_actions"] = ["nudge"]
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert any("exactly the forbidden" in error for error in errors)


def test_rejects_incorrect_review_counts(tmp_path: Path) -> None:
    document = materialized_packet(tmp_path)
    document["review_policy"]["max_repair_cycles_per_lane"] = 1
    errors = validate_run_packet(write_packet(tmp_path, document))
    assert "review_policy.max_repair_cycles_per_lane must be exactly 2" in errors
