---
name: admin-panel
description: This skill should be used when the user asks to "use the Vaultwarden admin API", "script the /admin panel", "disable or delete a Vaultwarden user", "reset a user's 2FA", "change Vaultwarden config", or mentions ADMIN_TOKEN or the VW_ADMIN cookie.
---

# Vaultwarden Admin Panel API

The `/admin` panel is Vaultwarden's own server-administration surface (not part of Bitwarden). It manages accounts across all organizations, server config and SQLite backups. Verified against `src/api/admin.rs`, Vaultwarden 1.37.4.

## Prerequisites

- `ADMIN_TOKEN` is set on the server. Without it (and without `DISABLE_ADMIN_TOKEN=true`) every route except `GET /admin` is absent and the page says "The admin panel is disabled".
- Prefer an Argon2 PHC value (`vaultwarden hash`, see `vaultwarden-dev:setup`); a plain-text token works but logs a warning on every start.
- `DISABLE_ADMIN_TOKEN=true` removes authentication entirely — acceptable only behind a reverse proxy that does its own auth.

## Log in — cookie, not bearer

The admin API accepts **only** the `VW_ADMIN` cookie. There is no bearer-header mode. Log in once per script run and keep the cookie jar private:

```bash
export VW_URL="https://vault.example.com"
JAR="$(mktemp)"                                  # holds a session JWT; delete it at the end
read -r -s -p "admin token: " VW_ADMIN_TOKEN && echo
printf '%s' "$VW_ADMIN_TOKEN" | curl -sS -c "$JAR" -o /dev/null -w '%{http_code}\n' \
  --data-urlencode 'token@-' "$VW_URL/admin"
unset VW_ADMIN_TOKEN
adm() { curl -fsS -b "$JAR" -H 'Content-Type: application/json' -H 'Accept: application/json' "$@"; }
```

`200` or `303` means logged in; `401` is a wrong token; `429` means the admin limiter tripped (`ADMIN_RATELIMIT_SECONDS`/`ADMIN_RATELIMIT_MAX_BURST`, default 300 s / 3 attempts). The token is piped through stdin so it never appears in the process list or the transcript.

The session lasts `ADMIN_SESSION_LIFETIME` minutes (default 20). An expired cookie returns 401 `Session expired` — log in again. The cookie path is `/admin`; with a path-prefixed `DOMAIN` it is `<prefix>/admin`.

JSON routes are declared `format = "application/json"`: send `Content-Type: application/json` even on POSTs with an empty body, otherwise the route does not match and the call fails with a not-found error.

## Routes

| Method | Path | Body | Effect |
|---|---|---|---|
| GET | `/admin/users` | — | all users (JSON) incl. `userEnabled`, `createdAt`, `lastActive`, `twoFactorEnabled` |
| GET | `/admin/users/<user-uuid>` | — | one user |
| GET | `/admin/users/by-mail/<email>` | — | one user by email |
| POST | `/admin/invite` | `{"email": "..."}` | create the account and send an invite (or record it when SMTP is off); 409 if it exists |
| POST | `/admin/users/<user-uuid>/invite/resend` | — | resend; 400 if already accepted |
| POST | `/admin/users/<user-uuid>/deauth` | — | log out every device, rotate the security stamp |
| POST | `/admin/users/<user-uuid>/disable` | — | block login, rotate the security stamp, drop devices (includes `deauth`) |
| POST | `/admin/users/<user-uuid>/enable` | — | undo disable |
| POST | `/admin/users/<user-uuid>/remove-2fa` | — | remove all 2FA methods |
| DELETE | `/admin/users/<user-uuid>/sso` | — | unlink the SSO identity |
| POST | `/admin/users/<user-uuid>/delete` | — | **delete the account and its personal vault** |
| POST | `/admin/users/org_type` | `{"user_type": "Admin", "user_uuid": "...", "org_uuid": "..."}` | change org membership type; refuses to demote the last Owner |
| POST | `/admin/users/update_revision` | — | force every client to resync |
| POST | `/admin/organizations/<org-uuid>/delete` | — | **delete an organization and its items** |
| GET | `/admin/diagnostics/config` | — | support string, secrets masked |
| GET | `/admin/diagnostics/http?code=<n>` | — | returns status `<n>` — tests proxy error pages |
| POST | `/admin/config` | config JSON | write `config.json` (see caution below) |
| POST | `/admin/config/delete` | — | delete `config.json`, fall back to env |
| POST | `/admin/config/backup_db` | — | SQLite only: `VACUUM INTO` a timestamped copy next to the DB |
| POST | `/admin/test/smtp` | `{"email": "..."}` | send a test email |
| GET | `/admin/logout` | — | drop the cookie |

`/admin/users/overview`, `/admin/organizations/overview` and `/admin/diagnostics` return HTML pages, not JSON.

`user_type` accepts `0`–`3` or `"Owner"`, `"Admin"`, `"User"`, `"Manager"` (case-sensitive). The member must already belong to the organization.

## Recipes

```bash
# Users without 2FA, newest activity first — never print the whole object (it carries encrypted keys)
adm "$VW_URL/admin/users" | jq -r 'map(select(.twoFactorEnabled == false))
  | sort_by(.lastActive) | reverse[] | [.email, .id, .userEnabled, .lastActive] | @tsv'

# Look up one user's id
USER_ID="$(adm "$VW_URL/admin/users/by-mail/someone@example.com" | jq -r .id)"

# Invite
adm -X POST "$VW_URL/admin/invite" -d '{"email":"new.person@example.com"}' | jq '{id, email, _status}'

# Lost phone: remove 2FA, then force re-login everywhere
adm -X POST "$VW_URL/admin/users/$USER_ID/remove-2fa"
adm -X POST "$VW_URL/admin/users/$USER_ID/deauth"

# SQLite backup through the running server
adm -X POST "$VW_URL/admin/config/backup_db"

# Clean up
curl -sS -b "$JAR" -o /dev/null "$VW_URL/admin/logout"; rm -f "$JAR"
```

`_status` in user JSON: `0` enabled, `1` invited (not yet registered).

## Before any destructive call

`delete` (user or organization), `disable`, `deauth`, `remove-2fa`, `POST /admin/config` and `config/delete` take effect immediately; `delete` cannot be undone at all, and the others need a follow-up call (`enable`, re-enrolling 2FA, re-posting the old config) to reverse. Before running one:

1. Read the target back (`GET /admin/users/<id>`) and show the user email, id and what will happen.
2. For deletes, make sure a database backup from today exists (`config/backup_db` or `vaultwarden backup`).
3. Get an explicit confirmation from the user, then run exactly one call and read the target again to verify.

Why: an account deletion removes the person's personal vault, which only a database restore brings back.

## Caution: `POST /admin/config` replaces the file

The posted object becomes the whole `config.json`: it is merged over the environment, **not** over the existing `config.json`. Posting `{"signups_allowed": false}` alone silently erases every other setting made earlier in the admin page. Change settings in the admin UI, or set environment variables and restart. Keys are snake_case (`signups_allowed`, `smtp_host`); values in `config.json` override environment variables. Editable versus restart-only keys: [references/config-keys.md](references/config-keys.md).

## Python alternative

For anything beyond a few calls, `python-vaultwarden` wraps this API (`VaultwardenAdminClient`) — see `vaultwarden-dev:sdk-patterns`.
