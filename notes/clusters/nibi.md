# Nibi (Alliance Canada) cluster notes

## Access summary

- Host: nibi.alliancecan.ca
- Status: first Duo-backed SSH login succeeded on 2026-07-26.
- Access method: interactive password login followed by Duo MFA.
- Credential source: the home-based secrets file at ~/.config/agent-workbench/secrets.env.
- Required values in that file: CCDB_USERNAME and CCDB_PASSWORD.
- Important: the first login requires Duo approval from the user's iPhone app. After that, the persistent-connection helper can be enabled.

## How to log in

1. Ensure ~/.config/agent-workbench/secrets.env exists and contains CCDB_USERNAME and CCDB_PASSWORD.
2. Start the interactive login flow:

   ssh -o PreferredAuthentications=keyboard-interactive,password \
       -o PasswordAuthentication=yes \
       -o PubkeyAuthentication=no \
       -o KbdInteractiveAuthentication=yes \
       -o ChallengeResponseAuthentication=yes \
       -o StrictHostKeyChecking=accept-new \
       -o UserKnownHostsFile=/dev/null \
       <username>@nibi.alliancecan.ca

3. When prompted:
   - enter the password from the secrets file
   - select option 1 for Duo Push (or the equivalent Duo MFA option shown by the system)
4. Approve the Duo prompt on the iPhone.

## Verified outcome

The login flow was verified on 2026-07-26. The terminal output showed:

- Duo two-factor login prompt
- the selection of option 1 for Duo Push
- a successful login banner with "Success. Logging you in..." and a subsequent "Last login" message

**Scope of verification (2026-07-26):** SSH login flow only. This did not verify Qwen3.6 model readiness, vLLM compatibility, or any model-loading capability. The 2026-08-01 P125 investigation found that vLLM 0.8.4 model-registry inspection did not complete before being interrupted by the user. Qwen3.6 readiness on Nibi remains unproven as of 2026-08-01.

## Operational note

This is now a known-good access path. Do not treat the first Alliance login as a one-off experiment. If the connection is lost, a new session is opened, or the persistent-connection helper needs to be re-enabled, return to this note first and repeat the same Duo-backed login flow.

## GPU scheduling note

Some of Nibi's H100 GPUs have been split into MIG instances. If your workload fits within a smaller GPU-memory footprint, requesting a MIG slice can make your job start sooner than requesting a full H100. See the Alliance documentation for details:

- https://docs.alliancecan.ca/wiki/Multi-Instance_GPU

Useful operational points:

- Nibi exposes H100 MIG profiles such as `nvidia_h100_80gb_hbm3_1g.10gb`, `nvidia_h100_80gb_hbm3_2g.20gb`, and `nvidia_h100_80gb_hbm3_3g.40gb`.
- A job can request at most one MIG instance; requesting multiple MIG instances in the same job is not supported.
- Prefer the smallest allocation that still satisfies the memory and compute needs of the workload.

Example interactive request for a 1g MIG slice:

```bash
salloc \
  --partition=gpubase_interac \
  --account=<alliance-account> \
  --gres=gpu:nvidia_h100_80gb_hbm3_1g.10gb:1 \
  --nodes=1 \
  --ntasks=1 \
  --cpus-per-task=2 \
  --mem=16G \
  --time=00:30:00
```

If the workload needs more memory, increase the profile size (for example `2g.20gb` or `3g.40gb`) instead of jumping straight to a full H100.

## Reproducible vLLM endpoint bring-up (2026-07-26)

This sequence was used to launch a temporary OpenAI-compatible vLLM endpoint on Nibi and expose it behind Cloudflare Access.

### 1. SSH login with Duo

Use the Duo-backed login flow and keep the credentials in the user-scoped secrets file at `~/.config/agent-workbench/secrets.env`.

```bash
ssh -o PreferredAuthentications=keyboard-interactive,password \
    -o PasswordAuthentication=yes \
    -o PubkeyAuthentication=no \
    -o KbdInteractiveAuthentication=yes \
    -o ChallengeResponseAuthentication=yes \
    -o StrictHostKeyChecking=accept-new \
    -o UserKnownHostsFile=/dev/null \
    <username>@nibi.alliancecan.ca
```

When prompted, enter the password from the secrets file and approve the Duo push or equivalent MFA prompt.

### 2. Request a GPU allocation

We requested exactly one MIG-backed GPU slice, not a full H100:

