# P114 agent-bridge tool compatibility matrix

Date: 2026-07-17

This matrix tracks tools observed in GPT-Codex or SDK workflow drills and their
status for the role-agnostic `agent_workbench.agent_bridge` package. It is not
an authorization list. A tool is exposed only when a run grant permits it.

| Tool | Surface | Plane | Authority | Bridge status | First acceptance probe |
| --- | --- | --- | --- | --- | --- |
| `exec` / `tools.shell_command` | Native Codex | Data | bounded read or declared command | accepted package proof (`p114_package_mcp_exec_r3`) | Fresh open-model role runs one exact declared command in one worktree. |
| `apply_patch` | Native Codex | Data | bounded workspace mutation | accepted package proof (`p114_package_mcp_adapter_r5`) | Fresh open-model role applies one exact declared patch with no shell-write fallback. |
| declared validation continuation | Native Codex | Data | bounded read/validate | accepted package composite (`p114_package_mcp_composite_r1`) | Fresh open-model role performs read -> patch -> validate through packaged bridge. |
| `tool_search` | Native Codex | Data | discovery only | accepted package composite | Fixture and live proof preserve `tool_search_call` -> `tool_search_output`. |
| namespaced MCP function call | MCP/native Codex | Data | grant-bound tool call | accepted package composite | Fixture and live proof preserve namespace/name instead of flat child name. |
| `agent_workbench_run_context` | SDK custom tool | Data | read-only run context | backlog P1 | Return public-safe run context for declared role/profile grant. |
| `agent_workbench_result_contract` | SDK custom tool | Data | read-only contract | backlog P1 | Return required result/blocker contract for declared artifact paths. |
| `agent_workbench_review_subject` | SDK custom tool | Data | bounded subject read | backlog P1 | Return only the declared review subject. |
| `agent_workbench_validate_result` | SDK custom tool | Data | result validation | backlog P1 | Validate a declared result file without broad filesystem access. |
| `agent_workbench_write_result` | SDK custom tool | Data/artifact | constrained write | backlog P2 | Write only a declared result path with result-envelope validation. |
| `spawn_agent` | Native Agent Hub | Control | orchestration | deferred | Separate authorization required; not part of P0/P1 bridge. |
| `wait_agent` | Native Agent Hub | Control | orchestration | deferred | Separate authorization required; not part of P0/P1 bridge. |
| `send_input` | Native Agent Hub | Control | orchestration | deferred | Separate authorization required; not part of P0/P1 bridge. |
| GitHub mutation | CLI/API | Control | L5 external mutation | nondelegable | Keep Coordinator-owned. |
| provider/config mutation | Local config | Control | boot-critical state | nondelegable except bridge transaction | Only package transaction may stage/restore run-scoped config. |
| phase closeout/release | Workflow | Control | L6 closeout | nondelegable | Keep Coordinator-owned. |

Future role substitution must bind this matrix through explicit role/profile
grants. Worker, Supervisor, Coordinator, and Advisor roles may share bridge
machinery, but they must not share authority by default.

`p114_agent_bridge_mcp_worker_r1` is superseded negative host/tool-registration evidence:
the fresh child had the intended literal worktree but no callable package tool
schema, made an unsupported server-level MCP attempt, then used prohibited
shell reads. The package server recorded discovery but zero `tools/call`
requests; the target remained `before\n`, and transaction teardown restored
the live configuration byte-for-byte. It is not a quality, protocol, or
economics acceptance. The fresh CLI-parent package route subsequently proved
the separate bounded `exec`, `apply_patch`, and read-to-patch-to-validate
composite calls. The current VS Code nested-host custom-tool route remains a
separate negative integration boundary and is not the P107 entry route.
