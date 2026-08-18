# systemd units for restic backups

Ready-to-paste unit files. Install to `/etc/systemd/system/`, `systemctl daemon-reload`, then enable **after** `verify-backup` passes.

## restic-backup.service

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
# alert on failure (see the monitoring skill):
# OnFailure=restic-backup-failure@%n.service
```

## restic-backup.timer

```ini
[Unit]
Description=Daily restic backup

[Timer]
OnCalendar=*-*-* 03:00:00
# Pin a timezone (systemd >= 252); otherwise the server's local tz is used:
# Timezone=Europe/Kyiv
Persistent=true
RandomizedDelaySec=1800

[Install]
WantedBy=timers.target
```

## restic-check.service (weekly integrity — see monitoring)

```ini
[Unit]
Description=restic repository integrity check
After=network-online.target

[Service]
Type=oneshot
Nice=15
IOSchedulingClass=idle
# read structure weekly; read a data subset for deeper (cheap) verification
ExecStart=/usr/bin/bash -lc 'set -a; . /root/.restic/r2.env; set +a; restic check --read-data-subset=10%%'
TimeoutStartSec=12h
```

> Note: `%` is doubled to `%%` in systemd `ExecStart` because `%` is a unit specifier escape.

## restic-check.timer

```ini
[Unit]
Description=Weekly restic check

[Timer]
OnCalendar=Sun *-*-* 05:00:00
Persistent=true
RandomizedDelaySec=1800

[Install]
WantedBy=timers.target
```

## restic-backup-failure@.service (OnFailure handler — see monitoring)

```ini
[Unit]
Description=Alert that %i failed

[Service]
Type=oneshot
# replace with your channel (ntfy/mail/telegram):
ExecStart=/usr/bin/bash -lc 'curl -fsS -m10 -d "restic unit %i FAILED on $(hostname)" https://ntfy.sh/your-topic || true'
```

## Commands

```bash
systemctl daemon-reload
systemd-analyze calendar "*-*-* 03:00:00" --iterations=3   # verify schedule
systemctl enable --now restic-backup.timer                 # AFTER verify-backup
systemctl enable --now restic-check.timer
systemctl list-timers 'restic-*'                           # confirm next runs
journalctl -u restic-backup.service -n 50 --no-pager       # last run logs
```
