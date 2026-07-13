"""Fail-closed validator for the P105 dry-run matched benchmark contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate(contract_path: Path, root: Path) -> list[str]:
    data: dict[str, Any] = json.loads(contract_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("phase") != "P105" or data.get("live_inference_allowed") is not False:
        errors.append("P105 must be dry-run-only")
    source = data.get("source", {})
    for key in ("source_manifest", "source_manifest_sha256", "source_sha256", "chunk_id"):
        if not source.get(key):
            errors.append(f"source.{key} is required")
    manifest = root / source.get("source_manifest", "")
    if not manifest.is_file():
        errors.append(f"source manifest missing: {manifest}")
    elif sha256(manifest) != source.get("source_manifest_sha256"):
        errors.append("source manifest sha256 mismatch")
    p89_manifest = root / data.get("p89_contract", {}).get("materialization_manifest", "")
    if p89_manifest.is_file():
        p89 = json.loads(p89_manifest.read_text(encoding="utf-8"))
        available = {item.get("ticket_id"): item.get("record_pass") for item in p89.get("ticket_specs", [])}
        selected_passes = [available.get(ticket_id) for ticket_id in data.get("records", {}).get("selected_ticket_ids", [])]
        if any(item is None for item in selected_passes):
            errors.append("selected ticket is absent from the P89 materialization manifest")
        counts = {kind: selected_passes.count(kind) for kind in ("structure", "content_metadata")}
        required_counts = data.get("records", {}).get("required_pass_counts", {})
        for kind, required in required_counts.items():
            if counts.get(kind, 0) < required:
                errors.append(f"selected records do not meet {kind} minimum")
    records = data.get("records", {})
    selected = records.get("selected_ticket_ids", [])
    minimum, maximum = records.get("minimum"), records.get("maximum")
    if not isinstance(selected, list) or not isinstance(minimum, int) or not isinstance(maximum, int):
        errors.append("record bounds and selected_ticket_ids are required")
    elif not minimum <= len(selected) <= maximum:
        errors.append("selected ticket count is outside declared bounds")
    required_counts = records.get("required_pass_counts", {})
    if required_counts.get("structure", 0) < 3 or required_counts.get("content_metadata", 0) < 3:
        errors.append("record composition must require at least three structure and three content_metadata records")
    lanes = data.get("lanes", {})
    for shared in ("shared_source_bundle", "shared_record_schema", "shared_repair_allowance", "shared_audit_rules", "shared_scoring"):
        if lanes.get(shared) is not True:
            errors.append(f"lane symmetry missing: {shared}")
    if lanes.get("direct", {}).get("model") != "GPT-5.6 Luna":
        errors.append("direct lane model must be GPT-5.6 Luna")
    delegated = lanes.get("delegated", {})
    if delegated.get("supervisor", {}).get("model") != "qwen3-coder:latest":
        errors.append("Supervisor model must be qwen3-coder:latest")
    if delegated.get("worker", {}).get("model") != "qwen3.6:35b-a3b-bf16":
        errors.append("Worker model must be qwen3.6:35b-a3b-bf16")
    if not data.get("stop_rules") or not data.get("output_contract", {}).get("candidate_record_schema"):
        errors.append("stop rules and output contract are required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=Path("benchmarks/document_library/p105_matched_benchmark_contract.json"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.contract, args.root)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"valid P105 dry-run contract: {args.contract}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
