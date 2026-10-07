# Vaultwarden Public API — Directory Import Only

Bitwarden's Public API (members, groups, collections, events, policies under `/public/...`) is a **paid, Bitwarden-licensed** surface. Vaultwarden implements exactly one route of it, for the Bitwarden Directory Connector:

| Method | Path | Auth |
|---|---|---|
| POST | `/api/public/organization/import` | bearer from the org API key (`scope=api.organization`) |

Source: `src/api/core/public.rs`. Every other Public API path returns 404 — this is why the organization tools of the official Bitwarden MCP server and of other Public-API clients do not work against Vaultwarden.

## Token

```bash
ORG_TOKEN="$(printf '%s' "$VW_ORG_CLIENT_SECRET" | curl -fsS "$VW_URL/identity/connect/token" \
  --data-urlencode grant_type=client_credentials \
  --data-urlencode scope=api.organization \
  --data-urlencode "client_id=organization.$ORG_ID" \
  --data-urlencode 'client_secret@-' | jq -r .access_token)"
```

No device fields. The token is only accepted by the import route.

## Body

```json
{
  "groups": [
    {"name": "Engineering", "externalId": "cn=engineering", "memberExternalIds": ["uid=alice"]}
  ],
  "members": [
    {"email": "alice@example.com", "externalId": "uid=alice", "deleted": false},
    {"email": "bob@example.com", "externalId": "uid=bob", "deleted": true}
  ],
  "overwriteExisting": false
}
```

## Behaviour

- Members are matched by email inside the organization.
- `deleted: true` **revokes** the member (an Owner is never revoked); `deleted: false` invites a new member or restores a revoked one.
- New members join as type User without access to all collections; they still need confirmation from a client.
- Groups are synced only when the server runs with `ORG_GROUPS_ENABLED=true`; otherwise they are skipped with a warning in the log.
- `overwriteExisting: true` **removes** every member whose `externalId` is not in the list (Owners excepted). Run it first with `false` and compare the member list before switching it on.
- `largeImport` is accepted but ignored.

```bash
curl -fsS -X POST "$VW_URL/api/public/organization/import" \
  -H "Authorization: Bearer $ORG_TOKEN" -H 'Content-Type: application/json' -d @import.json
```
