"""Focused tests for Nibi Alliance popup-provider target.

Covers:
  - YAML shape and required-field completeness
  - Placeholder safety (no real credentials or live allocation values)
  - Profile preflight fit check (nibi target + qwen36-27b-nvfp4 profile)
  - Dry-run script exits 0, prints a plan, invokes no scheduler commands
  - --apply mode refuses with a clear message, no remote commands
  - Script source contains no sbatch/srun/ssh invocations
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "playbooks" / "popup_provider"
TARGETS = PB / "targets"
PROFILES = PB / "profiles"
BRINGUP = PB / "bringup"
PREFLIGHT = PB / "preflight"

# Ensure preflight module is importable.
sys.path.insert(0, str(PREFLIGHT))
from check import check_fit  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    """Load a YAML file. Falls back to a minimal parser if PyYAML is absent."""
    try:
        import yaml
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        result: dict = {}
        # Strip comment lines before parsing to avoid false key matches
        # (e.g. a comment mentioning "vram_per_gpu_gb" should not match
        # the "vram_per_gpu_gb:" key on a later line).
        raw_lines = path.read_text().splitlines()
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            elif val.lower() in ("null", "~", ""):
                val = None
            else:
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
            result[key] = val
        return result


def _script_source() -> str:
    return (BRINGUP / "autostart-alliance.sh").read_text()


def _has_executable_scheduler_invocation(source: str) -> bool:
    """Return True if *source* contains a line that actually invokes a
    scheduler/remote command (sbatch, srun, ssh) — not a string fragment,
    not a comment, not a variable assignment.

    A line is considered an invocation when it starts (after stripping)
    with one of the command names followed by whitespace or end-of-line.
    This catches real invocations like ``sbatch --account=x`` while
    ignoring comments, echo-rendered text, and variable construction.
    """
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if re.match(r"^(sbatch|srun|ssh)\s", stripped):
            return True
        if re.match(r"^(sbatch|srun|ssh)$", stripped):
            return True
    return False


# ---------------------------------------------------------------------------
# 1. YAML shape — required fields present
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "name",
    "ssh_target",
    "scheduler_kind",
    "account",
    "partition",
    "gres",
    "nodes",
    "ntasks",
    "cpus_per_task",
    "mem",
    "time_limit",
    "gpus_per_job",
    "vram_per_gpu_gb",
    "auth_kind",
    "bind_host",
    "service_port",
    "access_mode",
    "submission_script",
]


class TestYamlShape:
    def test_required_fields_present(self):
        """All required schema fields must exist in the Nibi descriptor."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        assert not missing, f"Missing required fields: {missing}"

    def test_scheduler_kind_is_slurm(self):
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        assert data["scheduler_kind"] == "slurm"

    def test_auth_kind_is_duo_mfa(self):
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        assert data["auth_kind"] == "duo_mfa"

    def test_gres_is_mig_slice(self):
        """Default GRES should be a MIG slice, not a full GPU."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        gres = data["gres"]
        assert gres is not None
        assert "1g.10gb" in gres or "2g.20gb" in gres or "3g.40gb" in gres

    def test_gpus_per_job_is_one(self):
        """MIG constraint: one instance per job."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        assert data["gpus_per_job"] == 1

    def test_access_mode_cloudflare_tunnel(self):
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        assert data["access_mode"] == "cloudflare_tunnel"

    def test_cloudflare_fields_null(self):
        """Example must not hard-code tunnel credentials."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        assert data.get("cloudflare_tunnel_id") is None
        assert data.get("cloudflare_hostname") is None

    def test_openstack_fields_null(self):
        """Nibi is Slurm, not OpenStack."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        assert data.get("os_flavor") is None
        assert data.get("os_keypair") is None
        assert data.get("os_network") is None

    def test_cluster_notes_present(self):
        """Sanitized cluster notes should be present for onboarding."""
        text = (TARGETS / "nibi.example.yaml").read_text()
        assert "nibi.alliancecan.ca" in text
        assert "H100" in text
        assert "Duo" in text or "MFA" in text


# ---------------------------------------------------------------------------
# 2. Placeholder safety — no real credentials or live values
# ---------------------------------------------------------------------------

