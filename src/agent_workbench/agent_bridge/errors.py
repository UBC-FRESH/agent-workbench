"""Error types for agent bridge transactions."""

from __future__ import annotations


class AgentBridgeError(RuntimeError):
    """Base error for agent bridge failures."""


class TomlValidationError(AgentBridgeError):
    """Raised when a TOML document fails validation."""


class BridgeTransactionError(AgentBridgeError):
    """Raised when a bridge transaction cannot safely continue."""


class ConcurrentBridgeRunError(BridgeTransactionError):
    """Raised when another bridge transaction owns the config lock."""

