# Scenario: non-systemd host (cron + flock)

Same backup, but the host has no systemd (`ps -p 1 -o comm=` returns something other than `systemd` — a container, OpenRC, an older box). Use cron with `flock` for timezone-aware, non-overlapping runs.

## Difference from the systemd flow

Everything in `setup` → `discover-backup-sources` → `repository-setup` → `backup-script` → `verify-backup` is identical. Only the schedule changes.

## Schedule with cron

`/etc/cron.d/restic-backup`:

```cron
CRON_TZ=Europe/Kyiv
0 3 * * * root /usr/bin/flock -n /var/run/restic-backup.lock /usr/local/sbin/restic-backup.sh
```

- `CRON_TZ=Europe/Kyiv` makes `0 3 * * *` fire at 03:00 Kyiv time, not UTC.
- `flock -n /var/run/restic-backup.lock` guarantees a long-running backup never overlaps the next night's run (cron has no built-in overlap guard).
- cron's PATH is minimal — the script sets its own absolute `PATH` (the template does this).

## Verify the cron entry

```bash
# confirm cron picked up the file (syntax)
sudo crontab -l 2>/dev/null; ls -l /etc/cron.d/restic-backup
# run the script once by hand first (verify-backup), then trust the schedule
/usr/local/sbin/restic-backup.sh
grep restic /var/log/syslog 2>/dev/null | tail   # cron logs the invocation (distro-dependent)
```

## Monitoring without systemd OnFailure

No `OnFailure=` here, so the dead-man's-switch matters even more:

- Healthcheck ping at start/success/fail inside the script (`monitoring`).
- A second cron line for the snapshot-freshness check, a few hours after the backup:

```cron
CRON_TZ=Europe/Kyiv
30 6 * * * root /usr/local/sbin/restic-freshness-check.sh
```

## Gotchas

- **Set `CRON_TZ`** or the job runs in the system timezone (often UTC) — not what you intended.
- **Always `flock`** — without it a slow backup can stack on top of itself and lock the repo.
- **Test by hand first** — cron failures are silent; verify the script runs cleanly before relying on the schedule, and confirm the healthcheck ping arrives.
