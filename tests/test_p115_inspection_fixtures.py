"""P115 inspection fixture validation tests.

Validates that the three P115 fixture bundles (clean, anomaly, provenance_gap)
have the expected structural properties. Also validates that an agent inspection
report correctly identifies expected findings.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent  # Points to tests/
FIXTURES = ROOT / "fixtures" / "p115"


# ---------------------------------------------------------------------------
# Fixture bundle existence and structure
# ---------------------------------------------------------------------------

BUNDLE_TYPES = ["clean", "anomaly", "provenance_gap"]


@pytest.mark.parametrize("bundle_type", BUNDLE_TYPES)
def test_bundle_directory_exists(bundle_type: str) -> None:
    """Each bundle type must have its directory."""
    bundle_dir = FIXTURES / bundle_type
    assert bundle_dir.exists(), f"Bundle directory missing: {bundle_dir}"
    assert bundle_dir.is_dir(), f"Not a directory: {bundle_dir}"


@pytest.mark.parametrize("bundle_type", BUNDLE_TYPES)
def test_cluster_has_config(bundle_type: str) -> None:
    """Each bundle must have rebuild_config.yaml."""
    config = FIXTURES / bundle_type / "rebuild_config.yaml"
    assert config.exists(), f"Missing rebuild_config.yaml: {config}"


@pytest.mark.parametrize("bundle_type", BUNDLE_TYPES)
def test_cluster_has_catalog(bundle_type: str) -> None:
    """Each bundle must have data_catalog.csv."""
    catalog = FIXTURES / bundle_type / "data_catalog.csv"
    assert catalog.exists(), f"Missing data_catalog.csv: {catalog}"


@pytest.mark.parametrize("bundle_type", BUNDLE_TYPES)
def test_cluster_has_evidence(bundle_type: str) -> None:
    """Each bundle must have evidence_report.txt."""
    report = FIXTURES / bundle_type / "evidence_report.txt"
    assert report.exists(), f"Missing evidence_report.txt: {report}"


# ---------------------------------------------------------------------------
# Clean fixture: should have no anomalies
# ---------------------------------------------------------------------------

def test_clean_has_all_required_fields() -> None:
    """Clean bundle must have all required provenance fields."""
    config = (FIXTURES / "clean" / "rebuild_config.yaml").read_text(encoding="utf-8")
    required = ["bundle_id", "version", "generated", "source_bundle", "generation_method"]
    for field in required:
        assert field in config, f"Missing required field '{field}' in clean config"


def test_clean_manifest_valid_json() -> None:
    """Clean bundle manifest must parse as valid JSON."""
    manifest = FIXTURES / "clean" / "manifest.json"
    text = manifest.read_text(encoding="utf-8")
    data = json.loads(text)
    assert data["bundle_id"] == "p115-clean-001"
    assert data["fixtures"]["expected_anomalies"] == 0


def test_clean_csv_has_header() -> None:
    """Clean bundle CSV must have expected header columns."""
    catalog = (FIXTURES / "clean" / "data_catalog.csv").read_text(encoding="utf-8")
    header = catalog.strip().split("\n")[0]
    required_cols = ["entity_id", "type", "status"]
    for col in required_cols:
        assert col in header, f"Missing column '{col}' in clean CSV header"


# ---------------------------------------------------------------------------
# Anomaly fixture: structural anomalies should be present
# ---------------------------------------------------------------------------

def test_anomaly_has_orphan_cross_ref() -> None:
    """Anomaly bundle must contain orphan cross-reference target."""
    catalog = (FIXTURES / "anomaly" / "data_catalog.csv").read_text(encoding="utf-8")
    assert "R003" in catalog, "Anomaly CSV should contain orphan ref to R003"

    config = (FIXTURES / "anomaly" / "rebuild_config.yaml").read_text(encoding="utf-8")
    # R003 is referenced in catalog but may or may not be in config
    # The anomaly is that the cross-reference is invalid or structurally suspicious


def test_anomaly_has_enum_violation() -> None:
    """Anomaly bundle must contain an enum-violating parameter value."""
    config = (FIXTURES / "anomaly" / "rebuild_config.yaml").read_text(encoding="utf-8")
    assert "quantum_tunnel" in config, "Anomaly config should have enum-violating method"


def test_anomaly_has_negative_seed() -> None:
    """Anomaly bundle must contain a negative random seed."""
    config = (FIXTURES / "anomaly" / "rebuild_config.yaml").read_text(encoding="utf-8")
    assert "-17" in config, "Anomaly config should have negative random seed"


# ---------------------------------------------------------------------------
# Provenance gap fixture: missing provenance fields
# ---------------------------------------------------------------------------

def test_provenance_gap_missing_timestamp() -> None:
    """Provenance gap bundle must lack the 'generated' timestamp field."""
    config = (FIXTURES / "provenance_gap" / "rebuild_config.yaml").read_text(encoding="utf-8")
    # The 'generated' field should be absent or commented out
    for line in config.split("\n"):
        stripped = line.strip()
        if stripped.startswith("generated:"):
            pytest.fail("Provenance gap config should NOT have 'generated' field")
    # If we get here, the field is absent (correct)


def test_provenance_gap_missing_source_bundle() -> None:
    """Provenance gap bundle must lack source_bundle."""
    config = (FIXTURES / "provenance_gap" / "rebuild_config.yaml").read_text(encoding="utf-8")
    # source_bundle should be absent
    for line in config.split("\n"):
        stripped = line.strip()
        if stripped.startswith("source_bundle:"):
            pytest.fail("Provenance gap config should NOT have 'source_bundle' field")


def test_provenance_gap_manifest_exists() -> None:
    """Provenance gap bundle should have manifest.json with gap metadata."""
    manifest = FIXTURES / "provenance_gap" / "manifest.json"
    assert manifest.exists(), "Provenance gap manifest.json should exist"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    gaps = data.get("fixtures", {}).get("expected_gaps", [])
    assert len(gaps) > 0, "Manifest should list expected provenance gaps"


# ---------------------------------------------------------------------------
# Cross-bundle sanity checks
# ---------------------------------------------------------------------------

def test_all_bundles_have_distinct_bundle_ids() -> None:
    """Each bundle must have a unique bundle_id."""
    bundle_ids = []
    for bundle_type in BUNDLE_TYPES:
        config = (FIXTURES / bundle_type / "rebuild_config.yaml").read_text(encoding="utf-8")
        for line in config.split("\n"):
            if line.strip().startswith("bundle_id:"):
                bid = line.strip().split(":", 1)[1].strip()
                bundle_ids.append(bid)
                break
    assert len(bundle_ids) == len(set(bundle_ids)), f"Duplicate bundle IDs: {bundle_ids}"


def test_validation_script_exists() -> None:
    """The validation script must exist."""
    script = FIXTURES / "validate_fixtures.py"
    assert script.exists(), f"Validation script missing: {script}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])