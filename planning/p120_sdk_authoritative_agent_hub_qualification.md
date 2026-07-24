# P120: SDK-Authoritative vLLM Agent-Hub Qualification

Date: 2026-07-23

Parent issue: [#755](https://github.com/UBC-FRESH/agent-workbench/issues/755)

Branch: `feature/p120-sdk-authoritative-agent-hub`

Status: active

## Goal

Replace VS Code UI artifact polling as the authority for automated local-model
experiments with SDK-owned Copilot sessions that emit a session ID, event log,
renderable transcript, controller status, and independently verifiable
artifacts. Keep the Keklick Copilot UI route for manual visible smoke tests.

## Evidence To Date

### Quality

- The temporary vLLM swap to the Ornith 35B serving alias completed bounded
  read/edit/validate tasks through the Copilot tool loop.
- A clean SDK fixture run completed a `view -> edit -> PowerShell validation`
  sequence and emitted its required final marker.
- A medium SDK repository synthesis produced a structured, source-cited result
  with bounded reads and an ignored result artifact.
- A Coordinator SDK session invoked one read-only Advisor and received a
  bounded decision packet. The Advisor recommended Coordinator-only execution
  for the next medium read-only workload under the two-sequence cap.

### Protocol

- Keklick ticket transport was changed from stdin attachment to an on-disk
  UTF-8 attachment because the stdin route introduced Windows-codepage
  mojibake in non-ASCII ticket text.
- UI session persistence is not a reliable automation terminal signal: VS Code
  may show completion before `chatSessions`/transcript files settle, and stale
  state fields may persist. The UI bridge now recognizes transcript evidence
  when it is present, but SDK sessions are the automation authority.
- SDK manifests now accept a generic OpenAI-compatible base URL and model
  alias, with local-only request-header injection. A manifest model override
  ensures Coordinator, Advisor, and Worker profiles share the serving alias.
- The SDK profile catalog now includes the Coordinator and Advisor profiles.
  The Coordinator profile description was quoted to make its YAML parseable.

### Economics

- These local provider runs have no captured cloud spend record.
- The vLLM server concurrency cap is two sequences. Coordinator-plus-Advisor
  is therefore the maximum intended concurrent topology for the current
  qualification lane.

## Current Operating Rule

Use SDK-owned sessions for automated qualification and evidence capture. Use
Keklick Copilot UI sessions only for manual integration smoke tests. Do not
derive automation completion from UI artifact polling alone.

## Next Tasks

1. Run a tightly scoped Coordinator-to-Worker implementation and independent
   Coordinator validation through the SDK lane.
2. Tighten Coordinator/Advisor tool and context boundaries; the first Advisor
   run read more context than its bounded decision required.
3. Add a small public-safe SDK result renderer that reports quality, protocol,
   and economics separately from raw runtime events.
4. Resolve the unrelated `ROADMAP.md` worktree change before synchronizing this
   phase into the roadmap and changelog.

## Verification

- `pytest tests/test_copilot_sdk_bridge.py tests/test_copilot_agent_profiles.py -q`
  passed with 42 tests after the profile catalog and model-override changes.
- The ignored runtime directory contains the SDK manifests, event logs,
  transcripts, and fixture validators for the bounded S13/S14/S16 probes.

## Public-Safety Boundary

This note intentionally excludes endpoint URLs, authorization values, raw
transcripts, absolute local paths, and provider secrets.
