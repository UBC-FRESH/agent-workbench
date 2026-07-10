from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from agent_workbench.cli import run_foundrytk_profile_evidence_review_ticket
from agent_workbench.profile_evidence_review import (
    build_profile_evidence_review_contract,
    render_profile_evidence_review_contract_json,
    render_profile_evidence_review_ticket,
)


def write_manifest(
    tmp_path: Path,
    *,
    review_subject: str = "profile_summaries/source_run.md",
    task_family: str = "profile-evidence-review",
) -> Path:
    (tmp_path / "profile_summaries").mkdir()
    (tmp_path / "profile_summaries" / "source_run.md").write_text(
        "# Copilot SDK Profile Run Evidence\n\n- controller_health: `healthy`\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": 1,
        "run_id": "p78_profile_review_r1",
        "phase": "P78",
        "target_project": "agent-workbench",
        "target_task": task_family,
        "sdk": {
            "agent_profiles": {
                "selected": "agent-workbench-result-auditor",
                "task_overlay": {"name": "release-readiness-review"},
            }
        },
        "paths": {
            "ticket": "tickets/p78_profile_review_r1.md",
            "result": "results/p78_profile_review_r1.md",
            "blocker": "blockers/p78_profile_review_r1.md",
            "review_subject": review_subject,
        },
        "experiment": {
            "task_family": task_family,
            "review_subject_kind": "profile-run-summary",
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_profile_evidence_review_contract_accepts_preexisting_subject(
    tmp_path: Path,
) -> None:
    manifest_path = write_manifest(tmp_path)

    contract = build_profile_evidence_review_contract(
        load_manifest(manifest_path),
        manifest_path=manifest_path,
    )
    ticket = render_profile_evidence_review_ticket(contract)
    payload = json.loads(render_profile_evidence_review_contract_json(contract))

    assert contract.ok, contract.errors
    assert payload["valid"] is True
    assert payload["review_subject_path"] == "profile_summaries/source_run.md"
    assert payload["review_subject_kind"] == "profile-run-summary"
    assert "pre-existing artifact declared before this run starts" in ticket
    assert "Do not treat profile summaries" in ticket
    assert "agent_workbench_review_subject" in ticket
    assert "Do not search the filesystem" in ticket
    assert "agent_workbench_write_result" in ticket


def test_profile_evidence_review_contract_rejects_missing_subject(
    tmp_path: Path,
) -> None:
    manifest_path = write_manifest(tmp_path)
    manifest = load_manifest(manifest_path)
    manifest["paths"].pop("review_subject")

    contract = build_profile_evidence_review_contract(
        manifest,
        manifest_path=manifest_path,
    )

    assert not contract.ok
    assert any(
        "requires a pre-existing review subject" in error for error in contract.errors
    )


def test_profile_evidence_review_contract_rejects_current_run_output_subject(
    tmp_path: Path,
) -> None:
    manifest_path = write_manifest(
        tmp_path, review_subject="results/p78_profile_review_r1.md"
    )
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "p78_profile_review_r1.md").write_text(
        "Final status: accepted-candidate\n",
        encoding="utf-8",
    )

    contract = build_profile_evidence_review_contract(
        load_manifest(manifest_path),
        manifest_path=manifest_path,
    )

    assert not contract.ok
    assert any(
        "separate from current-run result path" in error for error in contract.errors
    )


def test_profile_evidence_review_contract_rejects_private_subject_path(
    tmp_path: Path,
) -> None:
    manifest_path = write_manifest(tmp_path, review_subject=r"C:\Users\somebody\run.md")

    contract = build_profile_evidence_review_contract(
        load_manifest(manifest_path),
        manifest_path=manifest_path,
    )

    assert not contract.ok
    assert any(
        "private-looking review subject path" in error for error in contract.errors
    )


def test_foundrytk_profile_evidence_review_ticket_cli_writes_outputs(
    tmp_path: Path,
    capsys: object,
) -> None:
    manifest_path = write_manifest(tmp_path)
    ticket_output = tmp_path / "ticket.md"
    json_output = tmp_path / "contract.json"

    exit_code = run_foundrytk_profile_evidence_review_ticket(
        Namespace(
            manifest=manifest_path,
            ticket_output=ticket_output,
            json_output=json_output,
            allow_missing_subject=False,
        )
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "valid=True" in captured.out
    assert ticket_output.exists()
    assert json_output.exists()
    assert (
        "review_subject_path: profile_summaries/source_run.md"
        in ticket_output.read_text(encoding="utf-8")
    )
