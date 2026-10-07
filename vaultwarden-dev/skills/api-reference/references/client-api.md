# Vaultwarden Client API — Route Tables

Source: route macros in `src/api/core/{accounts,ciphers,folders,organizations,sends,emergency_access,events}.rs`, Vaultwarden 1.37.4. Every path is under `/api` and needs `Authorization: Bearer <access_token>` unless marked otherwise. Bodies are JSON with camelCase keys.

Contents: [Account and devices](#account-and-devices) · [Sync and ciphers](#sync-and-ciphers-items) · [Folders](#folders) · [Organizations and collections](#organizations-and-collections) · [Members](#members) · [Groups](#groups-only-with-org_groups_enabledtrue) · [Policies](#policies) · [Events](#events-only-with-org_events_enabledtrue) · [Sends and emergency access](#sends-and-emergency-access) · [Misc](#misc)

Helper used below:

```bash
vw() { curl -fsS -H "Authorization: Bearer $VW_TOKEN" -H 'Content-Type: application/json' "$@"; }
```

## Account and devices

| Method | Path | Notes |
|---|---|---|
| GET | `/accounts/profile` | profile + `organizations[]` (id, name, type, status) |
| PUT | `/accounts/profile` | also POST; name, culture |
| GET | `/accounts/revision-date` | epoch ms; compare before `/sync` |
| GET | `/accounts/keys` | encrypted private key + public key |
| POST | `/accounts/verify-password` | `{masterPasswordHash}` |
| POST | `/accounts/api-key` | `{masterPasswordHash}` or `{otp}` → `{apiKey}` = personal `client_secret` |
| POST | `/accounts/rotate-api-key` | same body; old secret stops working |
| POST | `/accounts/password`, `/accounts/kdf`, `/accounts/email-token`, `/accounts/email`, `/accounts/security-stamp` | credential changes — need client crypto |
| POST | `/accounts/key-management/user-key-id` | used by `bw` 2026.9+; missing before 1.37.4 |
| DELETE | `/accounts` | also POST `/accounts/delete`; deletes the account |
| GET | `/devices` | devices logged in to this account |
| GET | `/devices/knowndevice` | headers `X-Request-Email` (base64url) and `X-Device-Identifier` |

## Sync and ciphers (items)

All item fields except ids, type, dates, `organizationId`, `folderId`, `collectionIds` are EncStrings.

| Method | Path | Notes |
|---|---|---|
| GET | `/sync?excludeDomains=true` | profile, folders, collections, ciphers, policies, sends |
| GET | `/ciphers`, `/ciphers/<id>`, `/ciphers/<id>/details` | read |
| GET | `/ciphers/organization-details?organizationId=<org-uuid>` | all org items (Admin+) |
| POST | `/ciphers`, `/ciphers/create`, `/ciphers/import` | create — encrypted payload only |
| PUT | `/ciphers/<id>` | also POST; full update, encrypted |
| PUT | `/ciphers/<id>/partial` | `{folderId, favorite}` — no crypto needed |
| PUT | `/ciphers/move` | `{ids:[...], folderId}` — no crypto needed |
| PUT | `/ciphers/<id>/collections_v2` | `{collectionIds:[...]}`; also `/collections`, `/collections-admin` |
| PUT | `/ciphers/<id>/share` | move a personal item into an org — re-encrypts, needs crypto |
| PUT | `/ciphers/<id>/delete` | soft delete (trash); `/delete-admin` for org items |
| PUT | `/ciphers/delete` | bulk soft delete `{ids:[...]}` |
| PUT | `/ciphers/<id>/restore` | from trash; `/restore-admin`; bulk `/ciphers/restore` |
| DELETE | `/ciphers/<id>` | hard delete; `/ciphers/<id>/admin` for org items |
| DELETE | `/ciphers` | bulk hard delete `{ids:[...]}` |
| POST | `/ciphers/purge` | `{masterPasswordHash}`; empties the whole personal vault |
| PUT | `/ciphers/<id>/archive`, `/unarchive` | archive flag |
| POST | `/ciphers/<id>/attachment/v2` | attachment upload slot |
| GET | `/ciphers/<id>/attachment/<attachment-id>` | metadata + signed download URL |

## Folders

| Method | Path | Notes |
|---|---|---|
| GET | `/folders` | names are EncStrings |
| POST | `/folders` | `{name: <EncString>}` — needs crypto |
| PUT | `/folders/<id>` | also POST |
| DELETE | `/folders/<id>` | also POST `/folders/<id>/delete`; items fall back to "No folder" |

## Organizations and collections

| Method | Path | Notes |
|---|---|---|
| POST | `/organizations` | create; limited by `ORG_CREATION_USERS` |
| GET | `/organizations/<org>` | details |
| PUT | `/organizations/<org>` | name, billing email (Owner) |
| DELETE | `/organizations/<org>` | `{masterPasswordHash}` (Owner) |
| POST | `/organizations/<org>/leave` | leave as a member |
| GET | `/organizations/<org>/collections` | collection ids + encrypted names |
| GET | `/organizations/<org>/collections/details` | with access lists |
| GET | `/organizations/<org>/collections/<col>/details` | one collection |
| POST | `/organizations/<org>/collections` | create — encrypted name |
| PUT | `/organizations/<org>/collections/<col>` | update access / name |
| DELETE | `/organizations/<org>/collections/<col>` | delete; bulk `DELETE /organizations/<org>/collections` |
| POST | `/organizations/<org>/collections/bulk-access` | set member/group access on many collections |
| GET | `/organizations/<org>/export` | encrypted org export |
| POST | `/organizations/<org>/api-key` | `{masterPasswordHash}` → org `client_secret` (Owner) |
| POST | `/organizations/<org>/rotate-api-key` | rotate it |

## Members

`<member>` is the **membership id** from the member list, not the user id.

| Method | Path | Notes |
|---|---|---|
| GET | `/organizations/<org>/users?includeCollections=true&includeGroups=true` | list (Admin+) |
| GET | `/organizations/<org>/users/mini-details` | id, email, name only |
| GET | `/organizations/<org>/users/<member>` | one member |
| POST | `/organizations/<org>/users/invite` | see body below |
| POST | `/organizations/<org>/users/reinvite` | bulk `{ids:[...]}` |
| POST | `/organizations/<org>/users/<member>/reinvite` | single |
| POST | `/organizations/<org>/users/<member>/confirm` | `{key}` = org key encrypted to the member — needs crypto |
| POST | `/organizations/<org>/users/confirm` | bulk `{keys:[{id,key}]}` |
| POST | `/organizations/<org>/users/public-keys` | `{ids:[...]}` → public keys for confirmation |
| PUT | `/organizations/<org>/users/<member>` | `{type, collections, groups, permissions}` |
| PUT | `/organizations/<org>/users/<member>/revoke` | bulk `PUT .../users/revoke {ids:[...]}` |
| PUT | `/organizations/<org>/users/<member>/restore` | bulk `PUT .../users/restore` |
| DELETE | `/organizations/<org>/users/<member>` | remove; bulk `DELETE .../users {ids:[...]}` |

Invite body — `groups` is required even when empty; `type` accepts `0..3` or `"Owner"`, `"Admin"`, `"User"`, `"Manager"` (case-sensitive):

```json
{
  "emails": ["new.member@example.com"],
  "type": 2,
  "groups": [],
  "collections": [
    {"id": "<collection-id>", "readOnly": false, "hidePasswords": false, "manage": false}
  ],
  "permissions": {}
}
```

```bash
vw -X POST "$VW_URL/api/organizations/$ORG_ID/users/invite" -d @invite.json
```

With SMTP configured the invitee gets an email; without SMTP the invitation is recorded and an existing account is auto-accepted. After acceptance an Owner/Admin must still **confirm** the member from a client.

## Groups (only with `ORG_GROUPS_ENABLED=true`)

| Method | Path | Notes |
|---|---|---|
| GET | `/organizations/<org>/groups`, `/groups/details` | list |
| POST | `/organizations/<org>/groups` | `{name, accessAll, externalId, collections, users}` — group names are plaintext |
| GET | `/organizations/<org>/groups/<group>`, `/groups/<group>/details` | one group |
| PUT | `/organizations/<org>/groups/<group>` | update |
| DELETE | `/organizations/<org>/groups/<group>` | delete; bulk `DELETE .../groups {ids:[...]}` |

## Policies

| Method | Path | Notes |
|---|---|---|
| GET | `/organizations/<org>/policies` | all policies |
| GET | `/organizations/<org>/policies/<type>` | one |
| PUT | `/organizations/<org>/policies/<type>` | body `{"policy": {"enabled": true, "data": null}}` |

Policy types implemented: `0` TwoFactorAuthentication, `1` MasterPassword, `2` PasswordGenerator, `3` SingleOrg, `5` PersonalOwnership, `6` DisableSend, `7` SendOptions, `8` ResetPassword, `14` RemoveUnlockWithPin, `15` RestrictedItemTypes, `16` UriMatchDefaults, `17` AutotypeDefaultSetting. Not supported: `4` RequireSso, `9` MaximumVaultTimeout, `10` DisablePersonalVaultExport.

## Events (only with `ORG_EVENTS_ENABLED=true`)

| Method | Path | Notes |
|---|---|---|
| GET | `/organizations/<org>/events?start=<iso>&end=<iso>` | page with `continuationToken` |
| GET | `/organizations/<org>/users/<member>/events?start=&end=` | one member |
| GET | `/ciphers/<id>/events?start=&end=` | one item |
| POST | `/events/collect` | client upload, mounted at `/events` not `/api` |

```bash
vw "$VW_URL/api/organizations/$ORG_ID/events?start=2026-10-01T00:00:00Z&end=2026-10-07T23:59:59Z" \
  | jq '.data[] | {date, type, actingUserId, memberId, itemId, ipAddress}'
```

Retention: `EVENTS_DAYS_RETAIN`, pruned by `EVENT_CLEANUP_SCHEDULE`.

## Sends and emergency access

| Method | Path | Notes |
|---|---|---|
| GET | `/sends`, `/sends/<id>` | encrypted |
| POST | `/sends`, `/sends/file/v2` | create — needs crypto |
| DELETE | `/sends/<id>` | delete |
| POST | `/sends/access` | anonymous access to a Send |
| GET | `/emergency-access/trusted`, `/emergency-access/granted` | grants |
| POST | `/emergency-access/invite` | `{email, type, waitTimeDays}` |
| POST | `/emergency-access/<id>/<step>` | lifecycle; `<step>` is one of accept, confirm, initiate, approve, reject, view, takeover, password |
| DELETE | `/emergency-access/<id>` | revoke grant |

## Misc

| Method | Path | Notes |
|---|---|---|
| GET | `/alive` | also `HEAD`; no auth; checks the DB |
| GET | `/version` | no auth; Vaultwarden version |
| GET | `/config` | no auth; emulated Bitwarden version, `gitHash`, `server.name` |
| GET | `/now` | server time |
| GET | `/plans` | static plan list for clients |
| POST | `/auth-requests` | passwordless login request; `GET /auth-requests/pending`, `PUT /auth-requests/<id>` |
