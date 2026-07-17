from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_p107_workload_contract import validate

def valid() -> dict:
    return {"schema_version":"p107_workload_contract_v1","workload_id":"source-audit-cli","baseline_commit":"a"*40,"ticket_path":"C:/ticket.md","ticket_sha256":"b"*64,"acceptance_fixture_path":"C:/fixture","acceptance_fixture_sha256":"c"*64,"acceptance_command":"python -m pytest acceptance -q","rubric_path":"templates/p107_advisor_verdict.schema.json","allowed_paths":["src/example.py"],"usefulness_statement":"generic provenance workflow","remote_github_mutation_allowed":False}

def test_materialized_contract_is_valid(tmp_path: Path) -> None:
    path=tmp_path/"workload.json"; path.write_text(json.dumps(valid()),encoding="utf-8")
    assert validate(path)==[]

def test_rejects_unfrozen_or_remote_github_contract(tmp_path: Path) -> None:
    data=valid(); data["ticket_sha256"]="bad"; data["remote_github_mutation_allowed"]=True
    path=tmp_path/"workload.json"; path.write_text(json.dumps(data),encoding="utf-8")
    errors=validate(path)
    assert "ticket_sha256 not frozen" in errors
    assert "remote GitHub mutation forbidden in first block" in errors
