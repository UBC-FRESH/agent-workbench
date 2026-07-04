"""Smoke-check Agent Workbench local command surfaces.

This helper is intentionally local and lightweight. It verifies that the
tracked script help surfaces are callable, that the SDK evaluation manifest
template is readable JSON with the expected fields, and that the repeated-run
harness can plan a dry run without contacting a model provider.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HelpCheck:
    script: str
    required_terms: tuple[str, ...]


HELP_CHECKS = (
    HelpCheck(
        "scripts/copilot_chat_bridge.py",
        ("--ticket", "--marker", "--workspace-root", "--mode"),
    ),
    HelpCheck(
        "scripts/copilot_sdk_ollama_probe.py",
        ("--model", "--base-url", "--ticket", "--output", "--wire-api"),
    ),
    HelpCheck(
        "scripts/sdk_same_ticket_eval.py",
        ("--manifest", "--dry-run", "--summary-only"),
    ),
    HelpCheck(
        "scripts/supervisor_patch_apply.py",
        ("--result-file", "--allowed-file", "--sandbox-root", "--report"),
    ),
)

REQUIRED_MANIFEST_FIELDS = {
    "evaluation_id",
    "ticket",
    "expected_marker",
    "required_sections",
    "forbidden_phrases",
    "allow_unexpected_sections",
    "allow_preamble",
    "require_patch",
    "allowed_patch_files",
    "models",
    "repeats",
    "timeout_seconds",
    "output_dir",
    "probe_script",
    "python_executable",
    "base_url_file",
    "provider_headers_file",
    "wire_api",
    "mode",
    "base_directory",
    "sdk_source",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke-check local Agent Workbench script command surfaces."
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("runtime/command_surface_smoke/p16_report.md"),
        help="Ignored Markdown report path.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_help_checks(root: Path) -> list[str]:
    lines = ["## Help Surface Checks", ""]
    for check in HELP_CHECKS:
        command = [sys.executable, check.script, "--help"]
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        output = completed.stdout + completed.stderr
        missing = [term for term in check.required_terms if term not in output]
        if completed.returncode != 0 or missing:
            raise RuntimeError(
                f"{check.script} help check failed; exit={completed.returncode}; "
                f"missing={missing}"
            )
        lines.append(f"- `{check.script}`: ok")
    lines.append("")
    return lines


def validate_manifest_template(root: Path) -> list[str]:
    template_path = root / "templates" / "sdk_eval_manifest.json"
    data = json.loads(template_path.read_text(encoding="utf-8-sig"))
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(data))
    if missing:
        raise RuntimeError(f"manifest template missing fields: {missing}")
    return [
        "## Manifest Template Check",
        "",
        "- `templates/sdk_eval_manifest.json`: ok",
        "",
    ]


def run_cli_help_check(root: Path) -> list[str]:
    checks = (
        (
            [sys.executable, "-m", "agent_workbench.cli", "decide", "task", "--help"],
            ("--input", "--output", "--json-output"),
            "agent-workbench decide task --help",
        ),
        (
            [
                sys.executable,
                "-m",
                "agent_workbench.cli",
                "accounting",
                "synthesize",
                "--help",
            ],
            ("--input", "--input-dir", "--output"),
            "agent-workbench accounting synthesize --help",
        ),
        (
            [sys.executable, "-m", "agent_workbench.cli", "policy", "tune", "--help"],
            ("--input", "--input-dir", "--output"),
            "agent-workbench policy tune --help",
        ),
        (
            [sys.executable, "-m", "agent_workbench.cli", "workflow", "render", "--help"],
            ("--input", "--output"),
            "agent-workbench workflow render --help",
        ),
    )
    for command, required_terms, label in checks:
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        output = completed.stdout + completed.stderr
        missing = [term for term in required_terms if term not in output]
        if completed.returncode != 0 or missing:
            raise RuntimeError(
                f"{label} check failed; exit={completed.returncode}; missing={missing}"
            )
    return [
        "## CLI Help Surface Checks",
        "",
        "- `agent-workbench decide task --help`: ok",
        "- `agent-workbench accounting synthesize --help`: ok",
        "- `agent-workbench policy tune --help`: ok",
        "- `agent-workbench workflow render --help`: ok",
        "",
    ]


def run_harness_dry_run(root: Path) -> list[str]:
    smoke_dir = root / "runtime" / "command_surface_smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    ticket_path = smoke_dir / "p16_smoke_ticket.md"
    manifest_path = smoke_dir / "p16_smoke_manifest.json"

    ticket_path.write_text(
        "Reply with exactly this marker and then stop:\n\nP16_COMMAND_SMOKE done\n",
        encoding="utf-8",
    )
    manifest = {
        "evaluation_id": "p16_command_surface_smoke",
        "ticket": str(ticket_path.relative_to(root)).replace("\\", "/"),
        "expected_marker": "P16_COMMAND_SMOKE done",
        "models": ["smoke-model:latest"],
        "repeats": 1,
        "timeout_seconds": 30,
        "output_dir": str((smoke_dir / "eval").relative_to(root)).replace("\\", "/"),
        "probe_script": "scripts/copilot_sdk_ollama_probe.py",
        "python_executable": sys.executable,
        "base_url": "http://127.0.0.1:11434/v1",
        "wire_api": "completions",
        "mode": "empty",
        "base_directory": str((smoke_dir / "sdk_home").relative_to(root)).replace("\\", "/"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    command = [
        sys.executable,
        "scripts/sdk_same_ticket_eval.py",
        "--manifest",
        str(manifest_path.relative_to(root)),
        "--dry-run",
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0 or "DRY-RUN" not in output:
        raise RuntimeError(
            "sdk_same_ticket_eval dry-run check failed; "
            f"exit={completed.returncode}; output={output.strip()}"
        )
    return [
        "## Harness Dry-Run Check",
        "",
        "- `scripts/sdk_same_ticket_eval.py --dry-run`: ok",
        "- model provider contact: not attempted",
        "",
    ]


def main() -> int:
    args = parse_args()
    root = repo_root()
    report_lines = [
        "# Command Surface Smoke Report",
        "",
        "This report is local runtime evidence and is not intended for commit.",
        "",
    ]
    report_lines.extend(run_help_checks(root))
    report_lines.extend(run_cli_help_check(root))
    report_lines.extend(validate_manifest_template(root))
    report_lines.extend(run_harness_dry_run(root))
    report_lines.extend(["## Result", "", "ok", ""])

    report_path = root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
