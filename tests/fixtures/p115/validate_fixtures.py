#!/usr/bin/env python
"""P115 Deterministic Validation Script for FEMIC Rebuild Inspection Fixtures.

Validates fixture bundles against known properties.

Usage:
    python validate_fixtures.py --fixture clean
    python validate_fixtures.py --fixture anomaly
    python validate_fixtures.py --fixture provenance_gap
    python validate_fixtures.py --all
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

FIXTURES_ROOT = Path(__file__).resolve().parent


def check_clean(fixture_dir: Path) -> list[str]:
    errors: list[str] = []
    config_path = fixture_dir / "rebuild_config.yaml"
    if not config_path.exists():
        return ["CLEAN: Missing rebuild_config.yaml"]

    config = config_path.read_text(encoding="utf-8")

    # Required fields
    for field in ["bundle_id:", "version:", "generated:", "source_bundle:", "generation_method:"]:
        if field not in config:
            errors.append(f"CLEAN: Missing required field '{field.rstrip(':')}'")

    # No negative values
    if "-17" in config or "-50" in config:
        errors.append("CLEAN: Config should not contain negative values")

    # Manifest
    manifest = fixture_dir / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("bundle_id") != "p115-clean-001":
            errors.append("CLEAN: Manifest bundle_id mismatch")
        if data.get("fixtures", {}).get("expected_anomalies", -1) != 0:
            errors.append("CLEAN: Manifest should report 0 expected anomalies")

    # Evidence report
    report = fixture_dir / "evidence_report.txt"
    if not report.exists():
        errors.append("CLEAN: Missing evidence_report.txt")

    return errors


def check_anomaly(fixture_dir: Path) -> list[str]:
    errors: list[str] = []
    config_path = fixture_dir / "rebuild_config.yaml"
    if not config_path.exists():
        return ["ANOMALY: Missing rebuild_config.yaml"]

    config = config_path.read_text(encoding="utf-8")

    # Enum violation
    if "quantum_tunnel" not in config:
        errors.append("ANOMALY: Should contain 'quantum_tunnel' enum violation")

    # Negative seed
    if "-17" not in config:
        errors.append("ANOMALY: Should contain negative random seed -17")

    # Negative area
    if "-50.0" not in config:
        errors.append("ANOMALY: Should contain negative area_ha -50.0")

    # Orphan cross-ref
    catalog = (fixture_dir / "data_catalog.csv").read_text(encoding="utf-8")
    if "R003" not in catalog:
        errors.append("ANOMALY: Catalog should have orphan ref to R003")

    # Manifest
    manifest = fixture_dir / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        known = set(data.get("known_anomalies", []))
        expected = {"negative_area_ha_in_R003", "negative_random_seed", "model_version_missing_patch"}
        if not expected.issubset(known):
            errors.append(f"ANOMALY: Manifest known_anomalies incomplete: missing {expected - known}")

    return errors


def check_provenance_gap(fixture_dir: Path) -> list[str]:
    errors: list[str] = []
    config_path = fixture_dir / "rebuild_config.yaml"
    if not config_path.exists():
        return ["PROVGAP: Missing rebuild_config.yaml"]

    config = config_path.read_text(encoding="utf-8")
    lines = [l.strip() for l in config.split("\n")]

    # Should NOT have provenance fields
    for field in ["generated:", "source_bundle:", "generation_method:"]:
        for line in lines:
            if line.startswith(field):
                errors.append(f"PROVGAP: Should NOT have '{field.rstrip(':')}'")

    # Should still have basic fields
    for field in ["bundle_id:", "version:"]:
        found = any(line.startswith(field) for line in lines)
        if not found:
            errors.append(f"PROVGAP: Must still have '{field.rstrip(':')}'")

    # CSV should be valid
    catalog_path = fixture_dir / "data_catalog.csv"
    if catalog_path.exists():
        catalog = catalog_path.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(catalog))
        rows = list(reader)
        for row in rows:
            pid = row.get("parent_id", "")
            if pid and pid not in ("R001", "R002"):
                errors.append(f"PROVGAP: Catalog should not have orphan ref '{pid}'")

    # Manifest
    manifest = fixture_dir / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        gaps = data.get("fixtures", {}).get("expected_gaps", [])
        if "missing_generated_timestamp" not in gaps:
            errors.append("PROVGAP: Manifest should list missing_generated_timestamp gap")

    return errors


CHECKERS = {
    "clean": check_clean,
    "anomaly": check_anomaly,
    "provenance_gap": check_provenance_gap,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate P115 fixtures")
    parser.add_argument(
        "--fixture",
        choices=["clean", "anomaly", "provenance_gap", "all"],
        default="all",
    )
    args = parser.parse_args()

    all_errors: list[str] = []
    for fixture_type, checker in CHECKERS.items():
        if args.fixture != "all" and fixture_type != args.fixture:
            continue
        fixture_dir = FIXTURES_ROOT / fixture_type
        if not fixture_dir.exists():
            all_errors.append(f"Missing: {fixture_dir}")
            print(f"  {fixture_type}: MISSING")
            continue

        errors = checker(fixture_dir)
        all_errors.extend(errors)
        status = "FAIL" if errors else "PASS"
        print(f"  {fixture_type}: {status}")
        for e in errors:
            print(f"    - {e}")

    if all_errors:
        print(f"\nFAILED: {len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print("\nALL PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()