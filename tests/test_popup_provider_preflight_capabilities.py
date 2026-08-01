"""Focused tests for popup-provider preflight architecture/kernel gate.

Covers defect 10: preflight must reject a model whose architecture or required
kernel is not available on the target runtime, even when VRAM fit is fine.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure the module is importable regardless of cwd.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "playbooks" / "popup_provider" / "preflight"))

from check import (  # noqa: E402
    check_capabilities,
    check_fit,
    find_catalog_entry,
    recommend_tp,
    _valid_tp_degrees,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# A target that supports a narrow set of architectures and kernels — simulates
# an sm70/Volta build that recognizes standard ARCs but has no MoE kernels.
VOLTA_TARGET = {
    "name": "sockeye-volta",
    "gpus_per_job": 4,
    "vram_per_gpu_gb": 32,
    "supported_architectures": [
        "LlamaForCausalLM",
        "MistralForCausalLM",
        "Qwen2ForCausalLM",
        "Qwen2_5_CoderForCausalLM",
    ],
    "supported_kernels": [
        "_quant_C.dequantize",
        "_cuda_C.flash_attn_fwd",
    ],
}

# A target with full modern support — simulates an H100/sm80 build.
H100_TARGET = {
    "name": "alliance-h100",
    "gpus_per_job": 1,
    "vram_per_gpu_gb": 80,
    "supported_architectures": [
        "LlamaForCausalLM",
        "MistralForCausalLM",
        "Qwen2ForCausalLM",
        "Qwen2_5_CoderForCausalLM",
        "Qwen3MoeForCausalLM",
        "DeepseekV2ForCausalLM",
    ],
    "supported_kernels": [
        "_quant_C.dequantize",
        "_cuda_C.flash_attn_fwd",
        "_moe_C.topk_softmax",
    ],
}

# A catalog entry for a standard causal-LM model (fits on both targets).
CAUSALLM_ENTRY = {
    "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
    "architecture": "Qwen2_5_CoderForCausalLM",
    "required_kernels": ["_quant_C.dequantize"],
    "vram_with_kv_headroom_gb": 8.0,
}

# A catalog entry for the MoE model that triggered defect 10.
MOE_ENTRY = {
    "model_id": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "architecture": "Qwen3MoeForCausalLM",
    "required_kernels": ["_moe_C.topk_softmax"],
    "vram_with_kv_headroom_gb": 42.0,
}

# A catalog entry with no architecture/kernel metadata.
NO_META_ENTRY = {
    "model_id": "bartowski/UnknownModel",
    "vram_with_kv_headroom_gb": 8.0,
}

PROFILE_STANDARD = {
    "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
    "quantization": "gguf",
    "load_format": "gguf",
}

PROFILE_MOE = {
    "model_id": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "quantization": "",
    "load_format": "",
}


# ---------------------------------------------------------------------------
# check_capabilities — architecture supported
# ---------------------------------------------------------------------------

class TestArchitectureSupported:
    def test_standard_model_passes_on_volta(self):
        result = check_capabilities(VOLTA_TARGET, CAUSALLM_ENTRY)
        assert result["compatible"] is True
        assert result.get("skipped") is not True
        assert "Qwen2_5_CoderForCausalLM" in result["reason"]

    def test_moe_model_passes_on_h100(self):
        result = check_capabilities(H100_TARGET, MOE_ENTRY)
        assert result["compatible"] is True
        assert result.get("skipped") is not True

    def test_standard_model_passes_on_h100(self):
        result = check_capabilities(H100_TARGET, CAUSALLM_ENTRY)
        assert result["compatible"] is True


# ---------------------------------------------------------------------------
# check_capabilities — architecture rejected
# ---------------------------------------------------------------------------

class TestArchitectureRejected:
    def test_moe_model_rejected_on_volta(self):
        result = check_capabilities(VOLTA_TARGET, MOE_ENTRY)
        assert result["compatible"] is False
        assert result["failure"] == "unsupported_architecture"
        assert "Qwen3MoeForCausalLM" in result["reason"]
        assert "supported_architectures" in result["reason"].lower() or \
               "Qwen3MoeForCausalLM" in result["reason"]

    def test_reject_reason_names_supported_list(self):
        result = check_capabilities(VOLTA_TARGET, MOE_ENTRY)
        # The reason should mention what architectures ARE supported.
        assert "LlamaForCausalLM" in result["reason"]


# ---------------------------------------------------------------------------
# check_capabilities — missing kernel rejected
# ---------------------------------------------------------------------------

class TestMissingKernelRejected:
    def test_required_kernel_missing(self):
        """Target supports the architecture but lacks the required kernel."""
        arch_supports_moe = {
            "supported_architectures": ["Qwen3MoeForCausalLM"],
            "supported_kernels": ["_quant_C.dequantize"],
            # Missing _moe_C.topk_softmax
        }
        result = check_capabilities(arch_supports_moe, MOE_ENTRY)
        assert result["compatible"] is False
        assert result["failure"] == "missing_kernel"
        assert "_moe_C.topk_softmax" in result["reason"]

    def test_partial_kernel_coverage(self):
        """Target has some required kernels but not all — should still reject."""
        partial_target = {
            "supported_architectures": ["Qwen3MoeForCausalLM"],
            "supported_kernels": ["_quant_C.dequantize"],
            # Missing _moe_C.topk_softmax
        }
        result = check_capabilities(partial_target, MOE_ENTRY)
        assert result["compatible"] is False
        assert result["failure"] == "missing_kernel"

    def test_all_kernels_present(self):
        """When all required kernels are in the target, no reject."""
        result = check_capabilities(H100_TARGET, MOE_ENTRY)
        assert result["compatible"] is True


# ---------------------------------------------------------------------------
# check_capabilities — metadata absent / skipped
# ---------------------------------------------------------------------------

class TestMetadataAbsentSkipped:
    def test_no_target_capabilities_skips(self):
        """Target with no capability fields → gate skipped."""
        silent_target = {"gpus_per_job": 1, "vram_per_gpu_gb": 80}
        result = check_capabilities(silent_target, MOE_ENTRY)
        assert result["compatible"] is True
        assert result["skipped"] is True
        assert "skipped" in result["reason"].lower()

    def test_no_model_requirements_skips(self):
        """Catalog entry with no arch/kernel fields → gate skipped."""
        result = check_capabilities(VOLTA_TARGET, NO_META_ENTRY)
        assert result["compatible"] is True
        assert result["skipped"] is True

    def test_neither_side_has_metadata_skips(self):
        silent_target = {"gpus_per_job": 1, "vram_per_gpu_gb": 80}
        result = check_capabilities(silent_target, NO_META_ENTRY)
        assert result["compatible"] is True
        assert result["skipped"] is True

    def test_target_has_arch_but_no_kernels_skips_kernel_check(self):
        """If target only declares architectures (no kernels), kernel check
        is skipped — only architecture gate is active."""
        arch_only_target = {
            "supported_architectures": ["Qwen3MoeForCausalLM"],
            # No supported_kernels
        }
        result = check_capabilities(arch_only_target, MOE_ENTRY)
        # Architecture passes, kernel check skipped → compatible
        assert result["compatible"] is True
        assert result.get("skipped") is not True

    def test_model_has_arch_but_no_kernels_skips_kernel_check(self):
        """If model only declares architecture (no required_kernels), kernel
        check is skipped — only architecture gate is active."""
        arch_only_entry = {
            "architecture": "Qwen3MoeForCausalLM",
            # No required_kernels
        }
        result = check_capabilities(VOLTA_TARGET, arch_only_entry)
        # Architecture is NOT in target → rejected
        assert result["compatible"] is False
        assert result["failure"] == "unsupported_architecture"


# ---------------------------------------------------------------------------
# check_capabilities — empty lists
# ---------------------------------------------------------------------------

class TestEmptyLists:
    def test_empty_target_architectures_rejects_any_model(self):
        """An empty supported_architectures list means nothing is supported."""
        empty_target = {
            "supported_architectures": [],
            "supported_kernels": ["_moe_C.topk_softmax"],
        }
        result = check_capabilities(empty_target, MOE_ENTRY)
        assert result["compatible"] is False
        assert result["failure"] == "unsupported_architecture"

    def test_empty_target_kernels_rejects_model_with_kernels(self):
        empty_target = {
            "supported_architectures": ["Qwen3MoeForCausalLM"],
            "supported_kernels": [],
        }
        result = check_capabilities(empty_target, MOE_ENTRY)
        assert result["compatible"] is False
        assert result["failure"] == "missing_kernel"

    def test_empty_model_kernels_passes(self):
        """If model declares no required kernels, kernel check is inert."""
        no_kernel_entry = {
            "architecture": "LlamaForCausalLM",
            "required_kernels": [],
        }
        result = check_capabilities(VOLTA_TARGET, no_kernel_entry)
        assert result["compatible"] is True


# ---------------------------------------------------------------------------
# check_fit integration — VRAM fit + capabilities pass
# ---------------------------------------------------------------------------

class TestCheckFitIntegration:
    def test_fit_with_capabilities_pass(self):
        """When both VRAM and capabilities pass, result is fits=True."""
        catalog = {"entries": [CAUSALLM_ENTRY]}
        result = check_fit(VOLTA_TARGET, PROFILE_STANDARD, catalog)
        assert result["fits"] is True
        assert result["capabilities_gate"]["compatible"] is True

    def test_fit_with_capabilities_fail(self):
        """When VRAM fits but capabilities fail, result is fits=False."""
        catalog = {"entries": [MOE_ENTRY]}
        result = check_fit(VOLTA_TARGET, PROFILE_MOE, catalog)
        assert result["fits"] is False
        # VOLTA_TARGET does not declare Qwen3MoeForCausalLM → architecture fail.
        assert result["capabilities_failure"] == "unsupported_architecture"
        assert "capabilities_gate" in result
        assert "Qwen3MoeForCausalLM" in result["reason"]

    def test_fit_preserves_vram_fields_on_capability_reject(self):
        """Even on capability reject, VRAM fields are still reported."""
        catalog = {"entries": [MOE_ENTRY]}
        result = check_fit(VOLTA_TARGET, PROFILE_MOE, catalog)
        assert result["vram_required_gb"] == 42.0
        assert result["gpus_requested"] == 4
        assert result["total_vram_gb"] == 128
        assert result["recommended_tp"] > 0

    def test_fit_preserves_billing_when_metadata_present(self):
        """Billing analysis still runs alongside capability gate."""
        billing_target = {
            "gpus_per_job": 4,
            "vram_per_gpu_gb": 32,
            "tres_billing_weights": {"CPU": 1.0, "Mem": "5.00G", "gres/gpu": 6.0},
            "priority_flags": "MAX_TRES",
            "supported_kernels": [],
        }
        catalog = {"entries": [MOE_ENTRY]}
        result = check_fit(billing_target, PROFILE_MOE, catalog)
        assert result["fits"] is False
        assert "billing_analysis" in result
        assert result["billing_analysis"]["has_billing_metadata"] is True

    def test_fit_skips_capability_gate_when_no_metadata(self):
        """When catalog has no arch/kernel fields, gate is skipped."""
        catalog = {"entries": [NO_META_ENTRY]}
        profile = {"model_id": "bartowski/UnknownModel", "quantization": "", "load_format": ""}
        result = check_fit(VOLTA_TARGET, profile, catalog)
        assert result["fits"] is True
        cg = result["capabilities_gate"]
        assert cg["skipped"] is True

    def test_fit_vram_fail_short_circuits_capabilities(self):
        """When VRAM doesn't fit, capabilities gate is not consulted."""
        tiny_target = {
            "gpus_per_job": 1,
            "vram_per_gpu_gb": 8,
            "supported_kernels": ["_moe_C.topk_softmax"],
        }
        catalog = {"entries": [MOE_ENTRY]}
        result = check_fit(tiny_target, PROFILE_MOE, catalog)
        assert result["fits"] is False
        # VRAM failure reason, not capability failure.
        assert "VRAM" in result["reason"] or "requires" in result["reason"].lower()
        assert "capabilities_gate" not in result


