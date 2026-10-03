---
name: monitoring
description: This skill should be used when the user asks to "monitor restic backups", "get alerted when a backup fails", "set up a healthcheck or dead-man's-switch for backups", "detect stale restic snapshots", "alert me if backups stop", or needs ongoing backup health monitoring.
---

# Monitoring restic Backups

The classic backup disaster: it silently stops working and nobody notices until a restore is needed. `verify-backup` is a one-time gate; **monitoring is the ongoing safety net.** Alert on *staleness*, not just on failed runs — a backup that never runs never reports a failure.

## 1 — Dead-man's-switch (the core)

A successful backup is invisible unless it actively reports in. Wire a heartbeat to healthchecks.io (or self-hosted Healthchecks / Uptime Kuma). The monitor alerts you when the expected ping **doesn't** arrive.

In the backup script, ping at start, success, and failure:

```bash
HC=https://hc-ping.com/<your-uuid>
curl -fsS -m10 --retry 5 "$HC/start" >/dev/null || true     # at the top
# ... backup ...
curl -fsS -m10 --retry 5 "$HC"        >/dev/null || true     # on success
curl -fsS -m10 --retry 5 "$HC/fail"   >/dev/null || true     # in the failure branch
```

Configure the check's period (1 day) + grace (a few hours) so a missed or hung run trips the alert.

## 2 — systemd OnFailure alert

Fire a notification when the unit fails. Add to `restic-backup.service`:

```ini
OnFailure=restic-backup-failure@%n.service
```

And a generic handler `restic-backup-failure@.service` that pushes to ntfy/mail/telegram (template in `scheduling/references/systemd-units.md`).

## 3 — Snapshot freshness check

Catches the case where the timer itself stops or never fires (so the script never runs to report failure). A small separate timer:

```bash
set -a; . /root/.restic/r2.env; set +a
latest_epoch=$(restic snapshots --json --latest 1 | \
  python3 -c 'import sys,json,datetime; s=json.load(sys.stdin); print(max(int(datetime.datetime.fromisoformat(x["time"].split(".")[0]).timestamp()) for x in s) if s else 0)')
age_h=$(( ( $(date +%s) - latest_epoch ) / 3600 ))
if [ "$latest_epoch" -eq 0 ] || [ "$age_h" -gt 26 ]; then
  curl -fsS -m10 -d "restic: newest snapshot is ${age_h}h old on $(hostname)" https://ntfy.sh/your-topic || true
fi
```

26h threshold = a daily backup plus slack. Run this on its own timer a few hours after the backup window.

`--latest 1` returns the newest snapshot **per host/path group**, so the snippet takes the maximum `time` over everything returned instead of trusting the first element. That keeps the check right on every restic version (0.19.0 briefly stopped grouping `snapshots --latest <n>` by default; 0.19.1 restored it).

## 4 — Periodic integrity check

Storage rots silently. Schedule integrity checks **off** the backup hour (they lock the repo):

- weekly `restic check` (structure/metadata — cheap)
- monthly `restic check --read-data-subset=10%` (reads a sample of pack data back from R2)
- on 0.19+, `restic check --tag daily` (or `--host` / `--path` / a snapshot ID) restricts the pack verification to the selected snapshots — a cheap check of just the fresh backups; combine with `--read-data-subset` for a sample

Units: `restic-check.service` + `.timer` in `scheduling/references/systemd-units.md`.

## 5 — Log rotation

```
# /etc/logrotate.d/restic
/var/log/restic-backup.log {
  weekly
  rotate 8
  compress
  missingok
  notifempty
}
```

## Gotchas

- **Alert on stale snapshots, not just failed runs** — a dead timer produces no failure, only silence; the freshness check + dead-man's-switch cover that.
- **Schedule `check` off the backup hour** — concurrent operations fight over the repo lock (→ `troubleshoot`).
- **Keep the healthcheck URL out of git** — it lives only in the on-server script / units.
- **Never run a full `restic check --read-data` daily** — it downloads the entire repo from R2 (slow, costs operations). Use `--read-data-subset` sampling.
- **Test the alert path once** — trigger a deliberate failure and confirm the notification actually arrives.

## What this skill does NOT cover

- The schedule itself → `scheduling`
- Diagnosing a reported failure → `troubleshoot`
- Restoring → `disaster-recovery`
