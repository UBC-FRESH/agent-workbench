"""Outcome classification helpers for benchmark summaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OutcomeInput:
    quality_validated_candidate: bool
    protocol_accepted_candidate: bool
    measured_token_delta: int = 0
    stale: bool = False
    aborted: bool = False
    hard_quality_reasons: tuple[str, ...] = ()
    protocol_rejection_reasons: tuple[str, ...] = ()
    economics_rejection_reasons: tuple[str, ...] = ()
    soft_penalty: float = 0.0
    soft_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def classify_outcome(input_data: OutcomeInput) -> dict[str, Any]:
    """Return canonical split outcome fields.

    The classifier intentionally separates artifact quality, protocol
    compliance, and economics usability. A quality-valid artifact can therefore
    remain useful evidence even when the run is protocol-rejected or only
    economics-diagnostic.
    """

    quality = bool(input_data.quality_validated_candidate)
    protocol = bool(input_data.protocol_accepted_candidate)
    reasons: list[str] = []
    reasons.extend(reason for reason in input_data.hard_quality_reasons if reason)
    reasons.extend(reason for reason in input_data.protocol_rejection_reasons if reason)
    reasons.extend(reason for reason in input_data.economics_rejection_reasons if reason)

    if input_data.stale:
        reasons.append("stale_session_or_artifact")
    if input_data.aborted:
        reasons.append("aborted_run")
    if not quality and not input_data.hard_quality_reasons:
        reasons.append("quality_not_validated")
    if not protocol and not input_data.protocol_rejection_reasons:
        reasons.append("protocol_not_accepted")
    if input_data.measured_token_delta <= 0:
        reasons.append("missing_positive_token_delta")

    economics = (
        quality
        and protocol
        and not input_data.stale
        and not input_data.aborted
        and input_data.measured_token_delta > 0
        and not input_data.economics_rejection_reasons
    )

    final_decision = final_decision_for(
        quality=quality,
        protocol=protocol,
        economics=economics,
        stale=input_data.stale,
        aborted=input_data.aborted,
    )

    return {
        "quality_validated_candidate": quality,
        "protocol_accepted_candidate": protocol,
        "economics_usable": economics,
        "final_decision": final_decision,
        "rejection_reasons": sorted(set(reasons)),
        "soft_penalty": round(float(input_data.soft_penalty), 6),
        "soft_reasons": sorted(set(reason for reason in input_data.soft_reasons if reason)),
        "metadata": input_data.metadata,
    }


def final_decision_for(
    *,
    quality: bool,
    protocol: bool,
    economics: bool,
    stale: bool,
    aborted: bool,
) -> str:
    if stale:
        return "stale_diagnostic"
    if aborted:
        return "aborted_diagnostic"
    if quality and protocol and economics:
        return "accepted_economics_evidence"
    if quality and protocol:
        return "accepted_quality_protocol_diagnostic"
    if quality and not protocol:
        return "quality_valid_protocol_rejected"
    if not quality and protocol:
        return "protocol_accepted_quality_rejected"
    return "rejected"


def outcome_from_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Backfill split fields for legacy summary dictionaries."""

    token_costs = data.get("token_costs", {})
    if not isinstance(token_costs, dict):
        token_costs = {}
    accepted_value = data.get("accepted_candidate")
    if accepted_value is None:
        status = str(data.get("status", ""))
        accepted = status.startswith("accepted") or status in {
            "completed",
            "completed_with_caveats",
        }
    else:
        accepted = bool(accepted_value)
    quality = bool(data.get("quality_validated_candidate", accepted))
    protocol = bool(data.get("protocol_accepted_candidate", accepted))
    economics = bool(token_costs.get("economics_usable", data.get("economics_usable")))
    token_delta = int(token_costs.get("codex_total_token_delta", 0) or 0)
    if token_delta <= 0 and economics:
        token_delta = 1
    return classify_outcome(
        OutcomeInput(
            quality_validated_candidate=quality,
            protocol_accepted_candidate=protocol,
            measured_token_delta=token_delta,
            economics_rejection_reasons=()
            if economics
            else ("legacy_summary_not_economics_usable",),
        )
    )
