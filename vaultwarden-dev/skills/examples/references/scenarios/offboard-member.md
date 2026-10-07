# Scenario: Offboard an Employee

Goal: `leaver@example.com` loses access immediately, and every shared secret they could read is listed for rotation. Order matters: block the account first (which also ends its sessions), then revoke the org membership, then decide about the account.

Needs: admin token, an org Admin/Owner bearer token (`VW_TOKEN`), `bw` unlocked as an org Admin/Owner.

## 1. Identify — read only

```bash
USER_ID="$(curl -fsS -b "$JAR" -H 'Accept: application/json' "$VW_URL/admin/users/by-mail/leaver@example.com" | jq -r .id)"
curl -fsS -H "Authorization: Bearer $VW_TOKEN" \
  "$VW_URL/api/organizations/<org-uuid>/users?includeCollections=true" \
  | jq '.data[] | select(.email == "leaver@example.com") | {id, type, status, accessAll, collections: [.collections[].id]}'
```

Show the user this summary and get confirmation before step 2.

## 2. Cut access — admin panel, then client API

```bash
adm() { curl -fsS -b "$JAR" -H 'Content-Type: application/json' -H 'Accept: application/json' "$@"; }
adm -X POST "$VW_URL/admin/users/$USER_ID/disable"       # block logins, rotate the security stamp, drop all devices

curl -fsS -X PUT -H "Authorization: Bearer $VW_TOKEN" \
  "$VW_URL/api/organizations/<org-uuid>/users/<member-id>/revoke"
```

Revoke (not remove) keeps the membership record, so it can be restored and the event log stays attributable. Remove later with `DELETE /api/organizations/<org-uuid>/users/<member-id>` once the handover is done.

Check: `GET /admin/users/$USER_ID` → `userEnabled: false`; member `status` `-1`.

## 3. List what must be rotated — bw, names only

Everything in the collections the person could reach (all collections if `accessAll` was true):

```bash
for col in <collection-id-1> <collection-id-2>; do
  bw list items --organizationid <org-uuid> --collectionid "$col" \
    | jq -r '.[] | [.id, .name, (.login.username // ""), ((.login.uris // [])[0].uri // "")] | @tsv'
done
```

This pipeline prints only ids, names, usernames and URIs; the guard hook will still ask because `bw list items` can print secrets — approve it, the `jq` projection removes them. Rotate each credential in its target system, then update the item (`vaultwarden-dev:cli-recipes` → "Rotate a password in place").

## 4. Audit — client API (if `ORG_EVENTS_ENABLED=true`)

```bash
curl -fsS -H "Authorization: Bearer $VW_TOKEN" \
  "$VW_URL/api/organizations/<org-uuid>/users/<member-id>/events?start=2026-09-01T00:00:00Z&end=2026-10-07T23:59:59Z" \
  | jq -r '.data[] | [.date, .type, (.itemId // "")] | @tsv'
```

## 5. Account fate — admin panel, after explicit confirmation

- Keep disabled (default): personal vault retained, nothing lost.
- Delete: `adm -X POST "$VW_URL/admin/users/$USER_ID/delete"` — removes the personal vault for good; take a DB backup first (`adm -X POST "$VW_URL/admin/config/backup_db"`).

Clean up: `curl -sS -b "$JAR" -o /dev/null "$VW_URL/admin/logout"; rm -f "$JAR"`.