# ---------------------------------------------------------------------------
# JSON output — machine-readable structure
# ---------------------------------------------------------------------------

class TestJsonOutput:
    def test_capability_failure_is_distinct_tag(self):
        """The failure reason is a stable machine-readable tag."""
        catalog = {"entries": [MOE_ENTRY]}
        result = check_fit(VOLTA_TARGET, PROFILE_MOE, catalog)
        # Must be one of the two defined tags.
        assert result["capabilities_failure"] in (
            "unsupported_architecture",
            "missing_kernel",
        )

    def test_compatibile_result_has_no_failure_tag(self):
        catalog = {"entries": [CAUSALLM_ENTRY]}
        result = check_fit(VOLTA_TARGET, PROFILE_STANDARD, catalog)
        assert result["fits"] is True
        assert result.get("capabilities_failure") is None


# ---------------------------------------------------------------------------
# recommend_tp — head-count divisor constraint (defect 9 / F9)
# ---------------------------------------------------------------------------

class TestRecommendTpHeadDivisor:
    """TP must evenly divide both attention heads and KV heads.

    For Qwen2.5-Coder-7B (32 attn, 4 KV): valid TP = [1, 2, 4].
    TP=3, 5, 6, 7 must be rejected even if VRAM would fit.
    """

    def test_valid_tp_degrees_qwen25_7b(self):
        """Qwen2.5-Coder-7B: 32 attn, 4 KV → valid TP = [1, 2, 4]."""
        assert _valid_tp_degrees(32, 4) == [1, 2, 4]

    def test_valid_tp_degrees_no_heads_returns_all(self):
        """Without head counts, all TP degrees 1..8 are valid (backward compat)."""
        assert _valid_tp_degrees(None, None) == list(range(1, 9))

    def test_recommend_tp_uses_valid_degrees_only(self):
        """recommend_tp returns TP=1 when model fits on one GPU regardless of heads."""
        # 32GB GPU, need 25GB → fits on one GPU, so TP=1.
        tp = recommend_tp(32.0, 25.0, num_attention_heads=32, num_key_value_heads=4)
        assert tp == 1, f"Expected TP=1 (fits on one GPU), got TP={tp}"

    def test_recommend_tp_skips_invalid_degrees_when_multi_gpu_needed(self):
        """recommend_tp must skip invalid TP degrees even if VRAM fits."""
        # 32GB GPU, need 70GB → TP=2: 64<70 (doesn't fit), TP=3: invalid, TP=4: 128>70 (fits).
        tp = recommend_tp(32.0, 70.0, num_attention_heads=32, num_key_value_heads=4)
        assert tp == 4, f"Expected TP=4 (next valid after 2), got TP={tp}"

    def test_tp3_rejected_for_qwen25_7b(self):
        """TP=3 must never be selected for a model with 32 attn / 4 KV heads.

        This is the core F9 regression: without the divisor check, the old
        linear scan would return TP=3 when 32*3 > vram_needed and 3 was the
        first TP to satisfy the inequality.
        """
        # 32GB GPU, need 60GB → TP=2 gives 64>60, so TP=2 would fit.
        # But test the case where TP=2 doesn't fit but TP=3 would (hypothetical).
        tp = recommend_tp(32.0, 70.0, num_attention_heads=32, num_key_value_heads=4)
        # TP=2: 64 < 70 → doesn't fit. TP=3: invalid (doesn't divide 32 or 4).
        # TP=4: 128 > 70 → fits. Must return 4, not 3.
        assert tp == 4, f"TP=3 must be rejected; got TP={tp}"
        assert tp != 3, "TP=3 must never be selected for 32/4 head config"

    def test_tp5_rejected(self):
        """TP=5 must be rejected for any model where 5 doesn't divide heads."""
        tp = recommend_tp(80.0, 100.0, num_attention_heads=32, num_key_value_heads=4)
        assert tp != 5
        assert tp != 3
        assert tp != 6
        assert tp != 7

    def test_recommend_tp_no_heads_falls_back_to_linear(self):
        """Without head counts, recommend_tp behaves like the old linear scan."""
        tp = recommend_tp(32.0, 50.0)  # no head counts
        assert tp == 2  # 32*2=64>50

    def test_recommend_tp_always_fits_on_one_gpu(self):
        """If VRAM fits on one GPU, TP=1 regardless of head counts."""
        tp = recommend_tp(80.0, 14.0, num_attention_heads=32, num_key_value_heads=4)
        assert tp == 1

    def test_recommend_tp_cannot_fit_returns_zero(self):
        """If no valid TP degree provides enough VRAM, return 0."""
        tp = recommend_tp(8.0, 200.0, num_attention_heads=32, num_key_value_heads=4)
        # Max valid TP=4, 8*4=32 < 200 → return 0
        assert tp == 0

    def test_recommend_tp_in_check_fit_passes_head_counts(self):
        """check_fit must pass head counts from catalog entry to recommend_tp."""
        entry_with_heads = {
            "model_id": "test/model",
            "num_attention_heads": 32,
            "num_key_value_heads": 4,
            "vram_with_kv_headroom_gb": 60.0,
        }
        catalog = {"entries": [entry_with_heads]}
        profile = {"model_id": "test/model", "quantization": "", "load_format": ""}
        target = {"gpus_per_job": 4, "vram_per_gpu_gb": 32}
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        # TP=2: 32*2=64>60 → fits. Valid divisor of 32 and 4.
        assert result["recommended_tp"] == 2


