# Cluster notes

This section tracks what we learn while testing Alliance and other HPC clusters.
Each note should include:

- host name and access status
- visible partition names and GPU-related resources
- queueing behavior and scheduler observations
- request shapes that worked or failed
- practical recommendations for future smoke tests

## Current notes

- FIR — see [fir.md](fir.md)
- Rorqual — see [rorqual.md](rorqual.md)
- Nibi — see [nibi.md](nibi.md)
- Sockeye (UBC ARC) — see [sockeye.md](sockeye.md) — **read before any SSH or
  tunnel work**; MFA-only host, agents must reuse the multiplexed master session

## Persistent access reminder

- The preferred home-based secrets file is ~/.config/agent-workbench/secrets.env.
- It should contain at least CCDB_USERNAME and CCDB_PASSWORD for Alliance login.
- The first Nibi login requires an interactive Duo MFA approval from the user's iPhone app.
- After that first approval, the persistent-connection helper can be enabled for future sessions.
