"""Fail-closed validator for the P105 dry-run matched benchmark contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_STOP_RULES = {
    "stop before any live model call",
    "stop on source or P89 contract hash mismatch",
    "stop on record count outside 8-12 or missing required pass composition",
    "stop on lane contract asymmetry",
    "stop on unknown output fields or missing required fields",
    "stop before a second document, second attempt, or direct-vs-delegated execution",
}
REQUIRED_AUDIT_STATUSES = ["accepted", "repairable", "rejected", "needs_review"]
REQUIRED_MODEL_ARGUMENTS = {
    "direct_model_argument": "--direct-model",
    "supervisor_model_argument": "--supervisor-model",
    "worker_model_argument": "--worker-model",
    "direct_model": "GPT-5.6 Luna",
    "supervisor_model": "qwen3-coder:latest",
    "worker_model": "qwen3.6:35b-a3b-bf16",
    "runtime_evidence_required_before_p106": True,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path, errors: list[str], label: str) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"{label} missing: {path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} is invalid JSON: {exc.msg}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{label} must contain a JSON object")
        return None
    return data


def require_hash(path: Path, expected: Any, label: str, errors: list[str]) -> None:
    if not isinstance(expected, str) or len(expected) != 64:
        errors.append(f"{label} sha256 is required")
    elif path.is_file() and sha256(path) != expected:
        errors.append(f"{label} sha256 mismatch")


def validate(contract_path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    data = load_json(contract_path, errors, "P105 contract")
    if data is None:
        return errors
    if data.get("phase") != "P105" or data.get("status") != "dry_run_only":
        errors.append("P105 phase and dry-run status are required")
    if data.get("live_inference_allowed") is not False:
        errors.append("P105 must be dry-run-only")

    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
        return errors
    source_manifest = root / str(source.get("source_manifest", ""))
    source_data = load_json(source_manifest, errors, "source manifest")
    require_hash(source_manifest, source.get("source_manifest_sha256"), "source manifest", errors)
    source_required = ("corpus_id", "document_id", "chunk_id", "source_sha256", "page_start", "page_end", "text_sha256", "text_char_count")
    if any(key not in source for key in source_required):
        errors.append("source semantic fields are required")
    if source_data is not None:
        for key in ("corpus_id", "document_id", "source_sha256"):
            if source_data.get(key) != source.get(key):
                errors.append(f"source manifest {key} mismatch")
        chunk = next((item for item in source_data.get("chunks", []) if item.get("chunk_id") == source.get("chunk_id")), None)
        if not isinstance(chunk, dict):
            errors.append("source chunk is absent from source manifest")
        else:
            for key in ("page_start", "page_end", "text_sha256", "text_char_count"):
                if chunk.get(key) != source.get(key):
                    errors.append(f"source chunk {key} mismatch")

    p89_contract = data.get("p89_contract")
    if not isinstance(p89_contract, dict):
        errors.append("p89_contract must be an object")
        return errors
    p89_manifest_path = root / str(p89_contract.get("materialization_manifest", ""))
    p89_manifest = load_json(p89_manifest_path, errors, "P89 materialization manifest")
    require_hash(p89_manifest_path, p89_contract.get("materialization_manifest_sha256"), "P89 materialization manifest", errors)
    record_contract_path = root / str(p89_contract.get("record_validation_contract", ""))
    record_contract = load_json(record_contract_path, errors, "P89 record validation contract")
    require_hash(record_contract_path, p89_contract.get("record_validation_contract_sha256"), "P89 record validation contract", errors)
    if record_contract is not None:
        if p89_contract.get("required_fields") != record_contract.get("required_fields"):
            errors.append("P89 required_fields mismatch")
        if p89_contract.get("required_review_status") != record_contract.get("required_review_status"):
            errors.append("P89 required_review_status mismatch")
        if record_contract.get("live_execution_allowed") is not False:
            errors.append("P89 record validation contract must be dry-run-only")

    records = data.get("records")
    if not isinstance(records, dict):
        errors.append("records must be an object")
        return errors
    selected = records.get("selected_ticket_ids")
    minimum, maximum = records.get("minimum"), records.get("maximum")
    if not isinstance(selected, list) or len(set(selected)) != len(selected):
        errors.append("selected_ticket_ids must be a unique list")
    elif not isinstance(minimum, int) or not isinstance(maximum, int) or not minimum <= len(selected) <= maximum:
        errors.append("selected ticket count is outside declared bounds")
    required_counts = records.get("required_pass_counts")
    if required_counts != {"structure": 3, "content_metadata": 3}:
        errors.append("record composition must require exactly three structure and three content_metadata records")
    if p89_manifest is not None and isinstance(selected, list):
        available = {item.get("ticket_id"): item for item in p89_manifest.get("ticket_specs", [])}
        selected_specs = [available.get(ticket_id) for ticket_id in selected]
        if any(item is None for item in selected_specs):
            errors.append("selected ticket is absent from the P89 materialization manifest")
        else:
            counts = {kind: sum(item.get("record_pass") == kind for item in selected_specs) for kind in required_counts or {}}
            for kind, required in (required_counts or {}).items():
                if counts.get(kind, 0) < required:
                    errors.append(f"selected records do not meet {kind} minimum")
            for item in selected_specs:
                if item.get("chunk_id") != source.get("chunk_id") or item.get("source_sha256") != source.get("source_sha256"):
                    errors.append("selected ticket source semantics mismatch")
                if item.get("live_execution_allowed") is not False:
                    errors.append("selected P89 ticket must prohibit live execution")

    lanes = data.get("lanes")
    if not isinstance(lanes, dict):
        errors.append("lanes must be an object")
    else:
        for shared in ("shared_source_bundle", "shared_record_schema", "shared_repair_allowance", "shared_audit_rules", "shared_scoring"):
            if lanes.get(shared) is not True:
                errors.append(f"lane symmetry missing: {shared}")
        direct = lanes.get("direct", {})
        delegated = lanes.get("delegated", {})
        if direct.get("role") != "Coordinator" or direct.get("model") != "GPT-5.6 Luna":
            errors.append("direct lane identity mismatch")
        expected_roles = {"coordinator": ("Coordinator", "GPT-5.6 Luna"), "supervisor": ("Supervisor", "qwen3-coder:latest"), "worker": ("Worker", "qwen3.6:35b-a3b-bf16")}
        for node, (role, model) in expected_roles.items():
            if delegated.get(node, {}).get("role") != role or delegated.get(node, {}).get("model") != model:
                errors.append(f"delegated {node} identity mismatch")
        if lanes.get("model_argument_contract") != REQUIRED_MODEL_ARGUMENTS:
            errors.append("model argument contract mismatch")

    if set(data.get("stop_rules", [])) != REQUIRED_STOP_RULES:
        errors.append("stop rules mismatch")
    output = data.get("output_contract")
    expected_output = {
        "candidate_record_schema": "p89_jsonl_validation_contract.json",
        "repair_allowance": "only deterministic P89 repairs; no semantic repair",
        "audit_statuses": REQUIRED_AUDIT_STATUSES,
        "quality_scoring": "identical source-anchor, schema, audit, and scoring rules for both lanes",
    }
    if output != expected_output:
        errors.append("output contract mismatch")
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
