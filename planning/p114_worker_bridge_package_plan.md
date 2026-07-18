# P114 clean agent-bridge package plan

Date: 2026-07-17

This note converts the R22/R23 MCP breakthrough into a package implementation
plan. It incorporates Advisor review and Luna Worker read-only planning slices.

## Critical milestone

R22 proved that nested VS Code Workers can reach a configured MCP server through
deferred `tool_search` when the child-facing MCP call is native namespaced:

```text
namespace: mcp__p114_exec_probe
name:      p114_exec
```

R23 proved the same route can perform a bounded mutation. The Worker emitted
`tool_search_call`, received `tool_search_output`, called namespaced
`mcp__p114_exec_probe / p114_exec` with `{"operation":"patch"}`, and the MCP
handler changed the ignored target from exact `before\n` to exact `after\n`.
No shell, `exec`, `apply_patch`, custom-tool, file-read, or fallback path
appeared in the raw child session.

The production lesson is that provider-facing flat compatibility names may be
needed at the OpenAI-compatible boundary, but child-facing calls must preserve
Codex's native namespaced MCP identity.

## Architecture

Create a neutral package surface under:

```text
src/agent_workbench/agent_bridge/
```

Core modules:

```text
contracts.py          # RunGrant, ToolGrant, role/profile/provider scopes
protocol.py           # flat provider <-> child-native namespaced translation
tools.py              # canonical tool schemas and compatibility names
mcp_server.py         # MCP initialize, tools/list, tools/call
policy.py             # deny-by-default tool authorization
evidence.py           # append-only decisions, outcomes, hashes, verdicts
transaction.py        # boot-critical config/role transaction API
toml_guard.py         # parse and validate config/role TOML
recovery.py           # journal recovery and stale-run handling
inventory.py          # observed native-tool inventory from drill JSONL
harness.py            # deterministic local and live proof helpers
tools/exec.py         # bounded shell execution adapter
tools/apply_patch.py  # bounded patch adapter
```

Scripts should become thin wrappers over package functions:

- `scripts/p114_capability_tool_adapter.py`
- `scripts/p114_mcp_exec_probe_server.py`
- `scripts/enable_p114_c4_role_bridge.ps1`
- `scripts/enable_p114_mcp_exec_probe.ps1`
- `scripts/verify_p114_*`

## Role-agnostic provider substitution

The bridge must not be Worker-only. It should support future replacement of any
Agent Hub role with an Ollama/open-model provider:

- Worker
- Supervisor
- Coordinator
- Advisor

Provider substitution must be explicit and grant-bound:

```text
Agent Hub role
  -> selected profile
  -> allowed provider/model implementation
  -> immutable RunGrant
  -> role-specific tool exposure profile
  -> evidence and restoration requirements
```

Do not infer authority from role name, model name, or TOML alone. A Worker grant
must not authorize Supervisor, Coordinator, or Advisor tools. Higher-authority
roles need stricter defaults, smaller exposed tool sets, stronger evidence, and
clear nondelegable boundaries.

## First package milestone

Name: packageized bridge MVP route-qualified.

Scope:

- Separate strict MCP tools:
  - `exec(command, workdir, timeout_ms?)`
  - `apply_patch(patch)`
- Preserve the R22/R23 flat-provider to namespaced-child translation.
- Use immutable per-run grants.
- Keep implemented tools separate from exposed tools.
- Fail closed on undeclared tools, malformed arguments, duplicate calls,
  path escapes, stale grants, and unauthorized sequence.
- Store append-only policy decisions and outcomes.
- Keep scripts as wrappers only.

This milestone has accepted standalone package `exec`, standalone package
`apply_patch`, and the package read-to-patch-to-validate composite on the fresh
CLI-parent Worker route. It is not general capability parity.

## Config transaction guardrail

All config and role edits must go through a package transaction:

1. Resolve canonical config and role paths.
2. Acquire one exclusive lock for the configuration scope.
3. Reject concurrent bridge runs.
4. Snapshot every target byte-for-byte and hash it.
5. Write a journal before mutation.
6. Parse original TOML before staging.
7. Render complete documents from structured data or validated templates.
8. Parse every staged document before touching the live path.
9. Replace live files via same-directory temp file and `os.replace`.
10. Reparse replaced files and verify expected provider/role values.
11. Restore all targets from backups on any failure.
12. Recover interrupted `prepared` or `committing` journals before new runs.

