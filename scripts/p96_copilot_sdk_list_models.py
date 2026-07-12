"""List available models via Copilot SDK and write a P96 evidence snapshot.

This script uses the local copilot-sdk source checkout and the repository's
existing BYOK runtime config files:
- runtime/ollama_openai_base_url.txt
- runtime/local_provider_headers.json

It creates a snapshot at:
- runtime/agent_jobs/p96_3_model_inventory_snapshot.md

The script is intentionally read-only with respect to model/provider state.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"missing file: {path}")
    return path.read_text(encoding="utf-8").strip()


def _load_headers(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"headers file is not an object: {path}")
    return data


def main() -> int:
    repo = _repo_root()

    sdk_source = Path.home() / "projects" / "copilot-sdk" / "python"
    if not sdk_source.exists():
        print(f"ERROR: copilot-sdk source not found at {sdk_source}", file=sys.stderr)
        return 2

    base_url_file = repo / "runtime" / "ollama_openai_base_url.txt"
    headers_file = repo / "runtime" / "local_provider_headers.json"
    output_path = repo / "runtime" / "agent_jobs" / "p96_3_model_inventory_snapshot.md"

    base_url = _load_text(base_url_file)
    headers = _load_headers(headers_file)

    # Import Copilot SDK from local clone.
    sys.path.insert(0, str(sdk_source))
    try:
        from copilot import CopilotClient, RuntimeConnection  # type: ignore
    except Exception as exc:  # pragma: no cover - runtime import path
        print(f"ERROR: failed to import copilot SDK from {sdk_source}: {exc}", file=sys.stderr)
        return 3

    # Build runtime env for OpenAI-compatible endpoint in this SDK process.
    env = {
        "AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL": base_url,
    }

    # Use bearer token if present in runtime headers.
    auth_header = None
    for key in ("Authorization", "authorization"):
        if key in headers and isinstance(headers[key], str) and headers[key].strip():
            auth_header = headers[key].strip()
            break
    if auth_header:
        env["AGENT_WORKBENCH_PROVIDER_AUTHORIZATION"] = auth_header

    try:
        import asyncio

        async def _run() -> list:
            copilot_wrapper = (
                Path.home()
                / "AppData"
                / "Roaming"
                / "Code"
                / "User"
                / "globalStorage"
                / "github.copilot-chat"
                / "copilotCli"
                / "copilot.ps1"
            )
            if not copilot_wrapper.exists():
                raise FileNotFoundError(f"copilot wrapper not found: {copilot_wrapper}")

            connection = RuntimeConnection.for_stdio(
                path="powershell.exe",
                args=(
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(copilot_wrapper),
                ),
            )

            client = CopilotClient(connection=connection, env=env)
            await client.start()
            try:
                return client.list_models()
            finally:
                await client.stop()

        models = asyncio.run(_run())
    except Exception as exc:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "\n".join(
                [
                    "# P96.3 Model Inventory Snapshot (Blocked)",
                    "",
                    f"- source: copilot-sdk list_models()",
                    f"- provider base_url: {base_url}",
                    f"- error: {exc}",
                    "",
                    "This run could not list models. Treat as blocker for P96.3.",
                ]
            ),
            encoding="utf-8",
        )
        print(f"blocked: {exc}")
        return 4

    # Normalize model output structures.
    normalized: list[str] = []
    for item in models or []:
        model_id = getattr(item, "id", None) or item.get("id") if isinstance(item, dict) else None
        model_name = getattr(item, "name", None) or item.get("name") if isinstance(item, dict) else None
        if model_id or model_name:
            normalized.append(f"- {model_id or model_name} ({model_name or model_id})")
        else:
            normalized.append(f"- {item}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# P96.3 Model Inventory Snapshot",
        "",
        "- source: copilot-sdk `list_models()`",
        f"- provider base_url: {base_url}",
        "- verification method: copilot-sdk model inventory API",
        "",
        "## Available Models",
    ]
    if normalized:
        lines.extend(normalized)
    else:
        lines.append("- (no models returned)")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
