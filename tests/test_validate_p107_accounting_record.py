import json
import hashlib
import sys
from pathlib import Path
import pytest

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