Regression tests must cover the R23 incident class:

```toml
P114_MCP_PROBE_LOG = ".../mcp_calls.jsonl"P114_MCP_PROBE_ALLOW_PATCH = "1"
```

The package must reject this before Codex startup can see it.

## Fixture plan

Freeze sanitized R22/R23 fixtures before refactoring:

```text
tests/fixtures/p114/r22_namespaced_mcp_inventory.json
tests/fixtures/p114/r23_namespaced_mcp_patch.json
tests/fixtures/p114/mcp_tool_search_contract.json
```

Fixtures should contain:

- ordered lifecycle;
- symbolic call IDs;
- search query;
- namespace and tool name;
- provider-flat compatibility name;
- operation arguments;
- handler marker;
- target before/after state;
- negative evidence for forbidden fallback tools.

Sanitize absolute user paths, timestamps, PIDs, ports, provider IDs, session
UUIDs, credentials, endpoints, full raw prompts, and raw provider bodies.

## Tool compatibility matrix

The initial matrix is captured in `planning/p114_agent_bridge_tool_matrix.md`.
It uses these fields:

```text
tool_name
surface
plane
observed_invocation
provider_shape
native_shape
arguments_schema
result_schema
authority
bridge_status
fail_closed_rules
acceptance_probe
evidence_refs
```

Initial rows:

- `exec` / `tools.shell_command`: P0 data plane, bounded.
- `apply_patch`: P0 data plane, bounded.
- declared validation continuation: P0 data plane.
- `tool_search`: P1 data plane.
- namespaced MCP calls: P1 data plane.
- `agent_workbench_run_context`: P1 SDK custom tool.
- `agent_workbench_result_contract`: P1 SDK custom tool.
- `agent_workbench_review_subject`: P1 SDK custom tool.
- `agent_workbench_validate_result`: P1 SDK custom tool.
- `agent_workbench_write_result`: P2 constrained artifact transport.
- `spawn_agent`, `wait_agent`, `send_input`: deferred control plane.

Do not bridge GitHub mutation, provider configuration mutation, model
installation, phase closeout, release actions, or unrestricted spawning in this
package milestone.

## Implementation tranches

### Tranche 0: freeze evidence and contracts

- Add sanitized R22/R23 fixtures.
- Add fixture tests that assert lifecycle order, namespaced child identity,
  provider-flat replay identity, target transition, and forbidden fallback
  absence.
- Add compatibility-matrix draft for observed tools.

### Tranche 1: package skeleton and pure protocol

- Add `agent_workbench.agent_bridge`.
- Move pure translation concepts from `p114_capability_tool_adapter.py` into
  `protocol.py` and `tools.py`.
- Keep P114 adapter tests passing through compatibility wrappers.
- No config mutation and no command execution in this tranche.

### Tranche 2: transaction layer

- Implement `transaction.py`, `toml_guard.py`, and `recovery.py`.
- Replace script-level direct TOML editing with package calls.
- Add tests for parse failure, concatenated assignments, restore, idempotent
  disable, interruption recovery, and concurrent-run rejection.

Initial implementation status: started under `agent_workbench.agent_bridge`.
The package now includes stable errors, TOML parse guards, and a journaled
`BridgeConfigTransaction` that snapshots targets, writes byte-for-byte backups,
validates staged TOML before live replacement, supports idempotent restore,
rejects concurrent locks, and recovers `prepared`/`committing` journals from
backups. Focused temp-file tests cover the R23 concatenated-assignment incident
class, backup/restore, idempotent restore, concurrent lock rejection, missing
staged content, and prepared-journal recovery. Scripts have not yet been
converted to use this transaction layer.

