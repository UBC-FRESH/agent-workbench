# Arbutus vGPU LLM Node Recipe

Reproducible procedure to provision an Arbutus cloud VM as an Ollama inference
node with a Cloudflare tunnel public endpoint. Verified on the
`g1-12gb-c3-35gb-125` flavor (H100L MIG 1g.12gb, 12 GB VRAM, 3 vCPU, 35 GB
RAM, 125 GB data volume).

## Prerequisites

- Arbutus project keypair available locally at `~/.ssh/arbutus-def-gep-dev`
- llm01 (134.87.8.128) is alive and acts as the SSH jump host for all internal
  subnet nodes
- The new VM is on the `192.168.220.0/24` subnet and has no public IP
- Cloudflare account with `01101.dev` zone; `fresh-llm01` cert already obtained
  (cert can be shared across nodes — see step 5)
- `cloudflared` installed on the provisioning host

---

## Step 1 — SSH access

Add an entry to `~/.ssh/config` on the provisioning host:

```
Host arbutus-def-gep-dev-llmNN
    HostName 192.168.220.XXX
    User ubuntu
    IdentityFile ~/.ssh/arbutus-def-gep-dev
    ProxyJump arbutus-def-gep-dev-llm01
    StrictHostKeyChecking accept-new
    UserKnownHostsFile ~/.ssh/known_hosts
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Verify: `ssh arbutus-def-gep-dev-llmNN hostname`

---

## Step 2 — Install the vGPU grid driver

The Arbutus vGPU requires the NVIDIA grid driver, **not** the standard Ubuntu
apt package. Standard packages (`nvidia-driver-5xx`) will fail with
`modprobe: ERROR: could not insert 'nvidia': No such device`.

```bash
# On the new VM:
sudo apt-get install -y dkms linux-headers-$(uname -r)

# Download the official Arbutus grid driver and license token
wget https://object-arbutus.alliancecan.ca/swift/v1/6c87c15eb7d2468daf3d2bd0c58bbfce/vgpu/NVIDIA-Linux-x86_64-580.105.08-grid.run
wget https://object-arbutus.alliancecan.ca/swift/v1/6c87c15eb7d2468daf3d2bd0c58bbfce/vgpu/kalpa-prod.tok

# Install with DKMS (warnings about X libs and Vulkan are harmless on headless)
chmod 755 NVIDIA-Linux-x86_64-580.105.08-grid.run
sudo ./NVIDIA-Linux-x86_64-580.105.08-grid.run --silent --dkms

sudo reboot
```

After reboot verify: `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader`
Expected: `NVIDIA H100L-1-12C, 12288 MiB, 580.105.08`

---

## Step 3 — License the vGPU

```bash
sudo mkdir -p /etc/nvidia/ClientConfigToken
sudo cp kalpa-prod.tok /etc/nvidia/ClientConfigToken/
echo "FeatureType=4" | sudo tee /etc/nvidia/gridd.conf
sudo systemctl enable --now nvidia-gridd
sleep 8
# Confirm: "License acquired successfully"
sudo journalctl -u nvidia-gridd -n 5 --no-pager | grep -i license
```

> **Note:** The token file is stored in `/tmp` and lost on reboot. Re-download
> it with the `wget` command above if needed.

---

## Step 4 — Install Ollama to `/mnt`

The root volume is only 19 GB. All large files go to `/mnt` (125 GB data vol,
already mounted at boot).

```bash
# Create directories
sudo mkdir -p /mnt/vllm/ollama-dist /mnt/vllm/ollama-models /mnt/vllm/ollama-home
sudo chown ubuntu:ubuntu /mnt/vllm/ollama-dist /mnt/vllm/ollama-models /mnt/vllm/ollama-home

# Download and extract Ollama
cd /mnt/vllm/ollama-dist
curl -fL https://ollama.com/download/ollama-linux-amd64.tar.zst -o ollama.tar.zst
tar -xf ollama.tar.zst && rm ollama.tar.zst
sudo ln -sf /mnt/vllm/ollama-dist/bin/ollama /usr/local/bin/ollama

# Create ollama system user
sudo useradd -r -s /bin/false -m -d /mnt/vllm/ollama-home ollama
sudo chown ollama:ollama /mnt/vllm/ollama-models /mnt/vllm/ollama-home

# Write systemd service
sudo tee /etc/systemd/system/ollama.service > /dev/null << 'EOF'
[Unit]
Description=Ollama (Ornith-9B)
After=network.target nvidia-gridd.service

