"""Focused tests for popup-provider preflight billing analysis.

Covers defect 11: preflight must report billing impact and flag oversized
memory requests when the target exposes TRESBillingWeights / PriorityFlags.
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
    analyze_billing,
    estimate_host_memory_gb,
    parse_billing_weights,
    parse_memory_value,
)

# ---------------------------------------------------------------------------
# parse_memory_value
# ---------------------------------------------------------------------------

class TestParseMemoryValue:
    def test_plain_float(self):
        assert parse_memory_value(120.0) == 120.0

    def test_int(self):
        assert parse_memory_value(4) == 4.0

    def test_gigabytes_upper(self):
        assert parse_memory_value("120G") == 120.0

    def test_gigabytes_lower(self):
        assert parse_memory_value("120g") == 120.0

    def test_gigabytes_decimal(self):
        assert parse_memory_value("5.00G") == 5.0

    def test_megabytes(self):
        # 500 MiB = 500 / 1024 GiB
        assert parse_memory_value("500M") == pytest.approx(500 / 1024, abs=1e-9)

    def test_kilobytes(self):
        # 512 KiB = 512 / 1024^2 GiB
        assert parse_memory_value("512K") == pytest.approx(512 / (1024**2), abs=1e-9)

    def test_terabytes(self):
        assert parse_memory_value("2T") == 2048.0

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_memory_value("not_a_number")


# ---------------------------------------------------------------------------
# parse_billing_weights
# ---------------------------------------------------------------------------

class TestParseBillingWeights:
    def test_none_returns_empty(self):
        assert parse_billing_weights(None) == {}

    def test_empty_dict(self):
        assert parse_billing_weights({}) == {}

    def test_plain_numbers(self):
        result = parse_billing_weights({"CPU": 1.0, "gres/gpu": 6.0})
        assert result == {"CPU": 1.0, "gres/gpu": 6.0}

    def test_memory_string_converted_to_gb(self):
        result = parse_billing_weights({"Mem": "5.00G"})
        assert result == {"Mem": 5.0}

    def test_mixed_values(self):
        result = parse_billing_weights({
            "CPU": 1.0,
            "Mem": "5.00G",
            "gres/gpu": 6.0,
        })
        assert result == {"CPU": 1.0, "Mem": 5.0, "gres/gpu": 6.0}


# ---------------------------------------------------------------------------
# estimate_host_memory_gb
# ---------------------------------------------------------------------------

MINIMAL_CATALOG = {
    "entries": [
        {
            "model_id": "test/model-7b",
            "quantization": "gguf",
            "load_format": "gguf",
            "vram_with_kv_headroom_gb": 8.0,
            # No host_memory_gb — should fall back to default.
        },
        {
            "model_id": "test/model-measured",
            "quantization": "gguf",
            "load_format": "gguf",
            "vram_with_kv_headroom_gb": 8.0,
            "host_memory_gb": 1.2,  # explicitly measured
        },
    ]
}


class TestEstimateHostMemoryGb:
    def test_fallback_to_default(self):
        profile = {"model_id": "test/model-7b", "quantization": "gguf", "load_format": "gguf"}
        assert estimate_host_memory_gb(profile, MINIMAL_CATALOG) == 1.5

    def test_measured_value_from_catalog(self):
        profile = {"model_id": "test/model-measured", "quantization": "gguf", "load_format": "gguf"}
        assert estimate_host_memory_gb(profile, MINIMAL_CATALOG) == 1.2

    def test_missing_model_returns_default(self):
        profile = {"model_id": "unknown/model", "quantization": "gguf", "load_format": "gguf"}
        assert estimate_host_memory_gb(profile, MINIMAL_CATALOG) == 1.5


# ---------------------------------------------------------------------------
# analyze_billing — Sockeye-style MAX_TRES scenario (defect 11)
# ---------------------------------------------------------------------------

SOCKEYE_TARGET = {
    "name": "sockeye",
    "gpus_per_job": 4,
    "vram_per_gpu_gb": 32,
    "cpus_per_task": 12,
    "mem": "120G",
    "tres_billing_weights": {"CPU": 1.0, "Mem": "5.00G", "gres/gpu": 6.0},
    "priority_flags": "MAX_TRES",
}

SOCKEYE_PROFILE = {
    "model_id": "test/model-7b",
    "quantization": "gguf",
    "load_format": "gguf",
}


class TestAnalyzeBillingSockeye:
    def test_returns_billing_analysis(self):
        result = analyze_billing(SOCKEYE_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        assert "billing_analysis" in result
        ba = result["billing_analysis"]
        assert ba["has_billing_metadata"] is True

    def test_weighted_terms_computed(self):
        result = analyze_billing(SOCKEYE_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        wt = ba["weighted_terms"]
        assert wt["CPU"] == 12.0        # 12 * 1.0
        assert wt["Mem"] == 600.0       # 120 * 5.0
        assert wt["gres/gpu"] == 24.0   # 4 * 6.0

    def test_billed_value_is_max_tres(self):
        result = analyze_billing(SOCKEYE_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        assert ba["billed_value"] == 600.0
        assert ba["billed_method"] == "MAX_TRES"

    def test_cost_driver_is_memory(self):
        result = analyze_billing(SOCKEYE_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        assert ba["cost_driver"] == "Mem"

    def test_memory_flagged_oversized(self):
        result = analyze_billing(SOCKEYE_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        assert ba["mem_oversized"] is True
        # 120G / 1.5G estimated = 80x
        assert ba["mem_ratio"] == pytest.approx(80.0, rel=0.01)

    def test_suggests_memory_reduction(self):
        result = analyze_billing(SOCKEYE_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        assert len(ba["suggestions"]) >= 1
        assert any("Memory" in s for s in ba["suggestions"])

    def test_gpu_suggestion_for_excess_gpus(self):
        result = analyze_billing(SOCKEYE_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        # 4 GPUs requested, VRAM needed is 8GB, per-GPU is 32GB → TP=1 suffices
        assert any("GPU" in s for s in ba["suggestions"])


# ---------------------------------------------------------------------------
# analyze_billing — no billing metadata → empty result
# ---------------------------------------------------------------------------

PLAIN_TARGET = {
    "gpus_per_job": 1,
    "vram_per_gpu_gb": 32,
}

class TestAnalyzeBillingNoMetadata:
    def test_empty_when_no_weights(self):
        result = analyze_billing(PLAIN_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        assert result == {}


# ---------------------------------------------------------------------------
# analyze_billing — SUM_TRES priority flags
# ---------------------------------------------------------------------------

SUM_TARGET = {
    "gpus_per_job": 2,
    "vram_per_gpu_gb": 80,
    "cpus_per_task": 8,
    "mem": "32G",
    "tres_billing_weights": {"CPU": 1.0, "Mem": "1.0G", "gres/gpu": 10.0},
    "priority_flags": "SUM_TRES",
}


class TestAnalyzeBillingSumTres:
    def test_billed_is_sum(self):
        result = analyze_billing(SUM_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        # CPU: 8*1=8, Mem: 32*1=32, GPU: 2*10=20 → sum=60
        assert ba["billed_value"] == 60.0
        assert ba["billed_method"] == "SUM_TRES"

    def test_cost_driver_is_memory(self):
        result = analyze_billing(SUM_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        # Mem=32 > gres/gpu=20 > CPU=8
        assert ba["cost_driver"] == "Mem"


# ---------------------------------------------------------------------------
# analyze_billing — well-sized request (no flag)
# ---------------------------------------------------------------------------

WELL_SIZED_TARGET = {
    "gpus_per_job": 1,
    "vram_per_gpu_gb": 32,
    "cpus_per_task": 4,
    "mem": "2G",
    "tres_billing_weights": {"CPU": 1.0, "Mem": "1.0G", "gres/gpu": 6.0},
    "priority_flags": "MAX_TRES",
}


class TestAnalyzeBillingWellSized:
    def test_not_oversized(self):
        result = analyze_billing(WELL_SIZED_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        assert ba["mem_oversized"] is False
        # 2G / 1.5G = 1.33x — under 2.0 threshold

    def test_no_memory_suggestion(self):
        result = analyze_billing(WELL_SIZED_TARGET, SOCKEYE_PROFILE, MINIMAL_CATALOG)
        ba = result["billing_analysis"]
        mem_suggestions = [s for s in ba["suggestions"] if "Memory" in s]
        assert len(mem_suggestions) == 0


# ---------------------------------------------------------------------------
# Integration: check_fit includes billing when metadata present
# ---------------------------------------------------------------------------

FULL_CATALOG = {
    "entries": [
        {
            "model_id": "test/model-7b",
            "quantization": "gguf",
            "load_format": "gguf",
            "vram_with_kv_headroom_gb": 8.0,
        },
    ]
}

FIT_TARGET = {
    "gpus_per_job": 1,
    "vram_per_gpu_gb": 32,
    "cpus_per_task": 4,
    "mem": "2G",
    "tres_billing_weights": {"CPU": 1.0, "Mem": "1.0G", "gres/gpu": 6.0},
    "priority_flags": "MAX_TRES",
}


class TestCheckFitIncludesBilling:
    def test_fit_result_has_billing(self):
        from check import check_fit

        profile = {"model_id": "test/model-7b", "quantization": "gguf", "load_format": "gguf"}
        result = check_fit(FIT_TARGET, profile, FULL_CATALOG)
        assert result["fits"] is True
        assert "billing_analysis" in result
        assert result["billing_analysis"]["has_billing_metadata"] is True

    def test_fit_result_preserves_vram_fields(self):
        from check import check_fit

        profile = {"model_id": "test/model-7b", "quantization": "gguf", "load_format": "gguf"}
        result = check_fit(FIT_TARGET, profile, FULL_CATALOG)
        assert result["gpus_requested"] == 1
        assert result["vram_per_gpu_gb"] == 32
        assert result["total_vram_gb"] == 32
        assert result["recommended_tp"] == 1