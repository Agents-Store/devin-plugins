---
name: setup
description: This skill should be used when the user asks to "connect to Vaultwarden", "point bw at my Vaultwarden server", "check Vaultwarden is reachable", "get a Vaultwarden API token", "call the Vaultwarden REST API", "manage org members via the API", or "sync users from LDAP into Vaultwarden".
---

# Vaultwarden Setup and Connection Check

Connect the tooling to a self-hosted Vaultwarden server and prove each layer works before writing any automation. Vaultwarden is a Rust re-implementation of the Bitwarden server: it speaks the Bitwarden **client** API, so the official Bitwarden clients and the `bw` CLI work against it.

Placeholders used throughout this plugin: `https://vault.example.com` for the server, `<user-uuid>`, `<org-uuid>`, `<item-id>` for identifiers. Replace them with the user's values; never write a real URL or token into a committed file.

## 1. Pick the right access path

Decide which of the four surfaces the task needs, because each has its own credentials and its own limits:

| Task | Surface | Credential |
|---|---|---|
| Read or write vault items, folders, Sends | `bw` CLI or `bw serve` | API key or email + master password, then the master password to unlock |
| Invite, revoke, remove org members; policies; events | Client API over HTTP (`/api/...`) | Bearer token from `/identity/connect/token` |
| Server-wide admin: users, 2FA reset, orgs, config, DB backup | Admin panel API (`/admin/...`) | `ADMIN_TOKEN` → `VW_ADMIN` cookie |
| Directory sync of members and groups | Public API `POST /api/public/organization/import` | Organization API key |

Vault content is end-to-end encrypted: names, usernames, passwords, notes, folder and collection names are `EncString`s (`2.<iv>|<ciphertext>|<mac>`), and the server never sees plaintext. Route each task by this boundary:

| Raw HTTP can | Needs client crypto (`bw`, `bw serve`, python-vaultwarden, Terraform) |
|---|---|
| log in, refresh, list devices | read or create item content |
| list orgs, members, groups, policies, events | create or rename folders and collections |
| invite, reinvite, revoke, restore, remove members; change member type | **confirm** an accepted member (needs the org key wrapped for that member) |
| soft-delete, restore, hard-delete, move items by id | create Sends, change password or KDF |
| everything under `/admin` | export a readable vault |

Writing raw HTTP for the right column produces ciphertext the official clients cannot decrypt — route those tasks to `vaultwarden-dev:cli-recipes`.

## 2. Check the server is up

Run the unauthenticated probes first — they separate network and proxy problems from credential problems:

```bash
export VW_URL="https://vault.example.com"
curl -fsS "$VW_URL/alive"                      # JSON date string; also checks the DB connection
curl -fsS "$VW_URL/api/version"                # Vaultwarden version, e.g. "1.37.4"
curl -fsS "$VW_URL/api/config" | jq '{version, gitHash, server}'
```

`/api/config` reports the Bitwarden server version it emulates (`version`) and `server.name = "Vaultwarden"`. A `200` from `/alive` with a `502`/`504` elsewhere points at the reverse proxy, not at Vaultwarden.

## 3. Install and point the Bitwarden CLI

```bash
npm install -g @bitwarden/cli        # or: brew install bitwarden-cli / snap install bw / native binary
bw --version
bw config server "$VW_URL"           # stores the server; run before the first login
bw config server                     # prints the configured server
```

Match versions before going further — a mismatch shows up later as a misleading "Username or password is incorrect". In short: `bw` 2026.9.x needs Vaultwarden 1.37.4+, and Vaultwarden 1.37.4+ rejects outdated CLIs. Run `/vaultwarden-dev:check-version` for a verdict; the full table and what to pin: [version matrix](../troubleshoot/references/version-matrix.md).

## 4. Log in for scripts with the personal API key

Prefer the personal API key for automation: it skips 2FA prompts and keeps the master password out of the login step. The user copies it from the web vault → Account settings → Security → Keys → View API key.

```bash
# client_id has the form user.<user-uuid>; enter both values without echoing them
read -r -p "client_id: " BW_CLIENTID && export BW_CLIENTID
read -r -s -p "client_secret: " BW_CLIENTSECRET && export BW_CLIENTSECRET && echo
bw login --apikey
```

An API-key login authenticates but does **not** decrypt. Unlock with the master password and keep the session key in a variable, never in the chat output:

```bash
read -r -s -p "master password: " BW_PASSWORD && export BW_PASSWORD && echo
export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"
unset BW_PASSWORD
bw sync && bw status | jq '{serverUrl, userEmail, status, lastSync}'
```

`bw status` must show the expected `serverUrl` and `"status": "unlocked"`. Interactive alternative: `bw login` (email, master password, 2FA code) followed by the same `bw unlock`.

Why the indirection: anything printed to the terminal lands in the conversation transcript, so the master password, `BW_SESSION`, and `client_secret` are read from the user's keyboard or a file and passed through variables. The `vaultwarden-dev:secret-hygiene` skill has the full rule set.

## 5. Get a bearer token for the client API (optional)

Only needed for raw `/api/...` calls such as member management. Use the same personal API key with the `client_credentials` grant:

```bash
export VW_DEVICE_ID="${VW_DEVICE_ID:-$(uuidgen | tr 'A-Z' 'a-z')}"   # generate once, keep it in the script's config
TOKEN_JSON="$(printf '%s' "$BW_CLIENTSECRET" | curl -fsS "$VW_URL/identity/connect/token" \
  --data-urlencode grant_type=client_credentials \
  --data-urlencode scope=api \
  --data-urlencode "client_id=$BW_CLIENTID" \
  --data-urlencode 'client_secret@-' \
  --data-urlencode device_type=14 \
  --data-urlencode "device_identifier=$VW_DEVICE_ID" \
  --data-urlencode device_name=vw-script)"
export VW_TOKEN="$(printf '%s' "$TOKEN_JSON" | jq -r .access_token)"
curl -fsS -H "Authorization: Bearer $VW_TOKEN" "$VW_URL/api/accounts/profile" | jq '{email, name, organizations: [.organizations[] | {id, name, type}]}'
```

The secret goes through stdin (`client_secret@-`) so it never appears in the process list. Reuse one stable `device_identifier` per script: every new identifier registers a new device and, with SMTP configured, mails the user a "new device" notice. Access tokens live 2 hours.

Next: route tables for members, policies, events and items in [client-api.md](../api-reference/references/client-api.md); every grant type, the master-password hash and token errors in [identity.md](../api-reference/references/identity.md); LDAP/directory sync through the one Public API route in [public-api.md](../api-reference/references/public-api.md).

## 6. Enable the admin panel (server operators only)

The `/admin` panel exists only when `ADMIN_TOKEN` is set on the server. Generate an Argon2 PHC hash instead of storing a plain token:

```bash
docker exec -it <container> /vaultwarden hash --preset owasp   # prints ADMIN_TOKEN='$argon2id$...'
```

Set that value as `ADMIN_TOKEN` in the container environment (in `docker-compose.yml` escape every `$` as `$$`) and restart. The admin API itself is covered by `vaultwarden-dev:admin-panel`.

## What this skill does not cover

- Deploying Vaultwarden itself (reverse proxy, TLS, volumes) — follow the upstream wiki: https://github.com/dani-garcia/vaultwarden/wiki
- Secrets Manager (`bws`, machine accounts): Vaultwarden does not implement it — use `bw` with items or custom fields instead.
- Failure diagnosis — `vaultwarden-dev:troubleshoot`.
