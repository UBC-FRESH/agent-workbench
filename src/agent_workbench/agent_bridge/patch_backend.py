"""Constrained apply_patch backend for grant-bound MCP patch calls."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from agent_workbench.agent_bridge.errors import AgentBridgeError


class PatchBackendError(AgentBridgeError):
    """Raised when a patch cannot be safely applied."""


@dataclass(frozen=True)
class PatchResult:
    changed_files: tuple[Path, ...]


def apply_patch_subset(patch: str, root: Path) -> PatchResult:
    """Apply a conservative subset of the Codex patch envelope.

    Supported operations:
    - `*** Add File: <relative path>`
    - `*** Delete File: <relative path>`
    - `*** Update File: <relative path>` with one or more `@@` hunks using
      leading space, `-`, and `+` lines.

    The backend is intentionally small. Unsupported patch features fail closed
    so live MCP routing cannot silently broaden file authority.
    """

    lines = patch.splitlines()
    if not lines:
        raise PatchBackendError("invalid_patch_envelope")
    if lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        return _apply_unified_patch(patch, root)
    resolved_root = root.resolve()
    changed: list[Path] = []
    index = 1
    while index < len(lines) - 1:
        line = lines[index]
        if line.startswith("*** Add File: "):
            path = _resolve_patch_path(resolved_root, line.removeprefix("*** Add File: "))
            index = _apply_add_file(lines, index + 1, path)
            changed.append(path)
        elif line.startswith("*** Delete File: "):
            path = _resolve_patch_path(resolved_root, line.removeprefix("*** Delete File: "))
            if not path.exists() or not path.is_file():
                raise PatchBackendError("delete_target_missing")
            path.unlink()
            changed.append(path)
            index += 1
        elif line.startswith("*** Update File: "):
            path = _resolve_patch_path(resolved_root, line.removeprefix("*** Update File: "))
            index = _apply_update_file(lines, index + 1, path)
            changed.append(path)
        else:
            raise PatchBackendError(f"unsupported_patch_line:{line}")
    return PatchResult(changed_files=tuple(changed))


def patch_paths(patch: str) -> tuple[str, ...]:
    """Return all audited relative paths named by a supported patch."""

    lines = patch.splitlines()
    if lines and lines[0] == "*** Begin Patch" and lines[-1] == "*** End Patch":
        paths = [
            line.split(": ", 1)[1]
            for line in lines
            if line.startswith(("*** Add File: ", "*** Delete File: ", "*** Update File: "))
        ]
    else:
        paths = _unified_patch_paths(lines)
    if not paths:
        raise PatchBackendError("patch_paths_missing")
    for path in paths:
        _validate_relative_path(path)
    return tuple(dict.fromkeys(paths))


def _apply_unified_patch(patch: str, root: Path) -> PatchResult:
    paths = patch_paths(patch)
    completed = subprocess.run(
        ["git", "apply", "--no-index", "--whitespace=nowarn", "-"],
        cwd=root,
        input=patch,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().replace("\n", " ")[:240]
        raise PatchBackendError(f"unified_patch_apply_failed:{detail or completed.returncode}")
    return PatchResult(changed_files=tuple(_resolve_patch_path(root.resolve(), path) for path in paths))


def _unified_patch_paths(lines: list[str]) -> list[str]:
    paths: list[str] = []
    index = 0
    while index < len(lines):
        if not lines[index].startswith("--- "):
            index += 1
            continue
        if index + 1 >= len(lines) or not lines[index + 1].startswith("+++ "):
            raise PatchBackendError("unified_patch_missing_new_header")
        old_path = _unified_header_path(lines[index].removeprefix("--- "))
        new_path = _unified_header_path(lines[index + 1].removeprefix("+++ "))
        if old_path is None and new_path is None:
            raise PatchBackendError("unified_patch_missing_path")
        paths.append(new_path or old_path)  # type: ignore[arg-type]
        index += 2
    return paths


def _unified_header_path(value: str) -> str | None:
    token = value.split("\t", 1)[0].strip()
    if token == "/dev/null":
        return None
    if token.startswith(("a/", "b/")):
        token = token[2:]
    _validate_relative_path(token)
    return token


def _validate_relative_path(path_text: str) -> None:
    candidate = Path(path_text)
    if not path_text or candidate.is_absolute() or ".." in candidate.parts:
        raise PatchBackendError("path_outside_root")


def _resolve_patch_path(root: Path, path_text: str) -> Path:
    candidate = Path(path_text)
    if candidate.is_absolute():
        raise PatchBackendError("absolute_path_rejected")
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise PatchBackendError("path_outside_root")
    return resolved


def _is_file_header(line: str) -> bool:
    return line.startswith("*** Add File: ") or line.startswith("*** Delete File: ") or line.startswith("*** Update File: ") or line == "*** End Patch"


def _apply_add_file(lines: list[str], index: int, path: Path) -> int:
    if path.exists():
        raise PatchBackendError("add_target_exists")
    added: list[str] = []
    while index < len(lines) and not _is_file_header(lines[index]):
        line = lines[index]
        if not line.startswith("+"):
            raise PatchBackendError("add_file_requires_plus_lines")
        added.append(line[1:])
        index += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(added) + ("\n" if added else ""), encoding="utf-8", newline="")
    return index


def _apply_update_file(lines: list[str], index: int, path: Path) -> int:
    if not path.exists() or not path.is_file():
        raise PatchBackendError("update_target_missing")
    content = path.read_text(encoding="utf-8")
    content_lines = content.splitlines()
    search_index = 0
    if index >= len(lines) or not lines[index].startswith("@@"):
        raise PatchBackendError("update_requires_hunk")
    while index < len(lines) and not _is_file_header(lines[index]):
        if not lines[index].startswith("@@"):
            raise PatchBackendError("update_requires_hunk")
        index += 1
        old: list[str] = []
        new: list[str] = []
        while index < len(lines) and not lines[index].startswith("@@") and not _is_file_header(lines[index]):
            line = lines[index]
            if line.startswith(" "):
                old.append(line[1:])
                new.append(line[1:])
            elif line.startswith("-"):
                old.append(line[1:])
            elif line.startswith("+"):
                new.append(line[1:])
            else:
                raise PatchBackendError("unsupported_hunk_line")
            index += 1
        if not old:
            raise PatchBackendError("empty_update_context")
        match_index = _find_sequence(content_lines, old, search_index)
        if match_index is None:
            raise PatchBackendError("update_context_not_found")
        content_lines[match_index : match_index + len(old)] = new
        search_index = match_index + len(new)
    path.write_text("\n".join(content_lines) + "\n", encoding="utf-8", newline="")
    return index


def _find_sequence(haystack: list[str], needle: list[str], start: int) -> int | None:
    if len(needle) > len(haystack):
        return None
    for index in range(start, len(haystack) - len(needle) + 1):
        if haystack[index : index + len(needle)] == needle:
            return index
    return None
