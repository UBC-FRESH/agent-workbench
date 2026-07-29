from pathlib import Path

from scripts.util.user_secrets import resolve_secrets_path

def test_resolve_secrets_path_prefers_home_config(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    secrets_file = home / ".config" / "agent-workbench" / "secrets.env"
    secrets_file.parent.mkdir(parents=True)
    secrets_file.write_text("CCDB_PASSWORD=secret\n", encoding="utf-8")

    monkeypatch.setenv("HOME", str(home))
    result = resolve_secrets_path(default_workdir=tmp_path / "workdir")

    assert result == secrets_file


def test_resolve_secrets_path_uses_explicit_override(monkeypatch, tmp_path: Path) -> None:
    explicit = tmp_path / "custom.env"
    explicit.write_text("GITHUB_PAT=token\n", encoding="utf-8")

    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("AGENT_WORKBENCH_SECRETS_ENV", str(explicit))
    result = resolve_secrets_path(default_workdir=tmp_path / "workdir")

    assert result == explicit


def test_resolve_secrets_path_falls_back_to_workdir_cache(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir(parents=True)
    workdir = tmp_path / "workdir"
    workdir.mkdir(parents=True)
    cache_file = workdir / ".cache" / "secrets.env"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text("HF_TOKEN=abc\n", encoding="utf-8")

    monkeypatch.setenv("HOME", str(home))
    result = resolve_secrets_path(default_workdir=workdir)

    assert result == cache_file
