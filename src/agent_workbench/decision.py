"""Rules-based delegation decision helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RECOMMENDATIONS = {
    "delegate",
    "do-directly",
    "split-smaller",
    "needs-human-decision",
    "defer",
}

RISK_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
SUITABILITY_LEVELS = {
    "high": 4,
    "medium-high": 3,
    "medium": 2,
    "low-medium": 1,
    "low": 0,
    "avoid": -1,
}
ROADMAP_LEVELS = {"project", "phase", "task", "subtask", "closeout"}
PROFILE_STATUSES = {"observed", "partial", "planned", "missing"}
AUTHORITY_LEVELS = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

REQUIRED_FIELDS = (
    "task_id",
    "title",
    "task_type",
    "roadmap_level",
    "suitability",
    "risk",
    "model",
    "authority_level",
    "expected_verification",
)


@dataclass(frozen=True)
class Economics:
    direct_supervisor_input_tokens: float = 0.0
    direct_supervisor_output_tokens: float = 0.0
    delegated_supervisor_input_tokens: float = 0.0
    delegated_supervisor_output_tokens: float = 0.0
    worker_input_tokens: float = 0.0
    worker_output_tokens: float = 0.0
    cleanup_supervisor_input_tokens: float = 0.0
    cleanup_supervisor_output_tokens: float = 0.0
    supervisor_input_price_per_1m_usd: float = 0.0
    supervisor_output_price_per_1m_usd: float = 0.0
    worker_input_price_per_1m_usd: float = 0.0
    worker_output_price_per_1m_usd: float = 0.0
    failure_probability: float = 0.0
    latency_friction_minutes: float = 0.0

    @property
    def direct_supervisor_cost_usd(self) -> float:
        return token_cost_usd(
            self.direct_supervisor_input_tokens,
            self.direct_supervisor_output_tokens,
            self.supervisor_input_price_per_1m_usd,
            self.supervisor_output_price_per_1m_usd,
        )

    @property
    def delegated_supervisor_cost_usd(self) -> float:
        return token_cost_usd(
            self.delegated_supervisor_input_tokens,
            self.delegated_supervisor_output_tokens,
            self.supervisor_input_price_per_1m_usd,
            self.supervisor_output_price_per_1m_usd,
        )

    @property
    def worker_cost_usd(self) -> float:
        return token_cost_usd(
            self.worker_input_tokens,
            self.worker_output_tokens,
            self.worker_input_price_per_1m_usd,
            self.worker_output_price_per_1m_usd,
        )

    @property
    def cleanup_cost_usd(self) -> float:
        return token_cost_usd(
            self.cleanup_supervisor_input_tokens,
            self.cleanup_supervisor_output_tokens,
            self.supervisor_input_price_per_1m_usd,
            self.supervisor_output_price_per_1m_usd,
        )

    @property
    def expected_cleanup_cost_usd(self) -> float:
        return self.failure_probability * self.cleanup_cost_usd

    @property
    def expected_delegated_cost_usd(self) -> float:
        return (
            self.delegated_supervisor_cost_usd
            + self.worker_cost_usd
            + self.expected_cleanup_cost_usd
        )

    @property
    def expected_net_savings_usd(self) -> float:
        return self.direct_supervisor_cost_usd - self.expected_delegated_cost_usd


@dataclass(frozen=True)
class DecisionResult:
    recommendation: str
    task_id: str
    title: str
    task_type: str
    roadmap_level: str
    model: str
    model_profile_status: str
    authority_level: str
    suitability: str
    risk: str
    economics: Economics
    reasons: tuple[str, ...]
    cautions: tuple[str, ...]
    next_action: str


class DecisionInputError(ValueError):
    """Raised when a decision input is missing required fields."""


def load_decision_input(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def decide_task(data: dict[str, Any]) -> DecisionResult:
    errors = validate_decision_input(data)
    if errors:
        raise DecisionInputError("; ".join(errors))

    task_id = str(data["task_id"]).strip()
    title = str(data["title"]).strip()
    task_type = str(data["task_type"]).strip()
    roadmap_level = normalized_lower(data["roadmap_level"])
    suitability = normalized_lower(data["suitability"])
    risk = normalized_lower(data["risk"])
    model = str(data["model"]).strip()
    profile_status = profile_status_from_input(data)
    authority_level = normalized_authority(data["authority_level"])
    economics = parse_economics(data.get("economics", {}))

    nondelegable_flags = {
        "requires_tracked_mutation": "tracked-file mutation",
        "requires_github_mutation": "GitHub mutation",
        "requires_release_or_closeout": "release or closeout authority",
    }
    reasons: list[str] = []
    cautions: list[str] = []

    for field, label in nondelegable_flags.items():
        if bool(data.get(field, False)):
            reasons.append(f"Task requires {label}, which is supervisor-owned.")

    if bool(data.get("requires_private_context", False)):
        reasons.append(
            "Task requires private or hidden context that should not be delegated."
        )

    authority_value = AUTHORITY_LEVELS[authority_level]
    if authority_value >= 4:
        reasons.append(
            f"Requested authority `{authority_level}` is outside the delegated boundary."
        )

    if roadmap_level == "closeout":
        reasons.append("Closeout work is nondelegable by default.")

    if risk == "critical":
        reasons.append("Critical-risk tasks stay in the supervisor lane.")

    if reasons:
        recommendation = "do-directly"
        if bool(data.get("requires_private_context", False)):
            recommendation = "defer"
        next_action = "Keep this work with the supervisor or rewrite the task to remove nondelegable scope."
        return build_result(
            recommendation,
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            next_action,
        )

    if profile_status in {"planned", "missing"}:
        reasons.append(
            f"Model profile status is `{profile_status}`, so capability is not yet observed."
        )
        cautions.append(
            "Run a marker or no-tool proposal probe before assigning project work."
        )
        return build_result(
            "defer",
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            "Verify the model inventory and collect a small capability probe first.",
        )

    if roadmap_level in {"project", "phase"}:
        reasons.append(
            f"Roadmap level `{roadmap_level}` is too broad for direct delegation."
        )
        if profile_status == "partial":
            cautions.append(
                "Partial model profile increases the need for a smaller probe."
            )
        return build_result(
            "split-smaller",
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            "Split into task or subtask tickets before delegation.",
        )

    if suitability == "avoid":
        reasons.append("Task suitability is `avoid`.")
        return build_result(
            "do-directly",
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            "Keep this task in the supervisor lane.",
        )

    if risk == "high":
        reasons.append("High-risk tasks need splitting or direct supervisor handling.")
        recommendation = "split-smaller" if roadmap_level == "task" else "do-directly"
        return build_result(
            recommendation,
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            "Reduce risk and authority before delegation.",
        )

    if economics.expected_net_savings_usd < 0:
        reasons.append(
            "Expected delegation economics are negative "
            f"({format_usd(economics.expected_net_savings_usd)} expected net USD)."
        )
        return build_result(
            "do-directly",
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            "Do the task directly unless it can be batched with related work.",
        )

    if profile_status == "partial":
        reasons.append("Model profile is partial; supervisor judgment is required.")
        cautions.append(
            "Use a repeated run or compare against an observed-profile model."
        )
        return build_result(
            "needs-human-decision",
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            "Review model fit manually before launching the worker ticket.",
        )

    if SUITABILITY_LEVELS[suitability] >= 2 and authority_value <= 1:
        reasons.append(
            "Task suitability, authority, risk, and economics support delegation."
        )
        return build_result(
            "delegate",
            task_id,
            title,
            task_type,
            roadmap_level,
            model,
            profile_status,
            authority_level,
            suitability,
            risk,
            economics,
            reasons,
            cautions,
            "Prepare an L0/L1 bounded worker ticket and verify claims independently.",
        )

    reasons.append(
        "Task may be useful, but the suitability or authority boundary is marginal."
    )
    cautions.append("Tighten the ticket or run a smaller probe before project use.")
    return build_result(
        "needs-human-decision",
        task_id,
        title,
        task_type,
        roadmap_level,
        model,
        profile_status,
        authority_level,
        suitability,
        risk,
        economics,
        reasons,
        cautions,
        "Supervisor should decide whether to split, retry, or proceed with extra verification.",
    )


def validate_decision_input(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data or str(data[field]).strip() == "":
            errors.append(f"missing required field `{field}`")

    if (
        "roadmap_level" in data
        and normalized_lower(data["roadmap_level"]) not in ROADMAP_LEVELS
    ):
        errors.append(f"`roadmap_level` must be one of {sorted(ROADMAP_LEVELS)}")
    if (
        "suitability" in data
        and normalized_lower(data["suitability"]) not in SUITABILITY_LEVELS
    ):
        errors.append(f"`suitability` must be one of {sorted(SUITABILITY_LEVELS)}")
    if "risk" in data and normalized_lower(data["risk"]) not in RISK_LEVELS:
        errors.append(f"`risk` must be one of {sorted(RISK_LEVELS)}")
    if (
        "authority_level" in data
        and normalized_authority(data["authority_level"]) not in AUTHORITY_LEVELS
    ):
        errors.append(f"`authority_level` must be one of {sorted(AUTHORITY_LEVELS)}")

    profile_status = profile_status_from_input(data, allow_missing=True)
    if profile_status is None:
        errors.append("provide `model_profile_status` or `model_profile_path`")
    elif profile_status not in PROFILE_STATUSES:
        errors.append(
            f"`model_profile_status` must be one of {sorted(PROFILE_STATUSES)}"
        )

    economics = data.get("economics", {})
    if economics is not None and not isinstance(economics, dict):
        errors.append("`economics` must be an object when provided")
    elif isinstance(economics, dict):
        probability = float_or_none(economics.get("failure_probability", 0.0))
        if probability is None or probability < 0 or probability > 1:
            errors.append("`economics.failure_probability` must be between 0 and 1")
        for field in (
            "direct_supervisor_input_tokens",
            "direct_supervisor_output_tokens",
            "delegated_supervisor_input_tokens",
            "delegated_supervisor_output_tokens",
            "worker_input_tokens",
            "worker_output_tokens",
            "cleanup_supervisor_input_tokens",
            "cleanup_supervisor_output_tokens",
            "supervisor_input_price_per_1m_usd",
            "supervisor_output_price_per_1m_usd",
            "worker_input_price_per_1m_usd",
            "worker_output_price_per_1m_usd",
            "latency_friction_minutes",
        ):
            value = float_or_none(economics.get(field, 0.0))
            if value is None or value < 0:
                errors.append(f"`economics.{field}` must be a nonnegative number")
    return errors


def render_markdown_report(result: DecisionResult) -> str:
    economics = result.economics
    lines = [
        "# Delegation Decision Report",
        "",
        "## Recommendation",
        "",
        f"- recommendation: `{result.recommendation}`",
        f"- task_id: `{result.task_id}`",
        f"- title: {result.title}",
        f"- task_type: {result.task_type}",
        f"- roadmap_level: `{result.roadmap_level}`",
        f"- model: `{result.model}`",
        f"- model_profile_status: `{result.model_profile_status}`",
        f"- authority_level: `{result.authority_level}`",
        f"- suitability: `{result.suitability}`",
        f"- risk: `{result.risk}`",
        "",
        "## Economics",
        "",
        f"- direct_supervisor_input_tokens: {format_count(economics.direct_supervisor_input_tokens)}",
        f"- direct_supervisor_output_tokens: {format_count(economics.direct_supervisor_output_tokens)}",
        f"- delegated_supervisor_input_tokens: {format_count(economics.delegated_supervisor_input_tokens)}",
        f"- delegated_supervisor_output_tokens: {format_count(economics.delegated_supervisor_output_tokens)}",
        f"- worker_input_tokens: {format_count(economics.worker_input_tokens)}",
        f"- worker_output_tokens: {format_count(economics.worker_output_tokens)}",
        f"- cleanup_supervisor_input_tokens: {format_count(economics.cleanup_supervisor_input_tokens)}",
        f"- cleanup_supervisor_output_tokens: {format_count(economics.cleanup_supervisor_output_tokens)}",
        f"- supervisor_input_price_per_1m_usd: {format_usd(economics.supervisor_input_price_per_1m_usd)}",
        f"- supervisor_output_price_per_1m_usd: {format_usd(economics.supervisor_output_price_per_1m_usd)}",
        f"- worker_input_price_per_1m_usd: {format_usd(economics.worker_input_price_per_1m_usd)}",
        f"- worker_output_price_per_1m_usd: {format_usd(economics.worker_output_price_per_1m_usd)}",
        f"- failure_probability: {economics.failure_probability:.2f}",
        f"- latency_friction_minutes: {format_minutes(economics.latency_friction_minutes)}",
        f"- direct_supervisor_cost_usd: {format_usd(economics.direct_supervisor_cost_usd)}",
        f"- delegated_supervisor_cost_usd: {format_usd(economics.delegated_supervisor_cost_usd)}",
        f"- worker_cost_usd: {format_usd(economics.worker_cost_usd)}",
        f"- expected_cleanup_cost_usd: {format_usd(economics.expected_cleanup_cost_usd)}",
        f"- expected_delegated_cost_usd: {format_usd(economics.expected_delegated_cost_usd)}",
        f"- expected_net_savings_usd: {format_usd(economics.expected_net_savings_usd)}",
        "",
        "## Reasons",
        "",
    ]
    lines.extend(f"- {reason}" for reason in result.reasons)
    if result.cautions:
        lines.extend(["", "## Cautions", ""])
        lines.extend(f"- {caution}" for caution in result.cautions)
    lines.extend(["", "## Supervisor Next Action", "", result.next_action, ""])
    return "\n".join(lines)


def result_to_jsonable(result: DecisionResult) -> dict[str, Any]:
    return {
        "recommendation": result.recommendation,
        "task_id": result.task_id,
        "title": result.title,
        "task_type": result.task_type,
        "roadmap_level": result.roadmap_level,
        "model": result.model,
        "model_profile_status": result.model_profile_status,
        "authority_level": result.authority_level,
        "suitability": result.suitability,
        "risk": result.risk,
        "economics": {
            "direct_supervisor_input_tokens": result.economics.direct_supervisor_input_tokens,
            "direct_supervisor_output_tokens": result.economics.direct_supervisor_output_tokens,
            "delegated_supervisor_input_tokens": (
                result.economics.delegated_supervisor_input_tokens
            ),
            "delegated_supervisor_output_tokens": (
                result.economics.delegated_supervisor_output_tokens
            ),
            "worker_input_tokens": result.economics.worker_input_tokens,
            "worker_output_tokens": result.economics.worker_output_tokens,
            "cleanup_supervisor_input_tokens": (
                result.economics.cleanup_supervisor_input_tokens
            ),
            "cleanup_supervisor_output_tokens": (
                result.economics.cleanup_supervisor_output_tokens
            ),
            "supervisor_input_price_per_1m_usd": (
                result.economics.supervisor_input_price_per_1m_usd
            ),
            "supervisor_output_price_per_1m_usd": (
                result.economics.supervisor_output_price_per_1m_usd
            ),
            "worker_input_price_per_1m_usd": result.economics.worker_input_price_per_1m_usd,
            "worker_output_price_per_1m_usd": (
                result.economics.worker_output_price_per_1m_usd
            ),
            "failure_probability": result.economics.failure_probability,
            "latency_friction_minutes": result.economics.latency_friction_minutes,
            "direct_supervisor_cost_usd": result.economics.direct_supervisor_cost_usd,
            "delegated_supervisor_cost_usd": result.economics.delegated_supervisor_cost_usd,
            "worker_cost_usd": result.economics.worker_cost_usd,
            "expected_cleanup_cost_usd": result.economics.expected_cleanup_cost_usd,
            "expected_delegated_cost_usd": result.economics.expected_delegated_cost_usd,
            "expected_net_savings_usd": result.economics.expected_net_savings_usd,
        },
        "reasons": list(result.reasons),
        "cautions": list(result.cautions),
        "next_action": result.next_action,
    }


def build_result(
    recommendation: str,
    task_id: str,
    title: str,
    task_type: str,
    roadmap_level: str,
    model: str,
    profile_status: str,
    authority_level: str,
    suitability: str,
    risk: str,
    economics: Economics,
    reasons: list[str],
    cautions: list[str],
    next_action: str,
) -> DecisionResult:
    if recommendation not in RECOMMENDATIONS:
        raise ValueError(f"unknown recommendation: {recommendation}")
    return DecisionResult(
        recommendation=recommendation,
        task_id=task_id,
        title=title,
        task_type=task_type,
        roadmap_level=roadmap_level,
        model=model,
        model_profile_status=profile_status,
        authority_level=authority_level,
        suitability=suitability,
        risk=risk,
        economics=economics,
        reasons=tuple(reasons),
        cautions=tuple(cautions),
        next_action=next_action,
    )


def parse_economics(data: Any) -> Economics:
    if not isinstance(data, dict):
        data = {}
    return Economics(
        direct_supervisor_input_tokens=float(
            data.get("direct_supervisor_input_tokens", 0.0)
        ),
        direct_supervisor_output_tokens=float(
            data.get("direct_supervisor_output_tokens", 0.0)
        ),
        delegated_supervisor_input_tokens=float(
            data.get("delegated_supervisor_input_tokens", 0.0)
        ),
        delegated_supervisor_output_tokens=float(
            data.get("delegated_supervisor_output_tokens", 0.0)
        ),
        worker_input_tokens=float(data.get("worker_input_tokens", 0.0)),
        worker_output_tokens=float(data.get("worker_output_tokens", 0.0)),
        cleanup_supervisor_input_tokens=float(
            data.get("cleanup_supervisor_input_tokens", 0.0)
        ),
        cleanup_supervisor_output_tokens=float(
            data.get("cleanup_supervisor_output_tokens", 0.0)
        ),
        supervisor_input_price_per_1m_usd=float(
            data.get("supervisor_input_price_per_1m_usd", 0.0)
        ),
        supervisor_output_price_per_1m_usd=float(
            data.get("supervisor_output_price_per_1m_usd", 0.0)
        ),
        worker_input_price_per_1m_usd=float(
            data.get("worker_input_price_per_1m_usd", 0.0)
        ),
        worker_output_price_per_1m_usd=float(
            data.get("worker_output_price_per_1m_usd", 0.0)
        ),
        failure_probability=float(data.get("failure_probability", 0.0)),
        latency_friction_minutes=float(data.get("latency_friction_minutes", 0.0)),
    )


def profile_status_from_input(
    data: dict[str, Any], allow_missing: bool = False
) -> str | None:
    explicit = data.get("model_profile_status")
    if explicit is not None and str(explicit).strip():
        return normalized_lower(explicit)
    profile_path = data.get("model_profile_path")
    if profile_path:
        path = Path(str(profile_path))
        if not path.exists():
            return "missing"
        text = path.read_text(encoding="utf-8-sig")
        for status in sorted(PROFILE_STATUSES):
            if (
                f"Profile status: `{status}`" in text
                or f"Profile status: {status}" in text
            ):
                return status
        return "partial"
    if allow_missing:
        return None
    return "missing"


def normalized_lower(value: Any) -> str:
    return str(value).strip().lower()


def normalized_authority(value: Any) -> str:
    return str(value).strip().upper()


def float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_minutes(value: float) -> str:
    return f"{value:.1f}"


def format_count(value: float) -> str:
    return f"{value:.0f}"


def format_usd(value: float) -> str:
    return f"{value:.6f}"


def token_cost_usd(
    input_tokens: float,
    output_tokens: float,
    input_price_per_1m_usd: float,
    output_price_per_1m_usd: float,
) -> float:
    return (
        input_tokens / 1_000_000 * input_price_per_1m_usd
        + output_tokens / 1_000_000 * output_price_per_1m_usd
    )
