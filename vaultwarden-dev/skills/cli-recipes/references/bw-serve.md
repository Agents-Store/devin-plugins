# `bw serve` — Local Vault Management API

`bw serve` runs the Bitwarden CLI as a local HTTP server that does the crypto for you. It is the right tool when an integration needs many vault reads/writes: one unlocked process instead of a `bw` start-up per call. Spec: "Vault Management API" in the Bitwarden Help Center (OpenAPI 3). Works against Vaultwarden because the crypto happens in the CLI, not on the server.

## Start

```bash
bw config server "https://vault.example.com"
bw login --apikey                                       # BW_CLIENTID / BW_CLIENTSECRET in env
bw serve --port 8087 --hostname localhost &             # defaults: port 8087, localhost
BW_SERVE="http://localhost:${BW_PORT:-8087}"
read -r -s -p "master password: " MP && echo
jq -n --arg p "$MP" '{password: $p}' | curl -fsS -X POST "$BW_SERVE/unlock" \
  -H 'Content-Type: application/json' -d @- | jq '{success}'
unset MP
```

The server has **no authentication**: any local process (or browser tab, if origin protection is off) that reaches the port can read the unlocked vault. Keep it on `localhost`, never pass `--disable-origin-protection`, and stop it with `POST /lock` + kill when done. Requests carrying an `Origin` header are rejected by default — call it from scripts, not from web pages.

## Endpoints

| Method | Path | Notes |
|---|---|---|
| POST | `/unlock` | `{password}` → session held by the server |
| POST | `/lock` | lock |
| POST | `/sync` | pull latest from the server |
| GET | `/status` | server URL, user, lock state |
| GET | `/list/object/items` | query `search`, `folderid`, `collectionid`, `organizationId`, `url`, `trash` — **returns secrets** |
| GET | `/object/item/<id>` | one item — **returns secrets** |
| POST | `/object/item` | create (plain JSON body, no `bw encode`) |
| PUT | `/object/item/<id>` | replace |
| DELETE | `/object/item/<id>` | to trash |
| POST | `/restore/item/<id>` | from trash |
| GET | `/object/username/<id>`, `/object/uri/<id>` | single non-secret field |
| GET | `/object/password/<id>`, `/object/totp/<id>`, `/object/notes/<id>` | single **secret** field |
| GET | `/list/object/folders`, `/object/folder/<id>` | folders |
| POST | `/object/folder` | `{name}` |
| GET | `/list/object/organizations`, `/list/object/collections`, `/list/object/org-collections?organizationId=` | org data |
| GET | `/list/object/org-members?organizationId=` | members |
| POST | `/confirm/org-member/<member-id>?organizationId=<org-uuid>` | confirm an accepted member |
| POST | `/move/<item-id>/<org-uuid>` | body: array of collection ids |
| GET | `/generate` | query `length`, `uppercase`, `lowercase`, `number`, `special`, `passphrase`, `words`, `separator` |
| GET | `/object/template/<type>` | `item`, `item.login`, `folder`, `org-collection`… |
| POST | `/attachment?itemid=<id>` | multipart upload |
| GET | `/object/fingerprint/me` | your fingerprint phrase |

Responses are wrapped: `{"success": true, "data": {...}}`.

## Recipes

```bash
# Ids and names only
curl -fsS "$BW_SERVE/list/object/items?search=postgres" | jq -r '.data.data[] | [.id, .name] | @tsv'

# A password straight into a variable
DB_PASSWORD="$(curl -fsS "$BW_SERVE/object/password/<item-id>" | jq -r .data.data)"

# Create a login (plain JSON — the CLI encrypts it)
export NEW_PW="$(curl -fsS "$BW_SERVE/generate?length=32&special=true" | jq -r .data.data)"
jq -n --arg n "Staging Redis" '{type: 1, name: $n, login: {username: "default", password: env.NEW_PW, uris: []}}' \
  | curl -fsS -X POST "$BW_SERVE/object/item" -H 'Content-Type: application/json' -d @- | jq '.data | {id, name}'
unset NEW_PW

# Lock when finished
curl -fsS -X POST "$BW_SERVE/lock" | jq '{success}'
```

## Running as a service

Run it under the account that owns the integration, with its own `BITWARDENCLI_APPDATA_DIR`, bound to `localhost`, and unlock it from the service's secret store at start-up. On Vaultwarden, check the CLI version against the server before upgrading either side (`vaultwarden-dev:troubleshoot`).
