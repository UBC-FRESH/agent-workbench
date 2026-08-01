#!/usr/bin/env python3
"""Fit preflight for popup provider deployments.

Reads a target descriptor and a launch profile, looks up the model's VRAM
requirement in the catalog, and reports whether the target has enough VRAM.
Also performs a billing/right-sizing analysis when the target exposes
sufficient billing metadata (TRESBillingWeights, PriorityFlags).

Exit codes:
  0 — model fits (with recommended TP)
  1 — model does not fit; print explanation and suggested alternatives
  2 — catalog lookup failed or invalid input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = SCRIPT_DIR / "catalog.json"

# Heuristic: vLLM keeps model weights in VRAM, so host RAM need is dominated
# by the Python process, tokenizer, and KV-cache bookkeeping — typically
# ~1.0-1.5 GB regardless of model size. This is the default assumed host
# memory need when the catalog entry does not carry a measured value.
DEFAULT_HOST_MEMORY_GB = 1.5

# Threshold ratio: flag requested memory when it exceeds estimated need by
# this factor. 2x is the "materially oversized" boundary.
MEMORY_OVERSIZE_RATIO = 2.0


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_catalog_entry(
    catalog: dict[str, Any],
    model_id: str,
    quantization: str | None = None,
    load_format: str | None = None,
    model_tag: str | None = None,
) -> dict[str, Any] | None:
    """Find the best-matching catalog entry for a model.

    When multiple entries share the same ``model_id`` (e.g. Q4 vs Q5 variants
    of Qwen2.5-Coder-7B), ``model_tag`` disambiguates by exact match on the
    entry's ``model_tag`` field. Without ``model_tag``, the first entry
    matching ``model_id`` (+ optional quantization/load_format) is returned.

    ``model_tag`` is the GGUF quantization tag (e.g. ``"Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M"``)
    or the ModelOpt tag (e.g. ``"Qwen3.6-27B-NVFP4"``). Profiles may carry
    this field to select among variants of the same base model.
    """
    entries = catalog.get("entries", [])

    # Fast path: no ambiguity — single entry per model_id, or no tag filter.
    if model_tag is None:
        candidates = []
        for entry in entries:
            if entry["model_id"] != model_id:
                continue
            if quantization:
                entry_quant = entry.get("quantization")
                if entry_quant is not None and entry_quant != quantization:
                    continue
            if load_format:
                entry_load = entry.get("load_format")
                if entry_load is not None and entry_load != load_format:
                    continue
            candidates.append(entry)
        return candidates[0] if candidates else None

    # Slow path: disambiguate by model_tag.
    # First, try exact model_tag match (with optional quantization/load_format).
    tagged = []
    for entry in entries:
        if entry["model_id"] != model_id:
            continue
        if entry.get("model_tag") != model_tag:
            continue
        if quantization:
            entry_quant = entry.get("quantization")
            if entry_quant is not None and entry_quant != quantization:
                continue
        if load_format:
            entry_load = entry.get("load_format")
            if entry_load is not None and entry_load != load_format:
                continue
        tagged.append(entry)
    if tagged:
        return tagged[0]

    # model_tag provided but no exact match — fall back to any entry with
    # matching model_id (preserves backward compatibility for profiles
    # that don't carry model_tag).
    fallback = [e for e in entries if e["model_id"] == model_id]
    return fallback[0] if fallback else None


def _valid_tp_degrees(
    num_attention_heads: int | None,
    num_key_value_heads: int | None,
    max_tp: int = 8,
) -> list[int]:
    """Return the list of valid TP degrees in ascending order.

    When head counts are unknown (None), all degrees 1..max_tp are valid —
    this preserves backward compatibility for catalog entries that predate
    the head-count metadata.

    When head counts are known, valid TP degrees are those that evenly
    divide both ``num_attention_heads`` and ``num_key_value_heads``. This
    matches vLLM's requirement that TP must partition the attention and KV
    heads evenly across devices (e.g. for Qwen2.5-Coder-7B with 32 attn
    heads and 4 KV heads, valid TP is [1, 2, 4] — not [3, 5, 6, 7]).
    """
    if num_attention_heads is None or num_key_value_heads is None:
        return list(range(1, max_tp + 1))
    valid = []
    for tp in range(1, max_tp + 1):
        if (num_attention_heads % tp == 0) and (num_key_value_heads % tp == 0):
            valid.append(tp)
    return valid


def recommend_tp(
    vram_available_gb: float,
    vram_needed_gb: float,
    num_attention_heads: int | None = None,
    num_key_value_heads: int | None = None,
    profile_attention_heads: int | None = None,
    profile_num_key_value_heads: int | None = None,
) -> int:
    """Recommend tensor parallelism degree.

    If the model fits on one GPU, TP=1. Otherwise, scale up TP until the
    per-GPU burden fits. Returns the recommended TP degree.

    Head metadata is resolved from catalog entry first, then profile as
    fallback. When head counts are unknown (None after both lookups), all
    degrees 1..8 are considered (backward-compatible with older catalog
    entries and profiles without head metadata).

    When head counts are known, only TP degrees that evenly divide both
    ``num_attention_heads`` and ``num_key_value_heads`` are considered.
    This prevents selecting invalid TP values like 3 for a model with 32
    attention heads and 4 KV heads (where valid TP is [1, 2, 4]).
    """
    # Resolve from catalog entry first, profile as fallback.
    num_attn = num_attention_heads or profile_attention_heads
    num_kv = num_key_value_heads or profile_num_key_value_heads

    if vram_available_gb > vram_needed_gb:
        return 1
    valid = _valid_tp_degrees(num_attn, num_kv)
    for tp in valid:
        if tp == 1:
            continue  # already handled above
        if (vram_available_gb * tp) > vram_needed_gb:
            return tp
    return 0  # cannot fit even with max valid TP


def check_fit(
    target: dict[str, Any],
    profile: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    """Run the fit check and return a result dict."""
    model_id = profile["model_id"]
    quantization = profile.get("quantization") or None
    load_format = profile.get("load_format") or None
    # model_tag/variant from profile disambiguates among same-model_id variants.
    model_tag = profile.get("model_tag") or profile.get("variant") or None
    gpus = target["gpus_per_job"]
    vram_per_gpu = target["vram_per_gpu_gb"]
    total_vram = gpus * vram_per_gpu

    entry = find_catalog_entry(catalog, model_id, quantization, load_format, model_tag)
    if entry is None:
        result: dict[str, Any] = {
            "fits": False,
            "reason": f"Model '{model_id}' not found in VRAM catalog",
            "model_id": model_id,
            "gpus_requested": gpus,
            "vram_per_gpu_gb": vram_per_gpu,
            "total_vram_gb": total_vram,
            "suggestions": [],
        }
        result.update(analyze_billing(target, profile, catalog, model_tag))
        return result

    vram_needed = entry["vram_with_kv_headroom_gb"]
    num_attn = entry.get("num_attention_heads") or profile.get("attention_heads")
    num_kv = entry.get("num_key_value_heads") or profile.get("num_key_value_heads")
    tp = recommend_tp(
        vram_per_gpu, vram_needed, num_attn, num_kv,
        profile_attention_heads=profile.get("attention_heads"),
        profile_num_key_value_heads=profile.get("num_key_value_heads"),
    )

    if tp == 0 or tp > gpus:
        result = {
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
        result.update(analyze_billing(target, profile, catalog, model_tag))
        return result

    # Defect 10 gate: architecture / kernel support.
    cap = check_capabilities(target, entry)
    if not cap.get("compatible", True):
        result = {
            "fits": False,
            "reason": (
                f"Model '{model_id}' fits in VRAM (TP={tp}, ~{vram_needed}GB) "
                f"but the target runtime cannot execute it: {cap['reason']}"
            ),
            "model_id": model_id,
            "vram_required_gb": vram_needed,
            "gpus_requested": gpus,
            "vram_per_gpu_gb": vram_per_gpu,
            "total_vram_gb": total_vram,
            "recommended_tp": tp,
            "catalog_entry": entry,
            "capabilities_gate": cap,
            "capabilities_failure": cap.get("failure"),
            "suggestions": _suggest_alternatives(catalog, model_id, total_vram),
        }
        result.update(analyze_billing(target, profile, catalog, model_tag))
        return result

    result = {
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
        "capabilities_gate": cap,
    }
    result.update(analyze_billing(target, profile, catalog, model_tag))
    return result


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


def parse_memory_value(value: str | float | int) -> float:
    """Parse a memory value string like '120G', '500M', '5.00G' into GB.

    Accepts:
      - float/int: returned as-is (already in GB)
      - '120G' / '120g': 120 GB
      - '500M' / '500m': 0.5 GB
      - '4T' / '4t': 4096 GB
    """
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*([KMGT]?)i?[Bb]?$", s, re.IGNORECASE)
    if not m:
        raise ValueError(f"Cannot parse memory value: {value!r}")
    num = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    multipliers = {
        "": 1,
        "K": 1 / (1024**2),
        "M": 1 / 1024,
        "G": 1,
        "T": 1024,
    }
    return num * multipliers.get(suffix, 1)


def parse_billing_weights(
    weights: dict[str, Any] | None,
) -> dict[str, float]:
    """Parse TRESBillingWeights into a normalized {tres: weight_float} dict.

    Values may be plain numbers or memory strings (e.g. '5.00G').
    Memory-valued weights are converted to GB for comparison.
    """
    if not weights:
        return {}
    result: dict[str, float] = {}
    for key, val in weights.items():
        if isinstance(val, (int, float)):
            result[key] = float(val)
        elif isinstance(val, str):
            # Try to parse as memory first, then as plain number
            try:
                result[key] = parse_memory_value(val)
            except ValueError:
                result[key] = float(val)
        else:
            result[key] = float(val)
    return result


def estimate_host_memory_gb(
    profile: dict[str, Any],
    catalog: dict[str, Any],
    model_tag: str | None = None,
) -> float:
    """Estimate the host RAM needed by the vLLM process.

    Prefers a measured value from the catalog entry (host_memory_gb). Falls
    back to the heuristic DEFAULT_HOST_MEMORY_GB since vLLM keeps weights
    in VRAM and host RAM is dominated by process overhead.
    """
    model_id = profile["model_id"]
    quantization = profile.get("quantization") or None
    load_format = profile.get("load_format") or None
    entry = find_catalog_entry(catalog, model_id, quantization, load_format, model_tag)
    if entry and "host_memory_gb" in entry and entry["host_memory_gb"] is not None:
        return float(entry["host_memory_gb"])
    return DEFAULT_HOST_MEMORY_GB


def analyze_billing(
    target: dict[str, Any],
    profile: dict[str, Any],
    catalog: dict[str, Any],
    model_tag: str | None = None,
) -> dict[str, Any]:
    """Analyze billing dimensions and right-sizing for the request.

    Returns a structured analysis when the target exposes sufficient billing
    metadata. Returns an empty dict if the target lacks the fields needed
    to compute anything meaningful.
    """
    tres_weights = target.get("tres_billing_weights")
    priority_flags = target.get("priority_flags")

    if not tres_weights and not priority_flags:
        return {}

    weights = parse_billing_weights(tres_weights)
    if not weights:
        return {}

    # Extract requested TRES dimensions from the target
    requested_cpu = target.get("cpus_per_task") or target.get("cpus") or 0
    requested_mem_str = target.get("mem")
    requested_mem_gb = parse_memory_value(requested_mem_str) if requested_mem_str else 0.0
    requested_gpus = target.get("gpus_per_job", 0)

    # Compute weighted terms for each dimension
    weighted_terms: dict[str, float] = {}
    if requested_cpu > 0 and "CPU" in weights:
        weighted_terms["CPU"] = requested_cpu * weights["CPU"]
    if requested_mem_gb > 0 and "Mem" in weights:
        weighted_terms["Mem"] = requested_mem_gb * weights["Mem"]
    # gres/gpu weight applies per GPU
    if requested_gpus > 0 and "gres/gpu" in weights:
        weighted_terms["gres/gpu"] = requested_gpus * weights["gres/gpu"]

    # Determine the billed figure based on priority flags
    billed = 0.0
    billed_method = "unknown"
    if priority_flags:
        pf = str(priority_flags).upper()
        if "MAX_TRES" in pf or "MAX" in pf:
            billed = max(weighted_terms.values()) if weighted_terms else 0.0
            billed_method = "MAX_TRES"
        elif "SUM" in pf or "TOTAL" in pf:
            billed = sum(weighted_terms.values())
            billed_method = "SUM_TRES"
        else:
            # Default: use MAX_TRES semantics (most common on Slurm partitions)
            billed = max(weighted_terms.values()) if weighted_terms else 0.0
            billed_method = "MAX_TRES (default)"

    # Estimate host memory need and check for oversizing
    estimated_host_mem = estimate_host_memory_gb(profile, catalog, model_tag)
    mem_ratio = requested_mem_gb / estimated_host_mem if estimated_host_mem > 0 else 0.0
    mem_oversized = mem_ratio > MEMORY_OVERSIZE_RATIO

    # Identify the cost driver dimension
    cost_driver = max(weighted_terms, key=weighted_terms.get) if weighted_terms else None

    # Build right-sizing suggestion
    suggestions: list[str] = []
    if mem_oversized:
        suggested_mem_gb = round(estimated_host_mem * 1.5)  # 50% headroom
        if requested_mem_str:
            suggestions.append(
                f"Memory is {mem_ratio:.1f}x estimated need "
                f"({requested_mem_gb:.0f}G requested vs ~{estimated_host_mem:.1f}G estimated). "
                f"Consider {suggested_mem_gb}G."
            )
    if requested_gpus > 1:
        # GPU billing is usually per-GPU; suggest TP-aware sizing
        vram_needed, num_attn, num_kv = _get_tp_params(profile, catalog, model_tag)
        tp = recommend_tp(
            target.get("vram_per_gpu_gb", 0),
            vram_needed,
            num_attn,
            num_kv,
        )
        if tp > 0 and tp < requested_gpus:
            suggestions.append(
                f"GPU request ({requested_gpus}) exceeds TP={tp} needed. "
                f"Reducing to {tp} GPU(s) does not change MAX_TRES billing "
                f"but frees contended capacity."
            )

    return {
        "billing_analysis": {
            "has_billing_metadata": bool(tres_weights),
            "priority_flags": priority_flags,
            "tres_billing_weights": weights,
            "requested": {
                "cpus": requested_cpu,
                "mem_gb": requested_mem_gb,
                "gpus": requested_gpus,
            },
            "weighted_terms": weighted_terms,
            "billed_value": billed,
            "billed_method": billed_method,
            "cost_driver": cost_driver,
            "estimated_host_memory_gb": estimated_host_mem,
            "mem_requested_gb": requested_mem_gb,
            "mem_ratio": round(mem_ratio, 2),
            "mem_oversized": mem_oversized,
            "suggestions": suggestions,
        },
    }


def _get_vram_needed(
    profile: dict[str, Any], catalog: dict[str, Any], model_tag: str | None = None
) -> float:
    """Return the VRAM needed for the profile's model (for TP suggestion)."""
    model_id = profile["model_id"]
    quantization = profile.get("quantization") or None
    load_format = profile.get("load_format") or None
    entry = find_catalog_entry(catalog, model_id, quantization, load_format, model_tag)
    if entry:
        return entry["vram_with_kv_headroom_gb"]
    return 0.0


