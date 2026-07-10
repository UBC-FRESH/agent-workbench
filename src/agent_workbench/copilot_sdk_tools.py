"""Agent Workbench custom tools for Copilot SDK sessions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .evidence import find_private_values


AGENT_WORKBENCH_TOOL_NAMES = (
    "agent_workbench_run_context",
    "agent_workbench_result_contract",
    "agent_workbench_review_subject",
    "agent_workbench_write_result",
    "agent_workbench_validate_result",
)

ALLOWED_FINAL_STATUSES = (
    "accepted-candidate",
    "rejected-candidate",
    "blocked",
    "needs-supervisor-review",
)


def validate_agent_workbench_tool_names(
    names: tuple[str, ...] | list[str],
) -> list[str]:
    allowed = set(AGENT_WORKBENCH_TOOL_NAMES)
    return [name for name in names if name not in allowed]


def build_agent_workbench_sdk_tools(
    names: tuple[str, ...] | list[str],
    *,
    manifest: dict[str, Any],
    manifest_path: Path | None = None,
) -> list[Any]:
    unknown = validate_agent_workbench_tool_names(names)
    if unknown:
        raise ValueError(f"unknown Agent Workbench SDK tool(s): {', '.join(unknown)}")
    if not names:
        return []

    from copilot import define_tool
    from pydantic import BaseModel, Field

    base = manifest_path.parent if manifest_path is not None else Path.cwd()

    class ValidateResultParams(BaseModel):
        path: str = Field(description="Result or blocker path to validate.")

    class WriteResultParams(BaseModel):
        path: str = Field(description="Manifest result or blocker path to write.")
        content: str = Field(description="Markdown result or blocker content.")

    tool_by_name: dict[str, Any] = {
        "agent_workbench_run_context": define_tool(
            name="agent_workbench_run_context",
            description="Return public-safe Agent Workbench run context.",
            params_type=None,
            handler=lambda _params, _invocation: json.dumps(
                run_context_payload(manifest), sort_keys=True
            ),
        ),
        "agent_workbench_result_contract": define_tool(
            name="agent_workbench_result_contract",
            description="Return the required result and blocker contract for this run.",
            params_type=None,
            handler=lambda _params, _invocation: json.dumps(
                result_contract_payload(manifest), sort_keys=True
            ),
        ),
        "agent_workbench_review_subject": define_tool(
            name="agent_workbench_review_subject",
            description=(
                "Resolve and read the declared profile-evidence-review subject. "
                "Use this instead of searching the filesystem."
            ),
            params_type=None,
            handler=lambda _params, _invocation: json.dumps(
                review_subject_payload(manifest, base=base), sort_keys=True
            ),
        ),
        "agent_workbench_write_result": define_tool(
            name="agent_workbench_write_result",
            description=(
                "Write the manifest result or blocker file. Only declared result "
                "and blocker paths are allowed."
            ),
            params_type=WriteResultParams,
            handler=lambda params, _invocation: json.dumps(
                write_result_payload(
                    manifest,
                    base=base,
                    requested_path=params.path,
                    content=params.content,
                ),
                sort_keys=True,
            ),
        ),
        "agent_workbench_validate_result": define_tool(
            name="agent_workbench_validate_result",
            description="Validate a result or blocker file against the manifest contract.",
            params_type=ValidateResultParams,
            handler=lambda params, _invocation: json.dumps(
                validate_result_payload(
                    manifest,
                    base=base,
                    requested_path=params.path,
                ),
                sort_keys=True,
            ),
        ),
    }
    return [tool_by_name[name] for name in names]


def run_context_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    paths = manifest.get("paths", {})
    control = manifest.get("control", {})
    public_paths = {
        key: value
        for key, value in paths.items()
        if isinstance(key, str) and isinstance(value, str) and value
    }
    return {
        "run_id": manifest.get("run_id", ""),
        "phase": manifest.get("phase", ""),
        "governing_issue": manifest.get("governing_issue", ""),
        "child_issue": manifest.get("child_issue", ""),
        "target_project": manifest.get("target_project", ""),
        "target_task": manifest.get("target_task", ""),
        "workspace_root": manifest.get("workspace_root", ""),
        "stop_condition": control.get("stop_condition", ""),
        "allowed_paths": {
            "ticket": paths.get("ticket", ""),
            "result": paths.get("result", ""),
            "blocker": paths.get("blocker", ""),
            "heartbeat": paths.get("heartbeat", ""),
            "review_subject": manifest_review_subject_path(manifest),
        },
        "artifact_paths": public_paths,
        "review_subject": review_subject_reference_payload(manifest),
    }


def result_contract_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    paths = manifest.get("paths", {})
    return {
        "result_path": paths.get("result", ""),
        "blocker_path": paths.get("blocker", ""),
        "review_subject": review_subject_reference_payload(manifest),
        "review_subject_tool": "agent_workbench_review_subject",
        "write_tool": "agent_workbench_write_result",
        "validate_tool": "agent_workbench_validate_result",
        "required_final_statuses": list(ALLOWED_FINAL_STATUSES),
        "required_result_sections": [
            "Final status",
            "Summary",
            "Files changed",
            "Validation",
            "Risks or follow-up",
        ],
        "required_blocker_sections": [
            "Final status",
            "Blocker",
            "Evidence",
            "Next required action",
        ],
    }


def review_subject_reference_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "declared_path": manifest_review_subject_path(manifest),
        "kind": manifest_review_subject_kind(manifest),
        "read_tool": "agent_workbench_review_subject",
    }


def review_subject_payload(
    manifest: dict[str, Any],
    *,
    base: Path,
    max_chars: int = 12000,
) -> dict[str, Any]:
    declared_path = manifest_review_subject_path(manifest)
    kind = manifest_review_subject_kind(manifest)
    errors: list[str] = []
    if not declared_path:
        errors.append("review subject path is missing")
        return review_subject_error_payload(declared_path, kind, errors)
    private_findings = find_private_values({"review_subject_path": declared_path})
    if private_findings:
        errors.append("review subject path is private-looking")
    candidate = resolve_manifest_path(declared_path, base=base)
    root = allowed_review_subject_root(manifest, base=base)
    if root is not None and not is_relative_to(candidate, root):
        errors.append("review subject is outside allowed root")
    if is_current_run_output(manifest, candidate, base=base):
        errors.append("review subject points at current-run output")
    if not candidate.exists():
        errors.append("review subject does not exist")
    if not candidate.is_file():
        errors.append("review subject is not a file")
    if errors:
        return {
            **review_subject_error_payload(declared_path, kind, errors),
            "resolved_path": public_path(candidate, base=base),
            "allowed_root": public_path(root, base=base) if root else "",
        }
    text = candidate.read_text(encoding="utf-8-sig")
    content = text[:max_chars]
    truncated = len(text) > max_chars
    content_findings = find_private_values({"content": content})
    if content_findings:
        return {
            **review_subject_error_payload(
                declared_path,
                kind,
                ["review subject content contains private-looking values"],
            ),
            "resolved_path": public_path(candidate, base=base),
            "allowed_root": public_path(root, base=base) if root else "",
        }
    return {
        "ok": True,
        "declared_path": declared_path,
        "resolved_path": public_path(candidate, base=base),
        "allowed_root": public_path(root, base=base) if root else "",
        "kind": kind,
        "size_chars": len(text),
        "content_chars": len(content),
        "truncated": truncated,
        "content": content,
        "errors": [],
    }


def review_subject_error_payload(
    declared_path: str,
    kind: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "ok": False,
        "declared_path": declared_path,
        "resolved_path": "",
        "allowed_root": "",
        "kind": kind,
        "size_chars": 0,
        "content_chars": 0,
        "truncated": False,
        "content": "",
        "errors": errors,
    }


def manifest_review_subject_path(manifest: dict[str, Any]) -> str:
    profile_review = manifest.get("profile_evidence_review", {})
    if isinstance(profile_review, dict):
        value = profile_review.get("review_subject_path")
        if isinstance(value, str) and value.strip():
            return value.strip()
    paths = manifest.get("paths", {})
    if isinstance(paths, dict):
        value = paths.get("review_subject")
        if isinstance(value, str) and value.strip():
            return value.strip()
    experiment = manifest.get("experiment", {})
    if isinstance(experiment, dict):
        value = experiment.get("review_subject_path")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def manifest_review_subject_kind(manifest: dict[str, Any]) -> str:
    profile_review = manifest.get("profile_evidence_review", {})
    if isinstance(profile_review, dict):
        value = profile_review.get("review_subject_kind")
        if isinstance(value, str) and value.strip():
            return value.strip()
    experiment = manifest.get("experiment", {})
    if isinstance(experiment, dict):
        value = experiment.get("review_subject_kind")
        if isinstance(value, str) and value.strip():
            return value.strip()
    path = manifest_review_subject_path(manifest).lower()
    if "profile_summaries" in path or "profile-summary" in path:
        return "profile-run-summary"
    if "compact" in path or "transcript" in path:
        return "compact-transcript"
    return "public-safe-artifact" if path else ""


def write_result_payload(
    manifest: dict[str, Any],
    *,
    base: Path,
    requested_path: str,
    content: str,
) -> dict[str, Any]:
    allowed = allowed_result_paths(manifest, base=base)
    candidate = resolve_result_path(requested_path, base=base)
    errors: list[str] = []
    if candidate not in allowed:
        errors.append("path is not the manifest result or blocker path")
    if len(content) > 100_000:
        errors.append("content exceeds 100000 characters")
    if "Final status:" not in content:
        errors.append("missing 'Final status:' line")
    if not any(status in content for status in ALLOWED_FINAL_STATUSES):
        errors.append("missing allowed final status value")
    for finding in find_private_values({"content": content}):
        errors.append(f"private-looking value detected: {finding}")
    if errors:
        return {
            "ok": False,
            "path": str(candidate),
            "errors": errors,
        }

    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(content.rstrip() + "\n", encoding="utf-8")
    return validate_result_payload(
        manifest,
        base=base,
        requested_path=requested_path,
    )


def validate_result_payload(
    manifest: dict[str, Any],
    *,
    base: Path,
    requested_path: str,
) -> dict[str, Any]:
    allowed = allowed_result_paths(manifest, base=base)
    candidate = resolve_result_path(requested_path, base=base)
    errors: list[str] = []
    if candidate not in allowed:
        errors.append("path is not the manifest result or blocker path")
    if not candidate.exists():
        errors.append("path does not exist")
        text = ""
    else:
        text = candidate.read_text(encoding="utf-8-sig")
    if text and "Final status:" not in text:
        errors.append("missing 'Final status:' line")
    if text and not any(status in text for status in ALLOWED_FINAL_STATUSES):
        errors.append("missing allowed final status value")
    return {
        "ok": not errors,
        "path": str(candidate),
        "errors": errors,
    }


def allowed_result_paths(manifest: dict[str, Any], *, base: Path) -> set[Path]:
    paths = manifest.get("paths", {})
    allowed: set[Path] = set()
    for key in ("result", "blocker"):
        value = paths.get(key)
        if isinstance(value, str) and value:
            allowed.add(resolve_result_path(value, base=base))
    return allowed


def resolve_result_path(path: str, *, base: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()


def resolve_manifest_path(path: str, *, base: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()


def allowed_review_subject_root(manifest: dict[str, Any], *, base: Path) -> Path | None:
    declared_path = manifest_review_subject_path(manifest)
    if not declared_path:
        return None
    candidate = Path(declared_path)
    if candidate.is_absolute():
        return None
    base_resolved = base.resolve()
    for ancestor in (base_resolved, *base_resolved.parents):
        if ancestor.name == "runtime":
            return ancestor
    first_part = candidate.parts[0] if candidate.parts else ""
    if first_part == "..":
        parts = list(candidate.parts)
        prefix: list[str] = []
        for part in parts:
            if part == "..":
                prefix.append(part)
                continue
            break
        return (base / Path(*prefix)).resolve()
    return base.resolve()


def is_current_run_output(
    manifest: dict[str, Any], candidate: Path, *, base: Path
) -> bool:
    paths = manifest.get("paths", {})
    if not isinstance(paths, dict):
        return False
    for key in (
        "result",
        "blocker",
        "heartbeat",
        "event_log",
        "status_summary",
        "nudge_log",
    ):
        value = paths.get(key)
        if isinstance(value, str) and value:
            if candidate == resolve_manifest_path(value, base=base):
                return True
    return False


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def public_path(path: Path | None, *, base: Path) -> str:
    if path is None:
        return ""
    try:
        return path.relative_to(base.resolve()).as_posix()
    except ValueError:
        pass
    cwd = Path.cwd().resolve()
    try:
        return path.relative_to(cwd).as_posix()
    except ValueError:
        return path.name
