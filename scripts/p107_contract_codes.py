"""Shared P107 replay reason-code vocabulary."""

REASON_CODES = frozenset(
    {
        "topology_session_reuse",
        "frozen_input_hash_drift",
        "advisor_hard_wait_failure",
        "accounting_ineligible",
        "contaminated",
        "c0_absent_or_mismatched",
        "verified_blocker",
    }
)

REVIEW_CAP = 3

