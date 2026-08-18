---
name: scheduling
description: This skill should be used when the user asks to "schedule daily restic backups", "create a systemd timer for restic", "set up a cron job for backups", "run my backup at a specific time/timezone", or needs a timezone-aware schedule (systemd timer, or cron fallback on non-systemd hosts).
---

# Scheduling restic Backups

Run the backup script daily, on time, in the right timezone. Prefer a **systemd timer** (timezone-aware, handles missed runs, integrates with `OnFailure=` alerting). Use **cron** only on non-systemd hosts. Ready-to-paste units are in [references/systemd-units.md](references/systemd-units.md).

**Do not enable the schedule until `verify-backup` passes** (first run + check + test-restore). Install the units now, enable them later.

## systemd timer (preferred)

Two units in `/etc/systemd/system/`:

`restic-backup.service` (oneshot, niced so it doesn't starve the host):

```ini
[Unit]
Description=restic backup to object storage (encrypted)
Wants=network-online.target
After=network-online.target docker.service

[Service]
Type=oneshot
Nice=10
IOSchedulingClass=idle
ExecStart=/usr/local/sbin/restic-backup.sh
TimeoutStartSec=6h
```

`restic-backup.timer`:

```ini
[Unit]
Description=Daily restic backup

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true
RandomizedDelaySec=1800

[Install]
WantedBy=timers.target
```

Reload and **verify the calendar resolves before enabling**:

```bash
systemctl daemon-reload
systemd-analyze calendar "*-*-* 03:00:00" --iterations=3   # prints the next 3 run times
```

### Timezone

systemd `OnCalendar` uses the **server's local time** by default — set the server timezone with `timedatectl set-timezone Europe/Kyiv`, or pin it per-timer (systemd ≥ 252):

```ini
[Timer]
OnCalendar=*-*-* 03:00:00
Timezone=Europe/Kyiv
```

`systemd-analyze calendar "*-*-* 03:00:00 Europe/Kyiv"` checks a zoned expression. `Persistent=true` runs a missed backup after downtime; `RandomizedDelaySec` spreads load and avoids hammering R2 at exactly the same second.

## cron fallback (non-systemd hosts)

`/etc/cron.d/restic-backup` — set the timezone and prevent overlapping runs with `flock`:

```cron
CRON_TZ=Europe/Kyiv
0 3 * * * root /usr/bin/flock -n /var/run/restic-backup.lock /usr/local/sbin/restic-backup.sh
```

`CRON_TZ` makes the schedule timezone-aware. `flock -n` ensures a long backup never overlaps the next run. cron's PATH is minimal — the script sets its own absolute PATH (see `backup-script`).

## Enable (only after verification)

```bash
systemctl enable --now restic-backup.timer
systemctl list-timers restic-backup.timer   # shows NEXT run time
```

## Gotchas

- **Enable only after `verify-backup`** — never schedule an unverified backup.
- **`daemon-reload` after editing units**, or systemd runs the old definition.
- **`Persistent=true`** catches runs missed while the host was off.
- **Avoid concurrent runs on one repo** — `flock` for cron; systemd oneshot won't overlap itself, but watch out for a manual run colliding with the timer (causes a repo lock → see `troubleshoot`).
- **Timezone source** — system tz vs per-timer `Timezone=` vs cron `CRON_TZ`; pick one and verify with `systemd-analyze calendar`.
- Schedule the periodic `check` (from `monitoring`) **off** the backup hour to avoid repo-lock contention.

## What this skill does NOT cover

- The script itself → `backup-script`
- First run + enabling gate → `verify-backup`
- Failure alerts / `OnFailure=` wiring → `monitoring`
