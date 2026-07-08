"""Copilot SDK-owned session manifests and runtime helpers."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .evidence import find_private_values


REQUIRED_MANIFEST_FIELDS = (
    "schema_version",
    "run_id",
    "phase",
    "governing_issue",
    "child_issue",
    "target_project",
    "target_task",
    "workspace_root",
    "sdk",
    "paths",
    "control",
    "state",
    "privacy",
)

REQUIRED_SDK_FIELDS = (
    "provider",
    "session_id",
    "resumable",
    "model",
    "permission_mode",
    "mode",
    "base_directory",
)
REQUIRED_PATH_FIELDS = (
    "ticket",
    "result",
    "blocker",
    "heartbeat",
    "event_log",
    "status_summary",
    "nudge_log",
)
REQUIRED_CONTROL_FIELDS = (
    "stall_seconds",
    "nonprogress_event_limit",
    "max_nudges",
    "max_retries",
    "stop_condition",
)
ALLOWED_PERMISSION_MODES = (
    "operator-configured",
    "autopilot",
    "bypass approvals",
    "default approvals",
)
TERMINAL_STATUSES = (
    "blocked",
    "completion_candidate",
    "accepted_candidate",
    "rejected_candidate",
)


@dataclass(frozen=True)
class SdkBridgeValidation:
    ok: bool
    errors: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class SdkTurnConfig:
    manifest_path: Path
    prompt_text: str | None = None
    prompt_path: Path | None = None
    resume: bool = False
    nudge_text: str | None = None
    timeout_seconds: int | None = None
    update_manifest: bool = True


class SdkSession(Protocol):
    session_id: str

    async def send(self, prompt: str) -> None:
        """Send text to the SDK session."""


class SdkAdapter(Protocol):
    async def start(self) -> None:
        """Start the SDK client."""

    async def stop(self) -> None:
        """Stop the SDK client."""

    async def create_session(
        self,
        manifest: dict[str, Any],
        on_event: Any,
    ) -> SdkSession:
        """Create a new SDK-owned session."""

    async def resume_session(
        self,
        manifest: dict[str, Any],
        on_event: Any,
    ) -> SdkSession:
        """Resume a previously recorded SDK-owned session."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_sdk_session_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Copilot SDK session manifest must be a JSON object")
    return data


def validate_sdk_session_manifest(
    manifest: dict[str, Any],
    *,
    manifest_path: Path | None = None,
    require_existing_ticket: bool = True,
    require_existing_workspace: bool = True,
) -> SdkBridgeValidation:
    errors: list[str] = []
    warnings: list[str] = []
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"missing required field: {field}")

    run_id = str(manifest.get("run_id", ""))
    if len(run_id) < 8 or any(char.isspace() for char in run_id):
        errors.append("run_id must be at least 8 non-whitespace characters")

    sdk = manifest.get("sdk")
    if not isinstance(sdk, dict):
        errors.append("sdk must be an object")
        sdk = {}
    for field in REQUIRED_SDK_FIELDS:
        if field not in sdk:
            errors.append(f"sdk missing required field: {field}")

    permission_mode = str(sdk.get("permission_mode", ""))
    if permission_mode not in ALLOWED_PERMISSION_MODES:
        errors.append(f"invalid sdk.permission_mode: {permission_mode}")
    for field in ("mode", "base_directory"):
        if field in sdk and not isinstance(sdk[field], str):
            errors.append(f"sdk.{field} must be a string")

    session_id = str(sdk.get("session_id", ""))
    if (
        manifest.get("state", {}).get("latest_status") in TERMINAL_STATUSES
        and not session_id
    ):
        warnings.append("terminal-looking state has no sdk.session_id")

    paths = manifest.get("paths")
    if not isinstance(paths, dict):
        errors.append("paths must be an object")
        paths = {}
    for field in REQUIRED_PATH_FIELDS:
        if field not in paths:
            errors.append(f"paths missing required field: {field}")
        elif not isinstance(paths[field], str) or not paths[field]:
            errors.append(f"paths.{field} must be a non-empty string")

    control = manifest.get("control")
    if not isinstance(control, dict):
        errors.append("control must be an object")
        control = {}
    for field in REQUIRED_CONTROL_FIELDS:
        if field not in control:
            errors.append(f"control missing required field: {field}")
    for field in (
        "stall_seconds",
        "nonprogress_event_limit",
        "max_nudges",
        "max_retries",
    ):
        value = control.get(field)
        if not isinstance(value, int) or value < 0:
            errors.append(f"control.{field} must be a non-negative integer")

    state = manifest.get("state")
    if not isinstance(state, dict):
        errors.append("state must be an object")
    privacy = manifest.get("privacy")
    if not isinstance(privacy, dict):
        errors.append("privacy must be an object")
    elif privacy.get("raw_events_local_only") is not True:
        errors.append("privacy.raw_events_local_only must be true")

    base = manifest_path.parent if manifest_path is not None else Path(".")
    workspace_root = resolve_manifest_path(base, manifest.get("workspace_root"))
    if (
        require_existing_workspace
        and workspace_root is not None
        and not workspace_root.exists()
    ):
        errors.append(f"workspace_root does not exist: {workspace_root}")

    ticket_path = resolve_manifest_path(base, paths.get("ticket"))
    if require_existing_ticket and ticket_path is not None and not ticket_path.exists():
        errors.append(f"paths.ticket does not exist: {ticket_path}")

    public_scan = dict(manifest)
    public_scan.pop("workspace_root", None)
    for finding in find_private_values(public_scan):
        errors.append(f"private-looking value detected: {finding}")

    return SdkBridgeValidation(ok=not errors, errors=errors, warnings=warnings)


