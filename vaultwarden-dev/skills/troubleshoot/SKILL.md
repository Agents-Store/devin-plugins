---
name: troubleshoot
description: This skill should be used when the user reports Vaultwarden errors — "Username or password is incorrect" with the right password, "404 on user-key-id", "Vaultwarden 401 or 429", "invites not arriving", "bw sync hangs" — or needs to diagnose a self-hosted Vaultwarden or bw failure.
---

# Vaultwarden Troubleshooting

Work from the outside in: server reachable → versions compatible → credentials → feature flags. Most "wrong password" reports on Vaultwarden are version or proxy problems, not passwords.

## Quick diagnostics

```bash
VW_URL="https://vault.example.com"
curl -sS -o /dev/null -w 'alive %{http_code}\n' "$VW_URL/alive"
curl -fsS "$VW_URL/api/version"; echo
curl -fsS "$VW_URL/api/config" | jq '{emulates: .version, gitHash, server: .server.name}'
bw --version
bw status | jq '{serverUrl, status, lastSync, userEmail}'
```

Then run `/vaultwarden-dev:check-version` for a verdict on the CLI/server pair. On the server side: `docker logs --tail 200 <container>`; raise detail temporarily with `LOG_LEVEL=debug` (restart-only, and debug logs contain request details — turn it back off).

## Version coupling

Most "right password, still rejected" reports are a client/server version mismatch: `bw` 2026.9.x needs Vaultwarden 1.37.4+ (older servers answer 404 on `key-management/user-key-id`), 2026.8 clients need 1.37.2+, 2026.7 clients 1.37.0+, and Vaultwarden 1.37.4+ rejects outdated CLIs that still call the removed `/api/accounts/prelogin`. Full table and what to pin per server version: [references/version-matrix.md](references/version-matrix.md). Upgrade the server first, then the clients, and read the release notes at https://github.com/dani-garcia/vaultwarden/releases before each upgrade.

## Login and token errors

| Error | Cause | Fix |
|---|---|---|
| `Username or password is incorrect. Try again` | wrong password, wrong `bw config server`, KDF mismatch in a hand-rolled hash, or a version mismatch (above) | check `bw config server`, versions; use the API-key login |
| `TwoFactorProviders2` in a 400 body | 2FA required on the password grant | use the personal API key (`bw login --apikey`), which skips 2FA |
| `Invalid client_id` / `Malformed client_id` | missing `user.` or `organization.` prefix | copy the full `client_id` from the web vault |
| `Incorrect client_secret` | key rotated | fetch the current key in the web vault |
| `Scope not supported` | wrong `scope` | `api` (user key), `api.organization` (org key), `api offline_access` (password) |
| `This user has been disabled` | admin disabled the account | `POST /admin/users/<id>/enable` |
| `Please verify your email before trying again.` | `SIGNUPS_VERIFY=true` | verify via the mail, or check SMTP |
| `Could not send login notification email` | new device + `REQUIRE_DEVICE_EMAIL=true` + SMTP failing | fix SMTP or reuse a known `device_identifier` |
| `SSO sign-in is required` | `SSO_ONLY=true` | log in with `bw login --sso`, or use the API key |
| `{"error":"invalid_grant"}` | refresh token expired or revoked (password change, deauth) | log in again |
| "Vault is locked" from `bw` | `BW_SESSION` missing or stale | `export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"` |

## Rate limits (429)

| Message | Limiter | Default |
|---|---|---|
| `Too many login requests` | `LOGIN_RATELIMIT_SECONDS` / `LOGIN_RATELIMIT_MAX_BURST` | 60 s / 10, per IP; password and 2FA steps share the budget |
| `Too many admin requests` / `Too many requests, try again later.` on `/admin` | `ADMIN_RATELIMIT_SECONDS` / `ADMIN_RATELIMIT_MAX_BURST` | 300 s / 3 |
| `Too many requests` on prelogin / Send access | `UNAUTHENTICATED_RATELIMIT_*` | 60 s / 50 |