# ---------------------------------------------------------------------------
# find_catalog_entry — model_tag disambiguation (defect 10 / F10)
# ---------------------------------------------------------------------------

class TestFindCatalogEntryDisambiguation:
    """When multiple entries share model_id, model_tag selects the variant.

    Qwen2.5-Coder-7B has Q4_K_M and Q5_K_M entries. Without model_tag, the
    first match wins (backward compatible). With model_tag, the exact variant
    is selected.
    """

    def test_no_tag_returns_first_match(self):
        """Without model_tag, first entry with matching model_id wins."""
        catalog = {
            "entries": [
                {"model_id": "m", "model_tag": "Q4", "vram_with_kv_headroom_gb": 8.0},
                {"model_id": "m", "model_tag": "Q5", "vram_with_kv_headroom_gb": 9.0},
            ]
        }
        entry = find_catalog_entry(catalog, "m")
        assert entry["model_tag"] == "Q4"

    def test_tag_selects_q5_variant(self):
        """model_tag='Q5' must return the Q5 entry, not Q4."""
        catalog = {
            "entries": [
                {"model_id": "m", "model_tag": "Q4_K_M", "vram_with_kv_headroom_gb": 8.0},
                {"model_id": "m", "model_tag": "Q5_K_M", "vram_with_kv_headroom_gb": 9.0},
            ]
        }
        entry = find_catalog_entry(catalog, "m", model_tag="Q5_K_M")
        assert entry["model_tag"] == "Q5_K_M"
        assert entry["vram_with_kv_headroom_gb"] == 9.0

    def test_tag_selects_q4_variant(self):
        """model_tag='Q4' must return the Q4 entry."""
        catalog = {
            "entries": [
                {"model_id": "m", "model_tag": "Q4_K_M", "vram_with_kv_headroom_gb": 8.0},
                {"model_id": "m", "model_tag": "Q5_K_M", "vram_with_kv_headroom_gb": 9.0},
            ]
        }
        entry = find_catalog_entry(catalog, "m", model_tag="Q4_K_M")
        assert entry["model_tag"] == "Q4_K_M"
        assert entry["vram_with_kv_headroom_gb"] == 8.0

    def test_tag_fallback_to_any_match(self):
        """If model_tag doesn't match any entry, fall back to any model_id match."""
        catalog = {
            "entries": [
                {"model_id": "m", "model_tag": "Q4_K_M", "vram_with_kv_headroom_gb": 8.0},
                {"model_id": "m", "model_tag": "Q5_K_M", "vram_with_kv_headroom_gb": 9.0},
            ]
        }
        # Unknown tag → falls back to first model_id match (Q4).
        entry = find_catalog_entry(catalog, "m", model_tag="Q8_K_M")
        assert entry is not None
        assert entry["model_id"] == "m"

    def test_tag_no_match_returns_none(self):
        """If model_tag doesn't match and no model_id match exists, return None."""
        catalog = {
            "entries": [
                {"model_id": "m", "model_tag": "Q4_K_M", "vram_with_kv_headroom_gb": 8.0},
            ]
        }
        entry = find_catalog_entry(catalog, "unknown/model", model_tag="Q4_K_M")
        assert entry is None

    def test_real_qwen25_catalog_q5_returns_q5_vram(self):
        """End-to-end: Qwen2.5-Coder-7B Q5 profile gets Q5 VRAM numbers."""
        # Use the real catalog.
        catalog_path = ROOT / "playbooks" / "popup_provider" / "preflight" / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        entry = find_catalog_entry(
            catalog,
            "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
            model_tag="Qwen2.5-Coder-7B-Instruct-GGUF:Q5_K_M",
        )
        assert entry is not None
        assert entry["model_tag"] == "Qwen2.5-Coder-7B-Instruct-GGUF:Q5_K_M"
        assert entry["vram_with_kv_headroom_gb"] == 9.0

    def test_real_qwen25_catalog_q4_returns_q4_vram(self):
        """End-to-end: Qwen2.5-Coder-7B Q4 profile gets Q4 VRAM numbers."""
        catalog_path = ROOT / "playbooks" / "popup_provider" / "preflight" / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        entry = find_catalog_entry(
            catalog,
            "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
            model_tag="Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M",
        )
        assert entry is not None
        assert entry["model_tag"] == "Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M"
        assert entry["vram_with_kv_headroom_gb"] == 8.0

    def test_check_fit_with_q5_profile_gets_q5_vram(self):
        """check_fit with a Q5 profile must use Q5 VRAM, not Q4."""
        catalog_path = ROOT / "playbooks" / "popup_provider" / "preflight" / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        target = {"gpus_per_job": 1, "vram_per_gpu_gb": 32}
        profile = {
            "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
            "model_tag": "Qwen2.5-Coder-7B-Instruct-GGUF:Q5_K_M",
            "quantization": "gguf",
            "load_format": "gguf",
        }
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        assert result["vram_required_gb"] == 9.0, \
            f"Q5 profile should report 9.0GB, got {result['vram_required_gb']}"


