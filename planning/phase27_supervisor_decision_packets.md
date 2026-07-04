# Phase 27 Supervisor Decision Packets

Phase 27 responds to the first real FreshForge deployment pilot. That pilot
showed two practical gaps:

- multiple scaffolded worker manifests can collide if they share one eval output
  directory; and
- the supervisor still has to manually turn several worker outputs into one
  decision packet.

## Implemented Surface

`agent-workbench pilot pack-scaffold` creates multiple proposal-ticket artifacts
in one command. Each task receives isolated paths for:

- ticket file;
- eval manifest;
- evidence summary stub;
- eval output directory; and
- Copilot SDK scratch directory.

`agent-workbench evidence synthesize` validates multiple evidence summary JSON
files and renders one Markdown supervisor decision packet. Invalid or
private-looking evidence summaries stop synthesis rather than being silently
promoted.

## Boundary

P27 does not add autonomous worker authority. Workers remain no-tool or
proposal-only by default. The decision packet is an input for supervisor review,
not proof that worker claims are true.
