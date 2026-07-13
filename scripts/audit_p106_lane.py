"""Audit one P106 lane's JSONL output against the matched P105 contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.build_p89_document_indexing_recipe_v2 import validate_jsonl_text
except ModuleNotFoundError:  # direct script execution from the scripts directory
    from build_p89_document_indexing_recipe_v2 import validate_jsonl_text


def audit_lane(
    *,
    output: Path,
    source_text: Path,
    p89_contract: Path,
    p105_contract: Path,
    lane: str,
    model: str,
) -> dict[str, Any]:
    p89 = json.loads(p89_contract.read_text(encoding="utf-8"))
    p105 = json.loads(p105_contract.read_text(encoding="utf-8"))
    text = output.read_text(encoding="utf-8-sig")
    validation, _ = validate_jsonl_text(text, p89)
    source = " ".join(source_text.read_text(encoding="utf-8").split())
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        try:
            value = json.loads(line.strip().rstrip(","))
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    useful = 0
    critical_anchor_defects = 0
    type_counts: dict[str, int] = {}
    for record in records:
        type_name = str(record.get("record_pass", ""))
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
        quote = " ".join(str(record.get("source_quote", "")).split())
        is_useful = bool(record.get("title")) and bool(record.get("summary")) and bool(quote)
        exact_anchor = bool(quote) and quote in source
        if is_useful and exact_anchor:
            useful += 1
        elif is_useful and not exact_anchor:
            critical_anchor_defects += 1
    total = len(records)
    yield_value = useful / total if total else 0.0
    required = p105["records"]["required_pass_counts"]
    composition_ok = all(type_counts.get(kind, 0) >= count for kind, count in required.items())
    result = {
        "schema_version": 1,
        "phase": "P106",
        "lane": lane,
        "model": model,
        "validation_status": validation["status"],
        "record_count": total,
        "useful_record_count": useful,
        "useful_yield": round(yield_value, 6),
        "critical_source_anchor_defect_count": critical_anchor_defects,
        "object_type_counts": type_counts,
        "composition_ok": composition_ok,
        "quality_gate": "pass" if total and yield_value >= 0.9 and critical_anchor_defects == 0 and composition_ok and validation["status"] == "valid" else "fail",
        "source_text_path_excluded": True,
        "raw_output_path_excluded": True,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-text", type=Path, required=True)
    parser.add_argument("--p89-contract", type=Path, required=True)
    parser.add_argument("--p105-contract", type=Path, required=True)
    parser.add_argument("--lane", choices=("direct", "delegated"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    summary = audit_lane(
        output=args.output,
        source_text=args.source_text,
        p89_contract=args.p89_contract,
        p105_contract=args.p105_contract,
        lane=args.lane,
        model=args.model,
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["quality_gate"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