Follow-on status: the two P114 staging scripts now use
`python -m agent_workbench.agent_bridge.transaction_cli` for run-scoped
commit/restore operations. They render complete staged TOML files under the run
directory, then pass staged path, live target, backup path, journal path, and
lock path to the package transaction CLI. Direct `Copy-Item` backup/restore and
direct live `config.toml`/role TOML writes were removed from these paths. The
C4 role bridge still stops the adapter process if transaction commit fails.
This is validated by focused tests, PowerShell parser checks, and an isolated
temp-home staging smoke. The smoke copied the operator Codex config and Worker
role into `%TEMP%`, then ran the converted MCP and C4 role-bridge scripts
against only that disposable `-CodexHome`. MCP run
`p114_mcp_tx_smoke_0b40beb0454d4874ad350de6aac72eff` committed and restored
one config target byte-for-byte. Role run
`p114_role_tx_smoke_bca6ad6823054fb89ca75154b4a74123` committed and restored
the temp config plus temp Worker role byte-for-byte. This proves the converted
scripts use the package transaction path for local staging and disable/restore.
It is not a fresh VS Code Worker bridge proof.

### Tranche 3: MCP server MVP

- Implement `mcp_server.py` with separate `exec` and `apply_patch` tools.
- Require a valid `RunGrant`.
- Log policy decision before execution and outcome after execution.
- Prove local scripted MCP calls without VS Code.

Initial implementation status: package primitives are in place under
`agent_workbench.agent_bridge.mcp_server`. The module exposes separate MCP
`exec` and `apply_patch` schemas, a minimal deny-by-default `RunGrant`,
stable SHA-256 patch grants, injectable execution/patch handlers, JSON-RPC
`initialize`/`tools/list`/`tools/call` handling, root-contained workdir checks,
and JSONL request, policy-decision, and tool-outcome logging. The module is
runnable as `python -m agent_workbench.agent_bridge.mcp_server` and includes
newline-delimited JSON-RPC stdio helpers. Focused tests cover schema listing,
notification behavior, deny-by-default calls, allowed exec dispatch,
outside-root rejection, allowed patch dispatch by hash, malformed-call JSON-RPC
errors, JSONL stdio handling, and the package module entrypoint. A local stdio
smoke with run `p114_pkg_mcp_stdio_smoke_e47272b6ab67483cb5504713539a3618`
listed tools, executed granted `python -V`, returned `isError:false`, and
wrote an allow policy decision to its event log. The package also includes
`patch_backend.py`, a constrained relative-root patch backend for `Add File`,
`Delete File`, and `Update File` hunks. It rejects outside-root paths and
missing update context, and is now the default MCP `apply_patch` handler after
a SHA-256 patch grant. Local patch stdio smoke
`p114_pkg_mcp_patch_stdio_smoke_acf11e9da19a4eefb869ef3cd40bd7b7` changed a
temp target from exact `before\n` to exact `after\n`, returned `PATCH_OK`, and
logged an allow policy decision. The legacy
`scripts/p114_mcp_exec_probe_server.py` remains untouched as the R22/R23 proof
server fallback; wiring the reversible config script to the package module is
now started. `scripts/enable_agent_bridge_mcp.ps1` stages a separate
package-backed MCP server with grant arguments for `exec` and `apply_patch`,
uses the same transaction CLI for config commit/restore, and keeps the legacy
proof server untouched. Temp-home staging smoke
`p114_agent_bridge_mcp_stage_smoke_dd7f7215acd748eca0603db73d069b1e`
committed the generated MCP server block, displayed exact config lines, then
restored the disposable config hash byte-for-byte. No live Codex config was
changed.

Forensic continuation note: an initial controller invocation for
`p114_agent_bridge_mcp_worker_r1` failed before command execution because it
emitted a malformed oversized `shell_command` argument while constructing the
run payload. The recreated run then staged the live config and launched the
Worker recorded below; retain the fresh-controller boundary for future proofs.

Live continuation result: the recreated fresh-controller run with the same ID
did stage the package MCP server and launched exactly one fresh
`ollama_qwen_coder_worker` child (`019f7388-f175-75a3-8a72-aecf66c0b427`) with
`fork_context:false` and the ticket contents verbatim. The child had the
literal intended worktree but no callable package `exec` or `apply_patch`
schema. Its unsupported server-level MCP attempt and subsequent direct shell
reads are prohibited fallback behavior, not a composite proof. The server saw
initialization/listing/discovery but zero `tools/call` requests, the target
remained exact `before\n`, and no direct patch ran. After inspection, the
transaction disable restored config byte-for-byte. This is a host/tool-
registration failure; it supplies no quality or protocol acceptance and no
economics result because an accepted checkpoint boundary was not captured.

