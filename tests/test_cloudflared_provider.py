from __future__ import annotations

from subprocess import CompletedProcess

import pytest

from agent_workbench.cloudflared_provider import (
    CloudflaredHost,
    TunnelConfiguratorError,
    TunnelProviderSpec,
    configure_tunnel_provider,
)


class FakeRunner:
    def __init__(self, responses: dict[str, str]) -> None:
        self.responses = responses
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str]) -> CompletedProcess[str]:
        self.commands.append(command)
        rendered = " ".join(command)
        for needle, stdout in self.responses.items():
            if needle in rendered:
                return CompletedProcess(command, 0, stdout, "")
        return CompletedProcess(command, 1, "", f"unexpected command: {rendered}")


def _spec() -> TunnelProviderSpec:
    return TunnelProviderSpec(
        tunnel_id="a1b2c3d4-e5f6-4a7b-8c9d-0123456789ab",
        hostname="model.example.edu",
        origin_url="http://127.0.0.1:8000",
        credentials_file="/etc/cloudflared/a1b2c3d4-e5f6-4a7b-8c9d-0123456789ab.json",
        ssh_target="provider.example.edu",
        live_config_path="/etc/cloudflared/config.yml",
        verification_url="https://model.example.edu/health",
    )


@pytest.mark.smoke
def test_plan_inspects_existing_tunnel_but_never_mutates() -> None:
    runner = FakeRunner({"cloudflared tunnel info": "healthy"})
    spec = _spec()

    report = configure_tunnel_provider(spec, host=CloudflaredHost(spec, runner))

    assert report.public_base_url == "https://model.example.edu/v1"
    assert "hostname: model.example.edu" in report.candidate_config
    assert any(action.kind == "would_route_dns" for action in report.actions)
    assert not any(" route dns " in " ".join(command) for command in runner.commands)
    assert not any(" cp " in f" {' '.join(command)} " for command in runner.commands)


@pytest.mark.smoke
def test_apply_dns_requires_matching_existing_live_ingress_and_backs_it_up() -> None:
    runner = FakeRunner(
        {
            "cloudflared tunnel info": "healthy",
            "cat /etc/cloudflared/config.yml": """tunnel: a1b2c3d4-e5f6-4a7b-8c9d-0123456789ab
ingress:
  - hostname: model.example.edu
    service: http://127.0.0.1:8000
  - service: http_status:404
""",
            "cp --preserve=mode,timestamps": "",
            "cloudflared tunnel route dns": "created",
            "curl --fail": "ok",
        }
    )
    spec = _spec()

    report = configure_tunnel_provider(
        spec,
        apply_dns=True,
        confirmed_tunnel_id=spec.tunnel_id,
        host=CloudflaredHost(spec, runner),
    )

    assert report.backup_path is not None
    commands = [" ".join(command) for command in runner.commands]
    assert any("cp --preserve=mode,timestamps" in command for command in commands)
    assert any("cloudflared tunnel route dns" in command for command in commands)
    assert any("curl --fail" in command for command in commands)
    assert [action.kind for action in report.actions][-2:] == [
        "inspect_tunnel",
        "verify_public_endpoint",
    ]


@pytest.mark.smoke
def test_apply_dns_refuses_unverified_live_ingress() -> None:
    runner = FakeRunner(
        {
            "cloudflared tunnel info": "healthy",
            "cat /etc/cloudflared/config.yml": """tunnel: a1b2c3d4-e5f6-4a7b-8c9d-0123456789ab
ingress:
  - hostname: other.example.edu
    service: http://127.0.0.1:8000
""",
        }
    )
    spec = _spec()

    with pytest.raises(TunnelConfiguratorError, match="no matching hostname"):
        configure_tunnel_provider(
            spec,
            apply_dns=True,
            confirmed_tunnel_id=spec.tunnel_id,
            host=CloudflaredHost(spec, runner),
        )

    assert not any(" route dns " in " ".join(command) for command in runner.commands)
    assert not any(" cp " in f" {' '.join(command)} " for command in runner.commands)


@pytest.mark.smoke
def test_apply_dns_requires_explicit_matching_confirmation() -> None:
    runner = FakeRunner({"cloudflared tunnel info": "healthy"})
    spec = _spec()

    with pytest.raises(TunnelConfiguratorError, match="confirm-tunnel-id"):
        configure_tunnel_provider(
            spec,
            apply_dns=True,
            confirmed_tunnel_id="not-the-configured-tunnel",
            host=CloudflaredHost(spec, runner),
        )

    assert len(runner.commands) == 1
