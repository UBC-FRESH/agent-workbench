# Arbutus OpenStack CLI Setup

Non-interactive access to the Arbutus cloud via the OpenStack CLI using an
application credential (no password prompt).

## Credential location

| File | Contents |
|---|---|
| `~/.config/openstack/clouds.yaml` | Application credential (ID + secret), mode 600 |
| `~/app-cred-llm-ops-openrc.sh` | Alternative shell-sourceable RC file for the same credential |

The secret is **not** in the repo. Do not commit either file.

## Usage

```bash
# Any terminal, no password needed
OS_CLOUD=openstack /home/gep/.venv/bin/openstack server list

# List LLM nodes with IPs
OS_CLOUD=openstack /home/gep/.venv/bin/openstack server list --name llm -f json \
  | python3 -c "
import sys,json
for s in json.load(sys.stdin):
    nets = [v for net in s['Networks'].values() for v in net]
    print(s['Name'], nets)
"
```

Add an alias if you use this frequently:
```bash
alias arbopenstack='OS_CLOUD=openstack /home/gep/.venv/bin/openstack'
```

## Credential details

- **Name:** `llm-ops`
- **ID:** `3a6147015f19437a853a02f636f001b6`
- **Project:** `def-gep-dev`
- **Auth URL:** `https://identity.arbutus.alliancecan.ca/`
- **Auth type:** `v3applicationcredential`
- **Created:** 2026-07-28 via Arbutus dashboard → Identity → Application Credentials

## How it was set up

Password-based auth (`OS_USERNAME` + `OS_PASSWORD`) consistently returned HTTP
401 despite the password appearing correct. Root cause was ambiguity between the
Alliance CCDB password and the Arbutus-specific identity password. Rather than
debugging further, an application credential was created through the web
dashboard which bypasses the password entirely.

Steps taken:
1. Log into [arbutus.alliancecan.ca](https://arbutus.alliancecan.ca)
2. Navigate to **Identity → Application Credentials → Create Application Credential**
3. Name: `llm-ops`, roles: inherited (default), unrestricted: no
4. Dashboard generated the RC file and `clouds.yaml` — downloaded both
5. Installed `clouds.yaml` to `~/.config/openstack/clouds.yaml` (mode 600)
6. Moved credential files out of repo `tmp/` to `~/`
7. Verified with `openstack server list` — all 6 LLM nodes returned correctly

## Node list (as of 2026-07-28)

```
llm01  134.87.8.128, 192.168.220.134  (public IP — jump host)
llm02  192.168.220.152
llm03  192.168.220.150
llm04  192.168.220.242
llm05  192.168.220.204
llm06  192.168.220.249
llm07  192.168.220.225
llm08  192.168.220.165
```
