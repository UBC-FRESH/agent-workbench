from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_workbench.agent_bridge.errors import BridgeTransactionError, ConcurrentBridgeRunError, TomlValidationError
from agent_workbench.agent_bridge.transaction import BridgeConfigTransaction, ConfigTarget, sha256_file
from agent_workbench.agent_bridge.transaction_cli import main as transaction_cli_main
from agent_workbench.agent_bridge.toml_guard import assert_valid_toml_text


def make_transaction(tmp_path: Path, *, original: str = 'model = "qwen"\n') -> tuple[BridgeConfigTransaction, Path, Path, Path, Path]:
    target = tmp_path / "config.toml"
    backup = tmp_path / "config.before.toml"
    journal = tmp_path / "transaction.json"
    lock = tmp_path / "bridge.lock"
    target.write_text(original, encoding="utf-8", newline="")
    transaction = BridgeConfigTransaction(
        run_id="test_run",
        targets=(ConfigTarget(path=target, backup_path=backup, kind="config"),),
        journal_path=journal,
        lock_path=lock,
    )
    return transaction, target, backup, journal, lock


def test_guard_rejects_concatenated_toml_assignments() -> None:
    bad = 'enabled = true\nmodel = "qwen"enabled = false\n'
    with pytest.raises(TomlValidationError):
        assert_valid_toml_text(bad)


def test_transaction_rejects_invalid_original_before_backup_or_journal(tmp_path: Path) -> None:
    transaction, target, backup, journal, lock = make_transaction(tmp_path, original='model = "qwen"enabled = false\n')
    original = target.read_bytes()
    with pytest.raises(TomlValidationError):
        transaction.begin()
    assert target.read_bytes() == original
    assert not backup.exists()
    assert not journal.exists()
    assert not lock.exists()


def test_transaction_backup_and_restore_are_byte_for_byte(tmp_path: Path) -> None:
    original = '[section]\r\nkey = "value"  \r\n'
    transaction, target, backup, journal, _lock = make_transaction(tmp_path, original=original)
    original_hash = sha256_file(target)
    transaction.begin()
    assert backup.read_bytes() == original.encode("utf-8")
    transaction.stage(target, '[section]\r\nkey = "changed"\r\n')
    transaction.commit()
    assert target.read_text(encoding="utf-8") != original
    transaction.restore()
    assert target.read_bytes() == original.encode("utf-8")
    assert sha256_file(target) == original_hash
    assert json.loads(journal.read_text(encoding="utf-8"))["state"] == "restored"
    transaction.close()


def test_transaction_restore_is_idempotent(tmp_path: Path) -> None:
    transaction, target, _backup, _journal, _lock = make_transaction(tmp_path)
    transaction.begin()
    transaction.stage(target, 'model = "changed"\n')
    transaction.commit()
    transaction.restore()
    first_restore = target.read_bytes()
    transaction.restore()
    assert target.read_bytes() == first_restore
    transaction.close()


def test_transaction_rejects_concurrent_lock(tmp_path: Path) -> None:
    first, _target, _backup, _journal, lock = make_transaction(tmp_path)
    first.begin()
    second = BridgeConfigTransaction(
        run_id="second_run",
        targets=first.targets,
        journal_path=tmp_path / "second-transaction.json",
        lock_path=lock,
    )
    with pytest.raises(ConcurrentBridgeRunError):
        second.begin()
    assert lock.exists()
    first.close()


def test_transaction_validates_all_staged_documents_before_mutation(tmp_path: Path) -> None:
    transaction, target, _backup, _journal, _lock = make_transaction(tmp_path)
    original = target.read_bytes()
    transaction.begin()
    with pytest.raises(TomlValidationError):
        transaction.stage(target, 'model = "qwen"enabled = false\n')
    assert target.read_bytes() == original
    transaction.close()


def test_transaction_requires_staged_content_for_every_target(tmp_path: Path) -> None:
    transaction, target, _backup, _journal, _lock = make_transaction(tmp_path)
    transaction.begin()
    with pytest.raises(BridgeTransactionError, match="missing staged content"):
        transaction.commit()
    assert target.read_text(encoding="utf-8") == 'model = "qwen"\n'
    transaction.close()


