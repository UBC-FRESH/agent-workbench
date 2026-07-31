#!/usr/bin/env python3
"""Fit preflight for popup provider deployments.

Reads a target descriptor and a launch profile, looks up the model's VRAM
requirement in the catalog, and reports whether the target has enough VRAM.

Exit codes:
  0 — model fits (with recommended TP)
  1 — model does not fit; print explanation and suggested alternatives
  2 — catalog lookup failed or invalid input
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = SCRIPT_DIR / "catalog.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_catalog_entry(
    catalog: dict[str, Any],
    model_id: str,
    quantization: str | None = None,
    load_format: str | None = None,
) -> dict[str, Any] | None:
    """Find the best-matching catalog entry for a model."""
    entries = catalog.get("entries", [])
    candidates = []
    for entry in entries:
        if entry["model_id"] != model_id:
            continue
        # Prefer exact quantization/load_format match
        if quantization and entry.get("quantization") != quantization:
            continue
        if load_format and entry.get("load_format") != load_format:
            continue
        candidates.append(entry)
    if not candidates:
        # Fall back to any entry with matching model_id
        candidates = [e for e in entries if e["model_id"] == model_id]
    return candidates[0] if candidates else None


def recommend_tp(vram_available_gb: float, vram_needed_gb: float) -> int:
    """Recommend tensor parallelism degree.

    If the model fits on one GPU, TP=1. Otherwise, scale up TP until the
    per-GPU burden fits. Returns the recommended TP degree.
    """
    if vram_available_gb >= vram_needed_gb:
        return 1
    # Scale TP until per-GPU VRAM is sufficient
    for tp in range(2, 9):
        if (vram_available_gb * tp) >= vram_needed_gb:
            return tp
    return 0  # cannot fit even with max TP


def check_fit(
    target: dict[str, Any],
    profile: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    """Run the fit check and return a result dict."""
    model_id = profile["model_id"]
    quantization = profile.get("quantization") or None
    load_format = profile.get("load_format") or None
    gpus = target["gpus_per_job"]
    vram_per_gpu = target["vram_per_gpu_gb"]
    total_vram = gpus * vram_per_gpu

    entry = find_catalog_entry(catalog, model_id, quantization, load_format)
    if entry is None:
        return {
            "fits": False,
            "reason": f"Model '{model_id}' not found in VRAM catalog",
            "model_id": model_id,
            "gpus_requested": gpus,
            "vram_per_gpu_gb": vram_per_gpu,
            "total_vram_gb": total_vram,
            "suggestions": [],
        }

    vram_needed = entry["vram_with_kv_headroom_gb"]
    tp = recommend_tp(vram_per_gpu, vram_needed)

    if tp == 0 or tp > gpus:
        return {
            "fits": False,
            "reason": (
                f"Model '{model_id}' requires ~{vram_needed}GB with KV headroom. "
                f"Target has {total_vram}GB across {gpus}x{vram_per_gpu}GB GPUs. "
                f"Even with TP={min(tp, 8)}, per-GPU burden exceeds capacity."
            ),
            "model_id": model_id,
            "vram_required_gb": vram_needed,
            "gpus_requested": gpus,
            "vram_per_gpu_gb": vram_per_gpu,
            "total_vram_gb": total_vram,
            "recommended_tp": 0,
            "suggestions": _suggest_alternatives(catalog, model_id, total_vram),
        }

    return {
        "fits": True,
        "reason": (
            f"Model '{model_id}' fits on {gpus}x{vram_per_gpu}GB GPUs with TP={tp}. "
            f"Required VRAM: ~{vram_needed}GB."
        ),
        "model_id": model_id,
        "vram_required_gb": vram_needed,
        "gpus_requested": gpus,
        "vram_per_gpu_gb": vram_per_gpu,
        "total_vram_gb": total_vram,
        "recommended_tp": tp,
        "catalog_entry": entry,
    }


def _suggest_alternatives(
    catalog: dict[str, Any],
    excluded_model_id: str,
    total_vram_gb: float,
) -> list[str]:
    """Suggest smaller models from the catalog that fit."""
    suggestions = []
    for entry in catalog.get("entries", []):
        if entry["model_id"] == excluded_model_id:
            continue
        needed = entry["vram_with_kv_headroom_gb"]
        if needed <= total_vram_gb:
            suggestions.append(
                f"- {entry['model_id']} ({entry.get('variant', 'unknown')}): "
                f"~{needed}GB required"
            )
    return suggestions[:5]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fit preflight: check if a model fits a target's VRAM"
    )
    parser.add_argument(
        "--target", required=True, type=Path,
        help="Path to target descriptor YAML"
    )
    parser.add_argument(
        "--profile", required=True, type=Path,
        help="Path to launch profile YAML"
    )
    parser.add_argument(
        "--catalog", type=Path, default=CATALOG_PATH,
        help="Path to VRAM catalog JSON (default: catalog.json next to this script)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output result as JSON"
    )
    args = parser.parse_args()

    # Load target and profile as JSON (YAML is a superset; for simple
    # key:value pairs this works. For full YAML support, install PyYAML).
    try:
        import yaml
        target = yaml.safe_load(args.target.read_text())
        profile = yaml.safe_load(args.profile.read_text())
    except ImportError:
        # Fallback: treat as JSON
        target = json.loads(args.target.read_text())
        profile = json.loads(args.profile.read_text())

    catalog = load_json(args.catalog)
    result = check_fit(target, profile, catalog)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["fits"]:
            print(f"OK: {result['reason']}")
        else:
            print(f"FAIL: {result['reason']}")
            if result.get("suggestions"):
                print("\nSuggested alternatives that fit:")
                for s in result["suggestions"]:
                    print(s)

    return 0 if result["fits"] else 1


if __name__ == "__main__":
    sys.exit(main())