[Service]
Type=simple
User=ollama
Group=ollama
Environment=OLLAMA_MODELS=/mnt/vllm/ollama-models
Environment=OLLAMA_HOST=0.0.0.0:8000
Environment=OLLAMA_KEEP_ALIVE=5m
Environment=OLLAMA_MAX_LOADED_MODELS=1
Environment=OLLAMA_CONTEXT_LENGTH=65536
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=PATH=/mnt/vllm/ollama-dist/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
ExecStart=/mnt/vllm/ollama-dist/bin/ollama serve
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
sleep 5
curl -sS http://127.0.0.1:8000/api/version
```

---

## Step 5 — Pull model

```bash
OLLAMA_HOST=http://127.0.0.1:8000 OLLAMA_MODELS=/mnt/vllm/ollama-models \
  /mnt/vllm/ollama-dist/bin/ollama pull hf.co/deepreinforce-ai/Ornith-1.0-9B-GGUF:Q4_K_M
```

---

## Step 6 — Install cloudflared and create tunnel

```bash
# Install cloudflared
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
  | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] \
  https://pkg.cloudflare.com/cloudflared noble main" \
  | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt-get update -qq && sudo apt-get install -y cloudflared

# Option A: copy cert from existing node (avoids browser login)
# On provisioning host:
#   scp -F ~/.ssh/config arbutus-def-gep-dev-llm01:/etc/cloudflared/cert.pem /tmp/cf-cert.pem
#   scp -F ~/.ssh/config /tmp/cf-cert.pem arbutus-def-gep-dev-llmNN:/tmp/
# On new VM:
sudo mkdir -p /root/.cloudflared
sudo cp /tmp/cf-cert.pem /root/.cloudflared/cert.pem

# Option B: browser login (generates new cert)
sudo cloudflared tunnel login

# Create tunnel and route DNS
LABEL=fresh-llmNN   # e.g. fresh-llm03
sudo cloudflared tunnel create $LABEL
TUNNEL_ID=$(sudo cloudflared tunnel list --output json \
  | python3 -c "import sys,json; t=[x for x in json.load(sys.stdin) if x['name']=='$LABEL'][0]; print(t['id'])")
sudo cloudflared tunnel route dns $LABEL ${LABEL}.01101.dev

# Write tunnel config
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/config.yml > /dev/null << EOF
tunnel: $LABEL
credentials-file: /etc/cloudflared/${TUNNEL_ID}.json

originRequest:
  connectTimeout: 30s
  tcpKeepAlive: 30s
  proxyConnectionTimeout: 600s
  keepAliveConnections: 10
  keepAliveTimeout: 90s
  http2Origin: false

ingress:
  - hostname: ${LABEL}.01101.dev
    service: http://127.0.0.1:8000
  - service: http_status:404
EOF

sudo cp /root/.cloudflared/${TUNNEL_ID}.json /etc/cloudflared/
sudo cp /root/.cloudflared/cert.pem /etc/cloudflared/
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
sleep 5
curl -sS https://${LABEL}.01101.dev/api/version
```

---

## Step 7 — Verify

```bash
# Inference speed check (~37 tok/s expected)
curl -sS -m 120 -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"hf.co/deepreinforce-ai/Ornith-1.0-9B-GGUF:Q4_K_M",
       "messages":[{"role":"user","content":"hi"}],
       "stream":false,"options":{"num_predict":30,"think":false}}' \
  | python3 -c "
import sys,json
r=json.load(sys.stdin)
ec=r.get('eval_count',0); ed=r.get('eval_duration',1)
print(f'{ec} tok / {ed/1e9:.2f}s = {ec/(ed/1e9):.1f} tok/s')
print(r['message']['content'][:80])
"
```

---

## Parallel provisioning (4+ nodes)

When provisioning multiple nodes simultaneously, split into two phases to avoid
`/tmp` loss on reboot:

**Phase 1 — driver only (run in parallel, then reboot):**
```bash
for node in llm03 llm04 llm05 llm06; do
  ssh -F ~/.ssh/config arbutus-def-gep-dev-${node} 'bash -s' << 'SCRIPT' &
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y dkms linux-headers-$(uname -r)
wget -q https://object-arbutus.alliancecan.ca/swift/v1/6c87c15eb7d2468daf3d2bd0c58bbfce/vgpu/NVIDIA-Linux-x86_64-580.105.08-grid.run -O /tmp/nvidia-grid.run
chmod 755 /tmp/nvidia-grid.run
sudo /tmp/nvidia-grid.run --silent --dkms
sudo reboot
SCRIPT
done
wait
```

**Phase 2 — everything else (after reboot):** re-download kalpa-prod.tok and
the cloudflared cert (both were in `/tmp` and got cleared by the reboot), then
run steps 3–7 as normal.

Copy the cloudflared cert from an existing node to skip browser login:
```bash
ssh arbutus-def-gep-dev-llm01 'sudo cat /etc/cloudflared/cert.pem' > /tmp/cf-cert.pem
for node in llm03 llm04 llm05 llm06; do
  scp -F ~/.ssh/config /tmp/cf-cert.pem arbutus-def-gep-dev-${node}:/tmp/cf-cert.pem &
