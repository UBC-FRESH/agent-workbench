from __future__ import annotations

from agent_workbench.outcomes import (
    OutcomeInput,
    classify_outcome,
    outcome_from_summary,
)


def test_outcome_accepts_quality_protocol_and_economics() -> None:
    outcome = classify_outcome(
        OutcomeInput(
            quality_validated_candidate=True,
            protocol_accepted_candidate=True,
            measured_token_delta=100,
        )
    )

    assert outcome["quality_validated_candidate"] is True
    assert outcome["protocol_accepted_candidate"] is True
    assert outcome["economics_usable"] is True
    assert outcome["final_decision"] == "accepted_economics_evidence"
    assert outcome["rejection_reasons"] == []


def test_quality_valid_protocol_rejected_is_not_bad_artifact() -> None:
    outcome = classify_outcome(
        OutcomeInput(
            quality_validated_candidate=True,
            protocol_accepted_candidate=False,
            measured_token_delta=100,
            protocol_rejection_reasons=("materializer_rerun",),
        )
    )

    assert outcome["quality_validated_candidate"] is True
    assert outcome["protocol_accepted_candidate"] is False
    assert outcome["economics_usable"] is False
    assert outcome["final_decision"] == "quality_valid_protocol_rejected"
    assert outcome["rejection_reasons"] == ["materializer_rerun"]


def test_soft_quote_penalty_does_not_force_rejection() -> None:
    outcome = classify_outcome(
        OutcomeInput(
            quality_validated_candidate=True,
            protocol_accepted_candidate=True,
            measured_token_delta=100,
            soft_penalty=1.25,
            soft_reasons=("quote_length_excess",),
        )
    )

    assert outcome["economics_usable"] is True
    assert outcome["final_decision"] == "accepted_economics_evidence"
    assert outcome["soft_penalty"] == 1.25
    assert outcome["soft_reasons"] == ["quote_length_excess"]
    assert "quote_length_excess" not in outcome["rejection_reasons"]


def test_stale_result_is_diagnostic_even_when_artifact_validates() -> None:
    outcome = classify_outcome(
        OutcomeInput(
            quality_validated_candidate=True,
            protocol_accepted_candidate=True,
            measured_token_delta=100,
            stale=True,
        )
    )

    assert outcome["economics_usable"] is False
    assert outcome["final_decision"] == "stale_diagnostic"
    assert "stale_session_or_artifact" in outcome["rejection_reasons"]


def test_hard_quality_reasons_are_explicit_rejections() -> None:
    outcome = classify_outcome(
        OutcomeInput(
            quality_validated_candidate=False,
            protocol_accepted_candidate=True,
            measured_token_delta=100,
            hard_quality_reasons=(
                "invalid_schema_shape",
                "invalid_source_identity",
                "authority_boundary_violation",
            ),
        )
    )

    assert outcome["quality_validated_candidate"] is False
    assert outcome["protocol_accepted_candidate"] is True
    assert outcome["economics_usable"] is False
    assert outcome["final_decision"] == "protocol_accepted_quality_rejected"
    assert outcome["rejection_reasons"] == [
        "authority_boundary_violation",
        "invalid_schema_shape",
        "invalid_source_identity",
    ]


def test_legacy_summary_backfill_preserves_quality_valid_protocol_rejected() -> None:
    outcome = outcome_from_summary(
        {
            "accepted_candidate": False,
            "quality_validated_candidate": True,
            "protocol_accepted_candidate": False,
            "token_costs": {
                "economics_usable": False,
                "codex_total_token_delta": 123,
            },
        }
    )

    assert outcome["quality_validated_candidate"] is True
    assert outcome["protocol_accepted_candidate"] is False
    assert outcome["final_decision"] == "quality_valid_protocol_rejected"


def test_legacy_summary_backfill_infers_accepted_status() -> None:
    outcome = outcome_from_summary(
        {
            "status": "accepted-candidate",
            "token_costs": {
                "economics_usable": True,
                "codex_total_token_delta": 123,
            },
        }
    )

    assert outcome["quality_validated_candidate"] is True
    assert outcome["protocol_accepted_candidate"] is True
    assert outcome["final_decision"] == "accepted_economics_evidence"