```bash
salloc \
  --partition=gpubase_interac \
  --account=<alliance-account> \
  --gres=gpu:nvidia_h100_80gb_hbm3_1g.10gb:1 \
  --nodes=1 \
  --ntasks=1 \
  --cpus-per-task=4 \
  --mem=8G \
  --time=01:00:00 \
  --no-shell
```

To verify the node once inside the allocation:

```bash
srun --partition=gpubase_interac \
  --account=<alliance-account> \
  --gres=gpu:nvidia_h100_80gb_hbm3_1g.10gb:1 \
  --nodes=1 \
  --ntasks=1 \
  --cpus-per-task=4 \
  --mem=8G \
  --time=00:30:00 \
  bash -lc 'hostname; echo GPU; nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader'
```

### 3. Prepare the remote worktree

On the compute node:

```bash
mkdir -p /scratch/gep
cd /scratch/gep
git clone <repo-url> agent-workbench
cd agent-workbench
```

### 4. Create the vLLM runtime environment

```bash
cd playbooks/vllm_blackwell
./scripts/install-native.sh
source .venv/bin/activate
```

If the server later fails with `ModuleNotFoundError: No module named 'pydantic'`, install the missing runtime dependencies explicitly:

```bash
python -m pip install --no-input pydantic pydantic-settings fastapi
```

### 5. Launch the server

```bash
nohup vllm serve nvidia/Qwen3.6-27B-NVFP4 \
  --served-model-name qwen3.6-27b-nvfp4 \
  --host 0.0.0.0 \
  --port 18000 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.88 \
  --max-num-seqs 16 \
  --max-num-batched-tokens 8192 \
  > /tmp/vllm-nibi.log 2>&1 &
```

### 6. Verify the endpoint locally on the node

```bash
curl http://127.0.0.1:18000/health
curl http://127.0.0.1:18000/v1/models
```

### 7. Expose it through Cloudflare Tunnel

The working tunnel route used here was:

```bash
sudo /usr/bin/cloudflared tunnel route dns <tunnel-name> <tunnel-hostname>.01101.dev
```

Use the existing `<tunnel-name>` tunnel config and add the public hostname to the ingress list pointing at `http://127.0.0.1:18000`.

Cloudflare CLI note:

- Run `cloudflared login` if the current environment does not already have a usable `cert.pem`.
- For a brand-new DNS route, use:

  ```bash
  cloudflared tunnel route dns <tunnel-id-or-name> <hostname>
  ```

- Only use `--overwrite-dns` when updating an existing route for a hostname that already has a DNS record.
- The `--overwrite-dns` flag can break the new-route flow with this CLI version because the error message is misleading.

Cloudflare tunnel safety note:

- Do not create, copy, launch, migrate, or "test" Cloudflare tunnel connectors without first inspecting the live tunnel topology.
- A tunnel credential is not a harmless config file: running it elsewhere immediately changes production routing.
- Before touching remote-access infrastructure, confirm the established architecture and tunnel ID, back up every live config, inspect `cloudflared tunnel info nginx` before and after any action, and never reuse production tunnel credentials on another host without explicit authorization.
- Never create `my-tunnel` or replace the established `nginx` tunnel.
- Make one minimal change at a time and verify remote access immediately.
- Preserve the access path you are currently using; do not experiment on the only door into the house.
- The repair required stopping the stray `cloudflared` process on `llm01` (`<llm-jump-host-ip>`) and removing connector `<tunnel-connector-id>-02be-4e6f-9b66-b27cd8cbaf8d`. The legitimate connector on `FRST-FRM-4645B` was preserved.
- The pinned session "Reconnect to sockeye for job" is the smoking gun: an agent mapped the production Cloudflare tunnel for this host to a remote VM while that VM was being set up, which caused the outage. That sequence is not a safe or acceptable workflow.
- Production ingress is not a scratchpad. Trace first, understand second, back up third, change last. Do not lock us out again.

If the hostname does not resolve locally, either:

- add an `/etc/hosts` entry for the hostname, or
- use `curl --resolve` with the Cloudflare IP for a one-off test.

### 8. Test the OpenAI-compatible endpoint

Use the public hostname with Cloudflare Access headers:

```bash
curl -sS https://<tunnel-hostname>.01101.dev/v1/models \
  -H "CF-Access-Client-Id: <CF_ACCESS_CLIENT_ID>" \
  -H "CF-Access-Client-Secret: <CF_ACCESS_CLIENT_SECRET>"
```