def resolve_manifest_path(base: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return base / path


def load_prompt(config: SdkTurnConfig, manifest: dict[str, Any]) -> str:
    if config.prompt_text is not None:
        return config.prompt_text
    if config.prompt_path is not None:
        return config.prompt_path.read_text(encoding="utf-8-sig")
    ticket_path = resolve_manifest_path(
        config.manifest_path.parent, manifest["paths"]["ticket"]
    )
    if ticket_path is None:
        raise ValueError("paths.ticket is required when no prompt is supplied")
    return ticket_path.read_text(encoding="utf-8-sig")


def event_to_record(event: Any) -> dict[str, Any]:
    event_type = getattr(getattr(event, "type", None), "value", None)
    if event_type is None:
        event_type = str(getattr(event, "type", "unknown"))
    data = getattr(event, "data", None)
    return {
        "timestamp": utc_now(),
        "type": event_type,
        "data": safe_jsonable(data),
    }


def safe_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, dict):
        return {str(key): safe_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [safe_jsonable(item) for item in value]
    if hasattr(value, "model_dump"):
        return safe_jsonable(value.model_dump())
    if hasattr(value, "__dict__"):
        return safe_jsonable(vars(value))
    return str(value)


def event_errors(events: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for event in events:
        if event.get("type") not in {"model.call_failure", "session.error"}:
            continue
        data = event.get("data")
        if isinstance(data, dict):
            message = (
                data.get("error_message") or data.get("message") or data.get("error")
            )
            if message:
                errors.append(str(message))
    return errors


def load_sdk_event_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"line {line_number}: invalid SDK event JSON: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number}: SDK event record must be an object")
        records.append(value)
    return records


def count_nudge_records(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid nudge JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number}: nudge record must be an object")
        count += 1
    return count


def monitor_sdk_session(
    manifest_path: Path,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    manifest = load_sdk_session_manifest(manifest_path)
    validation = validate_sdk_session_manifest(
        manifest,
        manifest_path=manifest_path,
        require_existing_ticket=False,
        require_existing_workspace=False,
    )
    base = manifest_path.parent
    event_log = resolve_manifest_path(base, manifest["paths"]["event_log"])
    nudge_log = resolve_manifest_path(base, manifest["paths"]["nudge_log"])
    if event_log is None or nudge_log is None:
        raise ValueError("event_log and nudge_log paths are required")
    events = load_sdk_event_jsonl(event_log)
    nudge_count = count_nudge_records(nudge_log)
    summary = summarize_sdk_events(
        manifest,
        events,
        validation=validation,
        nudge_count=nudge_count,
        now=now,
    )
    status_summary = resolve_manifest_path(base, manifest["paths"]["status_summary"])
    if status_summary is not None:
        status_summary.parent.mkdir(parents=True, exist_ok=True)
        status_summary.write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    return summary


def summarize_sdk_events(
    manifest: dict[str, Any],
    events: list[dict[str, Any]],
    *,
    validation: SdkBridgeValidation,
    nudge_count: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    event_types = [str(event.get("type", "")) for event in events]
    latest_event_at = latest_event_timestamp(manifest, events)
    age_seconds = event_age_seconds(latest_event_at, now)
    control = manifest.get("control", {})
    stall_seconds = int(control.get("stall_seconds", 0))
    max_nudges = int(control.get("max_nudges", 0))
    stop_rule_triggered = max_nudges > 0 and nudge_count >= max_nudges
    observed_errors = event_errors(events)
    latest_status = classify_sdk_status(
        manifest,
        events,
        validation=validation,
        observed_errors=observed_errors,
        age_seconds=age_seconds,
        stop_rule_triggered=stop_rule_triggered,
    )
    return {
        "generated_utc": utc_now(),
        "run_id": manifest.get("run_id", ""),
        "phase": manifest.get("phase", ""),
        "governing_issue": manifest.get("governing_issue", ""),
        "child_issue": manifest.get("child_issue", ""),
        "session_id": manifest.get("sdk", {}).get("session_id", ""),
        "event_count": len(events),
        "event_types": event_types,
        "last_event_type": event_types[-1] if event_types else "",
        "latest_event_at": latest_event_at,
        "age_seconds": age_seconds,
        "stall_seconds": stall_seconds,
        "nudge_count": nudge_count,
        "max_nudges": max_nudges,
        "stop_rule_triggered": stop_rule_triggered,
        "latest_status": latest_status,
        "observed_errors": observed_errors,
        "validation_ok": validation.ok,
        "validation_errors": validation.errors,
        "validation_warnings": validation.warnings,
        "recommended_coordinator_action": recommend_sdk_action(
            latest_status, stop_rule_triggered
        ),
        "recommended_nudge": suggest_sdk_nudge(latest_status, stop_rule_triggered),
    }


def latest_event_timestamp(
    manifest: dict[str, Any], events: list[dict[str, Any]]
) -> str:
    for event in reversed(events):
        timestamp = event.get("timestamp")
        if isinstance(timestamp, str) and timestamp.strip():
            return timestamp
    state = manifest.get("state", {})
    if isinstance(state, dict):
        timestamp = state.get("latest_event_at")
        if isinstance(timestamp, str):
            return timestamp
    return ""


def event_age_seconds(timestamp: str, now: datetime) -> int | None:
    if not timestamp:
        return None
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return max(0, int((now - parsed.astimezone(timezone.utc)).total_seconds()))


def classify_sdk_status(
    manifest: dict[str, Any],
    events: list[dict[str, Any]],
    *,
    validation: SdkBridgeValidation,
    observed_errors: list[str],
    age_seconds: int | None,
    stop_rule_triggered: bool,
) -> str:
    if not validation.ok or observed_errors:
        return "blocked"
    if stop_rule_triggered:
        return "quiet_stall"
    control = manifest.get("control", {})
    stall_seconds = int(control.get("stall_seconds", 0))
    event_types = [str(event.get("type", "")) for event in events]
    if "session.idle" in event_types and "assistant.message" in event_types:
        return "completion_candidate"
    if repeated_nonprogress(events, int(control.get("nonprogress_event_limit", 0))):
        return "nonprogress_stall"
    if age_seconds is not None and stall_seconds > 0 and age_seconds > stall_seconds:
        return "quiet_stall"
    if not events:
        return "monitoring"
    return "active"


def repeated_nonprogress(events: list[dict[str, Any]], limit: int) -> bool:
    if limit <= 1 or len(events) < limit:
        return False
    tail = events[-limit:]
    signatures = [json.dumps(event.get("data", {}), sort_keys=True) for event in tail]
    types = [str(event.get("type", "")) for event in tail]
    return len(set(types)) == 1 and len(set(signatures)) == 1


def recommend_sdk_action(latest_status: str, stop_rule_triggered: bool) -> str:
    if stop_rule_triggered:
        return "stop-and-review"
    if latest_status == "completion_candidate":
        return "verify-result-or-blocker"
    if latest_status == "blocked":
        return "inspect-blocker"
    if latest_status in {"quiet_stall", "nonprogress_stall"}:
        return "send-sdk-nudge"
    if latest_status == "monitoring":
        return "wait"
    return "continue-monitoring"


def suggest_sdk_nudge(latest_status: str, stop_rule_triggered: bool) -> str:
    if stop_rule_triggered:
        return (
            "Stop this SDK session lane and write the blocker file. The repeated-nudge "
            "stop rule has triggered; do not continue until the coordinator reviews "
            "the event log, nudge log, status summary, result, and blocker."
        )
    if latest_status == "quiet_stall":
        return (
            "You stalled. Continue the assigned task from the last concrete action. "
            "If you cannot proceed, write the blocker file with the exact blocker."
        )
    if latest_status == "nonprogress_stall":
        return (
            "Stop repeating status. Take the next concrete action for the assigned "
            "task now, or write the blocker file with the exact reason you cannot."
        )
    if latest_status == "blocked":
        return "No nudge yet. Inspect the blocker/error evidence and decide repair or abandon."
    if latest_status == "completion_candidate":
        return (
            "No nudge needed. Verify the result or blocker file against the worktree."
        )
    return "No nudge needed. Continue monitoring."


def render_sdk_monitor_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Copilot SDK Session Monitor",
        "",
        f"- run_id: `{summary.get('run_id', '')}`",
        f"- session_id: `{summary.get('session_id', '')}`",
        f"- latest_status: `{summary.get('latest_status', '')}`",
        f"- recommended_coordinator_action: `{summary.get('recommended_coordinator_action', '')}`",
        f"- event_count: {summary.get('event_count', 0)}",
        f"- last_event_type: `{summary.get('last_event_type', '')}`",
        f"- age_seconds: `{summary.get('age_seconds', '')}`",
        f"- nudge_count: {summary.get('nudge_count', 0)}",
        f"- stop_rule_triggered: `{summary.get('stop_rule_triggered', False)}`",
        "",
        "## Recommended Nudge",
        "",
        str(summary.get("recommended_nudge", "")),
        "",
    ]
    errors = summary.get("observed_errors", [])
    if errors:
        lines.extend(["## Observed Errors", ""])
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    validation_errors = summary.get("validation_errors", [])
    if validation_errors:
        lines.extend(["## Validation Errors", ""])
        lines.extend(f"- {error}" for error in validation_errors)
        lines.append("")
    return "\n".join(lines)


async def run_sdk_turn(config: SdkTurnConfig, adapter: SdkAdapter) -> dict[str, Any]:
    manifest = load_sdk_session_manifest(config.manifest_path)
    validation = validate_sdk_session_manifest(
        manifest, manifest_path=config.manifest_path
    )
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))

    prompt = load_prompt(config, manifest)
    events: list[dict[str, Any]] = []
    idle = asyncio.Event()

    def on_event(event: Any) -> None:
        record = event_to_record(event)
        events.append(record)
        if record["type"] == "session.idle":
            idle.set()

    await adapter.start()
    session: SdkSession | None = None
    status = "prompt_sent"
    blocker = ""
    try:
        if config.resume:
            if not str(manifest["sdk"].get("session_id", "")).strip():
                raise ValueError("resume requires sdk.session_id")
            session = await adapter.resume_session(manifest, on_event)
            status = "resumed"
        else:
            session = await adapter.create_session(manifest, on_event)
            manifest["sdk"]["session_id"] = session.session_id
            status = "created"

        await session.send(prompt)
        status = "nudge_sent" if config.nudge_text else "prompt_sent"
        timeout = config.timeout_seconds
        if timeout is None:
            timeout = int(manifest["control"]["stall_seconds"])
        try:
            await asyncio.wait_for(idle.wait(), timeout=max(1, timeout))
        except TimeoutError:
            status = "quiet_stall"
            blocker = "session-idle-timeout"
        errors = event_errors(events)
        if errors:
            status = "blocked"
            blocker = "sdk-event-error"
    finally:
        await adapter.stop()

    if status == "prompt_sent" and idle.is_set():
        status = "completion_candidate"
    if status == "nudge_sent" and idle.is_set():
        status = "completion_candidate"

    summary = build_status_summary(
        manifest,
        session_id=session.session_id if session is not None else "",
        status=status,
        blocker=blocker,
        events=events,
        validation=validation,
    )
    write_sdk_turn_outputs(
        config.manifest_path,
        manifest,
        summary,
        events,
        nudge_text=config.nudge_text,
        update_manifest=config.update_manifest,
    )
    return summary


