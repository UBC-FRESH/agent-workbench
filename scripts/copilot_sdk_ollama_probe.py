"""Probe Copilot SDK sessions against an Ollama OpenAI-compatible endpoint.

This helper is intentionally local-only. It records observable SDK events to an
ignored Markdown result file so a supervisor can compare model behavior without
depending on VS Code Chat model-picker state.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT = Path("runtime/agent_jobs/copilot_sdk_ollama_probe_result.md")
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_BASE_DIRECTORY = Path("runtime/copilot_sdk_home")


@dataclass
class ProbeConfig:
    model: str
    base_url: str
    ticket: Path | None
    prompt: str | None
    output: Path
    timeout_seconds: int
    wire_api: str
    mode: str
    sdk_source: Path | None
    base_directory: Path | None
    provider_headers: dict[str, str]


def parse_args() -> ProbeConfig:
    parser = argparse.ArgumentParser(
        description=(
            "Launch a Copilot SDK session through an OpenAI-compatible Ollama "
            "provider and write observed evidence to an ignored result file."
        )
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Explicit Ollama model name, for example qwen3-coder-next:latest.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL"),
        help=(
            "OpenAI-compatible Ollama base URL. Prefer setting "
            "AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL for non-local endpoints."
        ),
    )
    parser.add_argument(
        "--ticket",
        type=Path,
        help="Path to a worker ticket or prompt file. The file contents are sent.",
    )
    parser.add_argument(
        "--prompt",
        help="Inline prompt text. Use --ticket for reproducible worker trials.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Ignored Markdown evidence output path.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum time to wait for session.idle after sending the prompt.",
    )
    parser.add_argument(
        "--wire-api",
        choices=("completions", "responses"),
        default="completions",
        help="Provider wire API. Use completions for broad Ollama compatibility.",
    )
    parser.add_argument(
        "--mode",
        default="empty",
        help=(
            "CopilotClient mode. The default empty mode avoids ambient CLI-style "
            "tools while probing model behavior."
        ),
    )
    parser.add_argument(
        "--base-directory",
        type=Path,
        default=DEFAULT_BASE_DIRECTORY,
        help=(
            "Copilot SDK base directory. The default is ignored runtime storage "
            "so empty mode has explicit local state."
        ),
    )
    parser.add_argument(
        "--sdk-source",
        type=Path,
        default=(
            Path(os.environ["AGENT_WORKBENCH_COPILOT_SDK_PYTHON"])
            if os.environ.get("AGENT_WORKBENCH_COPILOT_SDK_PYTHON")
            else None
        ),
        help=(
            "Optional path to a local Copilot SDK Python source checkout. "
            "Can also be set with AGENT_WORKBENCH_COPILOT_SDK_PYTHON."
        ),
    )
    parser.add_argument(
        "--provider-headers-json",
        default=os.environ.get("AGENT_WORKBENCH_PROVIDER_HEADERS_JSON"),
        help=(
            "Optional JSON object of provider headers. Prefer environment "
            "variables or ignored files for private access headers."
        ),
    )
    parser.add_argument(
        "--provider-headers-file",
        type=Path,
        default=(
            Path(os.environ["AGENT_WORKBENCH_PROVIDER_HEADERS_FILE"])
            if os.environ.get("AGENT_WORKBENCH_PROVIDER_HEADERS_FILE")
            else None
        ),
        help="Optional ignored JSON file containing provider headers.",
    )
    args = parser.parse_args()

    if not args.base_url:
        parser.error(
            "--base-url or AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL is required"
        )
    if bool(args.ticket) == bool(args.prompt):
        parser.error("provide exactly one of --ticket or --prompt")

    return ProbeConfig(
        model=args.model,
        base_url=args.base_url,
        ticket=args.ticket,
        prompt=args.prompt,
        output=args.output,
        timeout_seconds=args.timeout_seconds,
        wire_api=args.wire_api,
        mode=args.mode,
        sdk_source=args.sdk_source,
        base_directory=args.base_directory,
        provider_headers=load_provider_headers(
            args.provider_headers_json,
            args.provider_headers_file,
        ),
    )


def load_prompt(config: ProbeConfig) -> str:
    if config.ticket is not None:
        return config.ticket.read_text(encoding="utf-8-sig")
    if config.prompt is None:
        raise ValueError("prompt is unexpectedly missing")
    return config.prompt


def scrub_base_url(base_url: str) -> str:
    if base_url.startswith("http://localhost") or base_url.startswith(
        "http://127.0.0.1"
    ):
        return base_url
    return "<configured-ollama-openai-base-url>"


def load_provider_headers(
    headers_json: str | None,
    headers_file: Path | None,
) -> dict[str, str]:
    if headers_json and headers_file:
        raise ValueError("use only one of --provider-headers-json or --provider-headers-file")
    raw: str | None = None
    if headers_file is not None:
        raw = headers_file.read_text(encoding="utf-8-sig")
    elif headers_json:
        raw = headers_json
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("provider headers must be a JSON object")
    return {str(key): str(value) for key, value in parsed.items()}


def event_to_record(event: Any) -> dict[str, Any]:
    event_type = getattr(getattr(event, "type", None), "value", None)
    if event_type is None:
        event_type = str(getattr(event, "type", "unknown"))
    data = getattr(event, "data", None)
    return {
        "type": event_type,
        "data": safe_jsonable(data),
    }


def safe_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, dict):
        return {str(k): safe_jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [safe_jsonable(v) for v in value]
    if hasattr(value, "model_dump"):
        return safe_jsonable(value.model_dump())
    if hasattr(value, "__dict__"):
        return safe_jsonable(vars(value))
    return str(value)


def observed_errors(events: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for event in events:
        if event["type"] not in {"model.call_failure", "session.error"}:
            continue
        data = event.get("data")
        if not isinstance(data, dict):
            continue
        message = data.get("error_message") or data.get("message")
        if message:
            errors.append(str(message))
    return errors


async def run_probe(config: ProbeConfig) -> dict[str, Any]:
    if config.sdk_source is not None:
        sys.path.insert(0, str(config.sdk_source))

    try:
        from copilot import CopilotClient
        from copilot.session import PermissionHandler
    except ImportError as exc:
        return {
            "status": "blocked",
            "blocker": "copilot-sdk-import-failed",
            "error": str(exc),
            "events": [],
            "assistant_messages": [],
        }

    prompt = load_prompt(config)
    events: list[dict[str, Any]] = []
    assistant_messages: list[str] = []
    idle = asyncio.Event()

    def on_event(event: Any) -> None:
        record = event_to_record(event)
        events.append(record)
        if record["type"] == "assistant.message":
            content = record.get("data", {}).get("content")
            if content:
                assistant_messages.append(str(content))
        if record["type"] == "session.idle":
            idle.set()

    provider = {
        "type": "openai",
        "base_url": config.base_url,
        "wire_api": config.wire_api,
    }
    if config.provider_headers:
        provider["headers"] = config.provider_headers

    client = None
    try:
        client = CopilotClient(
            mode=config.mode,
            base_directory=str(config.base_directory) if config.base_directory else None,
        )
        await client.start()
        async with await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model=config.model,
            provider=provider,
            available_tools=[],
        ) as session:
            session.on(on_event)
            await session.send(prompt)
            try:
                await asyncio.wait_for(idle.wait(), timeout=config.timeout_seconds)
                errors = observed_errors(events)
                if errors:
                    status = "blocked"
                    blocker = "model-call-failure"
                else:
                    status = "completed"
                    blocker = ""
            except TimeoutError:
                status = "blocked"
                blocker = "session-idle-timeout"
    except Exception as exc:
        status = "blocked"
        blocker = "sdk-runtime-error"
        return {
            "status": status,
            "blocker": blocker,
            "error": f"{type(exc).__name__}: {exc}",
            "events": events,
            "assistant_messages": assistant_messages,
        }
    finally:
        if client is not None:
            await client.stop()

    return {
        "status": status,
        "blocker": blocker,
        "error": "",
        "observed_errors": observed_errors(events),
        "events": events,
        "assistant_messages": assistant_messages,
    }


def write_result(config: ProbeConfig, result: dict[str, Any]) -> None:
    config.output.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    ticket_label = str(config.ticket) if config.ticket else "<inline-prompt>"
    event_types = [event["type"] for event in result["events"]]
    assistant_text = "\n\n".join(result["assistant_messages"]).strip()
    errors = result.get("observed_errors", [])

    body = [
        "# Copilot SDK Ollama Probe Result",
        "",
        f"- generated_utc: `{now}`",
        f"- status: `{result['status']}`",
        f"- blocker: `{result.get('blocker', '')}`",
        f"- error: `{result.get('error', '')}`",
        f"- model: `{config.model}`",
        "- provider_type: `openai`",
        f"- provider_base_url: `{scrub_base_url(config.base_url)}`",
        f"- wire_api: `{config.wire_api}`",
        f"- client_mode: `{config.mode}`",
        f"- base_directory: `{scrub_base_directory(config.base_directory)}`",
        f"- sdk_source: `{scrub_path(config.sdk_source)}`",
        f"- provider_headers: `{bool(config.provider_headers)}`",
        f"- ticket: `{ticket_label}`",
        f"- timeout_seconds: `{config.timeout_seconds}`",
        "",
        "## Event Types",
        "",
        "```json",
        json.dumps(event_types, indent=2),
        "```",
        "",
        "## Observed Errors",
        "",
        "```json",
        json.dumps(errors, indent=2),
        "```",
        "",
        "## Assistant Messages",
        "",
        assistant_text if assistant_text else "_No assistant messages captured._",
        "",
        "## Raw Event Records",
        "",
        "```json",
        json.dumps(result["events"], indent=2, sort_keys=True),
        "```",
        "",
    ]
    config.output.write_text("\n".join(body), encoding="utf-8")


def scrub_path(path: Path | None) -> str:
    if path is None:
        return ""
    return "<configured-copilot-sdk-python-source>"


def scrub_base_directory(path: Path | None) -> str:
    if path is None:
        return ""
    return "<ignored-runtime-base-directory>"


async def async_main() -> int:
    config = parse_args()
    result = await run_probe(config)
    write_result(config, result)
    print(f"wrote {config.output}")
    return 0 if result["status"] == "completed" else 2


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
