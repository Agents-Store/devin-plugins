# Scenario: Docker server → Cloudflare R2 (full setup)

A typical self-hosted box: a pile of Docker projects in `/docker`, one stack living elsewhere, a Postgres database, and a Cloudflare R2 bucket for offsite storage. Goal: encrypted nightly backups at 03:00 Europe/Kyiv, verified, monitored.

Given (substitute your own values):
```
BUCKET       = my-server-restic
S3_ENDPOINT  = https://<account_id>.r2.cloudflarestorage.com
ACCESS_KEY   = <R2 access key id>
SECRET_KEY   = <R2 secret access key>
BACKUP_TIME  = 03:00 Europe/Kyiv
```

## 1. Recon (`setup`)

```bash
uname -m                 # aarch64  -> arm64 binary
ps -p 1 -o comm=         # systemd  -> use a timer
timedatectl | grep -i 'time zone'   # set/confirm Europe/Kyiv
df -h /                  # enough room for the restic cache
docker ps                # yes, Docker host
```

Install the latest restic (arm64) per the `setup` skill → `restic version` ≥ 0.14.

## 2. Discover what to back up (`discover-backup-sources`)

```bash
ls -la /docker; du -sh /docker/* | sort -rh
for c in $(docker ps -aq); do
  docker inspect "$c" --format '{{.Name}} -> {{index .Config.Labels "com.docker.compose.project.working_dir"}}'
done
```

This reveals a stack **outside** `/docker` — e.g. `/projects/products/BAS` — and real state under `/agents/openclaw/<instance>/`. Inspect mounts:

```bash
docker inspect bas-postgres-1 --format '{{range .Mounts}}{{.Type}} {{.Name}} {{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
du -sh /var/lib/docker/volumes/*/_data | sort -rh
```

Findings → the plan:
- **paths:** `/docker`, `/agents`, `/projects`, the named volume `/var/lib/docker/volumes/bas_natsdata/_data`, plus `/var/backups/restic-dumps`.
- **excludes:** `node_modules`, `.cache`, `.npm`, `.venv`, `__pycache__`, `linuxbrew`, build caches, and `/var/lib/docker/{overlay2,image,containers,buildkit}`.
- **database:** `bas-postgres-1` (Postgres) → logical dump, exclude its data dir.

Write `/etc/restic/backup-paths.txt`, `/etc/restic/excludes.txt`, `/etc/restic/databases.tsv`. **Confirm the plan + FLAGS with the user.**

## 3. Repository on R2 (`repository-setup`)

```bash
install -d -m700 /root/.restic
openssl rand -base64 48 > /root/.restic/password; chmod 600 /root/.restic/password
# >>> copy the password into a password manager NOW <<<

cat > /root/.restic/r2.env <<'EOF'
AWS_ACCESS_KEY_ID=<ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<SECRET_KEY>
AWS_DEFAULT_REGION=auto
RESTIC_REPOSITORY=s3:https://<account_id>.r2.cloudflarestorage.com/my-server-restic
RESTIC_PASSWORD_FILE=/root/.restic/password
RESTIC_COMPRESSION=auto
EOF
chmod 600 /root/.restic/r2.env

set -a; . /root/.restic/r2.env; set +a
restic init
restic cat config        # readable + "version":2  => keys, password, compression all good
```

If `AccessDenied`: R2 token needs Object Read & Write, scope must include the bucket, and the endpoint's account id must match the token's account.

## 4. Backup script (`backup-script`)

Adapt `backup-script/references/restic-backup.sh` to `/usr/local/sbin/restic-backup.sh` (700). Add the Postgres dump block:

```bash
if docker ps --format '{{.Names}}' | grep -qx 'bas-postgres-1'; then
  docker exec -i bas-postgres-1 pg_dump -U bas -d bas --clean --if-exists \
    | gzip > "$DUMPDIR/db-bas-pg.sql.gz"
fi
```

The template already tolerates exit code 3 and runs `forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune`.

## 5. Schedule (`scheduling`) — install, don't enable yet

Install `restic-backup.service` + `.timer` (`OnCalendar=*-*-* 03:00:00`, `Timezone=Europe/Kyiv`, `Persistent=true`, `RandomizedDelaySec=1800`).

```bash
systemctl daemon-reload
systemd-analyze calendar "*-*-* 03:00:00 Europe/Kyiv"   # confirm it resolves
```

## 6. Verify (`verify-backup`) — the gate

```bash
/usr/local/sbin/restic-backup.sh         # first (slow) run
set -a; . /root/.restic/r2.env; set +a
restic snapshots                          # snapshot present, paths correct
restic check                              # no errors
restic restore latest --target /tmp/rtest --include /usr/local/sbin/restic-backup.sh
diff /tmp/rtest/usr/local/sbin/restic-backup.sh /usr/local/sbin/restic-backup.sh && echo OK
rm -rf /tmp/rtest
```

## 7. Enable + monitor (`scheduling` + `monitoring`)

```bash
systemctl enable --now restic-backup.timer
systemctl list-timers restic-backup.timer
```

Add a healthcheck ping to the script, a snapshot-freshness timer, and a weekly `restic-check.timer` (off the backup hour). Done.

## Recovery readiness (`disaster-recovery`)

Off-server, store: the **password**, the **R2 keys**, and the **repo URL**. On a new server: install restic → recreate `/root/.restic/{password,r2.env}` → `restic snapshots` → restore → replay the Postgres dump.
