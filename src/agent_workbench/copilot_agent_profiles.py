"""Resolve VS Code-style Copilot custom agent profiles for SDK sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


SUPPORTED_PROFILE_FIELDS = {
    "name",
    "display_name",
    "displayName",
    "description",
    "model",
    "tools",
    "infer",
    "skills",
}
SDK_PROFILE_FIELDS = {
    "name",
    "display_name",
    "description",
    "model",
    "tools",
    "prompt",
    "infer",
    "skills",
}
SUPPORTED_DEFAULT_AGENT_FIELDS = {"excluded_tools"}
KNOWN_BUILTIN_PROFILE_TOOLS = {
    "agent",
    "read",
    "search",
    "edit",
    "runCommands",
    "run_commands",
    "terminal",
    "shell",
}
AGENT_WORKBENCH_PROFILE_TOOLS = {
    "agent_workbench_run_context",
    "agent_workbench_result_contract",
    "agent_workbench_review_subject",
    "agent_workbench_write_result",
    "agent_workbench_validate_result",
}
AGENT_PROFILES_BLOCK = "agent_profiles"
TASK_OVERLAY_HEADING = "## Agent Workbench Task Overlay"
STANDARD_TASK_OVERLAY_DIR = Path(".github/agents/overlays")
STANDARD_TASK_OVERLAYS = {
    "repair-list-execution": STANDARD_TASK_OVERLAY_DIR / "repair-list-execution.md",
    "new-python-module-implementation": (
        STANDARD_TASK_OVERLAY_DIR / "new-python-module-implementation.md"
    ),
    "existing-code-debugging": STANDARD_TASK_OVERLAY_DIR / "existing-code-debugging.md",
    "systematic-refactor-sweep": STANDARD_TASK_OVERLAY_DIR
    / "systematic-refactor-sweep.md",
    "documentation-expansion": STANDARD_TASK_OVERLAY_DIR / "documentation-expansion.md",
    "notebook-example-authoring": STANDARD_TASK_OVERLAY_DIR
    / "notebook-example-authoring.md",
    "release-readiness-review": STANDARD_TASK_OVERLAY_DIR
    / "release-readiness-review.md",
}
STANDARD_AGENT_PROFILE_DIR = Path(".github/agents")
STANDARD_AGENT_PROFILES = {
    "agent-workbench-local-supervisor": (
        STANDARD_AGENT_PROFILE_DIR / "agent-workbench-local-supervisor.agent.md"
    ),
    "agent-workbench-result-auditor": (
        STANDARD_AGENT_PROFILE_DIR / "agent-workbench-result-auditor.agent.md"
    ),
    "qwen3-coder-strict-worker": (
        STANDARD_AGENT_PROFILE_DIR / "qwen3-coder-strict-worker.agent.md"
    ),
    "qwen3-coder-next-strict-worker": (
        STANDARD_AGENT_PROFILE_DIR / "qwen3-coder-next-strict-worker.agent.md"
    ),
}


@dataclass(frozen=True)
class AgentProfileDocument:
    source_path: Path
    frontmatter: dict[str, Any]
    prompt: str
    unsupported_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResolvedAgentProfiles:
    custom_agents: list[dict[str, Any]] = field(default_factory=list)
    selected_agent: str = ""
    default_agent: dict[str, Any] | None = None
    custom_agents_local_only: bool = True
    include_sub_agent_streaming_events: bool = True
    custom_tool_names: tuple[str, ...] = ()
    task_overlay_names: tuple[str, ...] = ()
    task_overlay_paths: tuple[Path, ...] = ()
    source_paths: tuple[Path, ...] = ()
    unsupported_fields: dict[str, tuple[str, ...]] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def has_profile_block(self) -> bool:
        return bool(
            self.custom_agents
            or self.selected_agent
            or self.default_agent
            or self.custom_tool_names
            or self.task_overlay_names
            or self.task_overlay_paths
            or self.source_paths
        )


def resolve_agent_profiles(
    manifest: dict[str, Any],
    *,
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> ResolvedAgentProfiles:
    """Resolve the optional sdk.agent_profiles manifest block."""

    manifest_path = manifest_path or manifest_private_path(manifest)
    sdk = manifest.get("sdk")
    if not isinstance(sdk, dict):
        return ResolvedAgentProfiles()
    block = sdk.get(AGENT_PROFILES_BLOCK)
    if block is None:
        return ResolvedAgentProfiles()
    if not isinstance(block, dict):
        return ResolvedAgentProfiles(errors=("sdk.agent_profiles must be an object",))

    base = manifest_path.parent if manifest_path is not None else Path.cwd()
    root = repo_root or find_repo_root(base)
    warnings: list[str] = []
    errors: list[str] = []
    source_paths: list[Path] = []
    documents: list[AgentProfileDocument] = []
    unsupported_by_agent: dict[str, tuple[str, ...]] = {}

    raw_source_paths = block.get("source_paths", [])
    if not isinstance(raw_source_paths, list):
        errors.append("sdk.agent_profiles.source_paths must be a list")
        raw_source_paths = []

    for index, raw_path in enumerate(raw_source_paths, 1):
        if not isinstance(raw_path, str) or not raw_path.strip():
            errors.append(f"sdk.agent_profiles.source_paths[{index}] must be a string")
            continue
        source_path = resolve_source_path(raw_path, base=base, repo_root=root)
        source_paths.append(source_path)
        if not source_path.exists():
            errors.append(f"profile source does not exist: {raw_path}")
            continue
        try:
            document = load_agent_profile_document(source_path)
        except ValueError as exc:
            errors.append(f"{raw_path}: {exc}")
            continue
        documents.append(document)
        name = str(document.frontmatter.get("name", "")).strip()
        if document.unsupported_fields:
            unsupported_by_agent[name or str(source_path)] = document.unsupported_fields
            warnings.append(
                "{path}: unsupported profile fields retained for validation only: {fields}".format(
                    path=raw_path,
                    fields=", ".join(document.unsupported_fields),
                )
            )

    custom_agents: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for document in documents:
        agent = agent_config_from_document(document)
        name = str(agent.get("name", "")).strip()
        if not name:
            errors.append(f"{document.source_path}: profile frontmatter missing name")
            continue
        if name in seen_names:
            errors.append(f"duplicate custom agent name: {name}")
            continue
        if not str(agent.get("prompt", "")).strip():
            errors.append(f"{document.source_path}: profile body prompt is empty")
            continue
        seen_names.add(name)
        custom_agents.append(agent)

    selected_agent = selected_agent_name(block)
    if selected_agent and selected_agent not in seen_names:
        errors.append(
            f"sdk.agent_profiles.selected does not match a loaded agent: {selected_agent}"
        )

    task_overlay = load_task_overlay(block, base=base, repo_root=root, errors=errors)
    custom_agents = apply_task_overlay(
        custom_agents,
        selected_agent=selected_agent,
        overlay_text=task_overlay.text,
    )

    default_agent = resolve_default_agent(block, errors=errors, warnings=warnings)
    custom_tool_names = resolve_custom_tool_names(block, errors=errors)
    custom_agents = attach_custom_tools_to_selected_agent(
        custom_agents,
        selected_agent=selected_agent,
        custom_tool_names=custom_tool_names,
    )
    validate_profile_tool_coverage(
        custom_agents,
        custom_tool_names=custom_tool_names,
        errors=errors,
    )
    local_only = bool(block.get("custom_agents_local_only", True))
    include_subagents = bool(block.get("include_sub_agent_streaming_events", True))
    return ResolvedAgentProfiles(
        custom_agents=custom_agents,
        selected_agent=selected_agent,
        default_agent=default_agent,
        custom_agents_local_only=local_only,
        include_sub_agent_streaming_events=include_subagents,
        custom_tool_names=tuple(custom_tool_names),
        task_overlay_names=tuple(task_overlay.names),
        task_overlay_paths=tuple(task_overlay.paths),
        source_paths=tuple(source_paths),
        unsupported_fields=unsupported_by_agent,
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


@dataclass(frozen=True)
class TaskOverlayResolution:
    text: str = ""
    names: tuple[str, ...] = ()
    paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class ProfileCatalogEntry:
    name: str
    path: Path
    exists: bool
    model: str = ""
    tools: tuple[str, ...] = ()
    unsupported_fields: tuple[str, ...] = ()
    prompt_chars: int = 0
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProfileCatalogValidation:
    profiles: tuple[ProfileCatalogEntry, ...] = ()
    overlays: tuple[tuple[str, Path, bool], ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def load_agent_profile_document(path: Path) -> AgentProfileDocument:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        raise ValueError("profile must start with YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("profile frontmatter must be closed with ---")
    _, raw_frontmatter, prompt = parts
    frontmatter = yaml.safe_load(raw_frontmatter) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError("profile frontmatter must parse to an object")
    unsupported = tuple(
        sorted(
            str(field) for field in frontmatter if field not in SUPPORTED_PROFILE_FIELDS
        )
    )
    return AgentProfileDocument(
        source_path=path,
        frontmatter=frontmatter,
        prompt=prompt.strip(),
        unsupported_fields=unsupported,
    )


def validate_standard_profile_catalog(
    *,
    repo_root: Path | None = None,
) -> ProfileCatalogValidation:
    root = repo_root or find_repo_root(Path.cwd())
    warnings: list[str] = []
    errors: list[str] = []
    entries: list[ProfileCatalogEntry] = []
    for name, relative_path in STANDARD_AGENT_PROFILES.items():
        path = root / relative_path
        if not path.exists():
            message = f"standard profile missing: {name} ({relative_path})"
            errors.append(message)
            entries.append(
                ProfileCatalogEntry(
                    name=name,
                    path=path,
                    exists=False,
                    errors=(message,),
                )
            )
            continue
        try:
            document = load_agent_profile_document(path)
        except ValueError as exc:
            message = f"{relative_path}: {exc}"
            errors.append(message)
            entries.append(
                ProfileCatalogEntry(
                    name=name,
                    path=path,
                    exists=True,
                    errors=(message,),
                )
            )
            continue
        agent = agent_config_from_document(document)
        entry_errors: list[str] = []
        actual_name = str(agent.get("name", "")).strip()
        if actual_name != name:
            entry_errors.append(
                f"{relative_path}: expected name {name}, found {actual_name or '(empty)'}"
            )
        prompt = str(agent.get("prompt", "")).strip()
        if not prompt:
            entry_errors.append(f"{relative_path}: profile body prompt is empty")
        raw_tools = agent.get("tools", [])
        tools = (
            tuple(str(tool).strip() for tool in raw_tools)
            if isinstance(raw_tools, list)
            else ()
        )
        validate_profile_tool_coverage(
            [agent],
            custom_tool_names=list(AGENT_WORKBENCH_PROFILE_TOOLS),
            errors=entry_errors,
        )
        if not isinstance(raw_tools, list):
            entry_errors.append(f"{relative_path}: tools must be a list")
        if document.unsupported_fields:
            warnings.append(
                "{path}: unsupported profile fields retained for validation only: {fields}".format(
                    path=relative_path,
                    fields=", ".join(document.unsupported_fields),
                )
            )
        errors.extend(entry_errors)
        entries.append(
            ProfileCatalogEntry(
                name=name,
                path=path,
                exists=True,
                model=str(agent.get("model", "")),
                tools=tools,
                unsupported_fields=document.unsupported_fields,
                prompt_chars=len(prompt),
                errors=tuple(entry_errors),
            )
        )
    overlays: list[tuple[str, Path, bool]] = []
    for name, relative_path in STANDARD_TASK_OVERLAYS.items():
        path = root / relative_path
        exists = path.exists()
        overlays.append((name, path, exists))
        if not exists:
            errors.append(f"standard task overlay missing: {name} ({relative_path})")
    return ProfileCatalogValidation(
        profiles=tuple(entries),
        overlays=tuple(overlays),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def agent_config_from_document(document: AgentProfileDocument) -> dict[str, Any]:
    source = dict(document.frontmatter)
    config: dict[str, Any] = {}
    if source.get("displayName") and not source.get("display_name"):
        source["display_name"] = source["displayName"]
    for field_name in SDK_PROFILE_FIELDS:
        if field_name == "prompt":
            continue
        if field_name in source:
            config[field_name] = source[field_name]
    config["prompt"] = document.prompt
    return config


def selected_agent_name(block: dict[str, Any]) -> str:
    value = block.get("selected", "")
    return str(value).strip() if value is not None else ""


def resolve_default_agent(
    block: dict[str, Any],
    *,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any] | None:
    raw = block.get("default_agent")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        errors.append("sdk.agent_profiles.default_agent must be an object")
        return None
    default_agent: dict[str, Any] = {}
    for field_name, value in raw.items():
        if field_name in SUPPORTED_DEFAULT_AGENT_FIELDS:
            default_agent[field_name] = value
        else:
            warnings.append(
                f"sdk.agent_profiles.default_agent.{field_name} is not passed to the SDK"
            )
    return default_agent


def attach_custom_tools_to_selected_agent(
    custom_agents: list[dict[str, Any]],
    *,
    selected_agent: str,
    custom_tool_names: list[str],
) -> list[dict[str, Any]]:
    if not custom_tool_names:
        return custom_agents
    target = selected_agent
    if not target and len(custom_agents) == 1:
        target = str(custom_agents[0].get("name", ""))
    updated_agents: list[dict[str, Any]] = []
    for agent in custom_agents:
        if str(agent.get("name", "")) != target:
            updated_agents.append(agent)
            continue
        updated = dict(agent)
        tools = updated.get("tools", [])
        merged = list(tools) if isinstance(tools, list) else []
        for tool_name in custom_tool_names:
            if tool_name not in merged:
                merged.append(tool_name)
        updated["tools"] = merged
        updated_agents.append(updated)
    return updated_agents


def resolve_custom_tool_names(block: dict[str, Any], *, errors: list[str]) -> list[str]:
    raw = block.get("custom_tools", [])
    if raw in (None, ""):
        return []
    if not isinstance(raw, list):
        errors.append("sdk.agent_profiles.custom_tools must be a list")
        return []
    names: list[str] = []
    for index, value in enumerate(raw, 1):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"sdk.agent_profiles.custom_tools[{index}] must be a string")
            continue
        names.append(value.strip())
    return names


def validate_profile_tool_coverage(
    custom_agents: list[dict[str, Any]],
    *,
    custom_tool_names: list[str],
    errors: list[str],
) -> None:
    custom_tool_set = set(custom_tool_names)
    for agent in custom_agents:
        name = str(agent.get("name", ""))
        tools = agent.get("tools", [])
        if tools in (None, ""):
            continue
        if not isinstance(tools, list):
            errors.append(f"profile {name} tools must be a list")
            continue
        for raw_tool in tools:
            tool_name = str(raw_tool).strip()
            if tool_name in KNOWN_BUILTIN_PROFILE_TOOLS:
                continue
            if tool_name in AGENT_WORKBENCH_PROFILE_TOOLS:
                if tool_name not in custom_tool_set:
                    errors.append(
                        f"profile {name} references unregistered custom tool: {tool_name}"
                    )
                continue
            errors.append(f"profile {name} references unknown tool: {tool_name}")


def apply_task_overlay(
    custom_agents: list[dict[str, Any]],
    *,
    selected_agent: str,
    overlay_text: str,
) -> list[dict[str, Any]]:
    if not overlay_text.strip():
        return custom_agents
    if not selected_agent and len(custom_agents) == 1:
        selected_agent = str(custom_agents[0].get("name", ""))
    resolved: list[dict[str, Any]] = []
    for agent in custom_agents:
        if str(agent.get("name", "")) != selected_agent:
            resolved.append(agent)
            continue
        updated = dict(agent)
        prompt = str(updated.get("prompt", "")).rstrip()
        updated["prompt"] = (
            f"{prompt}\n\n{TASK_OVERLAY_HEADING}\n\n{overlay_text.strip()}"
        )
        resolved.append(updated)
    return resolved


def load_task_overlay(
    block: dict[str, Any],
    *,
    base: Path,
    repo_root: Path,
    errors: list[str],
) -> TaskOverlayResolution:
    overlay = block.get("task_overlay")
    if overlay in (None, ""):
        return TaskOverlayResolution()
    if isinstance(overlay, str):
        return TaskOverlayResolution(text=overlay)
    if not isinstance(overlay, dict):
        errors.append("sdk.agent_profiles.task_overlay must be a string or object")
        return TaskOverlayResolution()
    fragments: list[str] = []
    names: list[str] = []
    paths: list[Path] = []
    for name in task_overlay_names_from_value(overlay.get("name"), errors=errors):
        text, path = load_standard_task_overlay(
            name, repo_root=repo_root, errors=errors
        )
        if text:
            fragments.append(text)
            names.append(name)
            paths.append(path)
    for name in task_overlay_names_from_value(overlay.get("names"), errors=errors):
        text, path = load_standard_task_overlay(
            name, repo_root=repo_root, errors=errors
        )
        if text:
            fragments.append(text)
            names.append(name)
            paths.append(path)
    for path in task_overlay_paths_from_value(overlay.get("path"), errors=errors):
        overlay_path = resolve_source_path(path, base=base, repo_root=repo_root)
        if overlay_path.exists():
            fragments.append(overlay_path.read_text(encoding="utf-8-sig").strip())
            paths.append(overlay_path)
        else:
            errors.append(
                f"sdk.agent_profiles.task_overlay.path does not exist: {path}"
            )
    for path in task_overlay_paths_from_value(overlay.get("paths"), errors=errors):
        overlay_path = resolve_source_path(path, base=base, repo_root=repo_root)
        if overlay_path.exists():
            fragments.append(overlay_path.read_text(encoding="utf-8-sig").strip())
            paths.append(overlay_path)
        else:
            errors.append(
                f"sdk.agent_profiles.task_overlay.path does not exist: {path}"
            )
    text = overlay.get("text")
    if isinstance(text, str) and text.strip():
        fragments.append(text.strip())
    elif text is not None:
        errors.append("sdk.agent_profiles.task_overlay.text must be a string")
    return TaskOverlayResolution(
        text="\n\n".join(fragment for fragment in fragments if fragment),
        names=tuple(names),
        paths=tuple(paths),
    )


def task_overlay_names_from_value(value: Any, *, errors: list[str]) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        names: list[str] = []
        for index, item in enumerate(value, 1):
            if not isinstance(item, str) or not item.strip():
                errors.append(
                    f"sdk.agent_profiles.task_overlay.names[{index}] must be a string"
                )
                continue
            names.append(item.strip())
        return names
    errors.append("sdk.agent_profiles.task_overlay.name must be a string")
    return []


def task_overlay_paths_from_value(value: Any, *, errors: list[str]) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        paths: list[str] = []
        for index, item in enumerate(value, 1):
            if not isinstance(item, str) or not item.strip():
                errors.append(
                    f"sdk.agent_profiles.task_overlay.paths[{index}] must be a string"
                )
                continue
            paths.append(item.strip())
        return paths
    errors.append("sdk.agent_profiles.task_overlay.path must be a string")
    return []


def load_standard_task_overlay(
    name: str,
    *,
    repo_root: Path,
    errors: list[str],
) -> tuple[str, Path]:
    if name not in STANDARD_TASK_OVERLAYS:
        available = ", ".join(sorted(STANDARD_TASK_OVERLAYS))
        errors.append(
            f"sdk.agent_profiles.task_overlay.name unknown: {name} "
            f"(available: {available})"
        )
        return "", Path()
    path = repo_root / STANDARD_TASK_OVERLAYS[name]
    if not path.exists():
        errors.append(f"standard task overlay does not exist: {name}")
        return "", path
    return path.read_text(encoding="utf-8-sig").strip(), path


def render_agent_profiles_markdown(resolved: ResolvedAgentProfiles) -> str:
    lines = [
        "# Copilot SDK Agent Profile Preview",
        "",
        f"- valid: `{resolved.ok}`",
        f"- loaded_agents: {len(resolved.custom_agents)}",
        f"- selected_agent: `{resolved.selected_agent}`",
        f"- custom_agents_local_only: `{resolved.custom_agents_local_only}`",
        "- include_sub_agent_streaming_events: "
        f"`{resolved.include_sub_agent_streaming_events}`",
        f"- custom_tools: {', '.join(resolved.custom_tool_names) or '(none)'}",
        f"- task_overlays: {', '.join(resolved.task_overlay_names) or '(none)'}",
        f"- task_overlay_paths: {len(resolved.task_overlay_paths)}",
        "",
    ]
    if resolved.default_agent:
        lines.extend(["## Default Agent", "", "```json"])
        lines.append(json_dump(resolved.default_agent))
        lines.extend(["```", ""])
    if resolved.errors:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in resolved.errors)
        lines.append("")
    if resolved.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in resolved.warnings)
        lines.append("")
    lines.extend(["## Agents", ""])
    if not resolved.custom_agents:
        lines.extend(["No custom agents loaded.", ""])
        return "\n".join(lines)
    for agent in resolved.custom_agents:
        name = str(agent.get("name", ""))
        lines.extend(
            [
                f"### {name or '(unnamed)'}",
                "",
                f"- display_name: `{agent.get('display_name', '')}`",
                f"- description: {agent.get('description', '')}",
                f"- model: `{agent.get('model', '')}`",
                f"- tools: {render_list(agent.get('tools'))}",
                f"- skills: {render_list(agent.get('skills'))}",
                f"- infer: `{agent.get('infer', '')}`",
                f"- prompt_chars: {len(str(agent.get('prompt', '')))}",
            ]
        )
        unsupported = resolved.unsupported_fields.get(name)
        if unsupported:
            lines.append(f"- unsupported_fields: {', '.join(unsupported)}")
        lines.append("")
    return "\n".join(lines)


def render_profile_catalog_markdown(validation: ProfileCatalogValidation) -> str:
    lines = [
        "# Agent Workbench Profile Catalog Preview",
        "",
        f"- valid: `{validation.ok}`",
        f"- standard_profiles: {len(validation.profiles)}",
        f"- standard_overlays: {len(validation.overlays)}",
        f"- warnings: {len(validation.warnings)}",
        f"- errors: {len(validation.errors)}",
        "",
    ]
    if validation.errors:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in validation.errors)
        lines.append("")
    if validation.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in validation.warnings)
        lines.append("")
    lines.extend(["## Standard Profiles", ""])
    for entry in validation.profiles:
        lines.extend(
            [
                f"### {entry.name}",
                "",
                f"- exists: `{entry.exists}`",
                f"- path: `{repo_relative_display(entry.path)}`",
                f"- model: `{entry.model}`",
                f"- tools: {render_list(list(entry.tools))}",
                f"- unsupported_fields: {render_list(list(entry.unsupported_fields))}",
                f"- prompt_chars: {entry.prompt_chars}",
                f"- errors: {len(entry.errors)}",
                "",
            ]
        )
    lines.extend(["## Standard Task Overlays", ""])
    for name, path, exists in validation.overlays:
        lines.extend(
            [
                f"- `{name}`: exists=`{exists}`, path=`{repo_relative_display(path)}`",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def repo_relative_display(path: Path) -> str:
    try:
        root = find_repo_root(path)
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path)


def render_list(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "(none)"
    if value in (None, ""):
        return "(none)"
    return str(value)


def json_dump(value: Any) -> str:
    import json

    return json.dumps(value, indent=2, sort_keys=True)


def resolve_source_path(raw_path: str, *, base: Path, repo_root: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    candidates = [base / path, repo_root / path, Path.cwd() / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def manifest_private_path(manifest: dict[str, Any]) -> Path | None:
    raw = manifest.get("_manifest_path")
    if isinstance(raw, str) and raw:
        return Path(raw)
    return None


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    return Path.cwd()
