---
title: Ubuntu VM image for the security lab
type: playbook
status: draft
updated: 2026-02-01
runs: 1
last_run: 2026-02-01
---
# Ubuntu VM image for the security lab
> Builds the VM image used in the lab sessions.

## Steps
1. **Download the ISO** — from the Ubuntu 22.04 mirror. Done when: the checksum matches.
2. **Create the VM** — 2 CPUs, 4 GB RAM. Done when: the installer boots.

## Gotchas
- **No network in the VM** — the bridge adapter is off; fix: enable it in the VM settings.
