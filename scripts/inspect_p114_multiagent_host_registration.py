"""Compare direct and code-mode host registration vocabulary without inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MARKERS = (
    "apply_patch_tool_type",
    "custom_tool_call",
    "unsupported custom tool call",
)


def marker_counts(path: Path) -> dict[str, int]:
    content = path.read_bytes().lower()
    return {marker: content.count(marker.encode("utf-8")) for marker in MARKERS}


def inspect(direct_host: Path, child_host: Path) -> dict[str, object]:
    direct = marker_counts(direct_host)
    child = marker_counts(child_host)
    direct_supports_patch_dispatch = all(direct[marker] > 0 for marker in MARKERS)
    child_supports_patch_dispatch = all(child[marker] > 0 for marker in MARKERS)
    return {
        "schema_version": 1,
        "direct_host": str(direct_host),
        "child_host": str(child_host),
        "direct_marker_counts": direct,
        "child_marker_counts": child,
        "direct_supports_patch_dispatch": direct_supports_patch_dispatch,
        "child_supports_patch_dispatch": child_supports_patch_dispatch,
        "verdict": "host_registration_gap"
        if direct_supports_patch_dispatch and not child_supports_patch_dispatch
        else "inconclusive",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct-host", type=Path, required=True)
    parser.add_argument("--child-host", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.direct_host, args.child_host)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["verdict"] != "host_registration_gap":
        raise SystemExit("P114 host-registration probe is inconclusive")


if __name__ == "__main__":
    main()
