import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p107_accounting_record import validate_accounting_record


def record(tmp_path: Path) -> Path:
    data = json.loads((ROOT / "templates/p107_accounting_record_template.json").read_text())
    data["configuration_id"] = "C0"
    data["roles"].append({"role": "advisor", "session_id": "advisor-session", "provider": "terra", "model": "medium", "tokens": {k: 1 for k in ("uncached_input", "cached_input", "output", "reasoning")}, "checkpoints": {"start": "a", "end": "b"}, "confidence": "medium"})
    path = tmp_path / "accounting.json"; path.write_text(json.dumps(data)); return path


def role(name: str) -> dict[str, object]:
    return {"role": name, "session_id": f"{name}-session", "provider": "provider", "model": "model", "tokens": {k: 1 for k in ("uncached_input", "cached_input", "output", "reasoning")}, "checkpoints": {"start": "a", "end": "b"}, "confidence": "high"}


def test_valid_role_sets_for_c0_through_c4(tmp_path: Path) -> None:
    expected = {
        "C0": {"coordinator", "advisor"},
        "C1": {"coordinator", "worker", "advisor"},
        "C2": {"coordinator", "supervisor", "worker", "advisor"},
        "C3": {"coordinator", "supervisor", "worker", "advisor"},
        "C4": {"coordinator", "supervisor", "worker", "advisor"},
    }
    for configuration, names in expected.items():
        data = json.loads((ROOT / "templates/p107_accounting_record_template.json").read_text())
        data["configuration_id"] = configuration
        data["roles"] = [role(name) for name in names]
        path = tmp_path / f"{configuration}.json"; path.write_text(json.dumps(data))
        assert validate_accounting_record(path) == []


def test_missing_role_and_unknown_zero_cost_fail_closed(tmp_path: Path) -> None:
    path = record(tmp_path); data = json.loads(path.read_text()); data["roles"] = data["roles"][:1]; data["local_cost"]["amount_usd"] = 0; path.write_text(json.dumps(data))
    errors = validate_accounting_record(path)
    assert "roles must contain exactly the required paid roles for configuration_id" in errors
    assert "unknown local cost cannot be represented as zero" in errors


def test_missing_token_class_and_catalog_provenance_fail(tmp_path: Path) -> None:
    path = record(tmp_path); data = json.loads(path.read_text()); del data["roles"][0]["tokens"]["reasoning"]; data["pricing_catalog"]["provenance"] = ""; path.write_text(json.dumps(data))
    errors = validate_accounting_record(path)
    assert any("tokens.reasoning" in error for error in errors)
    assert "pricing_catalog.provenance is required" in errors
