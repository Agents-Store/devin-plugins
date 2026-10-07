---
name: cli-recipes
description: This skill should be used when the user asks to "use bw with Vaultwarden", "get a password from Vaultwarden in a script", "create a Vaultwarden item from the CLI", "confirm org members with bw", "run bw serve", or needs Bitwarden CLI recipes for a self-hosted Vaultwarden.
---

# Bitwarden CLI (`bw`) Recipes for Vaultwarden

`bw` is the supported way to read and write **vault content** on Vaultwarden, because it performs the client-side encryption the server API expects. Connection and login: `vaultwarden-dev:setup`. Every recipe assumes `BW_SESSION` is exported (or `--session "$BW_SESSION"` is passed).

## Ground rules

- Pipe JSON through `jq` and select only the fields needed; keep passwords, TOTP seeds and notes inside `$(...)` captures. Command output becomes part of the conversation.
- The plugin's guard hook asks before `bw list items` / `bw get item` run uncaptured — including the filtered pipelines below, which it cannot prove safe. Approve those when the `jq` projection drops the secret fields; only captured forms pass silently.
- Run `bw sync` before reads in long-lived sessions — the CLI works from a local encrypted cache.
- Address items by id once found; names are not unique.

## Find things

```bash
bw list items --search github | jq -r '.[] | [.id, .name, .login.username // ""] | @tsv'
bw list items --folderid <folder-id> | jq -r '.[] | [.id, .name] | @tsv'
bw list items --url https://git.example.com | jq -r '.[] | [.id, .name] | @tsv'
bw list items --organizationid <org-uuid> --collectionid <collection-id> | jq -r '.[] | [.id, .name] | @tsv'
bw list folders | jq -r '.[] | [.id, .name] | @tsv'
bw list organizations | jq -r '.[] | [.id, .name, .type] | @tsv'
bw list org-collections --organizationid <org-uuid> | jq -r '.[] | [.id, .name] | @tsv'
bw list org-members --organizationid <org-uuid> | jq -r '.[] | [.id, .email, .status, .type] | @tsv'
```

`bw list items --trash` lists deleted items. `--search` matches name, username and URIs.

## Use a secret without printing it

```bash
export DB_PASSWORD="$(bw get password <item-id>)"
export API_TOKEN="$(bw get item <item-id> | jq -r '.fields[] | select(.name == "API_TOKEN") | .value')"
PGPASSWORD="$(bw get password <item-id>)" psql "postgresql://<db-user>@db.example.com:5432/<db>" -c 'select 1'
bw get username <item-id>            # usernames are not secret, printing is fine
```