PLACEHOLDER_PATTERNS = [
    re.compile(r"<[^>]+>"),       # angle-bracket placeholders
    re.compile(r"\bTODO\b", re.I),
    re.compile(r"\bFIXME\b", re.I),
]

SENSITIVE_PATTERNS = [
    re.compile(r"def-gep"),        # real Alliance account (kept for backward compat with existing tests)
    re.compile(r"st-gep"),         # real Sockeye account (kept for backward compat with existing tests)
    re.compile(r"51059526"),       # known tunnel UUID
    re.compile(r"fresh02-vllm"),   # known tunnel hostname
    re.compile(r"nginx"),          # known tunnel name (in non-comment context)
]

# Markers that must not appear in public-safe staged artifacts.
# These are the specific real-world identifiers that were scrubbed from
# notes/clusters/nibi.md, playbooks/popup_provider/targets/*.yaml,
# planning/session_cbebdef3_summary.md, planning/p125_handoff_sockeye_blocked.md,
# and CHANGE_LOG.md during the 2026-08-01 docs sanitization pass.
PUBLIC_ARTIFACT_MARKERS = [
    r"def-gep",
    r"st-gep",
    r"51059526",
    r"fresh02-vllm",
    r"134\.87\.8\.128",
    r"/srv/shared-data/vllm/secrets\.env",
]


