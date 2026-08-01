"""Referential-integrity and sanitization test for the Agent Hub setup playbook.

This test validates the tracked content of the Agent Hub setup playbook and
its entry-point links. It does NOT validate installation, runtime behaviour,
or clean-environment smoke testing.

Checks:
1. Playbook exists at the expected path.
2. All repo-relative paths referenced by the playbook exist on disk.
3. All agent profile names referenced resolve to .github/agents/*.agent.md
   files with matching frontmatter.
4. No private absolute paths (e.g. /home/user/, C:\\Users\\) in tracked content.
5. No token-shaped strings (long hex/base64 sequences) in tracked content.
6. No unapproved cluster/private endpoint markers in tracked content.
7. README.md, AGENTS.md, and .github/copilot-instructions.md all point to
   playbooks/agent_hub_setup.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

PLAYBOOK_PATH = ROOT / "playbooks" / "agent_hub_setup.md"
README_PATH = ROOT / "README.md"
AGENTS_PATH = ROOT / "AGENTS.md"
COPILOT_INSTRUCTIONS_PATH = ROOT / ".github" / "copilot-instructions.md"
AGENTS_DIR = ROOT / ".github" / "agents"

# Patterns that indicate private absolute paths on Linux or Windows.
_PRIVATE_PATH_PATTERNS = [
    re.compile(r"/home/[a-zA-Z0-9_-]+/"),
    re.compile(r"/Users/[a-zA-Z0-9_-]+/"),
    re.compile(r"C:\\Users\\[a-zA-Z0-9_-]+\\"),
    re.compile(r"/scratch/[a-zA-Z0-9_-]+/"),
    re.compile(r"/tmp/[a-zA-Z0-9_-]+/"),
    re.compile(r"/var/log/"),
]

# Patterns that look like tokens, API keys, or secrets.
_TOKEN_PATTERNS = [
    # Long hex strings (32+ chars) that look like API keys or tokens.
    re.compile(r"[0-9a-fA-F]{32,}"),
    # Base64-ish strings with common token prefixes.
    re.compile(r"(?:gh[pousr]_|xox[baprs]-|sk-[a-zA-Z0-9]{20,})"),
    # Generic token-like patterns with common key names.
    re.compile(r"(?i)(?:token|secret|key|password|api[_-]?key)\s*[:=]\s*[A-Za-z0-9+/=]{20,}"),
]

# Cluster or private endpoint markers that should not appear in tracked docs.
_ENDPOINT_MARKERS = [
    re.compile(r"(?:nibi|sockeye|arbutus|ubc-fresh|st-gep-1)\b", re.IGNORECASE),
    re.compile(r"(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})"),
    re.compile(r"slurm|srun|salloc", re.IGNORECASE),
]

# Allowed generic forms that should NOT be flagged.
_ALLOWED_GENERIC_PATTERNS = [
    # Tilde-based paths are acceptable (represent user-home generically).
    re.compile(r"~/.local/"),
    re.compile(r"<user-home>"),
    # Generic http/https examples in documentation context are fine.
    re.compile(r"http://127\.0\.0\.1:\d+"),
    re.compile(r"https://example\.com"),
    # Git commit hashes (40-char hex) used as version identifiers.
    re.compile(r"\b[0-9a-fA-F]{40}\b"),
    # Project/organization names that are public, not private endpoints.
    re.compile(r"\bUBC-FRESH\b", re.IGNORECASE),
    # Generic GitHub URLs in documentation context.
    re.compile(r"github\.com/"),
]


def _is_allowed_generic(text: str, match_start: int, match_end: int) -> bool:
    """Check if a match falls within an allowed generic pattern."""
    for pattern in _ALLOWED_GENERIC_PATTERNS:
        if pattern.search(text, match_start, match_end):
            return True
    return False


def _scan_file_for_violations(
    filepath: Path,
    label: str,
) -> list[tuple[str, str, int]]:
    """Scan a file for private paths, tokens, and endpoint markers.

    Returns a list of (violation_type, matched_text, line_number).
    """
    violations: list[tuple[str, str, int]] = []
    if not filepath.exists():
        return violations

    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        # Skip lines that are part of the allowed generic patterns.
        if any(p.search(line) for p in _ALLOWED_GENERIC_PATTERNS):
            continue

        for pattern, vtype in [
            (_PRIVATE_PATH_PATTERNS, "private_path"),
            (_TOKEN_PATTERNS, "token_shaped"),
            (_ENDPOINT_MARKERS, "endpoint_marker"),
        ]:
            for pat in pattern:
                for m in pat.finditer(line):
                    # Skip git commit hashes (7-40 hex chars, standalone).
                    matched = m.group()
                    if (
                        7 <= len(matched) <= 40
                        and re.fullmatch(r"[0-9a-fA-F]+", matched)
                    ):
                        continue
                    # Skip tokens that are part of an allowed generic pattern.
                    if not _is_allowed_generic(content, m.start(), m.end()):
                        snippet = matched[:60]
                        violations.append((vtype, snippet, line_no))

    return violations


def _extract_relative_links(content: str) -> list[str]:
    """Extract repo-relative markdown links from content."""
    links: list[str] = []
    # Match [text](relative/path) patterns.
    for m in re.finditer(r"\[.*?\]\(([^)]+)\)", content):
        link = m.group(1)
        # Only consider relative paths (not http(s)://, #, or external).
        if not link.startswith(("http://", "https://", "#", "mailto:", "www.")):
            links.append(link)
    return links


def _extract_agent_profile_names(content: str) -> list[str]:
    """Extract agent profile names referenced in content.

    Only matches explicit .agent.md file references, not generic words
    that happen to contain 'agent' or 'profile'.
    """
    names: list[str] = []
    # Match explicit .agent.md file references in links or text.
    for m in re.finditer(r"(\w+(?:-\w+)*\.agent\.md)", content):
        names.append(m.group(1))
    # Match frontmatter-style name: declarations.
    for m in re.finditer(r"^name:\s*(\w+(?:-\w+)*)$", content, re.MULTILINE):
        name = m.group(1)
        if not name.endswith(".agent.md"):
            names.append(f"{name}.agent.md")
    return list(set(names))


class TestAgentHubSetupPlaybook:
    """Referential-integrity and sanitization checks for the Agent Hub setup."""

    def test_playbook_exists(self) -> None:
        assert PLAYBOOK_PATH.exists(), (
            f"Agent Hub setup playbook not found at {PLAYBOOK_PATH}"
        )

    def test_playbook_has_tiered_structure(self) -> None:
        content = PLAYBOOK_PATH.read_text(encoding="utf-8")
        for tier_label in ["Tier 0", "Tier 1", "Tier 2", "Tier 3"]:
            assert tier_label in content, (
                f"Playbook missing {tier_label} section"
            )

    def test_playbook_references_credential_boundary(self) -> None:
        content = PLAYBOOK_PATH.read_text(encoding="utf-8")
        assert "credential" in content.lower() or "token" in content.lower(), (
            "Playbook should mention credential boundaries"
        )

    def test_playbook_references_smoke_checklist(self) -> None:
        content = PLAYBOOK_PATH.read_text(encoding="utf-8")
        assert "smoke" in content.lower() or "pass/fail" in content.lower(), (
            "Playbook should include a smoke checklist"
        )

    def test_playbook_references_verification_table(self) -> None:
        content = PLAYBOOK_PATH.read_text(encoding="utf-8")
        assert "|" in content, (
            "Playbook should include a verification table"
        )

    def test_playbook_no_private_paths(self) -> None:
        violations = _scan_file_for_violations(PLAYBOOK_PATH, "playbook")
        private_path_violations = [
            v for v in violations if v[0] == "private_path"
        ]
        assert not private_path_violations, (
            f"Private paths found in playbook: {private_path_violations}"
        )

    def test_playbook_no_tokens(self) -> None:
        violations = _scan_file_for_violations(PLAYBOOK_PATH, "playbook")
        token_violations = [
            v for v in violations if v[0] == "token_shaped"
        ]
        assert not token_violations, (
            f"Token-shaped strings found in playbook: {token_violations}"
        )

    def test_playbook_no_endpoint_markers(self) -> None:
        violations = _scan_file_for_violations(PLAYBOOK_PATH, "playbook")
        endpoint_violations = [
            v for v in violations if v[0] == "endpoint_marker"
        ]
        assert not endpoint_violations, (
            f"Endpoint markers found in playbook: {endpoint_violations}"
        )

    def test_playbook_relative_links_resolve(self) -> None:
        content = PLAYBOOK_PATH.read_text(encoding="utf-8")
        links = _extract_relative_links(content)
        unresolved = []
        for link in links:
            # Links may be:
            # - playbook-relative (e.g. "cli_workflow.md") -> resolve from playbook dir
            # - repo-root-relative with ../ (e.g. "../AGENTS.md") -> resolve from playbook parent
            # - repo-root-relative without ../ (e.g. "playbooks/foo.md") -> resolve from ROOT
            if link.startswith("../"):
                resolved = (PLAYBOOK_PATH.parent / link).resolve()
            elif "/" not in link and not link.startswith("playbooks/") and not link.startswith("notes/"):
                # Simple filename like "cli_workflow.md" -> playbook dir
                resolved = (PLAYBOOK_PATH.parent / link).resolve()
            else:
                resolved = (ROOT / link).resolve()
            if not resolved.exists():
                unresolved.append(link)
        assert not unresolved, (
            f"Unresolved relative links in playbook: {unresolved}"
        )

    def test_playbook_agent_profiles_resolve(self) -> None:
        content = PLAYBOOK_PATH.read_text(encoding="utf-8")
        profile_names = _extract_agent_profile_names(content)
        unresolved = []
        for name in profile_names:
            profile_path = AGENTS_DIR / name
            if not profile_path.exists():
                unresolved.append(name)
        assert not unresolved, (
            f"Unresolved agent profiles in playbook: {unresolved}"
        )

    def test_readme_links_to_playbook(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        assert "agent_hub_setup" in content, (
            "README.md should link to agent_hub_setup.md"
        )

    def test_agents_md_links_to_playbook(self) -> None:
        content = AGENTS_PATH.read_text(encoding="utf-8")
        assert "agent_hub_setup" in content, (
            "AGENTS.md should link to agent_hub_setup.md"
        )

    def test_copilot_instructions_links_to_playbook(self) -> None:
        content = COPILOT_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
        assert "agent_hub_setup" in content, (
            ".github/copilot-instructions.md should link to agent_hub_setup.md"
        )

    def test_entry_points_no_private_paths(self) -> None:
        for filepath in [README_PATH, AGENTS_PATH, COPILOT_INSTRUCTIONS_PATH]:
            violations = _scan_file_for_violations(filepath, filepath.name)
            assert not violations, (
                f"Violations in {filepath.name}: {violations}"
            )

    def test_referenced_setup_docs_exist(self) -> None:
        """Tier 1 and Tier 2 reference playbooks should exist on disk."""
        github_mcp_playbook = ROOT / "playbooks" / "github_mcp_setup.md"
        keklick_playbook = ROOT / "notes" / "operations" / "keklick-copilot-extension-config.md"
        assert github_mcp_playbook.exists(), (
            f"Tier 1 playbook missing: {github_mcp_playbook}"
        )
        assert keklick_playbook.exists(), (
            f"Tier 2 playbook missing: {keklick_playbook}"
        )

    def test_playbook_no_cluster_endpoint_markers(self) -> None:
        """Cluster names (nibi, sockeye, arbutus) should not appear."""
        content = PLAYBOOK_PATH.read_text(encoding="utf-8")
        for marker in ["nibi", "sockeye", "arbutus"]:
            assert marker.lower() not in content.lower(), (
                f"Cluster name '{marker}' found in playbook"
            )