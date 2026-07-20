"""Journaled file transaction helpers for bridge config staging."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from agent_workbench.agent_bridge.errors import BridgeTransactionError, ConcurrentBridgeRunError
from agent_workbench.agent_bridge.toml_guard import assert_valid_toml_file, assert_valid_toml_text


TargetKind = Literal["config", "agent_role", "hooks"]


@dataclass(frozen=True)
class ConfigTarget:
    """One boot-critical file managed by a bridge transaction."""

    path: Path
    backup_path: Path
    kind: TargetKind = "config"


@dataclass(frozen=True)
class TargetSnapshot:
    """Original bytes and hash for one managed target."""

    target: ConfigTarget
    sha256: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


class BridgeConfigTransaction:
    """Small, fail-closed transaction for config/role files.

    The transaction validates all staged TOML before replacing live files.
    It writes backups and a journal before mutation, then supports idempotent
    restore from those backups. This is intentionally local and deterministic;
    it does not know about live Codex processes.
    """

    def __init__(self, *, run_id: str, targets: tuple[ConfigTarget, ...], journal_path: Path, lock_path: Path) -> None:
        if not run_id:
            raise BridgeTransactionError("run_id is required")
        if not targets:
            raise BridgeTransactionError("at least one target is required")
        self.run_id = run_id
        self.targets = targets
        self.journal_path = journal_path
        self.lock_path = lock_path
        self._staged: dict[Path, str] = {}
        self._snapshots: dict[Path, TargetSnapshot] = {}
        self._lock_fd: int | None = None

    def __enter__(self) -> "BridgeConfigTransaction":
        self.begin()
        return self

    def __exit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        self.close()

    def begin(self) -> None:
        self._acquire_lock()
        try:
            self.journal_path.parent.mkdir(parents=True, exist_ok=True)
            for target in self.targets:
                target.path.parent.mkdir(parents=True, exist_ok=True)
                target.backup_path.parent.mkdir(parents=True, exist_ok=True)
                self._validate_file(target)
                data = target.path.read_bytes()
                target.backup_path.write_bytes(data)
                self._snapshots[target.path] = TargetSnapshot(target=target, sha256=sha256_bytes(data))
            self._write_journal("prepared")
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if self._lock_fd is not None:
            os.close(self._lock_fd)
            self._lock_fd = None
            try:
                self.lock_path.unlink()
            except FileNotFoundError:
                pass

    def stage(self, target_path: Path, content: str) -> None:
        target = self._target_for(target_path)
        self._validate_text(target, content)
        self._staged[target.path] = content

    def commit(self) -> None:
        missing = [str(target.path) for target in self.targets if target.path not in self._staged]
        if missing:
            raise BridgeTransactionError(f"missing staged content for: {', '.join(missing)}")
        for target in self.targets:
            self._validate_text(target, self._staged[target.path])
        self._write_journal("committing")
        replaced: list[ConfigTarget] = []
        try:
            for target in self.targets:
                self._atomic_write_text(target.path, self._staged[target.path])
                replaced.append(target)
                self._validate_file(target)
        except Exception:
            for target in reversed(replaced):
                target.path.write_bytes(target.backup_path.read_bytes())
            self._write_journal("restored")
            raise
        self._write_journal("committed")

    def restore(self) -> None:
        for target in self.targets:
            if not target.backup_path.exists():
                raise BridgeTransactionError(f"backup missing: {target.backup_path}")
            target.path.write_bytes(target.backup_path.read_bytes())
            self._validate_file(target)
        self._write_journal("restored")

    def restore_existing(self) -> None:
        """Restore from existing backups under the transaction lock."""
        self._acquire_lock()
        try:
            self.restore()
        finally:
            self.close()

    def recover_if_needed(self) -> bool:
        if not self.journal_path.exists():
            return False
        journal = json.loads(self.journal_path.read_text(encoding="utf-8"))
        if journal.get("state") not in {"prepared", "committing"}:
            return False
        self.restore()
        return True

    def _target_for(self, path: Path) -> ConfigTarget:
        resolved = path.resolve()
        for target in self.targets:
            if target.path.resolve() == resolved:
                return target
        raise BridgeTransactionError(f"unmanaged target: {path}")

    @staticmethod
    def _validate_text(target: ConfigTarget, content: str) -> None:
        if target.kind == "hooks":
            value = json.loads(content)
            if not isinstance(value, dict):
                raise BridgeTransactionError("hooks content must be a JSON object")
        else:
            assert_valid_toml_text(content)

    @classmethod
    def _validate_file(cls, target: ConfigTarget) -> None:
        if target.kind == "hooks":
            try:
                value = json.loads(target.path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise BridgeTransactionError(f"hooks file is not valid JSON: {target.path}") from exc
            if not isinstance(value, dict):
                raise BridgeTransactionError("hooks file must be a JSON object")
        else:
            assert_valid_toml_file(target.path)

    def _acquire_lock(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise ConcurrentBridgeRunError(f"bridge transaction lock exists: {self.lock_path}") from exc
        os.write(self._lock_fd, self.run_id.encode("utf-8"))

    def _write_journal(self, state: str) -> None:
        records = []
        for target in self.targets:
            snapshot = self._snapshots.get(target.path)
            records.append(
                {
                    "path": str(target.path),
                    "backup_path": str(target.backup_path),
                    "kind": target.kind,
                    "original_sha256": snapshot.sha256 if snapshot else None,
                    "current_sha256": sha256_file(target.path) if target.path.exists() else None,
                }
            )
        self.journal_path.write_text(json.dumps({"run_id": self.run_id, "state": state, "targets": records}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @staticmethod
    def _atomic_write_text(path: Path, content: str) -> None:
        tmp = path.with_name(f".{path.name}.tmp")
        with tmp.open("w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