def build_status_summary(
    manifest: dict[str, Any],
    *,
    session_id: str,
    status: str,
    blocker: str,
    events: list[dict[str, Any]],
    validation: SdkBridgeValidation,
) -> dict[str, Any]:
    event_types = [str(event.get("type", "")) for event in events]
    return {
        "generated_utc": utc_now(),
        "run_id": manifest.get("run_id", ""),
        "phase": manifest.get("phase", ""),
        "governing_issue": manifest.get("governing_issue", ""),
        "child_issue": manifest.get("child_issue", ""),
        "session_id": session_id or manifest.get("sdk", {}).get("session_id", ""),
        "latest_status": status,
        "blocker": blocker,
        "event_count": len(events),
        "event_types": event_types,
        "validation_ok": validation.ok,
        "validation_warnings": validation.warnings,
        "observed_errors": event_errors(events),
    }


def write_sdk_turn_outputs(
    manifest_path: Path,
    manifest: dict[str, Any],
    summary: dict[str, Any],
    events: list[dict[str, Any]],
    *,
    nudge_text: str | None,
    update_manifest: bool,
) -> None:
    base = manifest_path.parent
    paths = manifest["paths"]
    event_log = resolve_manifest_path(base, paths["event_log"])
    status_summary = resolve_manifest_path(base, paths["status_summary"])
    nudge_log = resolve_manifest_path(base, paths["nudge_log"])

    if event_log is None or status_summary is None or nudge_log is None:
        raise ValueError("event_log, status_summary, and nudge_log paths are required")

    event_log.parent.mkdir(parents=True, exist_ok=True)
    with event_log.open("a", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event, sort_keys=True) + "\n")

    status_summary.parent.mkdir(parents=True, exist_ok=True)
    status_summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if nudge_text is not None:
        nudge_log.parent.mkdir(parents=True, exist_ok=True)
        with nudge_log.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    {
                        "timestamp": utc_now(),
                        "run_id": manifest.get("run_id", ""),
                        "session_id": summary.get("session_id", ""),
                        "nudge_text": nudge_text,
                        "status_after_send": summary.get("latest_status", ""),
                    },
                    sort_keys=True,
                )
                + "\n"
            )

    manifest["state"]["latest_status"] = summary["latest_status"]
    manifest["state"]["latest_event_at"] = summary["generated_utc"]
    if nudge_text is not None:
        manifest["state"]["latest_nudge_at"] = summary["generated_utc"]
    if update_manifest:
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )


