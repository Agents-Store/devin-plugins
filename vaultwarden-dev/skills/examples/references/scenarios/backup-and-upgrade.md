# Scenario: Back Up and Upgrade a Vaultwarden Server

Goal: move to a new Vaultwarden release with a verified backup and without breaking `bw` and the apps.

## 1. Read the release notes

https://github.com/dani-garcia/vaultwarden/releases — look for "required for clients …", removed endpoints, changed env vars and security fixes. Example: 1.37.4 removed `/api/accounts/prelogin` (old `bw` stops logging in) and changed `X-Forwarded-For` handling (`IP_HEADER_TRUSTED_PROXIES`).

## 2. Record the current state

```bash
curl -fsS "$VW_URL/api/version"; echo
curl -fsS "$VW_URL/api/config" | jq '{emulates: .version, gitHash}'
docker inspect --format '{{.Config.Image}} {{.Image}}' <container>     # image tag and digest to roll back to
```

## 3. Back up

SQLite, server running — consistent copy via the server:

```bash
curl -fsS -b "$JAR" -H 'Content-Type: application/json' -X POST "$VW_URL/admin/config/backup_db"
```

or inside the container (also SQLite only):

```bash
docker exec <container> /vaultwarden backup
```

Then copy off the host: the new `db_*.sqlite3` file, `attachments/`, `sends/`, `config.json`, `rsa_key.pem`. MySQL/PostgreSQL: `mysqldump` / `pg_dump` plus the same files. Verify the copy opens: `sqlite3 <copy> 'PRAGMA integrity_check;'` → `ok`.

## 4. Upgrade

```bash
docker pull vaultwarden/server:<new-version>
# change the tag in docker-compose.yml, then:
docker compose up -d <service>
docker logs --tail 50 <container>       # migrations run on start; look for errors
```

## 5. Verify

```bash
curl -fsS "$VW_URL/alive"; echo
curl -fsS "$VW_URL/api/version"; echo
bw --version && bw sync && bw status | jq '{status, lastSync}'
```

Then log in once in the web vault and on one mobile device. If `bw` now fails, compare versions (`/vaultwarden-dev:check-version`) — usually the CLI needs an upgrade too.

## Roll back

Stop the container, restore the backed-up data folder (delete any `db.sqlite3-wal` from the failed run), start the previous image digest from step 2. Database migrations are not reversible in place — restoring the backup is the rollback.