If **every** user trips limits at once, the reverse proxy is not forwarding the client IP: set `IP_HEADER` to the header the proxy sends (`X-Real-IP` or `X-Forwarded-For`) and, for `X-Forwarded-For`, `IP_HEADER_TRUSTED_PROXIES` (1.37.4+).

## Admin panel

| Symptom | Cause | Fix |
|---|---|---|
| "The admin panel is disabled" | `ADMIN_TOKEN` unset | set it (Argon2 hash via `vaultwarden hash`) and restart |
| `Invalid admin token, please try again.` with the right value | `$` in the PHC hash eaten by docker-compose interpolation | escape as `$$` or use `ADMIN_TOKEN_FILE` |
| token change has no effect | `config.json` overrides the environment | change it in the admin page, or remove the key from `config.json` |
| 401 `Unauthorized` / `Session expired` on JSON routes | missing or expired `VW_ADMIN` cookie | log in again; see `vaultwarden-dev:admin-panel` |
| not-found error on a POST route | missing `Content-Type: application/json` | add the header, even for empty bodies |
| all admin sessions dropped after restore | `rsa_key.pem` changed | restore it with the database |

## Organizations and members

| Symptom | Cause | Fix |
|---|---|---|
| member stuck in "Accepted" | needs confirmation with the org key | `bw confirm org-member <member-id> --organizationid <org-uuid>` |
| invite email never arrives | SMTP not configured / failing | `POST /admin/test/smtp`; without SMTP the invite is recorded and the user can register directly |
| `Resource not found` / `Organization not found` on `/api/organizations/...` | wrong org id or the token's user is not Admin/Owner there | check `GET /api/accounts/profile` → `organizations[].type` |
| groups missing, import skips groups | `ORG_GROUPS_ENABLED=false` | enable (restart-only) |
| events endpoint empty | `ORG_EVENTS_ENABLED=false` | enable (restart-only); history starts then |
| Bitwarden Public API calls 404 (`/api/public/members`, …) | Vaultwarden implements only `/api/public/organization/import` | use the client API routes instead |
| `bws` / Secrets Manager does not work | not implemented in Vaultwarden | use items with custom fields via `bw` |

## Clients and sync

| Symptom | Cause | Fix |
|---|---|---|
| changes do not appear live on other devices | WebSocket not proxied | proxy `/notifications/hub` with `Upgrade` headers; `ENABLE_WEBSOCKET=true` |
| mobile apps do not update in the background | push not configured | `PUSH_ENABLED=true` with an installation id/key from bitwarden.com/host |
| attachments or icons broken, wrong links in mails | `DOMAIN` wrong (scheme, host or path) | set the exact external URL |
| `bw` TLS errors with a private CA | Node does not trust it | `export NODE_EXTRA_CA_CERTS=<ca.pem>`; keep TLS verification on — with it off, anyone on the path can capture the master-password hash and session |
| `bw sync` hangs | large vault or a stuck proxy connection | retry with `BITWARDENCLI_DEBUG=true` (prints tokens — keep the output private) |
| `bw` still talks to the old server | config is per data dir | `bw logout`, `bw config server <url>`, log in again; use `BITWARDENCLI_APPDATA_DIR` per server |

## Server state after an upgrade or restore

- "0 users" after an upgrade: the container started with an empty or wrong data volume (the folder `DATA_FOLDER` points at) — check the mount before anything else; do not create new accounts.
- After restoring `db.sqlite3`, delete a stale `db.sqlite3-wal` from the old run before starting, or the restore is partly undone.
- 503 errors: the DB pool is exhausted or the database is unreachable; check `DATABASE_URL` and `DATABASE_MAX_CONNS`.

## When to escalate

Check open issues and discussions at https://github.com/dani-garcia/vaultwarden — most client-compatibility breaks are reported there within days of a client release. Report Vaultwarden problems there, not to Bitwarden support — Bitwarden does not support third-party servers and will ask you to reproduce on its own.
