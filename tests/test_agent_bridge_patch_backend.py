from __future__ import annotations

from pathlib import Path

import pytest

from agent_workbench.agent_bridge.patch_backend import PatchBackendError, apply_patch_subset


def test_apply_patch_subset_updates_file_inside_root(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("before\n", encoding="utf-8", newline="")
    patch = "*** Begin Patch\n*** Update File: target.txt\n@@\n-before\n+after\n*** End Patch"

    result = apply_patch_subset(patch, tmp_path)

    assert target.read_text(encoding="utf-8") == "after\n"
    assert result.changed_files == (target.resolve(),)


def test_apply_patch_subset_accepts_standard_unified_new_file_inside_root(tmp_path: Path) -> None:
    patch = "--- /dev/null\n+++ b/src/new.py\n@@ -0,0 +1 @@\n+value = 1\n"

    result = apply_patch_subset(patch, tmp_path)

    assert result.changed_files == ((tmp_path / "src" / "new.py").resolve(),)
    assert (tmp_path / "src" / "new.py").read_text(encoding="utf-8") == "value = 1\n"


def test_apply_patch_subset_adds_and_deletes_relative_files(tmp_path: Path) -> None:
    delete_me = tmp_path / "delete-me.txt"
    delete_me.write_text("remove\n", encoding="utf-8", newline="")
    patch = "\n".join(
        [
            "*** Begin Patch",
            "*** Add File: nested/added.txt",
            "+added",
            "*** Delete File: delete-me.txt",
            "*** End Patch",
        ]
    )

    result = apply_patch_subset(patch, tmp_path)

    assert (tmp_path / "nested" / "added.txt").read_text(encoding="utf-8") == "added\n"
    assert not delete_me.exists()
    assert result.changed_files == ((tmp_path / "nested" / "added.txt").resolve(), delete_me.resolve())


def test_apply_patch_subset_rejects_paths_outside_root(tmp_path: Path) -> None:
    patch = "*** Begin Patch\n*** Add File: ../escape.txt\n+bad\n*** End Patch"

    with pytest.raises(PatchBackendError, match="path_outside_root"):
        apply_patch_subset(patch, tmp_path)


def test_apply_patch_subset_rejects_missing_update_context(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("before\n", encoding="utf-8", newline="")
    patch = "*** Begin Patch\n*** Update File: target.txt\n@@\n-missing\n+after\n*** End Patch"

    with pytest.raises(PatchBackendError, match="update_context_not_found"):
        apply_patch_subset(patch, tmp_path)
