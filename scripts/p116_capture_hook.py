"""Codex command-hook entry point for the P116 local capture probe."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.supervision_hook import capture_from_environment


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return 0
        capture_from_environment(payload)
    except Exception:
        # Hooks must never replace a Worker tool result with internal telemetry.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
