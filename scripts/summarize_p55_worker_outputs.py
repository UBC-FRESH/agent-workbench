"""Summarize P55 worker outputs without tracking raw source text.

The P55 runtime outputs include source quotes and full worker responses, so they
must remain ignored under runtime/. This script reads those ignored summaries
and writes aggregate metrics only.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


QUOTE_WORD_LIMIT = 25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize ignored P55 worker eval outputs into sanitized metrics.",
    )
    parser.add_argument("--packet-index", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--wave", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--github-parent-issue", type=int, default=367)
    parser.add_argument("--github-child-issue", type=int, default=369)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet_index = load_json(args.packet_index)
    packets = [
        packet
        for packet in packet_index.get("packets", packet_index.get("eval_packets", []))
        if packet.get("wave_id") == args.wave
    ]
    runs = [summarize_packet(packet, args.eval_root) for packet in packets]
    report = {
        "summary_id": f"p55_{args.wave}",
        "generated_utc": now_utc(),
        "phase": "P55",
        "github_parent_issue": args.github_parent_issue,
        "github_child_issue": args.github_child_issue,
        "packet_index": slash_path(args.packet_index),
        "runtime_output_root": slash_path(args.eval_root),
        "raw_output_policy": "Raw worker outputs and source quotes remain ignored under runtime/.",
        "wave": args.wave,
        "runs": runs,
        "totals": summarize_totals(runs),
        "gate_result": gate_result(args.wave, runs),
        "recommended_next_move": recommendation(args.wave, runs),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


def summarize_packet(packet: dict[str, Any], eval_root: Path) -> dict[str, Any]:
    packet_id = str(packet["packet_id"])
    summary_path = eval_root / packet_id / "summary.json"
    summary = load_json(summary_path) if summary_path.exists() else {}
    rows = summary.get("rows", []) if isinstance(summary, dict) else []
    row = rows[0] if rows and isinstance(rows[0], dict) else {}
    assistant_message = str(row.get("assistant_message", ""))
    records, malformed_lines = parse_jsonl_records(assistant_message)
    expected_chunks = expected_chunk_ids(packet)
    valid_records = [
        record
        for record in records
        if isinstance(record.get("chunk_id"), str) and record["chunk_id"] in expected_chunks
    ]
    invalid_chunk_ids = Counter(
        str(record.get("chunk_id", ""))
        for record in records
        if not (isinstance(record.get("chunk_id"), str) and record["chunk_id"] in expected_chunks)
    )
    record_ids = [str(record.get("record_id", "")) for record in records]
    object_type_counts = Counter(
        str(record.get("object_type", "")) for record in valid_records if record.get("object_type")
    )
    chunk_counts = Counter(str(record.get("chunk_id", "")) for record in valid_records)
    result_file = Path(str(row.get("result_file", "")))
    usage = parse_usage(eval_root, packet_id, result_file)
    worker_model = packet.get("models", [""])[0]
    return {
        "packet_id": packet_id,
        "wave_id": packet.get("wave_id", ""),
        "document_id": packet.get("document_id", ""),
        "shape_id": packet.get("shape_id", ""),
        "record_type": packet.get("record_type", ""),
        "model": worker_model,
        "status": row.get("status", "missing-summary"),
        "harness_classification": row.get("classification", ""),
        "requested_chunks": int(packet.get("included_chunk_count", 0)),
        "expected_chunk_ids": sorted(expected_chunks),
        "covered_valid_chunks": len(chunk_counts),
        "missing_expected_chunks": sorted(expected_chunks - set(chunk_counts)),
        "parseable_json_records": len(records),
        "malformed_lines": malformed_lines,
        "duplicate_record_ids": duplicate_count(record_ids),
        "invalid_chunk_id_records": len(records) - len(valid_records),
        "invalid_chunk_id_counts": dict(sorted(invalid_chunk_ids.items())),
        "worker_model_field_match_count": sum(
            1 for record in records if record.get("worker_model") == worker_model
        ),
        "records_with_source_quote": sum(1 for record in records if record.get("source_quote")),
        "source_quote_over_25_words": sum(
            1
            for record in records
            if word_count(str(record.get("source_quote", ""))) > QUOTE_WORD_LIMIT
        ),
        "object_type_counts": dict(sorted(object_type_counts.items())),
        "chunk_record_counts": dict(sorted(chunk_counts.items())),
        "worker_input_tokens": usage["input_tokens"],
        "worker_output_tokens": usage["output_tokens"],
        "runtime_summary_path": runtime_path(summary_path),
        "runtime_result_file": runtime_path(resolve_result_file(eval_root, packet_id, result_file)),
    }


def expected_chunk_ids(packet: dict[str, Any]) -> set[str]:
    selected = packet.get("selected_chunk_id")
    if isinstance(selected, str) and selected:
        return {selected}
    requested = int(packet.get("included_chunk_count", 0))
    ticket_path = Path(str(packet.get("ticket_path", "")))
    if ticket_path.exists():
        text = ticket_path.read_text(encoding="utf-8-sig")
        matches = re.findall(r"- `([^`]+::pages_\d{3}_\d{3})`", text)
        if matches:
            return set(matches)
    return {f"unknown_chunk_{index + 1}" for index in range(requested)}


def parse_jsonl_records(text: str) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    malformed = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        if not (line.startswith("{") and line.endswith("}")):
            malformed += 1
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            malformed += 1
    return records, malformed


def parse_usage(eval_root: Path, packet_id: str, result_file: Path) -> dict[str, int]:
    path = resolve_result_file(eval_root, packet_id, result_file)
    if not path.exists():
        return {"input_tokens": 0, "output_tokens": 0}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    input_matches = [int(value) for value in re.findall(r'"input_tokens":\s*(\d+)', text)]
    output_matches = [int(value) for value in re.findall(r'"output_tokens":\s*(\d+)', text)]
    return {
        "input_tokens": input_matches[-1] if input_matches else 0,
        "output_tokens": output_matches[-1] if output_matches else 0,
    }


def resolve_result_file(eval_root: Path, packet_id: str, result_file: Path) -> Path:
    if result_file.is_absolute():
        return result_file
    if result_file.exists():
        return result_file
    return eval_root / packet_id / result_file.name


def summarize_totals(runs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "worker_runs": len(runs),
        "completed_runs": sum(1 for run in runs if run.get("status") == "completed"),
        "parseable_json_records": sum(int(run["parseable_json_records"]) for run in runs),
        "malformed_lines": sum(int(run["malformed_lines"]) for run in runs),
        "requested_chunks": sum(int(run["requested_chunks"]) for run in runs),
        "covered_valid_chunks": sum(int(run["covered_valid_chunks"]) for run in runs),
        "invalid_chunk_id_records": sum(int(run["invalid_chunk_id_records"]) for run in runs),
        "source_quote_over_25_words": sum(int(run["source_quote_over_25_words"]) for run in runs),
        "worker_input_tokens": sum(int(run["worker_input_tokens"]) for run in runs),
        "worker_output_tokens": sum(int(run["worker_output_tokens"]) for run in runs),
        "worker_cash_cost_usd": 0.0,
    }


def gate_result(wave: str, runs: list[dict[str, Any]]) -> str:
    if not runs:
        return "no-runs"
    all_completed = all(run.get("status") == "completed" for run in runs)
    all_covered = all(not run.get("missing_expected_chunks") for run in runs)
    malformed = sum(int(run["malformed_lines"]) for run in runs)
    invalid_chunks = sum(int(run["invalid_chunk_id_records"]) for run in runs)
    if all_completed and all_covered and malformed == 0 and invalid_chunks == 0:
        return f"{wave}-coverage-pass-format-repair-needed"
    return f"{wave}-needs-repair-before-scaling"


def recommendation(wave: str, runs: list[dict[str, Any]]) -> str:
    if wave == "wave3_chunk_orchestration":
        return (
            "Use chunk-orchestrated tickets as the next extraction default if coverage "
            "improves; follow with a delegated quote-normalization repair pass before "
            "paid supervisor source audit."
        )
    return "Review aggregate defects before selecting the next worker ticket shape."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Phase 55 {report['wave']} Results",
        "",
        "Raw worker outputs and source quotes remain ignored under runtime paths.",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- gate_result: `{report['gate_result']}`",
        "",
        "## Aggregate Totals",
        "",
    ]
    totals = report["totals"]
    for key, value in totals.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| Packet | Status | Shape | Requested Chunks | Covered Chunks | Records | Bad Lines | Invalid Chunk IDs | Quote Violations | Input Tokens | Output Tokens |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for run in report["runs"]:
        lines.append(
            "| {packet} | `{status}` | `{shape}` | {requested} | {covered} | {records} | "
            "{bad} | {invalid} | {quotes} | {input_tokens} | {output_tokens} |".format(
                packet=run["packet_id"],
                status=run["status"],
                shape=run["shape_id"],
                requested=run["requested_chunks"],
                covered=run["covered_valid_chunks"],
                records=run["parseable_json_records"],
                bad=run["malformed_lines"],
                invalid=run["invalid_chunk_id_records"],
                quotes=run["source_quote_over_25_words"],
                input_tokens=run["worker_input_tokens"],
                output_tokens=run["worker_output_tokens"],
            )
        )
    lines.extend(["", "## Recommendation", "", str(report["recommended_next_move"]), ""])
    return "\n".join(lines)


def duplicate_count(values: list[str]) -> int:
    counts = Counter(value for value in values if value)
    return sum(count - 1 for count in counts.values() if count > 1)


def word_count(value: str) -> int:
    return len([word for word in re.split(r"\s+", value.strip()) if word])


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def runtime_path(path: Path) -> str:
    return slash_path(path) if not path.is_absolute() else slash_path(Path(*path.parts[-6:]))


def slash_path(path: Path) -> str:
    return path.as_posix()


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
