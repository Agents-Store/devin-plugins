---
name: examples
description: This skill should be used when the user asks for a "restic backup example", "end-to-end restic R2 walkthrough", "Docker server backup tutorial", "restic disaster recovery example", "how would this work on my server", or wants a complete scenario walkthrough.
---

# restic-dev Examples

Complete, end-to-end walkthroughs that thread the individual skills into a real workflow. Read the scenario closest to the situation, then use the underlying skills for detail.

## Scenarios

| Scenario | File | Covers |
|----------|------|--------|
| Docker server → R2 (the full setup) | [references/scenarios/docker-server-r2-full.md](references/scenarios/docker-server-r2-full.md) | recon → discover (incl. data outside `/docker`) → R2 repo → script → Kyiv systemd timer → verify → enable → monitoring |
| Non-systemd host (cron) | [references/scenarios/non-systemd-cron.md](references/scenarios/non-systemd-cron.md) | same flow with a `cron` + `flock` schedule instead of systemd |
| Disaster recovery / rebuild | [references/scenarios/disaster-recovery-rebuild.md](references/scenarios/disaster-recovery-rebuild.md) | restore files + replay DB dumps; rebuild on a fresh server |
| Multi-database stack | [references/scenarios/multi-db.md](references/scenarios/multi-db.md) | postgres + mysql + mongo + redis-as-cache in one backup |

## The shape of every setup

1. `setup` — recon (arch / init / tz / disk / docker), install latest restic.
2. `discover-backup-sources` — inspect every container, build the backup plan, **confirm with the user**.
3. `repository-setup` — password (copy off-server!), R2 creds, `init`.
4. `backup-script` — dumps + paths + exit-3 tolerance + retention.
5. `scheduling` — systemd timer (or cron), but **don't enable yet**.
6. `verify-backup` — first run, check, test-restore → **then enable**.
7. `monitoring` — dead-man's-switch + freshness + periodic check.
8. `disaster-recovery` — kept ready for the day you need it.

The scenarios make each step concrete with real commands and the decisions made along the way.
