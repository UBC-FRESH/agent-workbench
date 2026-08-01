from __future__ import annotations

from pathlib import Path

import pytest

from scripts.install_agent_hub_profiles import (
    install_global_contract,
    install_profiles,
    overlay_files,
    profile_files,
    render_global_contract,
)


def _write_profiles(source: Path, *names: str) -> None:
    source.mkdir(parents=True)
    for name in names:
        (source / f"{name}.agent.md").write_text(
            f"---\nname: {name}\n---\n\nProfile {name}\n",
            encoding="utf-8",
        )


def test_install_profiles_copies_all_profiles(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "home" / ".copilot" / "agents"
    _write_profiles(
        source, "agent-workbench-coordinator", "agent-workbench-worker"
    )

    installed, unchanged, conflicts = install_profiles(source, destination)

    assert installed == [
        "agent-workbench-coordinator.agent.md",
        "agent-workbench-worker.agent.md",
    ]
    assert unchanged == []
    assert conflicts == []
    assert sorted(path.name for path in destination.iterdir()) == installed


def test_install_profiles_is_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_profiles(source, "agent-workbench-coordinator")

    install_profiles(source, destination)
    installed, unchanged, conflicts = install_profiles(source, destination)

    assert installed == []
    assert unchanged == ["agent-workbench-coordinator.agent.md"]
    assert conflicts == []


def test_install_profiles_does_not_overwrite_conflicts(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_profiles(source, "agent-workbench-coordinator")
    destination.mkdir()
    target = destination / "agent-workbench-coordinator.agent.md"
    target.write_text("user copy\n", encoding="utf-8")

    installed, unchanged, conflicts = install_profiles(source, destination)

    assert installed == []
    assert unchanged == []
    assert conflicts == ["agent-workbench-coordinator.agent.md"]
    assert target.read_text(encoding="utf-8") == "user copy\n"


def test_install_profiles_can_replace_explicitly(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_profiles(source, "agent-workbench-coordinator")
    destination.mkdir()
    (destination / "agent-workbench-coordinator.agent.md").write_text(
        "old\n", encoding="utf-8"
    )

    installed, unchanged, conflicts = install_profiles(
        source, destination, replace=True
    )

    assert installed == ["agent-workbench-coordinator.agent.md"]
    assert unchanged == []
    assert conflicts == []
    assert "Profile agent-workbench-coordinator" in (
        destination / "agent-workbench-coordinator.agent.md"
    ).read_text(encoding="utf-8")


def test_install_profiles_check_does_not_create_destination(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_profiles(source, "agent-workbench-coordinator")

    installed, unchanged, conflicts = install_profiles(
        source, destination, dry_run=True
    )

    assert installed == ["agent-workbench-coordinator.agent.md"]
    assert unchanged == []
    assert conflicts == []
    assert not destination.exists()


def test_install_profiles_copies_overlays_to_user_scope(tmp_path: Path) -> None:
    source = tmp_path / "source"
    _write_profiles(source, "agent-workbench-coordinator")
    overlay = source / "overlays" / "documentation-expansion.md"
    overlay.parent.mkdir()
    overlay.write_text(
        "---\ntarget_roles: [coordinator]\n---\n\n# Documentation\n",
        encoding="utf-8",
    )
    destination = tmp_path / "destination"

    installed, unchanged, conflicts = install_profiles(source, destination)

    assert installed == [
        "agent-workbench-coordinator.agent.md",
        "overlays/documentation-expansion.md",
    ]
    assert unchanged == []
    assert conflicts == []
    assert overlay_files(source) == [overlay]
    assert profile_files(source) == [
        source / "agent-workbench-coordinator.agent.md"
    ]
    assert (destination / "overlays/documentation-expansion.md").exists()


def test_render_global_contract_has_user_instruction_frontmatter(tmp_path: Path) -> None:
    source = tmp_path / "copilot-instructions.md"
    source.write_text("# Agent Hub\n\nFull contract.\n", encoding="utf-8")

    rendered = render_global_contract(source)

    assert rendered.startswith("---\n")
    assert "applyTo: \"**\"" in rendered
    assert rendered.endswith("# Agent Hub\n\nFull contract.\n")


def test_install_global_contract_is_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "copilot-instructions.md"
    destination = (
        tmp_path
        / "home"
        / ".copilot"
        / "instructions"
        / "agent-workbench.instructions.md"
    )
    source.write_text("# Agent Hub\n", encoding="utf-8")

    first = install_global_contract(source, destination)
    second = install_global_contract(source, destination)

    assert first == (True, False, False)
    assert second == (False, True, False)


def test_install_global_contract_protects_conflicts(tmp_path: Path) -> None:
    source = tmp_path / "copilot-instructions.md"
    destination = tmp_path / "destination.md"
    source.write_text("# Agent Hub\n", encoding="utf-8")
    destination.write_text("user contract\n", encoding="utf-8")

    result = install_global_contract(source, destination)

    assert result == (False, False, True)
    assert destination.read_text(encoding="utf-8") == "user contract\n"