# Phase 16 Command Surface Stabilization Notes

Phase 16 stabilized the local script command surfaces enough to keep using
Markdown protocols plus scripts without introducing package, CLI, CI, extension,
MCP, or hosted-agent scope.

## Command Surfaces

The current reusable local scripts are:

- `scripts/copilot_chat_bridge.py`: visible VS Code Chat bridge for
  tool-observable worker trials.
- `scripts/copilot_sdk_ollama_probe.py`: one-shot SDK/Ollama probe with
  explicit provider and model inputs.
- `scripts/sdk_same_ticket_eval.py`: repeated same-ticket SDK/Ollama runner and
  summarizer.
- `scripts/supervisor_patch_apply.py`: supervisor-side add-only patch proposal
  applier for ignored sandbox targets.
- `scripts/check_command_surfaces.py`: P16 smoke checker for help surfaces,
  manifest template fields, and SDK harness dry-run planning.

The scripts remain direct Python files. They are not presented as a stable
installed CLI.

## Manifest And Report Metadata

The SDK evaluation manifest template remains the public contract for repeated
model trials. It includes:

- ticket and expected-output fields;
- required-section and forbidden-phrase fields;
- patch-proposal constraints;
- model list and repeat count;
- output directory and probe script references;
- provider input references; and
- mode, wire API, base-directory, and optional SDK source controls.

The smoke checker validates the template has the expected top-level fields. It
does not validate private runtime manifests because those may contain ignored
local provider references.

## Redaction Boundary

Tracked command examples may name ignored runtime files, but they must not
include provider URLs, access headers, raw assistant messages, workstation
paths, or private transcripts. The existing SDK harness redacts private command
values when printing dry-run commands. P16 keeps that policy and adds smoke
coverage to ensure command surfaces remain discoverable.

## Smoke Check

The P16 smoke checker performs three local checks:

- calls `--help` on every reusable script and confirms important option names
  are present;
- parses `templates/sdk_eval_manifest.json` and checks required field names;
  and
- creates an ignored runtime ticket/manifest and runs
  `scripts/sdk_same_ticket_eval.py --dry-run`.

The dry run uses a placeholder local provider URL and does not contact the
configured model host.

## Package-Readiness Checkpoint

The command surfaces are stable enough for continued local-script use. They are
not yet stable enough to justify a package or public CLI because:

- runtime evidence layout is still being normalized in P17;
- bridge/tool authority policy is still being formalized in P18-P19; and
- the expected interface after packaging is still uncertain until P20.

Decision: keep using direct scripts and Markdown protocols for the next phases.