class LiveCopilotSdkSession:
    def __init__(self, raw_session: Any, context_manager: Any | None = None):
        self.raw_session = raw_session
        self.context_manager = context_manager
        self.session_id = str(
            getattr(raw_session, "id", "")
            or getattr(raw_session, "session_id", "")
            or getattr(raw_session, "uuid", "")
        )

    async def send(self, prompt: str) -> None:
        await self.raw_session.send(prompt)

    async def close(self) -> None:
        if self.context_manager is not None:
            await self.context_manager.__aexit__(None, None, None)


class LiveCopilotSdkAdapter:
    def __init__(self) -> None:
        self.client: Any | None = None
        self.client_class: Any | None = None
        self.permission_handler: Any | None = None
        self.open_session: LiveCopilotSdkSession | None = None

    async def start(self) -> None:
        try:
            from copilot import CopilotClient
            from copilot.session import PermissionHandler
        except ImportError as exc:
            raise RuntimeError(f"copilot SDK import failed: {exc}") from exc
        self.client_class = CopilotClient
        self.permission_handler = PermissionHandler

    async def stop(self) -> None:
        if self.open_session is not None:
            await self.open_session.close()
            self.open_session = None
        if self.client is not None:
            await self.client.stop()
            self.client = None

    async def ensure_client(self, manifest: dict[str, Any]) -> None:
        if self.client is not None:
            return
        if self.client_class is None:
            raise RuntimeError("SDK client class is not loaded")
        sdk = manifest.get("sdk", {})
        mode = str(sdk.get("mode", "empty")).strip() or "empty"
        base_directory = str(sdk.get("base_directory", "")).strip()
        kwargs: dict[str, Any] = {"mode": mode}
        if base_directory:
            kwargs["base_directory"] = base_directory
        self.client = self.client_class(**kwargs)
        await self.client.start()

    async def create_session(
        self,
        manifest: dict[str, Any],
        on_event: Any,
    ) -> LiveCopilotSdkSession:
        await self.ensure_client(manifest)
        if self.client is None or self.permission_handler is None:
            raise RuntimeError("SDK client is not started")
        kwargs = self._session_kwargs(manifest)
        context_manager = await self.client.create_session(**kwargs)
        raw_session = await context_manager.__aenter__()
        raw_session.on(on_event)
        self.open_session = LiveCopilotSdkSession(raw_session, context_manager)
        return self.open_session

    async def resume_session(
        self,
        manifest: dict[str, Any],
        on_event: Any,
    ) -> LiveCopilotSdkSession:
        await self.ensure_client(manifest)
        if self.client is None:
            raise RuntimeError("SDK client is not started")
        if not hasattr(self.client, "resume_session"):
            raise RuntimeError("installed copilot SDK does not expose resume_session")
        session_id = str(manifest["sdk"].get("session_id", ""))
        raw = await self.client.resume_session(session_id)
        if hasattr(raw, "__aenter__"):
            raw_session = await raw.__aenter__()
            context_manager = raw
        else:
            raw_session = raw
            context_manager = None
        raw_session.on(on_event)
        self.open_session = LiveCopilotSdkSession(raw_session, context_manager)
        return self.open_session

    def _session_kwargs(self, manifest: dict[str, Any]) -> dict[str, Any]:
        sdk = manifest.get("sdk", {})
        kwargs: dict[str, Any] = {
            "on_permission_request": self.permission_handler.approve_all,
        }
        model = str(sdk.get("model", "")).strip()
        if model:
            kwargs["model"] = model
        provider_config = sdk.get("provider_config")
        if isinstance(provider_config, dict):
            kwargs["provider"] = provider_config
        working_directory = str(sdk.get("working_directory", "")).strip()
        if working_directory:
            working_directory_path = Path(working_directory)
            if not working_directory_path.is_absolute():
                working_directory_path = working_directory_path.resolve()
            kwargs["working_directory"] = str(working_directory_path)
        available_tools = sdk.get("available_tools", "default")
        if isinstance(available_tools, list):
            kwargs["available_tools"] = available_tools
        elif available_tools == "none":
            kwargs["available_tools"] = []
        elif available_tools == "builtin-isolated":
            from copilot import BUILTIN_TOOLS_ISOLATED, ToolSet

            kwargs["available_tools"] = ToolSet().add_builtin(BUILTIN_TOOLS_ISOLATED)
        return kwargs


async def run_live_sdk_turn(config: SdkTurnConfig) -> dict[str, Any]:
    return await run_sdk_turn(config, LiveCopilotSdkAdapter())
