---
name: api-reference
description: Manual reference (invoke /vaultwarden-dev:api-reference) for "Vaultwarden API endpoints", "Vaultwarden REST API routes", "Vaultwarden token grants", "Vaultwarden curl examples" — exact HTTP routes, payloads and auth of a Vaultwarden server.
disable-model-invocation: true
---

# Vaultwarden API Reference

Verified against Vaultwarden 1.37.4 (2026-10-05) source on `main`. Vaultwarden publishes **no OpenAPI spec**; the route macros in `src/api/` and the wiki (https://github.com/dani-garcia/vaultwarden/wiki) are the documentation. Bitwarden's own API docs describe a superset — only what is listed here exists on Vaultwarden.

## Mounts

| Prefix | Contents | Auth |
|---|---|---|
| `/identity` | prelogin, `connect/token` | none (rate-limited) |
| `/api` | client API: sync, ciphers, folders, orgs, members, policies, events, sends | `Authorization: Bearer <access_token>` |
| `/api/public` | only `POST /organization/import` | org API-key bearer |
| `/admin` | admin panel + JSON API | `VW_ADMIN` cookie — see `vaultwarden-dev:admin-panel` |
| `/alive`, `/api/version`, `/api/config` | health and version | none |
| `/notifications/hub` | WebSocket live sync | bearer |

If `DOMAIN` carries a path (`https://example.com/vault`), every prefix moves under it.

## Capability boundary — read before writing code

Vault content is end-to-end encrypted (`EncString`s); raw HTTP can manage auth, membership, policies, events, item delete/restore and `/admin`, but reading or writing item content, folders, collection names, member confirmation and exports need client crypto. The full table is in [setup § 1](../setup/SKILL.md) — route content tasks to `bw` (`vaultwarden-dev:cli-recipes`).

## Auth in one call

```bash
VW_TOKEN="$(printf '%s' "$BW_CLIENTSECRET" | curl -fsS "$VW_URL/identity/connect/token" \
  --data-urlencode grant_type=client_credentials --data-urlencode scope=api \
  --data-urlencode "client_id=$BW_CLIENTID" --data-urlencode 'client_secret@-' \
  --data-urlencode device_type=14 --data-urlencode "device_identifier=$VW_DEVICE_ID" \
  --data-urlencode device_name=vw-script | jq -r .access_token)"
```

All grants (password, user API key, org API key, refresh), the master-password hash and the error bodies: [references/identity.md](references/identity.md).

## Core endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/accounts/profile` | user, `organizations[]` with `id`, `type`, `status` |
| GET | `/api/accounts/revision-date` | cheap change detection before a full sync |
| GET | `/api/sync?excludeDomains=true` | whole vault, encrypted |
| GET | `/api/organizations/<org-uuid>/users?includeCollections=true&includeGroups=true` | members (Admin+) |
| POST | `/api/organizations/<org-uuid>/users/invite` | invite by email |
| PUT | `/api/organizations/<org-uuid>/users/<member-id>/revoke` | revoke access, keep the seat record |
| DELETE | `/api/organizations/<org-uuid>/users/<member-id>` | remove member |
| GET | `/api/organizations/<org-uuid>/policies` | policies |
| GET | `/api/organizations/<org-uuid>/events?start=&end=` | events (`ORG_EVENTS_ENABLED=true` only) |
| PUT | `/api/ciphers/<item-id>/delete` | move item to trash |
| PUT | `/api/ciphers/<item-id>/restore` | restore from trash |

Full route tables — account, ciphers, folders, collections, members, groups, policies, events, Sends, emergency access, devices: [references/client-api.md](references/client-api.md). Directory-sync import: [references/public-api.md](references/public-api.md).

Member `type`: `0` Owner, `1` Admin, `2` User, `3` Manager (`4`/Custom is mapped to Manager). Member `status`: `-1` Revoked, `0` Invited, `1` Accepted, `2` Confirmed.

<example>
User: "List who is still only invited in our org."
Call `GET /api/organizations/<org-uuid>/users` with the bearer token and filter `.data[] | select(.status == 0) | {id, email}`. The `email` field is plaintext; no decryption needed.
</example>

<example>
User: "Confirm the three people who accepted the invite."
Confirmation needs the organization key encrypted to each member's public key — not doable with curl. Use `bw` (`bw confirm org-member <member-id> --organizationid <org-uuid>`) or `bw serve` `POST /confirm/org-member/<member-id>`.
</example>
