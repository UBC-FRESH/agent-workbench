"""Run repeated Copilot SDK/Ollama probes from a local manifest.

This helper is local-only. It reads an ignored JSON manifest, invokes the
existing SDK probe helper for every model/repeat pair, and writes a compact
sanitized summary for supervisor review.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SUMMARY_MD = "summary.md"
DEFAULT_SUMMARY_JSON = "summary.json"


@dataclass(frozen=True)
class EvalConfig:
    evaluation_id: str
    ticket: Path
    expected_marker: str
    required_sections: list[str]
    forbidden_phrases: list[str]
    allow_unexpected_sections: bool
    allow_preamble: bool
    require_patch: bool
    allowed_patch_files: list[str]
    models: list[str]
    repeats: int
    timeout_seconds: int
    output_dir: Path
    probe_script: Path
    python_executable: str
    base_url: str
    provider_headers_file: Path | None
    wire_api: str
    mode: str
    base_directory: Path | None
    sdk_source: Path | None


@dataclass(frozen=True)
class PlannedRun:
    model: str
    repeat_index: int
    output_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the same SDK/Ollama worker ticket repeatedly across configured "
            "models and summarize the ignored result files."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned probe commands without contacting the model provider.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Skip probe execution and summarize existing result files.",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> EvalConfig:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    base_url = str(data.get("base_url", "")).strip()
    base_url_file = str(data.get("base_url_file", "")).strip()
    if not base_url and base_url_file:
        base_url = Path(base_url_file).read_text(encoding="utf-8-sig").strip()

    models = [str(model) for model in data.get("models", [])]
    if not models:
        raise ValueError("manifest models must contain at least one model")

    repeats = int(data.get("repeats", 1))
    if repeats < 1:
        raise ValueError("manifest repeats must be at least 1")

    ticket = Path(str(data["ticket"]))
    if not ticket.exists():
        raise FileNotFoundError(f"ticket not found: {ticket}")
    if not base_url:
        raise ValueError("manifest must provide base_url or base_url_file")

    provider_headers_file = optional_path(data.get("provider_headers_file"))
    if provider_headers_file is not None and not provider_headers_file.exists():
        raise FileNotFoundError(f"provider headers file not found: {provider_headers_file}")

    return EvalConfig(
        evaluation_id=str(data.get("evaluation_id", "sdk_same_ticket_eval")),
        ticket=ticket,
        expected_marker=str(data.get("expected_marker", "")),
        required_sections=[str(section) for section in data.get("required_sections", [])],
        forbidden_phrases=[str(phrase) for phrase in data.get("forbidden_phrases", [])],
        allow_unexpected_sections=bool(data.get("allow_unexpected_sections", True)),
        allow_preamble=bool(data.get("allow_preamble", True)),
        require_patch=bool(data.get("require_patch", False)),
        allowed_patch_files=[str(path) for path in data.get("allowed_patch_files", [])],
        models=models,
        repeats=repeats,
        timeout_seconds=int(data.get("timeout_seconds", 120)),
        output_dir=Path(str(data.get("output_dir", "runtime/agent_jobs/sdk_eval"))),
        probe_script=Path(str(data.get("probe_script", "scripts/copilot_sdk_ollama_probe.py"))),
        python_executable=str(data.get("python_executable", "")).strip() or sys.executable,
        base_url=base_url,
        provider_headers_file=provider_headers_file,
        wire_api=str(data.get("wire_api", "completions")),
        mode=str(data.get("mode", "empty")),
        base_directory=optional_path(data.get("base_directory")),
        sdk_source=optional_path(data.get("sdk_source")),
    )


def optional_path(value: Any) -> Path | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return Path(text)


def planned_runs(config: EvalConfig) -> list[PlannedRun]:
    runs: list[PlannedRun] = []
    for model in config.models:
        model_slug = slugify(model)
        for repeat_index in range(1, config.repeats + 1):
            output_path = config.output_dir / f"{model_slug}_run{repeat_index:02d}.md"
            runs.append(
                PlannedRun(
                    model=model,
                    repeat_index=repeat_index,
                    output_path=output_path,
                )
            )
    return runs


def build_command(config: EvalConfig, run: PlannedRun) -> list[str]:
    command = [
        config.python_executable,
        str(config.probe_script),
        "--model",
        run.model,
        "--base-url",
        config.base_url,
        "--ticket",
        str(config.ticket),
        "--output",
        str(run.output_path),
        "--timeout-seconds",
        str(config.timeout_seconds),
        "--wire-api",
        config.wire_api,
        "--mode",
        config.mode,
    ]
    if config.provider_headers_file is not None:
        command.extend(["--provider-headers-file", str(config.provider_headers_file)])
    if config.base_directory is not None:
        command.extend(["--base-directory", str(config.base_directory)])
    if config.sdk_source is not None:
        command.extend(["--sdk-source", str(config.sdk_source)])
    return command


def run_probes(config: EvalConfig, runs: list[PlannedRun], dry_run: bool) -> int:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    failure_count = 0
    for run in runs:
        command = build_command(config, run)
        display = redact_command(command, config)
        if dry_run:
            print("DRY-RUN " + " ".join(display))
            continue
        print(f"RUN {run.model} repeat {run.repeat_index}")
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            failure_count += 1
            print(
                f"FAILED {run.model} repeat {run.repeat_index}: exit {completed.returncode}",
                file=sys.stderr,
            )
    return failure_count


def redact_command(command: list[str], config: EvalConfig) -> list[str]:
    redacted: list[str] = []
    skip_next = False
    private_value_flags = {"--base-url", "--provider-headers-file", "--sdk-source"}
    for index, item in enumerate(command):
        if skip_next:
            skip_next = False
            continue
        redacted.append(item)
        if item in private_value_flags and index + 1 < len(command):
            replacement = {
                "--base-url": "<configured-ollama-openai-base-url>",
                "--provider-headers-file": "<ignored-provider-headers-file>",
                "--sdk-source": "<configured-copilot-sdk-python-source>",
            }[item]
            redacted.append(replacement)
            skip_next = True
    return redacted


def summarize(config: EvalConfig, runs: list[PlannedRun]) -> dict[str, Any]:
    rows = [summarize_run(config, run) for run in runs]
    by_model: dict[str, dict[str, int]] = {}
    for row in rows:
        model_counts = by_model.setdefault(row["model"], {})
        classification = row["classification"]
        model_counts[classification] = model_counts.get(classification, 0) + 1

    return {
        "evaluation_id": config.evaluation_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "ticket": str(config.ticket),
        "expected_marker": config.expected_marker,
        "required_sections": config.required_sections,
        "require_patch": config.require_patch,
        "allowed_patch_files": config.allowed_patch_files,
        "models": config.models,
        "repeats": config.repeats,
        "rows": rows,
        "classification_counts": by_model,
    }


def summarize_run(config: EvalConfig, run: PlannedRun) -> dict[str, Any]:
    if not run.output_path.exists():
        return {
            "model": run.model,
            "repeat_index": run.repeat_index,
            "result_file": str(run.output_path),
            "status": "missing",
            "blocker": "missing-result-file",
            "assistant_message": "",
            "classification": "missing-result-file",
        }

    text = run.output_path.read_text(encoding="utf-8-sig")
    status = metadata_value(text, "status")
    blocker = metadata_value(text, "blocker")
    error = metadata_value(text, "error")
    assistant_message = assistant_section(text)
    classification = classify_result(
        status=status,
        blocker=blocker,
        error=error,
        assistant_message=assistant_message,
        expected_marker=config.expected_marker,
        required_sections=config.required_sections,
        forbidden_phrases=config.forbidden_phrases,
        allow_unexpected_sections=config.allow_unexpected_sections,
        allow_preamble=config.allow_preamble,
        require_patch=config.require_patch,
        allowed_patch_files=config.allowed_patch_files,
    )
    section_report = structured_section_report(assistant_message, config.required_sections)
    patch_report = patch_proposal_report(assistant_message, config.allowed_patch_files)
    return {
        "model": run.model,
        "repeat_index": run.repeat_index,
        "result_file": str(run.output_path),
        "status": status,
        "blocker": blocker,
        "error": error,
        "assistant_message": assistant_message,
        "classification": classification,
        "missing_sections": section_report["missing_sections"],
        "unexpected_sections": section_report["unexpected_sections"],
        "has_preamble": section_report["has_preamble"],
        "patch_files": patch_report["patch_files"],
        "patch_block_count": patch_report["patch_block_count"],
        "patch_error": patch_report["patch_error"],
    }


def metadata_value(text: str, key: str) -> str:
    pattern = re.compile(rf"^- {re.escape(key)}: `([^`]*)`$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def assistant_section(text: str) -> str:
    marker = "## Assistant Messages"
    next_marker = "\n## Raw Event Records"
    start = text.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    end = text.find(next_marker, start)
    if end == -1:
        end = len(text)
    return text[start:end].strip()


def classify_result(
    status: str,
    blocker: str,
    error: str,
    assistant_message: str,
    expected_marker: str,
    required_sections: list[str],
    forbidden_phrases: list[str],
    allow_unexpected_sections: bool,
    allow_preamble: bool,
    require_patch: bool,
    allowed_patch_files: list[str],
) -> str:
    if status != "completed":
        if blocker == "session-idle-timeout":
            return "timeout"
        if blocker == "model-call-failure":
            return "model-call-failure"
        if blocker == "sdk-runtime-error":
            return "sdk-runtime-error"
        if blocker:
            return blocker
        return "blocked"
    lower_message = assistant_message.lower()
    if any(phrase.lower() in lower_message for phrase in forbidden_phrases):
        return "refusal-or-forbidden-phrase"
    if looks_loop_like(assistant_message):
        return "loop-like-repetition"
    if require_patch:
        patch_report = patch_proposal_report(assistant_message, allowed_patch_files)
        if patch_report["patch_block_count"] == 0:
            return "missing-patch"
        if patch_report["patch_error"]:
            return patch_report["patch_error"]
    if required_sections:
        section_report = structured_section_report(assistant_message, required_sections)
        if section_report["missing_sections"]:
            return "missing-section"
        if section_report["unexpected_sections"] and not allow_unexpected_sections:
            return "extra-prose"
        if section_report["has_preamble"] and not allow_preamble:
            return "extra-prose"
        if require_patch:
            return "patch-proposal"
        return "structured-output"
    if assistant_message == expected_marker:
        return "exact-marker"
    marker_count = assistant_message.count(expected_marker)
    if marker_count > 1:
        return "duplicate-marker"
    if marker_count == 1:
        return "extra-output"
    return "missing-marker"


def patch_proposal_report(
    assistant_message: str,
    allowed_patch_files: list[str],
) -> dict[str, Any]:
    blocks = fenced_code_blocks(assistant_message, {"diff", "patch"})
    if not blocks:
        return {
            "patch_block_count": 0,
            "patch_files": [],
            "patch_error": "",
        }
    patch_files: list[str] = []
    malformed = False
    for block in blocks:
        files = patch_files_from_block(block)
        if not files:
            malformed = True
        for file_path in files:
            if file_path not in patch_files:
                patch_files.append(file_path)
    if malformed:
        return {
            "patch_block_count": len(blocks),
            "patch_files": patch_files,
            "patch_error": "malformed-patch",
        }
    allowed = set(allowed_patch_files)
    if allowed and any(file_path not in allowed for file_path in patch_files):
        return {
            "patch_block_count": len(blocks),
            "patch_files": patch_files,
            "patch_error": "wrong-file",
        }
    return {
        "patch_block_count": len(blocks),
        "patch_files": patch_files,
        "patch_error": "",
    }


def fenced_code_blocks(text: str, languages: set[str]) -> list[str]:
    pattern = re.compile(r"```([a-zA-Z0-9_-]*)\n(.*?)\n```", re.DOTALL)
    blocks: list[str] = []
    for match in pattern.finditer(text):
        language = match.group(1).strip().lower()
        if language in languages:
            blocks.append(match.group(2))
    return blocks


def patch_files_from_block(block: str) -> list[str]:
    files: list[str] = []
    for line in block.splitlines():
        if line.startswith("+++ "):
            path = normalize_patch_path(line[4:].strip())
            if path and path != "/dev/null" and path not in files:
                files.append(path)
    return files


def normalize_patch_path(path: str) -> str:
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def structured_section_report(
    assistant_message: str,
    required_sections: list[str],
) -> dict[str, Any]:
    headings = markdown_headings(assistant_message)
    required = [normalize_heading(section) for section in required_sections]
    observed = [normalize_heading(heading) for heading in headings]
    missing_sections = [
        required_sections[index]
        for index, normalized in enumerate(required)
        if normalized not in observed
    ]
    unexpected_sections = [
        headings[index]
        for index, normalized in enumerate(observed)
        if normalized not in required
    ]
    first_heading = re.search(r"^#{1,6}\s+\S.*$", assistant_message, re.MULTILINE)
    preamble = assistant_message[: first_heading.start()].strip() if first_heading else assistant_message
    return {
        "headings": headings,
        "missing_sections": missing_sections,
        "unexpected_sections": unexpected_sections,
        "has_preamble": bool(preamble.strip()),
    }


def markdown_headings(text: str) -> list[str]:
    headings: list[str] = []
    for match in re.finditer(r"^(#{1,6}\s+.+?)\s*$", text, re.MULTILINE):
        headings.append(match.group(1).strip())
    return headings


def normalize_heading(heading: str) -> str:
    text = heading.strip()
    text = re.sub(r"^#{1,6}\s+", "", text)
    text = re.sub(r"\s+#+\s*$", "", text)
    return re.sub(r"\s+", " ", text.strip()).casefold()


def looks_loop_like(text: str) -> bool:
    normalized = [line.strip() for line in text.splitlines() if line.strip()]
    if len(normalized) < 3:
        words = re.findall(r"\b[\w'-]+\b", text.lower())
        return len(words) >= 12 and len(set(words)) <= max(3, len(words) // 4)
    counts: dict[str, int] = {}
    for line in normalized:
        counts[line] = counts.get(line, 0) + 1
    return max(counts.values()) >= 3


def write_summary(config: EvalConfig, summary: dict[str, Any]) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = config.output_dir / DEFAULT_SUMMARY_JSON
    md_path = config.output_dir / DEFAULT_SUMMARY_MD
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md_path.write_text(summary_markdown(summary), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {json_path}")


def summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# SDK Same-Ticket Evaluation Summary",
        "",
        f"- evaluation_id: `{summary['evaluation_id']}`",
        f"- generated_utc: `{summary['generated_utc']}`",
        f"- ticket: `{summary['ticket']}`",
        f"- expected_marker: `{summary['expected_marker']}`",
        f"- required_sections: `{len(summary['required_sections'])}`",
        f"- require_patch: `{summary['require_patch']}`",
        f"- repeats: `{summary['repeats']}`",
        "",
        "## Classification Counts",
        "",
        "| Model | Classification | Count |",
        "| --- | --- | --- |",
    ]
    for model, counts in summary["classification_counts"].items():
        for classification, count in sorted(counts.items()):
            lines.append(f"| `{model}` | `{classification}` | {count} |")
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| Model | Repeat | Status | Blocker | Classification | Missing Sections | Patch Files | Result File |",
            "| --- | ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in summary["rows"]:
        missing = ", ".join(row.get("missing_sections", []))
        patch_files = ", ".join(row.get("patch_files", []))
        lines.append(
            "| "
            f"`{row['model']}` | "
            f"{row['repeat_index']} | "
            f"`{row['status']}` | "
            f"`{row['blocker']}` | "
            f"`{row['classification']}` | "
            f"`{missing}` | "
            f"`{patch_files}` | "
            f"`{row['result_file']}` |"
        )
    lines.extend(
        [
            "",
            "## Assistant Messages",
            "",
            "Assistant messages are summarized here for local supervisor inspection.",
            "Do not promote this section into tracked files unless sanitized.",
            "",
        ]
    )
    for row in summary["rows"]:
        message = row["assistant_message"] or "_No assistant message captured._"
        lines.extend(
            [
                f"### {row['model']} run {row['repeat_index']}",
                "",
                "```text",
                message,
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()


def main() -> int:
    args = parse_args()
    config = load_manifest(args.manifest)
    runs = planned_runs(config)
    failures = 0
    if not args.summary_only:
        failures = run_probes(config, runs, args.dry_run)
    if not args.dry_run:
        summary = summarize(config, runs)
        write_summary(config, summary)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
