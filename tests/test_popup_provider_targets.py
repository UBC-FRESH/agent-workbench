"""Focused tests for popup-provider target descriptors.

Validates that example target descriptors are structurally sound: required
fields present, types correct, and compatible with the preflight path.

Covers P125 Step 6: second target descriptor (Arbutus/OpenStack) added alongside
the existing Sockeye (Slurm) descriptor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

# Ensure the module is importable regardless of cwd.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "playbooks" / "popup_provider" / "preflight"))

from check import check_fit, load_json  # noqa: E402

# ---------------------------------------------------------------------------
# Fixture: load the Arbutus example descriptor
# ---------------------------------------------------------------------------

TARGETS_DIR = ROOT / "playbooks" / "popup_provider" / "targets"
ARBUS_TARGET_PATH = TARGETS_DIR / "arbutus.example.yaml"
SOCKEYE_TARGET_PATH = TARGETS_DIR / "sockeye.example.yaml"

PROFILES_DIR = ROOT / "playbooks" / "popup_provider" / "profiles"
PROFILE_PATH = PROFILES_DIR / "qwen36-27b-nvfp4.yaml"

CATALOG_PATH = ROOT / "playbooks" / "popup_provider" / "preflight" / "catalog.json"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def arbutus_target() -> dict:
    return _load_yaml(ARBUS_TARGET_PATH)


@pytest.fixture(scope="module")
def sockeye_target() -> dict:
    return _load_yaml(SOCKEYE_TARGET_PATH)


@pytest.fixture(scope="module")
def profile() -> dict:
    return _load_yaml(PROFILE_PATH)


@pytest.fixture(scope="module")
def catalog() -> dict:
    return load_json(CATALOG_PATH)


# ---------------------------------------------------------------------------
# Required field presence
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "name",
    "ssh_target",
    "scheduler_kind",
    "account",
    "partition",
    "gpus_per_job",
    "vram_per_gpu_gb",
    "auth_kind",
    "bind_host",
    "service_port",
    "access_mode",
    "submission_script",
]


class TestArbutusRequiredFields:
    def test_all_required_fields_present(self, arbutus_target):
        missing = [f for f in REQUIRED_FIELDS if f not in arbutus_target]
        assert missing == [], f"Missing required fields: {missing}"

    def test_name_is_string(self, arbutus_target):
        assert isinstance(arbutus_target["name"], str)
        assert arbutus_target["name"] == "arbutus"

    def test_scheduler_kind_is_openstack(self, arbutus_target):
        assert arbutus_target["scheduler_kind"] == "openstack"

    def test_auth_kind_is_keypair(self, arbutus_target):
        assert arbutus_target["auth_kind"] == "keypair"

    def test_service_port_is_int(self, arbutus_target):
        assert isinstance(arbutus_target["service_port"], int)
        assert arbutus_target["service_port"] == 8000

    def test_gpus_per_job_is_int(self, arbutus_target):
        assert isinstance(arbutus_target["gpus_per_job"], int)
        assert arbutus_target["gpus_per_job"] >= 1

    def test_vram_per_gpu_gb_is_int(self, arbutus_target):
        assert isinstance(arbutus_target["vram_per_gpu_gb"], int)
        assert arbutus_target["vram_per_gpu_gb"] >= 1

    def test_bind_host_is_string(self, arbutus_target):
        assert isinstance(arbutus_target["bind_host"], str)

    def test_access_mode_is_valid(self, arbutus_target):
        valid_modes = {"loopback_bridge", "ssh_forward", "cloudflare_tunnel"}
        assert arbutus_target["access_mode"] in valid_modes

    def test_placeholder_values_are_explicit(self, arbutus_target):
        """Placeholder fields use the <...> syntax to signal 'fill in real value'.

        This is the documented convention for example descriptors: fields that
        require cluster-specific secrets or unverified values use angle-bracket
        placeholders. Real example descriptors should resolve these before use.
        """
        placeholder_fields = {"os_flavor", "os_keypair", "os_network", "cloudflare_tunnel_id",
                              "cloudflare_hostname", "partition"}
        for key in placeholder_fields:
            if key in arbutus_target:
                val = arbutus_target[key]
                assert isinstance(val, str), f"Placeholder field '{key}' should be a string"
                assert val.startswith("<") and val.endswith(">"), \
                    f"Placeholder field '{key}' should use <...> syntax, got: {val!r}"


class TestSockeyeRequiredFields:
    """Sanity check that the existing Sockeye descriptor still validates."""

    def test_all_required_fields_present(self, sockeye_target):
        missing = [f for f in REQUIRED_FIELDS if f not in sockeye_target]
        assert missing == [], f"Missing required fields: {missing}"

    def test_scheduler_kind_is_slurm(self, sockeye_target):
        assert sockeye_target["scheduler_kind"] == "slurm"


# ---------------------------------------------------------------------------
# OpenStack-specific fields
# ---------------------------------------------------------------------------

class TestArbutusOpenStackFields:
    def test_os_flavor_present(self, arbutus_target):
        assert "os_flavor" in arbutus_target
        assert isinstance(arbutus_target["os_flavor"], str)

    def test_os_keypair_present(self, arbutus_target):
        assert "os_keypair" in arbutus_target
        assert isinstance(arbutus_target["os_keypair"], str)

    def test_os_network_present(self, arbutus_target):
        assert "os_network" in arbutus_target
        assert isinstance(arbutus_target["os_network"], str)

    def test_proxy_jump_present(self, arbutus_target):
        assert "proxy_jump" in arbutus_target
        assert isinstance(arbutus_target["proxy_jump"], str)
        assert "<" in arbutus_target["proxy_jump"]


# ---------------------------------------------------------------------------
# Capabilities fields
# ---------------------------------------------------------------------------

class TestArbutusCapabilities:
    def test_supported_architectures_present(self, arbutus_target):
        archs = arbutus_target.get("supported_architectures")
        assert isinstance(archs, list)
        assert len(archs) > 0
        assert "Qwen3MoeForCausalLM" in archs

    def test_supported_kernels_is_null(self, arbutus_target):
        """supported_kernels is null: no direct runtime observation of kernel
        compilation on Arbutus. The capability gate is skipped for kernel
        checks on this target, not falsely claiming kernel support."""
        kernels = arbutus_target.get("supported_kernels")
        assert kernels is None, \
            f"supported_kernels should be null (no direct evidence), got: {kernels!r}"


# ---------------------------------------------------------------------------
# Preflight compatibility
# ---------------------------------------------------------------------------

class TestArbutusPreflightCompatibility:
    """Verify the Arbutus descriptor is compatible with the preflight path."""

    def test_preflight_runs_without_error(self, arbutus_target, profile, catalog):
        """check_fit must return a structured result dict without raising."""
        result = check_fit(arbutus_target, profile, catalog)
        assert isinstance(result, dict)
        assert "fits" in result
        assert "model_id" in result

    def test_preflight_result_has_required_keys(self, arbutus_target, profile, catalog):
        """Result must contain the standard preflight keys."""
        result = check_fit(arbutus_target, profile, catalog)
        required_keys = {"fits", "model_id", "gpus_requested", "vram_per_gpu_gb", "total_vram_gb"}
        for key in required_keys:
            assert key in result, f"Missing key in preflight result: {key}"

    def test_preflight_reports_vram(self, arbutus_target, profile, catalog):
        """Result must report total VRAM matching the target config."""
        result = check_fit(arbutus_target, profile, catalog)
        expected_total = arbutus_target["gpus_per_job"] * arbutus_target["vram_per_gpu_gb"]
        assert result["total_vram_gb"] == expected_total

    def test_capabilities_gate_passes(self, arbutus_target, profile, catalog):
        """The Arbutus target should pass the capabilities gate for qwen36-27b-nvfp4."""
        result = check_fit(arbutus_target, profile, catalog)
        # If the model fits in VRAM, capabilities_gate should be present and compatible.
        if result.get("fits"):
            cap = result.get("capabilities_gate", {})
            assert cap.get("compatible", False) is True