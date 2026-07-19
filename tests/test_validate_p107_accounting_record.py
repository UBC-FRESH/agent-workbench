import json
import hashlib
import sys
from pathlib import Path
import pytest
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_accounting_record import validate_accounting_record


def make_record(tmp_path: Path, configuration: str = "C1") -> tuple[Path, dict]:
    data = json.loads((ROOT / "templates/p107_accounting_record_template.json").read_text())
    data["configuration_id"] = configuration
    if configuration == "C0":
        data["roles"] = [r for r in data["roles"] if r["role"] in {"coordinator", "advisor"}]
    elif configuration in {"C2", "C3", "C4"}:
        supervisor = dict(data["roles"][0])
        supervisor["role"] = "supervisor"
        supervisor["session_id"] = "supervisor-session"
        data["roles"].append(supervisor)
    data["source_session_identity"]["session_ids"] = [r["session_id"] for r in data["roles"]]
    repo = tmp_path / "repo"; repo.mkdir(exist_ok=True)
    if not (repo / ".git").exists():
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
        (repo / "tracked").write_text("fixture\n"); subprocess.run(["git", "add", "tracked"], cwd=repo, check=True); subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    expected_edges = {
        "C0": [("coordinator", "advisor")],
        "C1": [("coordinator", "worker"), ("coordinator", "advisor")],
        "C2": [("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")],
        "C3": [("coordinator", "supervisor"), ("coordinator", "advisor"), ("supervisor", "worker")],
        "C4": [("coordinator", "supervisor"), ("coordinator", "worker"), ("coordinator", "advisor")],
    }[configuration]
    parent_by_role = {child: parent for parent, child in expected_edges}
    raw_sessions = []
    for role_name in {r["role"] for r in data["roles"]}:
        raw = tmp_path / f"{role_name}.json"; raw.write_text(json.dumps({"schema_version": "p107_session_record_v1", "session_id": f"{role_name}-session", "parent_session_id": None if parent_by_role.get(role_name) is None else f"{parent_by_role[role_name]}-session", "role": role_name, "provider": "fixture", "model_class": "fixture", "terminal_event": "completed", "event_type": "session"}))
        parent_role = parent_by_role.get(role_name)
        raw_sessions.append({"role": role_name, "session_id": f"{role_name}-session", "parent_session_id": None if parent_role is None else f"{parent_role}-session", "provider": "fixture", "model_class": "fixture", "raw_session_path": raw.name, "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "terminal_event": "completed"})
    edges = [{"parent_session_id": f"{parent}-session", "child_session_id": f"{child}-session", "parent_role": parent, "child_role": child, "fork_context": False, "source_artifact_path": f"edge-{parent}-{child}.json", "source_artifact_sha256": ""} for parent, child in expected_edges]
    for edge in edges:
        artifact = tmp_path / edge["source_artifact_path"]; artifact.write_text(json.dumps({"schema_version": "p107_spawn_event_v1", "parent_session_id": edge["parent_session_id"], "child_session_id": edge["child_session_id"], "parent_role": edge["parent_role"], "child_role": edge["child_role"], "fork_context": False, "terminal_event": "completed", "observed_event": "spawn"})); edge["source_artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    manifest = {"schema_version": "p107_run_evidence_manifest_v1", "run_id": data["run_id"], "configuration_id": configuration, "repository_path": str(repo), "starting_commit": commit, "terminal_event": "completed", "raw_sessions": raw_sessions, "spawn_edges": edges}
    manifest_path = tmp_path / "run-evidence-manifest.json"; manifest_path.write_text(json.dumps(manifest))
    data["run_evidence_manifest"] = {"path": manifest_path.name, "sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest()}
    for role in data["roles"]:
        raw = next(s for s in raw_sessions if s["role"] == role["role"])
        start = tmp_path / f"{role['role']}-start.json"; end = tmp_path / f"{role['role']}-end.json"
        for target, ordinal in ((start, 1), (end, 2)):
            target.write_text(json.dumps({"schema_version": "p107_parsed_session_event_v1", "session_id": role["session_id"], "event_ordinal": ordinal, "event_timestamp": f"2026-01-01T00:00:0{ordinal}Z", "token_snapshot": {"uncached_input": ordinal, "cached_input": 0, "output": ordinal, "reasoning": 0}}))
        role["checkpoints"] = {"start": {"session_id": role["session_id"], "snapshot_path": start.name, "snapshot_sha256": hashlib.sha256(start.read_bytes()).hexdigest()}, "end": {"session_id": role["session_id"], "snapshot_path": end.name, "snapshot_sha256": hashlib.sha256(end.read_bytes()).hexdigest()}}
    catalog = {"schema_version": 1, "entries": [{"model_id": "model-id", "rates": {"input_per_1m_usd": 1.0, "cached_input_read_per_1m_usd": 0.1, "output_per_1m_usd": 2.0}}]}
    catalog_path = tmp_path / "pricing-catalog.json"
    raw = json.dumps(catalog).encode()
    catalog_path.write_bytes(raw)
    data["pricing_catalog"]["path"] = str(catalog_path)
    data["pricing_catalog"]["content_hash"] = "sha256:" + hashlib.sha256(raw).hexdigest()
    path = tmp_path / "record.json"
    path.write_text(json.dumps(data))
    return path, data


def test_valid_configurations(tmp_path: Path) -> None:
    for config in ("C0", "C1", "C2", "C3", "C4"):
        path, _ = make_record(tmp_path, config)
        assert validate_accounting_record(path) == []


def test_role_sessions_must_be_unique_and_source_bound(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["roles"][1]["session_id"] = data["roles"][0]["session_id"]
    data["source_session_identity"]["session_ids"] = ["coordinator-session"]
    path.write_text(json.dumps(data))
    errors = validate_accounting_record(path)
    assert any("duplicate session_id" in e for e in errors)
    assert any("exactly all role session IDs" in e for e in errors)


def test_tokens_prices_totals_and_catalog_are_checked(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["roles"][0]["tokens"]["output"] = 1.5
    data["roles"][0]["token_usd"]["output"] = 2.0
    data["roles"][0]["total_usd"] = 2.0
    data["pricing_catalog"].pop("content_hash")
    path.write_text(json.dumps(data))
    errors = validate_accounting_record(path)
    assert any("nonnegative integer" in e for e in errors)
    assert any("pricing_catalog.content_hash" in e for e in errors)


def test_c4_unknown_or_measured_local_cost_only(tmp_path: Path) -> None:
    path, data = make_record(tmp_path, "C4")
    data["local_cost"] = {"status": "not_applicable", "amount_usd": 0}
    path.write_text(json.dumps(data))
    errors = validate_accounting_record(path)
    assert any("invalid for configuration" in e for e in errors)
    assert any("cannot be zero" in e for e in errors)


def test_unknown_local_cost_never_zero_and_required_run_accounting(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["local_cost"]["amount_usd"] = 0
    data["run_accounting"].pop("adapter_identity")
    path.write_text(json.dumps(data))
    errors = validate_accounting_record(path)
    assert "unknown local cost cannot be represented as zero" in errors
    assert "run_accounting.adapter_identity is required" in errors


def test_cli_success_does_not_claim_comparison_eligibility() -> None:
    text = (ROOT / "scripts/validate_p107_accounting_record.py").read_text()
    assert "comparison eligible" not in text


def test_rejects_missing_or_tampered_catalog(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["pricing_catalog"]["path"] = str(tmp_path / "missing.json")
    path.write_text(json.dumps(data))
    assert any("cannot load pricing_catalog artifact" in e for e in validate_accounting_record(path))


def test_rejects_incorrect_derived_usd(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["roles"][0]["tokens"]["output"] = 10
    data["roles"][0]["token_usd"]["output"] = 0
    path.write_text(json.dumps(data))
    assert any("catalog-derived USD" in e for e in validate_accounting_record(path))

def test_rejects_nonexistent_or_altered_manifest(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["run_evidence_manifest"]["path"] = "missing.json"
    path.write_text(json.dumps(data))
    assert any("run_evidence_manifest.path" in e for e in validate_accounting_record(path))
    path, data = make_record(tmp_path)
    data["run_evidence_manifest"]["sha256"] = "0" * 64
    path.write_text(json.dumps(data))
    assert any("run_evidence_manifest.sha256" in e for e in validate_accounting_record(path))

def test_rejects_checkpoint_not_bound_to_manifest_session(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["roles"][0]["checkpoints"]["start"]["session_id"] = "forged-session"
    path.write_text(json.dumps(data))
    assert any("session_id must match role session" in e for e in validate_accounting_record(path))

def test_rejects_checkpoint_without_snapshot_evidence(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["roles"][0]["checkpoints"]["end"] = "checkpoint prose"
    path.write_text(json.dumps(data))
    assert any("hashed parsed session record" in e for e in validate_accounting_record(path))


@pytest.mark.parametrize("mutation", ["identical", "prose", "wrong-session", "reversed"])
def test_rejects_invalid_checkpoint_event_records(tmp_path: Path, mutation: str) -> None:
    path, data = make_record(tmp_path)
    start = data["roles"][0]["checkpoints"]["start"]
    end = data["roles"][0]["checkpoints"]["end"]
    if mutation == "identical":
        end.update(start)
    elif mutation == "prose":
        target = Path(path).parent / end["snapshot_path"]; target.write_text("checkpoint prose")
        end["snapshot_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    elif mutation == "wrong-session":
        target = Path(path).parent / end["snapshot_path"]; record = json.loads(target.read_text()); record["session_id"] = "other-session"; target.write_text(json.dumps(record)); end["snapshot_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    else:
        target = Path(path).parent / end["snapshot_path"]; record = json.loads(target.read_text()); record["event_ordinal"] = 0; target.write_text(json.dumps(record)); end["snapshot_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    path.write_text(json.dumps(data))
    assert any("checkpoint" in error and ("ordered" in error or "parsed" in error or "session_id" in error or "token_snapshot" in error) for error in validate_accounting_record(path))


def test_measured_local_cost_requires_adapter_identity(tmp_path: Path) -> None:
    path, data = make_record(tmp_path)
    data["local_cost"] = {"status": "measured", "amount_usd": 1.0, "basis": "metered"}
    data["run_accounting"]["adapter_identity"] = None
    path.write_text(json.dumps(data))
    assert any("measured local cost requires run_accounting.adapter_identity" in e for e in validate_accounting_record(path))


@pytest.mark.parametrize("nonfinite", [float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize("location", [
    "local_cost.amount_usd",
    "run_accounting.active_time_seconds",
    "run_accounting.wait_time_seconds",
    "run_accounting.review_count",
    "run_accounting.repair_count",
    "run_accounting.transport_count",
    "run_accounting.invalid_run_spend_usd",
    "roles[0].tokens.output",
    "roles[0].token_usd.output",
    "roles[0].total_usd",
    "total_paid_usd",
])
def test_rejects_nonfinite_accounting_numbers(tmp_path: Path, nonfinite: float, location: str) -> None:
    path, data = make_record(tmp_path)
    target = data
    parts = location.replace("]", "").replace("[", ".").split(".")
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    target[parts[-1]] = nonfinite
    path.write_text(json.dumps(data))
    assert validate_accounting_record(path), location


@pytest.mark.parametrize("nonfinite", [float("inf"), float("-inf"), float("nan")])
def test_rejects_nonfinite_catalog_rates(tmp_path: Path, nonfinite: float) -> None:
    path, data = make_record(tmp_path)
    catalog_path = Path(data["pricing_catalog"]["path"])
    catalog = json.loads(catalog_path.read_text())
    catalog["entries"][0]["rates"]["output_per_1m_usd"] = nonfinite
    raw = json.dumps(catalog).encode()
    catalog_path.write_bytes(raw)
    data["pricing_catalog"]["content_hash"] = "sha256:" + hashlib.sha256(raw).hexdigest()
    path.write_text(json.dumps(data))
    assert any("pricing catalog rate" in error for error in validate_accounting_record(path))
