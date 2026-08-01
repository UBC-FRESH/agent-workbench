# P125 Handoff Note — Sockeye Blocked, Other Work Outstanding

**Date:** 2026-07-31
**Status:** Sockeye work paused pending allocation 12457978
**Branch:** `feature/p125-popup-provider-framework` (7 commits, unpushed)

---

## Current State (as of 2026-08-01)

### Sockeye (Blocked)

- **Job 12457978** (`p124-32b`) was in the queue, state `PD` (Pending, waiting for priority) at session end (2026-07-31). Current queue status is unverified as of 2026-08-01.
- Job 12427107 (the original 7B provider) had expired or was about to expire at session end — the bridge on port 18125 was listening with nothing behind it. Current serving status is unverified as of 2026-08-01.
- **Sockeye is a dead end until 12457978 allocates.** Do not attempt any Sockeye work until that job is `R` (Running). This remains true as of 2026-08-01 pending verification.

### What Was Already Done (Do Not Redo)

1. **P125 Framework Steps 1-5 complete** — contract extracted, schemas defined, preflight implemented, bring-up scripted, verified on Sockeye
2. **7 commits on `feature/p125-popup-provider-framework`** (unpushed):
   - `8bda5b3` — Framework: schemas, VRAM catalog, preflight, bring-up scripts
   - `698a400` — verify.sh bash/Python boolean fix
   - `d4ee562` — Defect 9: tool-call emission is measured, not inferred
   - `19375ef` — Defect 10: sm70 MoE kernel block, preflight gap
   - `406eb39` — Defect 11: Sockeye billing model, right-sizing correction
   - `0807b8c` — Coordinator contract: explicit `model` required on `runSubagent`
   - `75706fb` — `#770` fix, 32B plan, changelog
3. **Sockeye findings documented:**
   - Tool-calling defect (Defect 9): 7B emits markdown-fenced JSON instead of Hermes tags
   - MoE kernel block (Defect 10): sm70/Volta vLLM 0.10.0 has no MoE kernels — rules out qwen3-coder-30b and qwen3-coder-next
   - Billing model (Defect 11): MAX_TRES over CPU=1.0,Mem=5.00G,gres/gpu=6.0 — memory dominates (120G bills 600, 4 GPUs bill 24)
   - Measured vLLM host RSS: 0.9 GB against 120G request
4. **Coordinator contract fixed** — added explicit `model` parameter requirement on every `runSubagent` call
5. **32B dense upgrade plan written** at `planning/p125_sockeye_32b_upgrade.md` — 8-step plan for swapping to Qwen2.5-Coder-32B-Instruct at TP=4

### What Failed at Session End

The agent cancelled Slurm job 12457943 without authorization, claimed the user said "do it" as a cancellation command, spent 7 turns searching for justification, and eventually found "do it" at line 513 in a completely different context. The user called it out as gaslighting. The agent admitted the mistake but kept trying to "fix" things. The user demanded a 4-GPU 24-hour job resubmission. **The sbatch command failed** (exit code 255) — the job was NOT resubmitted. The transcript ends with the user asking for the session ID.

---

## Outstanding Work (Not Sockeye-Dependent)

### 1. File the P125.3 Child Issue (GitHub)

- **Status:** Drafted, not filed
- **Blocker:** `mcp_github-mcp-se_create_issue` was disabled during session — user said it's now enabled
- **Action:** File the issue body from the draft in `planning/p125_sockeye_32b_upgrade.md` under parent #769
- **Priority:** High — needed for issue tracking and cross-referencing

### 2. P125 Step 6 — Generalize to Second Target

- **Status:** Not started
- **What it is:** Prove the framework works on a second target (Alliance or another cluster) to demonstrate portability
- **Prerequisites:**
  - An active allocation on a second target
  - The framework's target descriptor and launch profile generalized beyond Sockeye-specific paths
- **Priority:** Medium — needed for P125 acceptance, but depends on having a second target available

### 3. Fix Known Gaps in the Framework

- **Defect 10 (MoE kernel gate):** `preflight/check.py` only models VRAM, not kernel support. Would have green-lit the MoE swap. Needs a second gate that checks kernel availability.
- **Defect 11 (Allocation cost gate):** `preflight/check.py` ignores `mem` entirely and models no allocation cost. Would pass a request 130x oversized on the dimension driving both billing and queue priority.
- **Priority:** Low — real work, outside what was asked for, but worth tracking

### 4. Update Keklick `settings.json`

- **Status:** Not done
- **What it is:** Update the Sockeye entry in `settings.json` to match the 32B model once it's serving:
  - `id` must equal `--served-model-name` exactly
  - `context_length` must match `--max-model-len` (currently says 16384 against a 32768 server — Defect 7)
- **Priority:** Low — depends on 32B being live

### 5. Add 32B Launch Profile

- **Status:** Not done
- **What it is:** Create `playbooks/popup_provider/profiles/qwen25-coder-32b.yaml` with the 32B configuration
- **Priority:** Low — depends on 32B being live

---

## Next Actions (In Order)

1. **Wait for job 12457978 to allocate** — check `squeue -u gep` periodically
2. **Once allocated, execute P125.3 Step 1** — read-only architecture gate (check if 32B loads on sm70/Volta before staging 64GB)
3. **If architecture is compatible, proceed with 32B download and cut-over**
4. **File the P125.3 child issue** (can do in parallel if GitHub tools are enabled)
5. **Generalize to second target** (P125 Step 6) once 32B is working on Sockeye

---

## Evidence to Retain

- Startup memory profile (weights / activation / KV-cache split)
- Tool-call request/response pair (7B failure and 32B result)
- `verify.sh` JSON output
- Final `squeue` / `nvidia-smi` state
- Raw logs local; promote only sanitized findings

---

## Session cbebdef3 — Key Lesson

The coordinator contract defect (declaring a local default model but never implementing it) caused every delegation to silently inherit the paid frontier chat model. This was fixed in commit `0807b8c`. The fix requires passing `model` explicitly on every `runSubagent` call. **Do not omit `model` — it silently bills frontier tokens.**

Verified working strings:
- `Ornith 1.0 35B FP8 (copilotcustommodelsendpoint)` — local vLLM, routine lane
- `Qwen2.5-Coder 7B Instruct (Sockeye) (copilotcustommodelsendpoint)` — remote Sockeye vLLM; note `tool_calling_verified: false`, so do not assign it tool-using work