The model alias that succeeded in this run was `qwen3.6-27b-nvfp4`.

### 9. Provider config note

If a custom provider or Copilot environment is pointed at this endpoint, set the model id to `qwen3.6-27b-nvfp4` rather than a suffixed name such as `qwen3.6-27b-nvfp4-fresh02`.

## Nearline storage note

For large, infrequently accessed bundles of deployment artifacts, use nearline storage as a cold archive rather than scratch or project storage. This is a good fit for tarballs that contain large vLLM-related assets such as model-weight directories, cached model blobs, or other deployment bundles that may need to be rehydrated later.

Operational guidance:

- For the shared, cross-cluster working copy of a vLLM bundle, prefer `~/projects/<alliance-project>` (or the equivalent project-space path for the default project) because it is the group-shared storage that should be visible across Alliance clusters once you are logged into the relevant account.
- Use `~/nearline/<alliance-project>` only for long-lived archival copies that may sit for months and be recalled later.
- Prefer a single tarball per bundle, because small files on nearline are inefficient to retrieve.
- Create the archive directly in nearline if possible, and keep the source files in their original filesystem until the archive is complete.
- Expect slow recall from tape; this is appropriate for data that may sit for months before being unpacked again.
- For large archives, build an index file beside the tarball so individual files can be located later.

Example pattern:

```bash
mkdir -p ~/projects/<alliance-project>/vllm-bundles

tar -cvf ~/nearline/<alliance-project>/vllm-bundles/my-model-bundle.tar \
  /path/to/model-cache \
  /path/to/vllm-runtime-artifacts \
  > ~/nearline/<alliance-project>/vllm-bundles/my-model-bundle.index
```

The likely best workflow is:

1. Stage and maintain the active bundle once under `~/projects/<alliance-project>` so it is available on subsequent cluster logins.
2. Optionally archive a copy to nearline for cold storage and long retention.
3. Treat nearline as the place to stash a bundle for a long time and recall it later when needed.

## P125 Nibi deployment findings (2026-08-01)

This section records the complete Nibi investigation performed after the
earlier 2026-07-26 recipe. It is sanitized: no passwords, access tokens,
tunnel credentials, or private endpoint secrets are recorded here.

### SSH persistence and alias

- The local SSH config initially had a generic `Host nibi` match but no
  `HostName`, so `ssh nibi` tried to resolve the literal name `nibi` and
  failed with `Could not resolve hostname nibi`.
- DNS for `nibi.alliancecan.ca` resolved to `199.241.160.0`.
- The alias was repaired locally with `Host nibi`,
  `HostName nibi.alliancecan.ca`, user `gep`, keyboard-interactive/password
  authentication, and the existing shared multiplexing settings:
  `ControlMaster auto`, `ControlPath ~/.ssh/sockets/%r@%h:%p`,
  `ControlPersist yes`, and 30-second server keepalives.
- The persistent master was verified with `ssh -O check nibi`; a harmless
  remote identity check returned `l2.nibi.sharcnet` and user `gep`.
- The first human Duo/password bootstrap remains necessary after the master
  socket disappears. Multiplexing avoids repeated MFA prompts but cannot
  recreate a dead session without another human bootstrap.

### Scheduler and allocation observations

- Read-only inspection showed `<alliance-account>` associated with the user and
  `gpubase_interac` available with an 8-hour partition limit.
- The requested shape for Qwen3.6 on a 20 GB MIG slice was:

  ```bash
  salloc --job-name=p125-nibi-qwen36 \
    --partition=gpubase_interac --account=<alliance-account> \
    --gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1 \
    --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=8G \
    --time=08:00:00 --no-shell
  ```

- Allocation `18939706` ran on `g30` for 1:11:09 before it was canceled.
  It was canceled after the model-load investigation had no active server;
  it did not leave a provider or listener running.
- Earlier two-hour probes included allocation `18923603` on `g30`, which
  timed out during environment installation, and `18927835` on `g31`, which
  was canceled by Slurm with `ReqNodeNotAvail` before vLLM started.
- The interactive partition showed many down or mixed nodes. A node becoming
  unavailable can cancel a granted no-shell allocation even when the
  allocation initially reports `RUNNING`.
