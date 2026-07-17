from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_p107_economics_contract import validate

REGISTRY=ROOT/"templates"/"p107_configuration_registry.json"

def test_registry_is_valid() -> None:
    assert validate(REGISTRY)==[]

def test_rejects_c2_supervisor_spawn(tmp_path: Path) -> None:
    data=json.loads(REGISTRY.read_text(encoding="utf-8"))
    next(row for row in data["configurations"] if row["id"]=="C2")["supervisor_may_spawn"]=True
    path=tmp_path/"registry.json"; path.write_text(json.dumps(data),encoding="utf-8")
    assert "C2.supervisor_may_spawn must be False" in validate(path)
