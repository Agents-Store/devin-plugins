# Scenario: disaster recovery — rebuild on a new server

The original server is gone (hardware failure, provider incident, fat-fingered `rm`). You have the off-server copies: the **restic password**, the **R2 keys**, and the **repo URL**. Rebuild on a fresh box.

> If you do **not** have the password, stop — the repository is unreadable and there is no recovery. This is why `repository-setup` insists on an off-server copy.

## 1. Fresh server prep (`setup`)

```bash
uname -m; ps -p 1 -o comm=; docker --version   # recon
# install latest restic for the arch (see setup skill)
restic version
```

## 2. Reconnect to the repository (`repository-setup`)

Recreate the credential files from your off-server copies:

```bash
install -d -m700 /root/.restic
printf '%s' '<the saved password>' > /root/.restic/password; chmod 600 /root/.restic/password
cat > /root/.restic/r2.env <<'EOF'
AWS_ACCESS_KEY_ID=<ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<SECRET_KEY>
AWS_DEFAULT_REGION=auto
RESTIC_REPOSITORY=s3:https://<account_id>.r2.cloudflarestorage.com/<bucket>
RESTIC_PASSWORD_FILE=/root/.restic/password
RESTIC_COMPRESSION=auto
EOF
chmod 600 /root/.restic/r2.env

set -a; . /root/.restic/r2.env; set +a
restic snapshots        # you should see your history — do NOT run init
```

## 3. Restore files and volumes (`disaster-recovery`)

```bash
restic ls latest                                  # inspect the tree
restic restore latest --target /restore           # full restore to staging
# move project dirs into place
rsync -a /restore/docker/  /docker/
rsync -a /restore/agents/  /agents/
# named-volume data: recreate the volume, then restore its _data
docker volume create bas_natsdata
rsync -a /restore/var/lib/docker/volumes/bas_natsdata/_data/  /var/lib/docker/volumes/bas_natsdata/_data/
```

## 4. Bring up databases and replay dumps

```bash
cd /docker/bas && docker compose up -d postgres   # start just the DB first
# replay the logical dump straight from the repo
restic dump latest /var/backups/restic-dumps/db-bas-pg.sql.gz \
  | zcat | docker exec -i bas-postgres-1 psql -U bas -d bas
```

## 5. Start the rest and verify

```bash
cd /docker/bas && docker compose up -d            # full stack
# verify
docker exec -i bas-postgres-1 psql -U bas -d bas -c '\dt'   # tables present, rows there
curl -fsS localhost:<port>/health || true                  # app responds
```

## 6. Re-establish backups

Re-run `backup-script` + `scheduling` + `verify-backup` on the new server so it protects itself going forward.

## Gotchas

- **No password = no recovery.** Verify you can read `restic snapshots` before assuming you can recover.
- **Never `init`** when reconnecting — that's a new empty repo. You want `snapshots` to list your existing history.
- **Stop apps before replaying a DB**; bring the DB up alone, replay, then start the rest.
- **Map volume `_data` paths exactly**, or the app starts with empty storage.
- **Verify with real checks** — table listings, row counts, an app health endpoint — not just "the restore command exited 0".
