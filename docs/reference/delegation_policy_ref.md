Delegation Policy Reference
==========================

Full delegation policy is maintained at `planning/delegation_policy.md`. This page summarizes key concepts.

**Trust Levels**: L0–L6 define worker authority boundaries from no-tools through release authority. Only L0–L3 are currently delegated by default.

**Decision Model**: Delegation decisions consider task boundedness, evidence availability, verification capability, and risk assessment before granting tool access to workers.

**Recovery Mechanisms**: Failed runs may trigger supervised repair loops. After two unsuccessful attempts in the same lane, the supervisor must ask the developer whether to continue.

For the complete policy including trust level tables, delegation decisions matrix, and recovery procedures, see `planning/delegation_policy.md`.