def test_transaction_recovers_prepared_journal_from_backup(tmp_path: Path) -> None:
    transaction, target, _backup, journal, _lock = make_transaction(tmp_path)
    transaction.begin()
    target.write_text('model = "interrupted"\n', encoding="utf-8", newline="")
    assert json.loads(journal.read_text(encoding="utf-8"))["state"] == "prepared"
    assert transaction.recover_if_needed() is True
    assert target.read_text(encoding="utf-8") == 'model = "qwen"\n'
    assert json.loads(journal.read_text(encoding="utf-8"))["state"] == "restored"
    assert transaction.recover_if_needed() is False
    transaction.close()


def test_transaction_cli_commits_and_restores_staged_toml(tmp_path: Path) -> None:
    target = tmp_path / "config.toml"
    backup = tmp_path / "config.before.toml"
    staged = tmp_path / "config.staged.toml"
    journal = tmp_path / "transaction.json"
    lock = tmp_path / "transaction.lock"
    target.write_text('model = "qwen"\n', encoding="utf-8", newline="")
    staged.write_text('model = "bridge"\n', encoding="utf-8", newline="")

    assert (
        transaction_cli_main(
            [
                "commit",
                "--run-id",
                "cli_run",
                "--journal",
                str(journal),
                "--lock",
                str(lock),
                "--target",
                f"config|{target}|{backup}|{staged}",
            ]
        )
        == 0
    )
    assert target.read_text(encoding="utf-8") == 'model = "bridge"\n'
    assert backup.read_text(encoding="utf-8") == 'model = "qwen"\n'
    assert json.loads(journal.read_text(encoding="utf-8"))["state"] == "committed"

    assert (
        transaction_cli_main(
            [
                "restore",
                "--run-id",
                "cli_run",
                "--journal",
                str(journal),
                "--lock",
                str(lock),
                "--target",
                f"config|{target}|{backup}",
            ]
        )
        == 0
    )
    assert target.read_text(encoding="utf-8") == 'model = "qwen"\n'
    assert json.loads(journal.read_text(encoding="utf-8"))["state"] == "restored"


def test_combined_toml_and_hooks_commit_restore_byte_for_byte(tmp_path: Path) -> None:
    config, hooks = tmp_path / "config.toml", tmp_path / "hooks.json"
    config.write_bytes(b'model = "qwen"\r\n')
    hooks.write_bytes(b'{"original": true}\r\n')
    config_backup, hooks_backup = tmp_path / "config.bak", tmp_path / "hooks.bak"
    tx = BridgeConfigTransaction(run_id="combined", targets=(ConfigTarget(config, config_backup), ConfigTarget(hooks, hooks_backup, "hooks")), journal_path=tmp_path / "j", lock_path=tmp_path / "l")
    tx.begin(); tx.stage(config, 'model = "changed"\n'); tx.stage(hooks, '{"staged": true}\n'); tx.commit()
    tx.restore()
    assert config.read_bytes() == b'model = "qwen"\r\n' and hooks.read_bytes() == b'{"original": true}\r\n'
    tx.close()


def test_invalid_hooks_json_is_rejected_before_mutation(tmp_path: Path) -> None:
    config, hooks = tmp_path / "config.toml", tmp_path / "hooks.json"
    config.write_text('model = "qwen"\n'); hooks.write_text('{"original": true}\n')
    tx = BridgeConfigTransaction(run_id="bad-hooks", targets=(ConfigTarget(config, tmp_path / "cb"), ConfigTarget(hooks, tmp_path / "hb", "hooks")), journal_path=tmp_path / "j", lock_path=tmp_path / "l")
    tx.begin(); original = (config.read_bytes(), hooks.read_bytes())
    with pytest.raises((json.JSONDecodeError, BridgeTransactionError)):
        tx.stage(hooks, '{broken')
    assert (config.read_bytes(), hooks.read_bytes()) == original
    tx.close()


def test_transaction_cli_hooks_round_trip(tmp_path: Path) -> None:
    target, backup, staged = tmp_path / "hooks.json", tmp_path / "hooks.bak", tmp_path / "hooks.staged.json"
    target.write_bytes(b'{"before":true}\r\n'); staged.write_text('{"after":true}\n')
    args = ["--run-id", "hooks-cli", "--journal", str(tmp_path / "j"), "--lock", str(tmp_path / "l")]
    assert transaction_cli_main(["commit", *args, "--target", f"hooks|{target}|{backup}|{staged}"]) == 0
    assert transaction_cli_main(["restore", *args, "--target", f"hooks|{target}|{backup}"]) == 0
    assert target.read_bytes() == b'{"before":true}\r\n'