Follow-on status: the package role bridge now has a separate
`-PackageMcpExec` mode. It grants one cross-shell Python read command and
renders an exec-only ticket while retaining deferred discovery of the package
namespace. The initial exec run `p114_package_mcp_exec_r1` exposed a malformed
Windows-path workdir in the ticket; after normalizing it to forward slashes,
`p114_package_mcp_exec_r2` reached the MCP handler but showed that the
PowerShell-only command returned exit code 1 through the package shell backend.
Run `p114_package_mcp_exec_r3` then launched one fresh
`ollama_qwen_coder_worker` (`019f73b6-3db7-7a71-9a93-06472751e404`) with
`fork_context:false`, performed one `tool_search` followed by one namespaced
`mcp__agent_bridge_p114_package_mcp_exec_r3 / exec` call, received an allow
policy decision and exit code 0, and returned
`P114_C4_PACKAGE_MCP_EXEC_DONE`. The target remained exact `before\n`, no
fallback tool appeared, and config plus role restored byte-for-byte. This
accepts the bounded package `exec` proof; the composite proof remains next.

Composite completion: `p114_package_mcp_composite_r1` launched one fresh
`ollama_qwen_coder_worker` (`019f73b8-913a-7701-9dca-d2038466720b`) with
`fork_context:false`. Its raw child sequence is exactly `tool_search`, package
`exec` read, package `apply_patch`, and package `exec` validation. The MCP log
records allow decisions with exit code 0 for both exec calls and an allowed
patch (SHA-256 `2856533c1855832437100fd1ff8efcd37aa14dcaad063a65b944e2c31a3fe337`)
that changed the target. The final target is exact `after\n`, the Worker
returned `P114_C4_PACKAGE_MCP_COMPOSITE_DONE`, no fallback tool appeared, and
config plus role restored byte-for-byte. This accepts the first package
milestone's composite proof: `quality_validated_candidate` and
`protocol_accepted_candidate` are accepted; `economics_usable` remains
unproven without an accepted checkpoint/token-ledger boundary.

### Tranche 4: fresh CLI-parent package-MCP Worker proofs

- [x] Run one fresh Worker for bounded `exec`.
- [x] Run one separate fresh Worker for bounded `apply_patch`.
- [x] Run one composite Worker for read -> patch -> validate.
- [x] Restore operator state after each run.

These are accepted for the fresh CLI-parent package-MCP route. The known VS
Code nested-host custom-tool route is separate negative integration evidence;
it is not an unstated requirement for this package milestone or P107 entry.

### Tranche 5: toolset expansion

- Add matrix-backed, one-tool-at-a-time bridges for observed SDK/data-plane
  tools.
- Keep control-plane tools deferred until separately authorized.
- Re-run matched C2/C4 drills only after equivalent tool availability is
  proven for the relevant task family.

## Acceptance for the first package milestone

- Runtime implementation lives under `src/agent_workbench/agent_bridge`.
- Scripts only dispatch package commands.
- Strict separate `exec` and `apply_patch` MCP schemas exist.
- Deny-by-default grants and stable rejection behavior exist.
- R22/R23 fixture tests pass.
- Config and role files restore byte-for-byte after success, parse failure, and
  simulated interruption.
- Negative tests cover undeclared commands, outside-root paths, duplicate
  calls, malformed patches, and failed rollback.
- Fresh CLI-parent package-MCP Worker proofs pass for bounded `exec`, bounded
  `apply_patch`, and composite read/patch/validate.
- Evidence includes raw child sequence, MCP calls, policy decisions, target
  hashes, terminal marker, and restoration proof.
- Focused tests, compile checks, and `git diff --check` pass.

## What not to do next

- Do not productize `p114_exec(operation=patch)` as the bridge API.
- Do not delete dirty proof artifacts before freezing sanitized fixtures.
- Do not expose unrestricted shell.
- Do not bridge every advertised tool.
- Do not bridge L5/L6 authority in this milestone.
- Do not use string-appended TOML for boot-critical config.
- Do not compare C2/C4 quality until tool availability is qualified.
- Do not claim R23 proves general parity.