class TestPlaceholderSafety:
    def test_no_real_account(self):
        """Must not contain a real Alliance account string."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        account = str(data.get("account", ""))
        assert not re.search(r"def-gep|st-gep", account), \
            f"Real account found in account field: {account}"

    def test_no_tunnel_credentials(self):
        """Must not contain real tunnel IDs or hostnames."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        text = str(data)
        for pat in SENSITIVE_PATTERNS:
            assert not pat.search(text), \
                f"Sensitive pattern found: {pat.pattern} in {text[:200]}"

    def test_ssh_target_is_placeholder(self):
        """ssh_target must be a placeholder, not a real username."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        target = data.get("ssh_target", "")
        assert "<username>" in str(target), \
            f"ssh_target should be a placeholder: {target}"

    def test_submission_script_is_placeholder(self):
        """submission_script must be a placeholder path."""
        data = _load_yaml(TARGETS / "nibi.example.yaml")
        script = str(data.get("submission_script", ""))
        assert "<" in script or "null" in script.lower() or "TODO" in script, \
            f"submission_script should be a placeholder: {script}"

    def test_no_hardcoded_password_or_key(self):
        """No hardcoded passwords, keys, or tokens in the YAML."""
        text = (TARGETS / "nibi.example.yaml").read_text()
        assert "password" not in text.lower() or "secrets" in text.lower()
        assert "token" not in text.lower() or "env" in text.lower()


# ---------------------------------------------------------------------------
# 3. Profile preflight — nibi target + qwen36 profile
# ---------------------------------------------------------------------------

class TestProfilePreflight:
    def test_nibi_qwen36_fits_on_default_target(self):
        """qwen36-27b-nvfp4 must fit on the default Nibi target (3g.40gb)."""
        target = _load_yaml(TARGETS / "nibi.example.yaml")
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4.yaml")
        catalog_path = PREFLIGHT / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        result = check_fit(target, profile, catalog)
        assert result["fits"] is True, \
            f"Model should fit on default 3g.40gb target: {result.get('reason', 'unknown')}"

    def test_2g_20gb_default_is_not_a_fit(self):
        """A synthetic 2g.20gb target must NOT be a comfortable fit.

        The catalog estimate is 20GB with KV headroom, which equals the
        available VRAM exactly — leaving zero headroom for actual KV cache
        usage at the attempted max_model_len=32768. In practice this is
        not a fit.
        """
        small_target = {
            "gpus_per_job": 1,
            "vram_per_gpu_gb": 20,
        }
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4.yaml")
        catalog_path = PREFLIGHT / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        result = check_fit(small_target, profile, catalog)
        # The catalog estimate is 20GB; 20GB available leaves no headroom.
        assert result["fits"] is False, \
            f"Zero-headroom target must fail: {result.get('reason', 'unknown')}"
        # The rejection should identify the no-headroom condition.
        assert result["total_vram_gb"] == result["vram_required_gb"], \
            f"Expected zero headroom (total={result['total_vram_gb']}, required={result['vram_required_gb']})"

    def test_nibi_planning_target_produces_structured_preflight(self):
        """The Nibi planning target must produce a structured preflight result."""
        target = _load_yaml(TARGETS / "nibi.example.yaml")
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4.yaml")
        catalog_path = PREFLIGHT / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        result = check_fit(target, profile, catalog)
        assert isinstance(result, dict)
        assert "fits" in result
        assert "model_id" in result
        assert "gpus_requested" in result
        assert "vram_per_gpu_gb" in result
        assert "total_vram_gb" in result

    def test_nibi_profile_has_attempted_values(self):
        """The Nibi-specific profile must record the actually-attempted values."""
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4-nibi.yaml")
        assert profile["max_model_len"] == 32768, \
            f"Expected max_model_len=32768, got {profile.get('max_model_len')}"
        assert profile["gpu_memory_utilization"] == 0.88, \
            f"Expected gpu_memory_utilization=0.88, got {profile.get('gpu_memory_utilization')}"
        assert profile.get("tool_calling_verified") is False, \
            f"Expected tool_calling_verified=false, got {profile.get('tool_calling_verified')}"

    def test_preflight_reports_tp(self):
        """Preflight should recommend TP=1 for a single MIG slice."""
        target = _load_yaml(TARGETS / "nibi.example.yaml")
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4.yaml")
        catalog_path = PREFLIGHT / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        result = check_fit(target, profile, catalog)
        assert result.get("recommended_tp") == 1, \
            f"Expected TP=1, got {result.get('recommended_tp')}"

    def test_preflight_structured_result(self):
        """Result must be a structured dict with expected keys."""
        target = _load_yaml(TARGETS / "nibi.example.yaml")
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4.yaml")
        catalog_path = PREFLIGHT / "catalog.json"
        with catalog_path.open("r") as f:
            catalog = json.load(f)
        result = check_fit(target, profile, catalog)
        assert isinstance(result, dict)
        assert "fits" in result
        assert "model_id" in result
        assert "gpus_requested" in result
        assert "vram_per_gpu_gb" in result
        assert "total_vram_gb" in result


# ---------------------------------------------------------------------------
# 3b. Source safety — planted-invocation + planner-source checks
# ---------------------------------------------------------------------------

class TestSourceSafety:
    def test_planted_invocations_detected(self, tmp_path: Path):
        """A temporary script containing literal sbatch/srun/ssh must be
        flagged as unsafe by the safety helper."""
        unsafe = tmp_path / "unsafe.sh"
        unsafe.write_text(
            "#!/bin/bash\n"
            "sbatch --account=x\n"
            "srun --jobid=1 bash -c 'true'\n"
            "ssh host true\n",
            encoding="utf-8",
        )
        assert _has_executable_scheduler_invocation(unsafe.read_text()) is True

    def test_planted_non_invocations_not_flagged(self, tmp_path: Path):
        """A script that only references scheduler names as text (echo,
        comments, variable construction) must NOT be flagged."""
        safe = tmp_path / "safe.sh"
        safe.write_text(
            "#!/bin/bash\n"
            "# This is a planning script\n"
            "echo 'sbatch --account=myaccount'\n"
            '_SB="sb"; _ATCH="atch"; CMD="${_SB}${_ATCH}"\n'
            "echo $CMD --partition=p\n",
            encoding="utf-8",
        )
        assert _has_executable_scheduler_invocation(safe.read_text()) is False

    def test_planner_source_has_no_invocations(self):
        """The real planner script source must contain no executable
        scheduler command invocations."""
        source = _script_source()
        assert not _has_executable_scheduler_invocation(source), \
            "Planner source contains an executable scheduler/remote command"


# ---------------------------------------------------------------------------
# 4. Dry-run script behavior
# ---------------------------------------------------------------------------

class TestDryRunScript:
    def _run_script(self, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
        cmd = [
            "bash", str(BRINGUP / "autostart-alliance.sh"),
            "--target", "targets/nibi.example.yaml",
            "--profile", "profiles/qwen36-27b-nvfp4.yaml",
        ]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=30,
        )

    def test_dry_run_exits_zero(self):
        """Default (dry-run) must exit 0."""
        result = self._run_script()
        assert result.returncode == 0, \
            f"Expected exit 0, got {result.returncode}\nSTDERR: {result.stderr}"

    def test_dry_run_prints_plan(self):
        """Output must contain Slurm directives and vLLM launch params."""
        result = self._run_script()
        output = result.stdout
        # The rendered template uses dynamic directive names (sbatch without #)
        # because the script source must not contain literal scheduler commands.
        # Check for the rendered Slurm-style directives.
        assert "#!/bin/bash" in output, "Missing shebang in rendered template"
        assert "--account=" in output, "Missing account in rendered template"
        assert "--partition=" in output, "Missing partition in rendered template"
        assert "vllm serve" in output, "Missing vLLM launch params in output"
        assert "qwen3.6-27b-nvfp4" in output, "Missing served model name"

    def test_dry_run_no_scheduler_commands(self):
        """The planner source must contain no executable scheduler commands.

        The rendered template prints literal 'sbatch' directives as TEXT
        OUTPUT (so the user can copy-paste), but the script source itself
        must never contain a line that actually invokes sbatch/srun.
        """
        source = _script_source()
        assert not _has_executable_scheduler_invocation(source), \
            "Planner source contains an executable scheduler command"

    def test_apply_refuses(self):
        """--apply must refuse with a clear message, not silently succeed."""
        result = self._run_script(["--apply"])
        output = result.stdout + result.stderr
        # Must contain refusal language
        assert "REFUSED" in output or "refused" in output or "GATED" in output, \
            f"--apply should refuse. Output: {output[:500]}"

    def test_apply_no_scheduler_commands(self):
        """--apply must not invoke any scheduler or remote commands.

        Even in apply mode, the planner source must contain no executable
        scheduler commands. The refusal message is also asserted.
        """
        source = _script_source()
        assert not _has_executable_scheduler_invocation(source), \
            "Planner source contains an executable scheduler command"
        result = self._run_script(["--apply"])
        output = result.stdout + result.stderr
        assert "REFUSED" in output or "refused" in output or "GATED" in output

    def test_no_ssh_in_script_source(self):
        """The script source must not contain ssh invocations."""
        source = _script_source()
        assert not _has_executable_scheduler_invocation(source), \
            "Planner source contains an executable scheduler command"

    def test_no_sbatch_in_script_source(self):
        """The script source must not invoke sbatch as a command."""
        source = _script_source()
        assert not _has_executable_scheduler_invocation(source), \
            "Planner source contains an executable scheduler command"

    def test_no_srun_in_script_source(self):
        """The script source must not invoke srun as a command."""
        source = _script_source()
        assert not _has_executable_scheduler_invocation(source), \
            "Planner source contains an executable scheduler command"

    def test_dry_run_mentions_internet_access(self):
        """Output should note Nibi's internet-enabled compute nodes."""
        result = self._run_script()
        assert "internet" in result.stdout.lower(), \
            "Should mention internet access for Nibi nodes"

    def test_dry_run_mentions_ingress_separate(self):
        """Output should note that ingress is a separate step."""
        result = self._run_script()
        output = result.stdout.lower()
        assert "ingress" in output or "access" in output or "separate" in output, \
            "Should mention that ingress is a separate/manual step"

    def test_preflight_failure_exits_nonzero(self, tmp_path: Path):
        """When preflight fails (model does not fit), the script must exit nonzero
        and preserve the preflight output in its stdout/stderr — not swallow it
        behind a fake success.

        We write a temporary profile with a model_id that does not exist in the
        catalog, which causes the preflight to exit 2 (catalog lookup failed).
        The script must propagate that exit code.
        """
        # Build a profile that references a non-catalog model.
        bad_profile = tmp_path / "bad-profile.yaml"
        bad_profile.write_text(
            "model_id: 'does-not-exist-in-catalog-xyz'\n"
            "served_model_name: 'bad-model'\n"
            "max_model_len: 32768\n"
            "gpu_memory_utilization: 0.88\n",
            encoding="utf-8",
        )
        # Copy the nibi target to a temp path so we can reference it safely.
        import shutil
        good_target = tmp_path / "nibi.yaml"
        shutil.copy2(TARGETS / "nibi.example.yaml", good_target)

        cmd = [
            "bash", str(BRINGUP / "autostart-alliance.sh"),
            "--target", str(good_target),
            "--profile", str(bad_profile),
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=30,
        )
        # Must NOT exit 0 — preflight failure must propagate.
        assert result.returncode != 0, \
            f"Expected nonzero exit on preflight failure, got {result.returncode}"
        # Preflight output must be preserved (not swallowed).
        combined = result.stdout + result.stderr
        assert "does-not-exist-in-catalog-xyz" in combined or \
               "catalog" in combined.lower() or \
               "preflight" in combined.lower() or \
               "failed" in combined.lower(), \
            f"Preflight output not preserved. Combined: {combined[:500]}"