Run a program with several secrets in its environment, without writing them to disk or into any argv (a `VAR=value cmd` prefix sets the environment; `env VAR=value cmd` would put the value in `env`'s arguments):

```bash
DB_PASSWORD="$(bw get password <db-item-id>)" \
STRIPE_KEY="$(bw get item <stripe-item-id> | jq -r '.fields[] | select(.name=="key") | .value')" \
  ./deploy.sh
```

Pattern for "secrets as env vars": store one secure note per service with custom fields named like the variables, then export every field:

```bash
while IFS=$'\t' read -r name value; do export "$name=$value"; done \
  < <(bw get item <item-id> | jq -r '.fields[] | [.name, .value] | @tsv')
```

## Create and edit

`bw create` and `bw edit` take **base64-encoded JSON** — always go through `bw encode`.

```bash
# Login item from the template
# (secrets reach jq through the environment, not through --arg, so they stay out of argv)
export NEW_PW="$(bw generate -ulns --length 32)"
bw get template item | jq --arg name "Staging DB" --arg user app \
  '.type = 1 | .name = $name | .notes = null
   | .login = {username: $user, password: env.NEW_PW, uris: [{uri: "postgresql://db.example.com", match: null}]}' \
  | bw encode | bw create item | jq '{id, name}'
unset NEW_PW

# Secure note with custom fields (type 0 = text, 1 = hidden, 2 = boolean)
bw get template item | jq '.type = 2 | .secureNote = {type: 0} | .name = "ci-secrets"
  | .fields = [{name: "API_TOKEN", value: "<value>", type: 1}]' | bw encode | bw create item | jq '{id, name}'

# Rotate a password in place
export NEW_PW="$(bw generate -ulns --length 32)"
bw get item <item-id> | jq '.login.password = env.NEW_PW' \
  | bw encode | bw edit item <item-id> | jq '{id, revisionDate}'
unset NEW_PW

# Folder and org collection
bw get template folder | jq '.name = "Infra"' | bw encode | bw create folder | jq '{id, name}'
bw get template org-collection | jq --arg org <org-uuid> '.organizationId = $org | .name = "Infra"' \
  | bw encode | bw create org-collection --organizationid <org-uuid> | jq '{id, name}'
```

Item types: `1` login, `2` secure note, `3` card, `4` identity, `5` SSH key.

## Share, move, delete

```bash
# Move a personal item into an organization collection (re-encrypts with the org key)
echo '["<collection-id>"]' | bw encode | bw move <item-id> <org-uuid> | jq '{id, organizationId}'

bw delete item <item-id>                 # to trash, restorable
bw restore item <item-id>
bw delete item <item-id> --permanent     # gone
```

## Organization members — what only the CLI can do

```bash
bw list org-members --organizationid <org-uuid> | jq -r '.[] | select(.status == 1) | [.id, .email] | @tsv'   # accepted, not confirmed
bw confirm org-member <member-id> --organizationid <org-uuid>
```

Confirmation encrypts the organization key to the member's public key. Compare the member's fingerprint phrase out of band first if the org requires it (`bw get fingerprint <user-id>`). Inviting, revoking and removing members works without crypto — see [client API routes](../api-reference/references/client-api.md).

## Generate

```bash
bw generate -ulns --length 32                 # upper, lower, numbers, special
bw generate --passphrase --words 5 --separator - --capitalize --includeNumber
```

## Backups and exports

```bash
# Encrypted, password-protected export — safe to store; restorable on any Bitwarden/Vaultwarden
bw export --format encrypted_json --password "$EXPORT_PASSWORD" --output "vault-$(date +%F).json"
bw export --organizationid <org-uuid> --format encrypted_json --password "$EXPORT_PASSWORD" --output "org-$(date +%F).json"
```

`bw export` accepts the export password only as `--password` (no env or stdin option), so it is visible in the process list while the export runs — run it on a machine you control. Plain `--format json` / `csv` writes every password in clear text; the guard hook asks before it runs. A vault export is not a server backup — server-side backup is in `vaultwarden-dev:admin-panel`.

## Local REST API: `bw serve`

For long-running integrations, `bw serve` keeps one unlocked session and exposes a local HTTP API (Vault Management API) — no Node process per call. Endpoints, start-up and safety rules: [references/bw-serve.md](references/bw-serve.md).

## Flags and environment

| Flag / variable | Effect |
|---|---|
| `--session <key>` / `BW_SESSION` | unlocked session to use |
| `--raw` | print only the value (no JSON envelope / no message) |
| `--pretty` | indent JSON |
| `--nointeraction` | never prompt; fail instead — use in scripts |
| `--response` | wrap output in `{success, data}` JSON |
| `BW_CLIENTID`, `BW_CLIENTSECRET` | personal API key for `bw login --apikey` |
| `BITWARDENCLI_APPDATA_DIR` | separate CLI state per account or server |
| `NODE_EXTRA_CA_CERTS` | trust a private CA in front of Vaultwarden |
| `BITWARDENCLI_DEBUG=true` | verbose HTTP logging (contains tokens — do not share) |

<example>
User: "Put the staging DB password into DATABASE_URL for my migration run."
Find the id with `bw list items --search staging | jq -r '.[] | [.id, .name] | @tsv'`, then run
`DATABASE_URL="postgresql://<db-user>:$(bw get password <item-id>)@db.example.com:5432/<db>" npm run migrate` — the password stays inside the capture and never appears in the output.
</example>

<example>
User: "Add the new Grafana admin login to the Infra collection."
Create the item with the template recipe, then `echo '["<infra-collection-id>"]' | bw encode | bw move <item-id> <org-uuid>`; report only `{id, name, organizationId}`.
</example>