- Do not interpret `ReqNodeNotAvail`, job-prolog failure, or a canceled
  `srun` step as a model incompatibility result. Those failures occurred
  before model loading.

### GPU and MIG visibility

- Inside the allocation, `nvidia-smi -L` showed a parent H100 with one
  `MIG 2g.20gb` device.
- Slurm exported a UUID form such as
  `CUDA_VISIBLE_DEVICES=MIG-<uuid>`. vLLM 0.8.4 could not parse this form and
  failed with:
  `ValueError: invalid literal for int() with base 10: 'MIG-...'`.
- Inside the same allocation, setting `CUDA_VISIBLE_DEVICES=0` was verified
  with PyTorch and still exposed exactly one H100 MIG 2g.20gb device:
  1 device, 19.625 GiB visible memory, compute capability `(9, 0)`.
- This numeric remap is a safe workaround for this vLLM release on this
  allocation shape, provided it is verified with PyTorch before launch. Do
  not assume numeric remapping is safe on another cluster or allocation.

### vLLM environment repair

- The existing remote worktree was `/scratch/gep/agent-workbench`.
- Its pre-existing `playbooks/vllm_blackwell/.venv` contained vLLM
  `0.8.4+computecanada` but was incomplete: importing vLLM initially failed
  with `ModuleNotFoundError: No module named 'cachetools'` and many declared
  dependencies were absent.
- Running the repository-provided `scripts/install-native.sh` inside the
  allocation repaired the environment. The resulting probe reported:
  `vllm=0.8.4`, `torch=2.6.0+cu126`, CUDA 12.6, CUDA available, H100 MIG
  2g.20gb, 19.6 GiB, and capability `(9, 0)`.
- The installer downloaded and installed a large dependency set, including
  the matching Torch 2.6.0 / torchvision 0.21.0 / torchaudio 2.6.0 set.
  It also replaced the earlier Compute Canada Torch 2.11 package in that
  remote venv. This was a remote scratch/worktree environment change, not a
  tracked repository change.
- The vLLM venv contains `huggingface_hub 1.24.0+computecanada` and the `hf`
  CLI. `hf_transfer` was absent, so the fastest available tested path was the
  native `hf download` CLI with `--max-workers 16`.

### Hugging Face credential handling and model staging

- The local source credential file is `<local-secrets-path>`,
  mode `600`. Its values were never printed.
- The two assignments `HF_TOKEN` and `HUGGING_FACE_HUB_TOKEN` were securely
  transferred to Nibi as `$HOME/.config/agent-workbench/huggingface.env`,
  also mode `600`.
- Nibi `$HOME/.bashrc` now contains an idempotent source block for that file,
  so new interactive shells export both variables. Presence was verified
  without exposing either value.
- This credential provisioning was performed outside the repository and must
  not be copied into tracked content, command lines, logs, or model profiles.
- Authenticated download of `nvidia/Qwen3.6-27B-NVFP4` completed into
  `/scratch/gep/p125-nibi-test/model-dir` using 16 workers. The result was
  approximately 21G with three safetensors shards:
  `model-00001-of-00003.safetensors`,
  `model-00002-of-00003.safetensors`, and
  `model-00003-of-00003.safetensors`.
- The original model directory contains `config.json`, tokenizer files,
  `hf_quant_config.json`, the safetensors index, and all three weight shards.

### vLLM 0.8.4 and Qwen3.6 compatibility findings

The Qwen3.6 load was investigated with scratch-only copies. The original
downloaded model files were preserved; no tracked files were changed.

1. **ModelOpt config-key mismatch.** The original `config.json` carries a
   modern `quantization_config` object with ModelOpt fields such as
   `quant_algo`, while vLLM 0.8.4's ModelOpt parser expected a legacy nested
   `quantization` key in the config object. Passing `--quantization nvfp4`,
   `--quantization modelopt`, or `--load-format dummy` did not solve this.
2. **Correct isolated config shape.** The working scratch transformation
   preserved the original `quant_method=modelopt` selector and added the
   nested legacy `quantization` payload where vLLM 0.8.4 actually reads it.
   The original config hash was restored and kept separate from the
   transformed test copy. This let vLLM pass ModelOpt validation.
3. **Transformers API mismatch.** The repaired venv has Transformers
   `5.14.1`, while vLLM 0.8.4's tokenizer path expects
   `PreTrainedTokenizerBase.all_special_tokens_extended`, which is absent in
   that Transformers version. A scratch-only `sitecustomize.py` shim adding
   that property was validated and moved vLLM past tokenizer initialization.
