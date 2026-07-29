"""Safely attach an existing Cloudflare Tunnel to a model-provider hostname.

This helper deliberately does *not* create, copy credentials for, start, stop,
or replace a Cloudflare Tunnel connector.  It produces a reviewed ingress
candidate and can optionally attach DNS to an existing, already-running tunnel
only after it verifies the configured live topology.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlparse

import yaml


class TunnelConfiguratorError(RuntimeError):
    """Raised when a tunnel configuration is unsafe or cannot be verified."""


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]
TUNNEL_ID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)
HOSTNAME_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TunnelProviderSpec:
    """One existing connector and the provider route intended for it."""

    tunnel_id: str
    hostname: str
    origin_url: str
    credentials_file: str
    ssh_target: str | None = None
    live_config_path: str | None = None
    verification_url: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TunnelProviderSpec":
        required = ("tunnel_id", "hostname", "origin_url", "credentials_file")
        missing = [field for field in required if not value.get(field)]
        if missing:
            raise TunnelConfiguratorError(
                f"tunnel configuration is missing required fields: {', '.join(missing)}"
            )
        spec = cls(
            tunnel_id=str(value["tunnel_id"]),
            hostname=str(value["hostname"]).lower(),
            origin_url=str(value["origin_url"]),
            credentials_file=str(value["credentials_file"]),
            ssh_target=_optional_string(value.get("ssh_target")),
            live_config_path=_optional_string(value.get("live_config_path")),
            verification_url=_optional_string(value.get("verification_url")),
        )
        spec.validate()
        return spec

    def validate(self) -> None:
        if not TUNNEL_ID_PATTERN.fullmatch(self.tunnel_id):
            raise TunnelConfiguratorError("tunnel_id must be a UUID for an existing tunnel")
        if not HOSTNAME_PATTERN.fullmatch(self.hostname):
            raise TunnelConfiguratorError("hostname must be a fully qualified DNS hostname")
        _validate_http_url("origin_url", self.origin_url, allow_loopback=True)
        if self.verification_url:
            _validate_http_url("verification_url", self.verification_url, allow_loopback=False)
        if not self.credentials_file.startswith("/"):
            raise TunnelConfiguratorError("credentials_file must be an absolute path")
        if self.live_config_path and not self.live_config_path.startswith("/"):
            raise TunnelConfiguratorError("live_config_path must be an absolute path")


@dataclass(frozen=True)
class TunnelAction:
    """One planned or applied operation, without secret-bearing command output."""

    kind: str
    detail: str
    applied: bool = False


@dataclass
class TunnelReport:
    """Evidence produced by one configuration pass."""

    public_base_url: str
    candidate_config: str
    actions: list[TunnelAction]
    backup_path: str | None = None


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _validate_http_url(field: str, value: str, *, allow_loopback: bool) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise TunnelConfiguratorError(f"{field} must be an absolute http(s) URL")
    host = parsed.hostname or ""
    if not allow_loopback and host in {"127.0.0.1", "::1", "localhost"}:
        raise TunnelConfiguratorError(f"{field} must be externally reachable, not loopback")


def load_tunnel_provider_spec(config_path: Path) -> TunnelProviderSpec:
    """Load one untracked, environment-specific tunnel configuration."""
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise TunnelConfiguratorError(f"could not read config {config_path}: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise TunnelConfiguratorError("config must be a YAML mapping")
    tunnel = raw.get("tunnel")
    if not isinstance(tunnel, Mapping):
        raise TunnelConfiguratorError("config must contain a tunnel mapping")
    return TunnelProviderSpec.from_mapping(tunnel)


def render_candidate_config(spec: TunnelProviderSpec) -> str:
    """Render a standalone candidate for review or manual ingress merging."""
    document = {
        "tunnel": spec.tunnel_id,
        "credentials-file": spec.credentials_file,
        "ingress": [
            {"hostname": spec.hostname, "service": spec.origin_url},
            {"service": "http_status:404"},
        ],
    }
    return yaml.safe_dump(document, sort_keys=False)


def _default_runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), capture_output=True, text=True, check=False)


class CloudflaredHost:
    """Run verified Cloudflare commands locally or over a single SSH hop."""

    def __init__(self, spec: TunnelProviderSpec, runner: CommandRunner | None = None) -> None:
        self.spec = spec
        self._runner = runner or _default_runner

    def _run(self, args: Sequence[str]) -> str:
        command = (
            ["ssh", self.spec.ssh_target, shlex.join(args)]
            if self.spec.ssh_target
            else list(args)
        )
        completed = self._runner(command)
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()
            raise TunnelConfiguratorError(f"{' '.join(args[:3])} failed: {detail}")
        return completed.stdout

    def inspect_tunnel(self) -> None:
        self._run(["cloudflared", "tunnel", "info", self.spec.tunnel_id])

    def read_live_config(self) -> Mapping[str, Any]:
        if not self.spec.live_config_path:
            raise TunnelConfiguratorError("live_config_path is required before applying DNS")
        raw = self._run(["cat", self.spec.live_config_path])
        try:
            parsed = yaml.safe_load(raw) or {}
        except yaml.YAMLError as exc:
            raise TunnelConfiguratorError("live cloudflared config is not valid YAML") from exc
        if not isinstance(parsed, Mapping):
            raise TunnelConfiguratorError("live cloudflared config must be a YAML mapping")
        return parsed

    def backup_live_config(self) -> str:
        if not self.spec.live_config_path:
            raise TunnelConfiguratorError("live_config_path is required before applying DNS")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = f"{self.spec.live_config_path}.before-model-provider-{timestamp}.bak"
        self._run(["cp", "--preserve=mode,timestamps", self.spec.live_config_path, backup_path])
        return backup_path

    def route_dns(self) -> None:
        self._run(["cloudflared", "tunnel", "route", "dns", self.spec.tunnel_id, self.spec.hostname])

    def verify_public_endpoint(self) -> None:
        if not self.spec.verification_url:
            raise TunnelConfiguratorError("verification_url is required before applying DNS")
        self._run(
            [
                "curl",
                "--fail",
                "--silent",
                "--show-error",
                "--location",
                "--max-time=20",
                self.spec.verification_url,
            ]
        )


def _live_config_matches(spec: TunnelProviderSpec, config: Mapping[str, Any]) -> None:
    if str(config.get("tunnel", "")).strip() != spec.tunnel_id:
        raise TunnelConfiguratorError("live config tunnel ID does not match configured existing tunnel")
    ingress = config.get("ingress")
    if not isinstance(ingress, list):
        raise TunnelConfiguratorError("live config does not contain an ingress list")
    for rule in ingress:
        if not isinstance(rule, Mapping):
            continue
        if str(rule.get("hostname", "")).lower() == spec.hostname:
            if str(rule.get("service", "")) != spec.origin_url:
                raise TunnelConfiguratorError("live hostname route points to a different origin service")
            return
    raise TunnelConfiguratorError("live config has no matching hostname ingress route")


def configure_tunnel_provider(
    spec: TunnelProviderSpec,
    *,
    write_candidate: Path | None = None,
    apply_dns: bool = False,
    confirmed_tunnel_id: str | None = None,
    host: CloudflaredHost | None = None,
) -> TunnelReport:
    """Inspect an existing tunnel and optionally attach one verified DNS route.

    The function never creates, launches, stops, or rewrites a connector.  DNS
    mutation requires both ``apply_dns`` and a command-line confirmation of the
    exact configured tunnel UUID.  Before the DNS operation it verifies that
    the active configuration already routes the hostname to the requested
    local origin, then creates a timestamped backup of that configuration.
    """
    host = host or CloudflaredHost(spec)
    candidate = render_candidate_config(spec)
    actions = [TunnelAction("inspect_tunnel", "inspect the configured existing tunnel")]
    host.inspect_tunnel()

    if write_candidate:
        if write_candidate.exists():
            raise TunnelConfiguratorError(f"candidate path already exists: {write_candidate}")
        write_candidate.parent.mkdir(parents=True, exist_ok=True)
        write_candidate.write_text(candidate, encoding="utf-8")
        actions.append(
            TunnelAction("write_candidate", f"wrote review-only candidate to {write_candidate}", True)
        )
    else:
        actions.append(
            TunnelAction("render_candidate", "rendered review-only ingress candidate")
        )

    backup_path: str | None = None
    if apply_dns:
        if confirmed_tunnel_id != spec.tunnel_id:
            raise TunnelConfiguratorError(
                "DNS mutation requires --confirm-tunnel-id matching the configured tunnel_id"
            )
        live_config = host.read_live_config()
        _live_config_matches(spec, live_config)
        actions.append(TunnelAction("verify_live_ingress", "verified existing hostname route", True))
        backup_path = host.backup_live_config()
        actions.append(TunnelAction("backup_live_config", f"created {backup_path}", True))
        host.route_dns()
        actions.append(TunnelAction("route_dns", f"attached {spec.hostname} to existing tunnel", True))
        host.inspect_tunnel()
        actions.append(TunnelAction("inspect_tunnel", "inspected tunnel after DNS change", True))
        host.verify_public_endpoint()
        actions.append(TunnelAction("verify_public_endpoint", spec.verification_url or "", True))
    else:
        actions.append(
            TunnelAction(
                "would_route_dns",
                "would require verified live ingress, backup, explicit tunnel confirmation, and health check",
            )
        )

    return TunnelReport(
        public_base_url=f"https://{spec.hostname}/v1",
        candidate_config=candidate,
        actions=actions,
        backup_path=backup_path,
    )


def render_report(report: TunnelReport) -> str:
    """Render an operator-oriented, non-secret-bearing result."""
    lines = [f"Provider base URL: {report.public_base_url}", "", "Actions:"]
    for action in report.actions:
        mode = "applied" if action.applied else "plan"
        lines.append(f"- [{mode}] {action.kind}: {action.detail}")
    lines.extend(["", "Candidate cloudflared configuration:", report.candidate_config.rstrip()])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="untracked provider tunnel YAML")
    parser.add_argument(
        "--write-candidate",
        type=Path,
        help="write a new review-only cloudflared config candidate; refuses to overwrite",
    )
    parser.add_argument(
        "--apply-dns",
        action="store_true",
        help="attach DNS to the pre-existing tunnel after all topology checks",
    )
    parser.add_argument(
        "--confirm-tunnel-id",
        help="required with --apply-dns; must exactly match config tunnel_id",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        spec = load_tunnel_provider_spec(args.config)
        report = configure_tunnel_provider(
            spec,
            write_candidate=args.write_candidate,
            apply_dns=args.apply_dns,
            confirmed_tunnel_id=args.confirm_tunnel_id,
        )
    except TunnelConfiguratorError as exc:
        print(f"tunnel-provider: {exc}", file=sys.stderr)
        return 2
    print(render_report(report), end="")
    if not args.apply_dns:
        print("Plan only: no DNS change was made. Do not launch or replace a connector with this helper.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