# ---------------------------------------------------------------------------
# Regression: model_tag threading through check_fit (defect F10)
# ---------------------------------------------------------------------------

class TestRegressionModelTagThreading:
    """Regression: a profile carrying model_tag must not silently receive
    the wrong catalog variant. Without model_tag threading, a Q5 profile
    would get the Q4 entry's VRAM number."""

    def test_check_fit_q5_profile_rejects_q4_vram(self):
        """Q5 profile must NOT report Q4 VRAM (8.0GB).

        This is the F10 regression: before model_tag was threaded through
        check_fit, find_catalog_entry was called without model_tag, so the
        first matching entry (Q4, 8.0GB) was returned regardless of the
        profile's Q5 tag.
        """
        catalog = {
            "entries": [
                {
                    "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
                    "model_tag": "Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M",
                    "vram_with_kv_headroom_gb": 8.0,
                },
                {
                    "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
                    "model_tag": "Qwen2.5-Coder-7B-Instruct-GGUF:Q5_K_M",
                    "vram_with_kv_headroom_gb": 9.0,
                },
            ]
        }
        target = {"gpus_per_job": 1, "vram_per_gpu_gb": 32}
        profile = {
            "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
            "model_tag": "Qwen2.5-Coder-7B-Instruct-GGUF:Q5_K_M",
            "quantization": "gguf",
            "load_format": "gguf",
        }
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        assert result["vram_required_gb"] == 9.0, \
            f"Q5 profile must report 9.0GB, not {result['vram_required_gb']}GB"
        # Verify the correct entry was selected.
        assert result["catalog_entry"]["model_tag"] == "Qwen2.5-Coder-7B-Instruct-GGUF:Q5_K_M"

    def test_check_fit_q4_profile_rejects_q5_vram(self):
        """Q4 profile must NOT report Q5 VRAM (9.0GB)."""
        catalog = {
            "entries": [
                {
                    "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
                    "model_tag": "Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M",
                    "vram_with_kv_headroom_gb": 8.0,
                },
                {
                    "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
                    "model_tag": "Qwen2.5-Coder-7B-Instruct-GGUF:Q5_K_M",
                    "vram_with_kv_headroom_gb": 9.0,
                },
            ]
        }
        target = {"gpus_per_job": 1, "vram_per_gpu_gb": 32}
        profile = {
            "model_id": "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF",
            "model_tag": "Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M",
            "quantization": "gguf",
            "load_format": "gguf",
        }
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        assert result["vram_required_gb"] == 8.0, \
            f"Q4 profile must report 8.0GB, not {result['vram_required_gb']}GB"

    def test_check_fit_no_tag_falls_back_to_first_match(self):
        """Without model_tag in profile, first matching entry wins (backward compat)."""
        catalog = {
            "entries": [
                {
                    "model_id": "m",
                    "model_tag": "Q4",
                    "vram_with_kv_headroom_gb": 8.0,
                },
                {
                    "model_id": "m",
                    "model_tag": "Q5",
                    "vram_with_kv_headroom_gb": 9.0,
                },
            ]
        }
        target = {"gpus_per_job": 1, "vram_per_gpu_gb": 32}
        profile = {
            "model_id": "m",
            "quantization": "gguf",
            "load_format": "gguf",
        }
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        assert result["vram_required_gb"] == 8.0, \
            "No model_tag → first match (Q4, 8.0GB) wins"