def _get_tp_params(
    profile: dict[str, Any], catalog: dict[str, Any], model_tag: str | None = None
) -> tuple[float, int | None, int | None]:
    """Return (vram_needed, num_attention_heads, num_key_value_heads) for the profile's model."""
    model_id = profile["model_id"]
    quantization = profile.get("quantization") or None
    load_format = profile.get("load_format") or None
    entry = find_catalog_entry(catalog, model_id, quantization, load_format, model_tag)
    if entry:
        return (
            entry["vram_with_kv_headroom_gb"],
            entry.get("num_attention_heads"),
            entry.get("num_key_value_heads"),
        )
    return (0.0, None, None)


# ---------------------------------------------------------------------------
# Defect 10: architecture / kernel support gate
# ---------------------------------------------------------------------------

def check_capabilities(
    target: dict[str, Any],
    entry: dict[str, Any],
) -> dict[str, Any]:
    """Check whether the target's runtime can execute the model's architecture.

    This is a *separate* gate from VRAM fit. A model may fit comfortably in
    VRAM but still be unloadable because the target's vLLM build lacks the
    compiled kernels its architecture requires (e.g. MoE kernels on an
    sm70/Volta build).

    Returns one of:
      - {"compatible": True, "skipped": True, "reason": "..."}
          when the target declares no capabilities or the catalog carries no
          requirements — the gate is inert and VRAM fit alone decides.
      - {"compatible": True, "reason": "..."}
          when both sides carry metadata and the model passes.
      - {"compatible": False, "reason": "...", "failure": "<tag>"}
          when metadata is present and the model fails. ``failure`` is one of
          ``unsupported_architecture`` or ``missing_kernel``.

    The target declares capabilities via optional fields:
      - ``supported_architectures``: list of architecture class names the
        runtime recognizes (e.g. ``["LlamaForCausalLM", "MistralForCausalLM"]``).
      - ``supported_kernels``: list of kernel / op namespace prefixes the
        runtime has compiled (e.g. ``["_moe_C.topk_softmax"]``).

    The catalog entry declares requirements via optional fields:
      - ``architecture``: the model's architecture class name (e.g.
        ``"Qwen3MoeForCausalLM"``).
      - ``required_kernels``: list of kernel / op namespace prefixes the
        runtime must provide (e.g. ``["_moe_C.topk_softmax"]``).

    When either side is silent the gate is skipped — never a false reject.
    """
    target_archs = target.get("supported_architectures")
    target_kernels = target.get("supported_kernels")
    model_arch = entry.get("architecture")
    model_kernels = entry.get("required_kernels")

    # If neither side has metadata, skip silently.
    # Use `is not None` so an explicit empty list (meaning "declared nothing
    # is supported") is distinct from "field absent".
    any_target_cap = target_archs is not None or target_kernels is not None
    any_model_req = model_arch is not None or model_kernels is not None
    if not any_target_cap or not any_model_req:
        return {
            "compatible": True,
            "skipped": True,
            "reason": (
                "Capability gate skipped: target has no declared capabilities "
                "or catalog carries no architecture/kernel requirements."
            ),
        }

    # Architecture check.
    if model_arch and target_archs is not None:
        if model_arch not in target_archs:
            return {
                "compatible": False,
                "failure": "unsupported_architecture",
                "reason": (
                    f"Target does not declare support for architecture "
                    f"'{model_arch}'. Supported: {target_archs}."
                ),
            }

    # Kernel check.
    if model_kernels and target_kernels is not None:
        missing = [k for k in model_kernels if k not in target_kernels]
        if missing:
            return {
                "compatible": False,
                "failure": "missing_kernel",
                "reason": (
                    f"Target runtime is missing required kernels "
                    f"{missing}. Declared target kernels: {target_kernels}."
                ),
            }

    return {
        "compatible": True,
        "reason": (
            f"Architecture '{model_arch}' and required kernels "
            f"{model_kernels} are supported by this target."
        ),
    }


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
        # Billing analysis (present when target has billing metadata)
        billing = result.get("billing_analysis")
        if billing and billing.get("has_billing_metadata"):
            print("\n--- Billing Analysis ---")
            print(
                f"  Method: {billing['billed_method']}  |  "
                f"Billed value: {billing['billed_value']:.1f}"
            )
            if billing.get("cost_driver"):
                print(f"  Cost driver: {billing['cost_driver']}")
            req = billing["requested"]
            print(
                f"  Requested: CPU={req['cpus']}  "
                f"Mem={req['mem_gb']:.0f}G  "
                f"GPUs={req['gpus']}"
            )
            if billing.get("weighted_terms"):
                print("  Weighted terms:")
                for dim, val in billing["weighted_terms"].items():
                    print(f"    {dim}: {val:.1f}")
            if billing.get("suggestions"):
                print("\n  Right-sizing suggestions:")
                for s in billing["suggestions"]:
                    print(f"    - {s}")

    return 0 if result["fits"] else 1


if __name__ == "__main__":
    sys.exit(main())