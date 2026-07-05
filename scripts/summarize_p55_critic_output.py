"""Summarize P55 Wave 9 critic output without tracking raw instructions."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a P55 Wave 9 critic run.")
    parser.add_argument("--packet-index", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = load_json(args.packet_index)
    summary_path = args.eval_root / packet["packet_id"] / "summary.json"
    summary = load_json(summary_path)
    row = summary["rows"][0]
    parsed, parse_error = parse_json_object(str(row.get("assistant_message", "")))
    issues = parsed.get("issues", []) if isinstance(parsed, dict) else []
    issue_rows = summarize_issues(issues)
    usage = parse_usage(args.eval_root, packet["packet_id"], Path(str(row.get("result_file", ""))))
    report = {
        "summary_id": "p55_wave9_validation_critic",
        "generated_utc": now_utc(),
        "phase": "P55",
        "wave_id": packet["wave_id"],
        "packet_id": packet["packet_id"],
        "source_packet_id": packet["source_packet_id"],
        "critic_model": packet["critic_model"],
        "raw_output_policy": "Raw critic instructions remain ignored under runtime/.",
        "status": row.get("status", "missing-summary"),
        "harness_classification": row.get("classification", ""),
        "parse_status": "parsed" if parsed is not None else "parse_failed",
        "parse_error": parse_error,
        "issue_count": len(issue_rows),
        "issue_type_counts": dict(sorted(Counter(row["issue_type"] for row in issue_rows).items())),
        "severity_counts": dict(sorted(Counter(row["severity"] for row in issue_rows).items())),
        "repair_strategy_step_count": len(parsed.get("repair_strategy", []))
        if isinstance(parsed, dict) and isinstance(parsed.get("repair_strategy"), list)
        else 0,
        "do_not_change_count": len(parsed.get("do_not_change", []))
        if isinstance(parsed, dict) and isinstance(parsed.get("do_not_change"), list)
        else 0,
        "worker_input_tokens": usage["input_tokens"],
        "worker_output_tokens": usage["output_tokens"],
        "worker_cash_cost_usd": 0.0,
        "gate_result": gate_result(parsed, issue_rows),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


def parse_json_object(text: str) -> tuple[dict[str, Any] | None, str]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        return None, "no-json-object-found"
    try:
        value = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        return None, f"json-decode-error:{exc.msg}"
    if not isinstance(value, dict):
        return None, "top-level-not-object"
    return value, ""


def summarize_issues(issues: Any) -> list[dict[str, str]]:
    if not isinstance(issues, list):
        return []
    rows: list[dict[str, str]] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        rows.append(
            {
                "issue_type": str(issue.get("issue_type", "missing")),
                "severity": str(issue.get("severity", "missing")),
                "field_present": str(issue.get("field") is not None),
            }
        )
    return rows


def gate_result(parsed: dict[str, Any] | None, issues: list[dict[str, str]]) -> str:
    if parsed is None:
        return "wave9-critic-parse-failed"
    if not issues:
        return "wave9-critic-no-issues"
    return "wave9-critic-produced-repair-instructions"


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Phase 55 Wave 9 Validation Critic Results",
            "",
            "Raw critic instructions remain ignored under runtime paths.",
            "",
            f"- generated_utc: `{report['generated_utc']}`",
            f"- gate_result: `{report['gate_result']}`",
            f"- critic_model: `{report['critic_model']}`",
            f"- parse_status: `{report['parse_status']}`",
            f"- harness_classification: `{report['harness_classification']}`",
            "",
            "## Aggregate Totals",
            "",
            f"- issue_count: `{report['issue_count']}`",
            f"- issue_type_counts: `{json.dumps(report['issue_type_counts'], sort_keys=True)}`",
            f"- severity_counts: `{json.dumps(report['severity_counts'], sort_keys=True)}`",
            f"- repair_strategy_step_count: `{report['repair_strategy_step_count']}`",
            f"- do_not_change_count: `{report['do_not_change_count']}`",
            f"- worker_input_tokens: `{report['worker_input_tokens']}`",
            f"- worker_output_tokens: `{report['worker_output_tokens']}`",
            f"- worker_cash_cost_usd: `{report['worker_cash_cost_usd']}`",
            "",
        ]
    )


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


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
