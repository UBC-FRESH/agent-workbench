"""Apply a worker patch proposal to an ignored supervisor sandbox.

This helper is intentionally narrow. It reads a Copilot SDK probe result,
extracts one fenced diff/patch block from the assistant message, verifies that
the proposed file is explicitly allowed, and writes the result under a sandbox
root supplied by the supervisor.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ApplyConfig:
    result_file: Path
    allowed_file: str
    sandbox_root: Path
    report: Path
    expect_contains: str


def parse_args() -> ApplyConfig:
    parser = argparse.ArgumentParser(
        description="Apply a proposed patch to an ignored supervisor sandbox."
    )
    parser.add_argument("--result-file", type=Path, required=True)
    parser.add_argument("--allowed-file", required=True)
    parser.add_argument("--sandbox-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expect-contains", default="")
    args = parser.parse_args()
    return ApplyConfig(
        result_file=args.result_file,
        allowed_file=args.allowed_file,
        sandbox_root=args.sandbox_root,
        report=args.report,
        expect_contains=args.expect_contains,
    )


def assistant_section(text: str) -> str:
    marker = "## Assistant Messages"
    next_marker = "\n## Raw Event Records"
    start = text.find(marker)
    if start == -1:
        return text
    start += len(marker)
    end = text.find(next_marker, start)
    if end == -1:
        end = len(text)
    return text[start:end].strip()


def fenced_diff_blocks(text: str) -> list[str]:
    pattern = re.compile(r"```(?:diff|patch)\n(.*?)\n```", re.DOTALL)
    return [match.group(1) for match in pattern.finditer(text)]


def patch_target(block: str) -> str:
    for line in block.splitlines():
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path.startswith("b/") or path.startswith("a/"):
                path = path[2:]
            return path
    return ""


def added_lines(block: str) -> list[str]:
    additions: list[str] = []
    for line in block.splitlines():
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            additions.append(line[1:])
    return additions


def apply_add_only_patch(config: ApplyConfig) -> dict[str, str]:
    text = config.result_file.read_text(encoding="utf-8-sig")
    assistant = assistant_section(text)
    blocks = fenced_diff_blocks(assistant)
    if not blocks:
        return {"status": "blocked", "classification": "missing-patch", "error": "no fenced diff block"}
    if len(blocks) != 1:
        return {"status": "blocked", "classification": "ambiguous-patch", "error": "multiple diff blocks"}

    block = blocks[0]
    target = patch_target(block)
    if target != config.allowed_file:
        return {
            "status": "blocked",
            "classification": "wrong-file",
            "error": f"expected {config.allowed_file}, observed {target}",
        }

    additions = added_lines(block)
    if not additions:
        return {"status": "blocked", "classification": "malformed-patch", "error": "no added lines"}

    output_path = config.sandbox_root / config.allowed_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    existing = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
    prefix = existing.rstrip("\n")
    new_text = "\n".join(part for part in [prefix, *additions] if part) + "\n"
    output_path.write_text(new_text, encoding="utf-8")

    if config.expect_contains and config.expect_contains not in new_text:
        return {
            "status": "blocked",
            "classification": "check-failed",
            "error": "expected text not found after apply",
        }
    return {
        "status": "completed",
        "classification": "applied-in-sandbox",
        "error": "",
        "target": str(output_path),
    }


def write_report(config: ApplyConfig, result: dict[str, str]) -> None:
    config.report.parent.mkdir(parents=True, exist_ok=True)
    body = [
        "# Supervisor Patch Apply Report",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- status: `{result.get('status', '')}`",
        f"- classification: `{result.get('classification', '')}`",
        f"- error: `{result.get('error', '')}`",
        f"- result_file: `{config.result_file}`",
        f"- allowed_file: `{config.allowed_file}`",
        f"- sandbox_root: `<ignored-supervisor-sandbox>`",
        f"- target: `{result.get('target', '')}`",
        "",
    ]
    config.report.write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    config = parse_args()
    result = apply_add_only_patch(config)
    write_report(config, result)
    print(f"wrote {config.report}")
    return 0 if result.get("status") == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