# ---------------------------------------------------------------------------
# Regression: recommend_tp head-divisor via check_fit (defect F9)
# ---------------------------------------------------------------------------

class TestRegressionTpHeadDivisorInCheckFit:
    """Regression: check_fit must not select arbitrary TP degrees.

    Without head-divisor constraints, recommend_tp would pick TP=3 when
    32*3 > vram_needed, even though TP=3 doesn't evenly divide 32 attn
    heads and 4 KV heads. Valid TP for that config is [1, 2, 4].
    """

    def test_check_fit_rejects_tp3_for_32_4_heads(self):
        """Memory fits at TP=3 (32*3=96 > 90) but valid divisors force TP=4.

        This is the F9 regression scenario: a 32GB GPU, 90GB model with
        32 attn / 4 KV heads. TP=2 gives 64GB < 90 → doesn't fit.
        TP=3 gives 96GB > 90 → would fit, but 3 doesn't divide 32 or 4.
        TP=4 gives 128GB > 90 → fits and is valid.
        """
        catalog = {
            "entries": [
                {
                    "model_id": "test/divisor-model",
                    "architecture": "Qwen2_5_CoderForCausalLM",
                    "num_attention_heads": 32,
                    "num_key_value_heads": 4,
                    "vram_with_kv_headroom_gb": 90.0,
                },
            ]
        }
        target = {"gpus_per_job": 4, "vram_per_gpu_gb": 32}
        profile = {
            "model_id": "test/divisor-model",
            "quantization": "",
            "load_format": "",
        }
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        assert result["recommended_tp"] == 4, \
            f"TP=3 must be rejected for 32/4 heads; got TP={result['recommended_tp']}"
        assert result["recommended_tp"] != 3

    def test_check_fit_profile_head_metadata_as_fallback(self):
        """Profile-level head metadata serves as fallback when catalog entry lacks it."""
        catalog = {
            "entries": [
                {
                    "model_id": "test/no-meta-model",
                    "vram_with_kv_headroom_gb": 90.0,
                    # No num_attention_heads / num_key_value_heads
                },
            ]
        }
        target = {"gpus_per_job": 4, "vram_per_gpu_gb": 32}
        profile = {
            "model_id": "test/no-meta-model",
            "attention_heads": 32,
            "num_key_value_heads": 4,
            "quantization": "",
            "load_format": "",
        }
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        assert result["recommended_tp"] == 4, \
            f"Profile head metadata must restrict TP; got TP={result['recommended_tp']}"
        assert result["recommended_tp"] != 3

    def test_check_fit_no_head_metadata_allows_all_tp(self):
        """Without head metadata on either side, all TP degrees 1..8 are valid."""
        catalog = {
            "entries": [
                {
                    "model_id": "test/old-model",
                    "vram_with_kv_headroom_gb": 70.0,
                },
            ]
        }
        target = {"gpus_per_job": 4, "vram_per_gpu_gb": 32}
        profile = {
            "model_id": "test/old-model",
            "quantization": "",
            "load_format": "",
        }
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True
        # TP=3: 32*3=96 > 70 → fits. Without head constraints, TP=3 is valid.
        assert result["recommended_tp"] == 3