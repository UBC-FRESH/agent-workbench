"""Run a P90 side-by-side qwen3.6 extraction batch.

Raw model outputs and candidate JSONL stay under ``runtime/``. The optional
tracked summary contains counts, defects, paths, and validation statuses only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TICKETS_DIR = Path(
    "runtime/document_library/tsa23_tsr/p89_document_indexing_recipe_v2/tickets"
)
DEFAULT_OUTPUT_DIR = Path(
    "runtime/document_library/tsa23_tsr/p90_qwen36_side_by_side_batch"
)
DEFAULT_TRACKED_SUMMARY = Path(
    "benchmarks/document_library/p90_qwen36_side_by_side_batch_summary.json"
)
DEFAULT_BASE_URL_FILE = Path("runtime/ollama_openai_base_url.txt")
DEFAULT_PROVIDER_HEADERS_FILE = Path("runtime/local_provider_headers.json")
DEFAULT_MODELS = (
    "qwen3.6:35b-a3b-q8_0",
    "qwen3.6:35b-a3b-bf16",
)
MODEL_LABELS = {
    "qwen3.6:35b-a3b-q8_0": "qwen36_q8",
    "qwen3.6:35b-a3b-bf16": "qwen36_bf16",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run P90 qwen3.6 side-by-side extraction batch."
    )
    parser.add_argument("--tickets-dir", type=Path, default=DEFAULT_TICKETS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--tracked-summary",
        type=Path,
        default=DEFAULT_TRACKED_SUMMARY,
        help="Sanitized tracked summary output path.",
    )
    parser.add_argument("--base-url-file", type=Path, default=DEFAULT_BASE_URL_FILE)
    parser.add_argument(
        "--provider-headers-file",
        type=Path,
        default=DEFAULT_PROVIDER_HEADERS_FILE,
    )
    parser.add_argument(
        "--model",
        action="append",
        default=None,
        help="Model to run. May be repeated. Defaults to both qwen3.6 lanes.",
    )
    parser.add_argument(
        "--max-tickets",
        type=int,
        default=10,
        help="Number of structure tickets to compare.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse existing raw result files instead of rerunning completed probes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    models = tuple(args.model or DEFAULT_MODELS)
    tickets = select_structure_tickets(args.tickets_dir, args.max_tickets)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    runs: list[dict[str, Any]] = []
    for ticket in tickets:
        for model in models:
            runs.append(run_or_reuse(args, ticket, model))

    summary = build_summary(runs, tickets, models)
    write_json(
        args.output_dir / "p90_qwen36_side_by_side_runtime_summary.json", summary
    )
    write_json(args.tracked_summary, summary)
    print(f"wrote {args.tracked_summary}")
    print(f"completed={summary['completed_run_count']} total={summary['run_count']}")
    return 0 if summary["blocked_run_count"] == 0 else 2


def select_structure_tickets(tickets_dir: Path, max_tickets: int) -> list[Path]:
    tickets = sorted(tickets_dir.glob("*_structure.ticket.md"))
    selected = tickets[:max_tickets]
    if len(selected) != max_tickets:
        raise FileNotFoundError(
            f"expected {max_tickets} structure tickets, found {len(selected)}"
        )
    return selected


def run_or_reuse(args: argparse.Namespace, ticket: Path, model: str) -> dict[str, Any]:
    model_label = MODEL_LABELS.get(model, slug(model))
    ticket_id = ticket.name.removesuffix(".ticket.md")
    run_id = f"{ticket_id}__{model_label}"
    result_path = args.output_dir / f"{run_id}.md"
    candidate_path = args.output_dir / f"{run_id}.candidate.jsonl"
    repaired_path = args.output_dir / f"{run_id}.repaired.jsonl"
    validation_path = args.output_dir / f"{run_id}.validation.json"

    if not should_reuse_result(args.resume, result_path):
        command = [
            sys.executable,
            "scripts/copilot_sdk_ollama_probe.py",
            "--model",
            model,
            "--base-url",
            args.base_url_file.read_text(encoding="utf-8").strip(),
            "--provider-headers-file",
            str(args.provider_headers_file),
            "--ticket",
            str(ticket),
            "--output",
            str(result_path),
            "--timeout-seconds",
            str(args.timeout_seconds),
            "--wire-api",
            "completions",
        ]
        completed = subprocess.run(command, check=False)
        probe_exit_code = completed.returncode
    else:
        probe_exit_code = 0

    extraction = extract_candidate_jsonl(result_path)
    candidate_path.write_text(extraction["jsonl"], encoding="utf-8")

    validate_command = [
        sys.executable,
        "scripts/build_p89_document_indexing_recipe_v2.py",
        "--project-root",
        ".",
        "validate-jsonl",
        "--input",
        str(candidate_path),
        "--output",
        str(validation_path),
        "--repaired-output",
        str(repaired_path),
    ]
    subprocess.run(validate_command, check=False)
    validation = load_json(validation_path)

    return {
        "run_id": run_id,
        "ticket_id": ticket_id,
        "ticket_path": ticket.as_posix(),
        "model": model,
        "model_label": model_label,
        "probe_exit_code": probe_exit_code,
        "probe_status": read_probe_status(result_path),
        "raw_result_path": result_path.as_posix(),
        "candidate_jsonl_path": candidate_path.as_posix(),
        "repaired_jsonl_path": repaired_path.as_posix(),
        "validation_report_path": validation_path.as_posix(),
        "extraction_mode": extraction["mode"],
        "candidate_line_count": extraction["line_count"],
        "validation_status": validation.get("status"),
        "parseable_record_count": validation.get("parseable_record_count", 0),
        "fatal_error_count": validation.get("fatal_error_count", 0),
        "repaired_line_count": validation.get("repaired_line_count", 0),
        "dropped_non_json_line_count": validation.get("dropped_non_json_line_count", 0),
        "error_kinds": sorted(
            {
                str(error.get("kind", "unknown"))
                for error in validation.get("errors", [])
                if isinstance(error, dict)
            }
        ),
    }


def extract_candidate_jsonl(result_path: Path) -> dict[str, Any]:
    text = result_path.read_text(encoding="utf-8")
    assistant = text.split("## Assistant Messages", 1)[1].split(
        "## Raw Event Records", 1
    )[0]
    fenced = re.search(r"```(?:jsonl|json)?\s*(.*?)\s*```", assistant, flags=re.S)
    if fenced:
        jsonl = fenced.group(1).strip()
        return {
            "mode": "fenced_jsonl",
            "jsonl": jsonl + "\n",
            "line_count": count_lines(jsonl),
        }

    json_lines = [
        line.strip()
        for line in assistant.splitlines()
        if line.strip().startswith("{") and line.strip().endswith("}")
    ]
    if json_lines:
        return {
            "mode": "bare_jsonl_with_possible_prose",
            "jsonl": "\n".join(json_lines) + "\n",
            "line_count": len(json_lines),
        }

    records = parse_key_value_records(assistant)
    jsonl = "\n".join(json.dumps(record, separators=(",", ":")) for record in records)
    return {
        "mode": "key_value_blocks",
        "jsonl": jsonl + ("\n" if jsonl else ""),
        "line_count": len(records),
    }


def parse_key_value_records(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        if key == "confidence":
            try:
                current[key] = float(value)
            except ValueError:
                current[key] = value
        else:
            current[key] = value.strip().strip('"')
    if current:
        records.append(current)
    return records


def build_summary(
    runs: list[dict[str, Any]], tickets: list[Path], models: tuple[str, ...]
) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for model in models:
        model_runs = [run for run in runs if run["model"] == model]
        by_model[MODEL_LABELS.get(model, slug(model))] = {
            "model": model,
            "run_count": len(model_runs),
            "completed_run_count": sum(
                1 for run in model_runs if run["probe_status"] == "completed"
            ),
            "valid_run_count": sum(
                1 for run in model_runs if run["validation_status"] == "valid"
            ),
            "valid_candidate_record_count": sum(
                int(run["parseable_record_count"])
                for run in model_runs
                if run["validation_status"] == "valid"
            ),
            "fatal_error_count": sum(
                int(run["fatal_error_count"]) for run in model_runs
            ),
            "extraction_modes": dict(
                Counter(str(run["extraction_mode"]) for run in model_runs)
            ),
            "error_kinds": sorted(
                {kind for run in model_runs for kind in run.get("error_kinds", [])}
            ),
        }

    paired: list[dict[str, Any]] = []
    by_ticket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        by_ticket[str(run["ticket_id"])].append(run)
    for ticket_id, ticket_runs in sorted(by_ticket.items()):
        paired.append(
            {
                "ticket_id": ticket_id,
                "models": {
                    str(run["model_label"]): {
                        "validation_status": run["validation_status"],
                        "parseable_record_count": run["parseable_record_count"],
                        "extraction_mode": run["extraction_mode"],
                        "fatal_error_count": run["fatal_error_count"],
                    }
                    for run in sorted(
                        ticket_runs, key=lambda item: str(item["model_label"])
                    )
                },
            }
        )

    return {
        "schema_version": 1,
        "phase": "P90",
        "summary_id": "p90_qwen36_side_by_side_structure_batch",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "side_by_side_batch_completed",
        "source_slice": "p88_tsa23_2012_data_package_full_document_pages_001_041",
        "document_id": "tsa23_2012_23tsdp12",
        "ticket_count": len(tickets),
        "run_count": len(runs),
        "completed_run_count": sum(
            1 for run in runs if run["probe_status"] == "completed"
        ),
        "blocked_run_count": sum(
            1 for run in runs if run["probe_status"] != "completed"
        ),
        "valid_run_count": sum(
            1 for run in runs if run["validation_status"] == "valid"
        ),
        "selected_record_pass": "structure",
        "models": by_model,
        "paired_ticket_comparison": paired,
        "runs": runs,
        "accepted_record_count": 0,
        "accepted_record_note": "No source audit has been performed; records are raw worker candidates only.",
        "public_safety": {
            "raw_source_text_tracked": False,
            "raw_worker_output_tracked": False,
            "source_quotes_tracked": False,
            "provider_urls_or_headers_tracked": False,
            "personal_paths_tracked": False,
        },
    }


def read_probe_status(result_path: Path) -> str:
    if not result_path.exists():
        return "missing_result"
    for line in result_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("- status:"):
            return line.split("`", 2)[1]
    return "unknown"


def should_reuse_result(resume: bool, result_path: Path) -> bool:
    if not resume or not result_path.exists():
        return False
    return read_probe_status(result_path) == "completed"


def count_lines(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


if __name__ == "__main__":
    raise SystemExit(main())