4. **Registry inspection stop.** With the MIG remap, corrected config, and
   tokenizer shim, vLLM entered `registry.is_multimodal_model()` and
   `inspect_model_cls()`. The inspection subprocess remained active without
   opening port 18000, allocating model memory, or reaching model loading.
   It was later interrupted by the user with `Ctrl-C`; that interruption was
   user error and is not evidence of a model or scheduler failure.

The precise current conclusion is therefore: **Nibi authentication, MIG
visibility, HF authentication, model staging, and several vLLM compatibility
layers are working. Qwen3.6 readiness on Nibi is not yet proven because the
vLLM 0.8.4 model-registry inspection did not complete before the foreground
process was interrupted.** Do not claim the model is incompatible based on
this evidence.

### Ingress and safety boundary

- No Nibi Cloudflare tunnel or DNS route was changed during this investigation.
- No Nibi provider was exposed externally.
- All model tests bound vLLM to node-local `127.0.0.1:18000`.
- No Arbutus provider was inspected, restarted, or modified.
- No Sockeye job or endpoint was touched.
- No tracked repository files were modified by the live Nibi investigation.

### Remote-state changes performed on Nibi (2026-08-01)

The following changes were made to Nibi's runtime state during the P125
investigation. None of these are tracked repository changes; they live on
the remote host and must be managed there.

- **SSH alias repair.** Added `Host nibi` with `HostName nibi.alliancecan.ca`,
  user `gep`, keyboard-interactive/password auth, and multiplexing settings
  (`ControlMaster auto`, `ControlPath ~/.ssh/sockets/%r@%h:%p`,
  `ControlPersist yes`, 30s keepalives) to the local `~/.ssh/config`.
- **Hugging Face credential provisioning.** Transferred `HF_TOKEN` and
  `HUGGING_FACE_HUB_TOKEN` to Nibi as `$HOME/.config/agent-workbench/huggingface.env`
  (mode `600`). Added an idempotent source block to Nibi's `$HOME/.bashrc`
  so new interactive shells export both variables. Presence verified without
  exposing either value.
- **vLLM venv repair.** Ran `scripts/install-native.sh` inside the allocation
  to repair the pre-existing `playbooks/vllm_blackwell/.venv`. This installed
  missing dependencies (`cachetools`, `pydantic`, etc.) and replaced the
  earlier Compute Canada Torch 2.11 package with matching Torch 2.6.0.
- **Scratch model/config/shim.** Downloaded `nvidia/Qwen3.6-27B-NVFP4` into
  `/scratch/gep/p125-nibi-test/model-dir`. Created an isolated `config.json`
  transformation preserving the original hash. Added a scratch-only
  `sitecustomize.py` tokenizer shim to the venv. All scratch changes are
  confined to `/scratch/gep/`.
- **Cleanup.** No Nibi Cloudflare tunnel or DNS route was changed. No Nibi
  provider was exposed externally. All model tests bound vLLM to node-local
  `127.0.0.1:18000`. No tracked repository files were modified by the live
  Nibi investigation.

**Token scope and revocation caution.** The Hugging Face tokens transferred
to Nibi carry the scope granted by the local source file. If those tokens
are ever rotated or revoked, the Nibi `$HOME/.config/agent-workbench/huggingface.env`
file and its `$HOME/.bashrc` source block must be updated or removed to
avoid stale credentials persisting in interactive shells. Do not copy the
Nibi token file back to the local machine or into tracked content.

### Next recommended experiment

Use a fresh 8-hour 2g.20gb allocation and repeat only the final corrected
launch, preserving the following conditions:

- `CUDA_VISIBLE_DEVICES=0` after verifying the visible device is the MIG
  slice;
- the authenticated `$HOME/.config/agent-workbench/huggingface.env` source;
- the repaired vLLM venv;
- the full downloaded model directory;
- the isolated `config.json` transformation;
- the scratch `sitecustomize.py` tokenizer shim;
- a foreground `srun --overlap` server step;
- a separate readiness probe and a bounded timeout around registry
  inspection.

If registry inspection again does not complete, capture a Python stack sample
or subprocess trace before interrupting it. The next engineering question is
whether vLLM 0.8.4's subprocess model inspection is incompatible with the
Qwen3.6 architecture, not whether the MIG allocation or HF download works.
