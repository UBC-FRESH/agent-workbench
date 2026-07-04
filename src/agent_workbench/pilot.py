"""Real-project pilot scaffold helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class PilotScaffoldConfig:
    project_root: Path
    task_id: str
    title: str
    mode: str
    model: str
    output_dir: Path
    marker: str
    repeats: int
    timeout_seconds: int
    base_url_file: str
    provider_headers_file: str
    force: bool


@dataclass(frozen=True)
class PilotScaffoldResult:
    ticket_path: Path
    manifest_path: Path
    evidence_path: Path


@dataclass(frozen=True)
class PilotPackTask:
    task_id: str
    title: str


@dataclass(frozen=True)
class PilotPackScaffoldConfig:
    project_root: Path
    tasks: tuple[PilotPackTask, ...]
    mode: str
    model: str
    output_dir: Path
    repeats: int
    timeout_seconds: int
    base_url_file: str
    provider_headers_file: str
    force: bool


@dataclass(frozen=True)
class PilotPackScaffoldResult:
    results: tuple[PilotScaffoldResult, ...]


def scaffold_pilot(config: PilotScaffoldConfig) -> PilotScaffoldResult:
    project_root = config.project_root.resolve()
    output_dir = resolve_output_dir(project_root, config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = safe_slug(config.task_id)
    ticket_path = output_dir / f"{stem}.ticket.md"
    manifest_path = output_dir / f"{stem}.manifest.json"
    evidence_path = output_dir / f"{stem}.evidence.json"

    for path in (ticket_path, manifest_path, evidence_path):
        if path.exists() and not config.force:
            raise FileExistsError(f"refusing to overwrite existing file: {path}")

    ticket_path.write_text(render_ticket(config), encoding="utf-8")
    manifest_path.write_text(
        json.dumps(render_manifest(config, project_root, output_dir, ticket_path), indent=2) + "\n",
        encoding="utf-8",
    )
    evidence_path.write_text(
        json.dumps(render_evidence(config, project_root, output_dir, manifest_path), indent=2) + "\n",
        encoding="utf-8",
    )

    return PilotScaffoldResult(
        ticket_path=ticket_path,
        manifest_path=manifest_path,
        evidence_path=evidence_path,
    )


def scaffold_pilot_pack(config: PilotPackScaffoldConfig) -> PilotPackScaffoldResult:
    if not config.tasks:
        raise ValueError("pack scaffold requires at least one task")
    results: list[PilotScaffoldResult] = []
    for task in config.tasks:
        marker = f"{task.task_id.upper().replace('-', '_')} done"
        results.append(
            scaffold_pilot(
                PilotScaffoldConfig(
                    project_root=config.project_root,
                    task_id=task.task_id,
                    title=task.title,
                    mode=config.mode,
                    model=config.model,
                    output_dir=config.output_dir,
                    marker=marker,
                    repeats=config.repeats,
                    timeout_seconds=config.timeout_seconds,
                    base_url_file=config.base_url_file,
                    provider_headers_file=config.provider_headers_file,
                    force=config.force,
                )
            )
        )
    return PilotPackScaffoldResult(results=tuple(results))


def resolve_output_dir(project_root: Path, output_dir: Path) -> Path:
    if output_dir.is_absolute():
        return output_dir
    return project_root / output_dir


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-._")
    if not slug:
        raise ValueError("task id must contain at least one safe filename character")
    return slug.lower()


def render_ticket(config: PilotScaffoldConfig) -> str:
    if config.mode == "marker":
        task_text = (
            "Reply with exactly the marker line requested below. Do not inspect "
            "the repository or propose changes."
        )
        expected = config.marker
        final_response = f"""Reply with exactly:

```text
{config.marker}
```"""
    elif config.mode == "proposal":
        task_text = (
            "Produce a proposal-only Markdown response for the supervisor. Do not "
            "edit files, run commands, or claim that changes were applied."
        )
        expected = "A bounded proposal with rationale, proposed next step, and verification notes."
        final_response = """Return only these sections:

```text
## Rationale

## Proposal

## Verification
```"""
    else:
        raise ValueError(f"unsupported pilot mode: {config.mode}")

    return f"""# Agent Workbench Pilot Ticket

## Task ID

`{config.task_id}`

## Title

{config.title}

## Mode

`{config.mode}`

## Boundary

- Worker authority: no tools, no commands, no file edits.
- GitHub mutation: forbidden.
- Tracked-file mutation: forbidden.
- Supervisor must verify any output before using it.

## Task

{task_text}

## Expected Output

{expected}

## Final Response Requirement

{final_response}
"""


def render_manifest(
    config: PilotScaffoldConfig,
    project_root: Path,
    output_dir: Path,
    ticket_path: Path,
) -> dict[str, object]:
    stem = safe_slug(config.task_id)
    return {
        "evaluation_id": safe_slug(config.task_id),
        "ticket": relpath(ticket_path, project_root),
        "expected_marker": config.marker if config.mode == "marker" else "",
        "required_sections": []
        if config.mode == "marker"
        else ["## Rationale", "## Proposal", "## Verification"],
        "forbidden_phrases": ["I cannot", "I can't", "would have", "applied", "edited"],
        "allow_unexpected_sections": False,
        "allow_preamble": False,
        "models": [config.model],
        "repeats": config.repeats,
        "timeout_seconds": config.timeout_seconds,
        "output_dir": relpath(output_dir / "eval" / stem, project_root),
        "probe_script": "scripts/copilot_sdk_ollama_probe.py",
        "python_executable": ".venv/Scripts/python.exe",
        "base_url_file": config.base_url_file,
        "provider_headers_file": config.provider_headers_file,
        "wire_api": "completions",
        "mode": "empty",
        "base_directory": relpath(output_dir / stem / "copilot_sdk_home", project_root),
    }


def render_evidence(
    config: PilotScaffoldConfig,
    project_root: Path,
    output_dir: Path,
    manifest_path: Path,
) -> dict[str, object]:
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "phase": "pilot",
        "task": config.task_id,
        "evidence_id": safe_slug(config.task_id),
        "evidence_type": "planning-audit",
        "generated_utc": generated,
        "source_runtime_paths": [
            relpath(manifest_path, project_root),
            relpath(
                output_dir / "eval" / safe_slug(config.task_id) / "summary.json",
                project_root,
            ),
        ],
        "ticket_family": f"{config.mode} pilot",
        "models_or_agent_host": [config.model],
        "bridge_or_harness": "agent-workbench eval",
        "allowed_authority": ["no-tool assistant response", "ignored runtime output"],
        "forbidden_authority": [
            "tools",
            "commands",
            "file edits",
            "github mutation",
            "tracked-file mutation",
        ],
        "outcomes": [],
        "verification": {
            "commands_run": [],
            "checks_passed": [],
            "blockers": [],
        },
        "promotion_boundary": {
            "raw_evidence_retained_under": relpath(output_dir, project_root) + "/",
            "tracked_files_updated": [],
            "private_values_excluded": True,
        },
        "supervisor_decision": {
            "decision": "defer",
            "rationale": "Scaffold created; populate after running and reviewing the pilot.",
        },
    }


def relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