done
wait
```

---

## Known issues

| Issue | Cause | Fix |
|---|---|---|
| `modprobe: No such device` | Standard apt nvidia driver, not grid driver | Use the `.run` grid installer from Arbutus object storage |
| `dpkg broken pipe on nvidia-firmware` | Partial apt nvidia install blocking grid .run installer | `dpkg --purge --force-all` all nvidia packages first |
| `set -e` exits on gridd enable | `systemctl enable nvidia-gridd` calls `update-rc.d` which returns non-zero | Add `\|\| true` after the enable command, or drop `set -e` for that line |
| `kalpa-prod.tok` and cert lost | Both placed in `/tmp` before reboot; `/tmp` cleared on boot | Re-download token and re-copy cert in phase 2, after the reboot |
| DNS resolve fails on the new VM immediately after tunnel creation | Cloudflare DNS propagation lag | Test the public URL from the provisioning host, not the new VM |
| `gridd: Valid license settings not found` in journal | Benign startup race before token is processed | Ignore; the license is acquired shortly after — check for `acquired successfully` |
| First inference ~11 tok/s on cold start | Model loaded into GPU on first request | Warm speed (37 tok/s) is reached after the first request completes |
| Ollama OOM / slow on pure-transformer 8B+ | Large KV cache from all-attention layers fills 12 GB | Use Ornith-9B (hybrid SSM+attention, ~7× smaller KV cache per token) |
| vLLM 0.26 fails on MIG | V1 engine spawns subprocess that can't init CUDA on MIG | Use Ollama; vLLM 0.26 removed V0 engine entirely, MIG incompatible |
| Copilot `gpt-4o-mini` 401 | Missing `chat.byokUtilityModelDefault` in VS Code settings | Add `"chat.byokUtilityModelDefault": "mainAgent"` |
| Copilot context too short (400 error) | Default Ollama context is 4096 | Set `OLLAMA_CONTEXT_LENGTH=65536` in the systemd service env |

---

## Node inventory

| Node | Internal IP | Public endpoint | Status |
|---|---|---|---|
| llm01 | 134.87.8.128 (public) | https://fresh-llm01.01101.dev | live |
| llm02 | 192.168.220.152 | https://fresh-llm02.01101.dev | live |
| llm03 | 192.168.220.150 | https://fresh-llm03.01101.dev | live |
| llm04 | 192.168.220.242 | https://fresh-llm04.01101.dev | live |
| llm05 | 192.168.220.204 | https://fresh-llm05.01101.dev | live |
| llm06 | 192.168.220.249 | https://fresh-llm06.01101.dev | live |
| llm07 | 192.168.220.225 | https://fresh-llm07.01101.dev | live |
| llm08 | 192.168.220.165 | https://fresh-llm08.01101.dev | live |

**def-elmci1 project** (gateway: llm09 at 134.87.10.50, subnet 192.168.110.0/24)

| Node | Internal IP | Public endpoint | Status |
|---|---|---|---|
| llm09 | 192.168.110.133 + 134.87.10.50 (float) | https://fresh-llm09.01101.dev | live — jump host |
| llm10 | 192.168.110.199 | https://fresh-llm10.01101.dev | live |
| llm11 | 192.168.110.216 | https://fresh-llm11.01101.dev | live |
| llm12 | 192.168.110.15 | https://fresh-llm12.01101.dev | live |
| llm13 | 192.168.110.38 | https://fresh-llm13.01101.dev | live |
| llm14 | 192.168.110.103 | https://fresh-llm14.01101.dev | live |
| llm15 | 192.168.110.43 | https://fresh-llm15.01101.dev | live |
| llm16 | 192.168.110.6 | https://fresh-llm16.01101.dev | live |

Provisioned 2026-07-28. 16 nodes total across 2 projects, 592 tok/s combined. All nodes: Ornith-1.0-9B Q4_K_M, 37 tok/s warm, 65536
context. Cloudflare tunnel IDs recorded in `/etc/cloudflared/config.yml` on each VM.
