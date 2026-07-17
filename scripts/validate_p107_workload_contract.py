from __future__ import annotations
import json, re, sys
from pathlib import Path
SHA=re.compile(r"^[0-9a-f]{64}$"); COMMIT=re.compile(r"^[0-9a-f]{40}$")
def validate(path: str|Path)->list[str]:
    d=json.loads(Path(path).read_text(encoding="utf-8")); e=[]
    if d.get("schema_version")!="p107_workload_contract_v1": e.append("bad schema version")
    if not isinstance(d.get("baseline_commit"),str) or not COMMIT.fullmatch(d["baseline_commit"]): e.append("baseline commit not frozen")
    for key in ("ticket_sha256","acceptance_fixture_sha256"):
        if not isinstance(d.get(key),str) or not SHA.fullmatch(d[key]): e.append(f"{key} not frozen")
    for key in ("workload_id","ticket_path","acceptance_fixture_path","acceptance_command","usefulness_statement"):
        if not isinstance(d.get(key),str) or not d[key].strip() or "REPLACE_WITH" in d[key]: e.append(f"{key} not materialized")
    if not isinstance(d.get("allowed_paths"),list) or not d["allowed_paths"] or any("REPLACE_WITH" in x for x in d["allowed_paths"]): e.append("allowed paths not materialized")
    if d.get("remote_github_mutation_allowed") is not False: e.append("remote GitHub mutation forbidden in first block")
    return e
if __name__=="__main__":
    errors=validate(sys.argv[1])
    if errors: print("\\n".join(errors)); raise SystemExit(1)
    print("P107 workload contract valid")
