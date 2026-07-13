from __future__ import annotations

from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_dev_extra_contains_python_side_tooling() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = config["project"]["optional-dependencies"]["dev"]

    assert "build>=1.3" in dependencies
    assert "nodeenv>=1.10" in dependencies
    assert "twine>=6.2" in dependencies
    assert "sphinx>=7.0" in dependencies
    assert not any(item.startswith("gh") for item in dependencies)
    assert not any(item.startswith("ripgrep") for item in dependencies)


def test_bootstrap_installs_verified_native_tools_in_venv() -> None:
    script = (ROOT / "scripts" / "bootstrap_dev_environment.ps1").read_text(
        encoding="utf-8"
    )

    assert "https://github.com/cli/cli/releases/download/" in script
    assert "https://github.com/BurntSushi/ripgrep/releases/download/" in script
    assert "Get-FileHash -Algorithm SHA256" in script
    assert 'ExecutableName "gh.exe"' in script
    assert 'ExecutableName "rg.exe"' in script
    assert "-m nodeenv -p" in script
    assert 'Install-CommandShim -CommandName "git"' in script
    assert 'Install-CommandShim -CommandName "codex"' in script