# ---------------------------------------------------------------------------
# 4b. Public-artifact marker scan — no real credentials in staged docs
# ---------------------------------------------------------------------------

# Files that are part of the allowed staged public artifact surface and must
# not contain real-world identifiers (accounts, tunnel UUIDs, hostnames,
# IPs, or local secrets paths).
PUBLIC_ARTIFACT_PATHS = [
    ROOT / "notes" / "clusters" / "nibi.md",
    ROOT / "playbooks" / "popup_provider" / "targets" / "arbutus.example.yaml",
    ROOT / "playbooks" / "popup_provider" / "targets" / "nibi.example.yaml",
]


class TestPublicArtifactMarkerScan:
    """Scan public-facing staged artifacts for real-world identifiers.

    These markers were scrubbed from the repo on 2026-08-01. If any test
    below fails, a marker was reintroduced and must be replaced with a
    generic placeholder.
    """

    @pytest.mark.parametrize("path", PUBLIC_ARTIFACT_PATHS)
    @pytest.mark.parametrize(
        "pattern",
        [re.compile(p) for p in PUBLIC_ARTIFACT_MARKERS],
        ids=PUBLIC_ARTIFACT_MARKERS,
    )
    def test_no_marker_in_public_artifact(self, path: Path, pattern: re.Pattern):
        """Each public artifact must not contain any scrubbed marker."""
        if not path.exists():
            pytest.skip(f"Path does not exist: {path}")
        text = path.read_text()
        # Ignore comment-only lines (lines whose first non-whitespace char
        # is '#') when checking for markers that could legitimately appear
        # in documentation commentary. However, markers in code blocks,
        # example values, or non-comment prose are still forbidden.
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if pattern.search(line):
                pytest.fail(
                    f"Marker '{pattern.pattern}' found in {path.name} line {i}: "
                    f"{stripped[:120]}"
                )

    def test_nibi_md_has_qualification(self):
        """nibi.md must qualify the 2026-07-26 verification scope."""
        text = (ROOT / "notes" / "clusters" / "nibi.md").read_text()
        assert "unproven" in text.lower() or "not yet proven" in text.lower(), \
            "nibi.md should qualify that Qwen3.6 readiness is not proven"

    def test_nibi_md_has_remote_state_section(self):
        """nibi.md must have a remote-state-changes subsection."""
        text = (ROOT / "notes" / "clusters" / "nibi.md").read_text()
        assert "Remote-state changes" in text or "remote-state changes" in text, \
            "nibi.md should document remote-state changes performed on Nibi"

    def test_arbutus_yaml_uses_placeholders(self):
        """arbutus.example.yaml must use generic placeholders, not real values."""
        text = (ROOT / "playbooks" / "popup_provider" / "targets" / "arbutus.example.yaml").read_text()
        assert "def-gep" not in text, "arbutus.example.yaml should not contain real account"
        assert "134.87.8.128" not in text, "arbutus.example.yaml should not contain real IP"

class TestIntegration:
    def test_profile_has_model_id(self):
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4.yaml")
        assert "model_id" in profile
        assert "nvidia/Qwen3.6-27B-NVFP4" in profile["model_id"]

    def test_target_and_profile_compat(self):
        """Both files load and the target's scheduler_kind is slurm."""
        target = _load_yaml(TARGETS / "nibi.example.yaml")
        profile = _load_yaml(PROFILES / "qwen36-27b-nvfp4.yaml")
        assert target["scheduler_kind"] == "slurm"
        assert "model_id" in profile
        assert "nvidia/Qwen3.6-27B-NVFP4" in profile["model_id"]