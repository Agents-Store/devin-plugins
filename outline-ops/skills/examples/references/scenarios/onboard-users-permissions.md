# Scenario: Onboard users & permissions

Invite people, bundle them into a group, and grant the group (and one individual) access to content. Assumes `setup` has run with an **admin** key (invites/role changes require admin). 

```bash
OUT="${OUTLINE_API_URL%/}"
H_AUTH="Authorization: Bearer ${OUTLINE_API_KEY}"
JSON="Content-Type: application/json"
ACC="Accept: application/json"
```

## 1. Invite users by email

```bash
curl -s -X POST "${OUT}/users.invite" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d '{"invites":[
        {"email":"alice@acme.com","name":"Alice","role":"member"},
        {"email":"bob@acme.com","name":"Bob","role":"viewer"}
      ]}' \
  | jq '.data | {sent: (.sent|length), users: [.users[].email]}'
```
`role` is `admin` | `member` | `viewer`. (→ `users-groups.md`)

## 2. Create a group and add members

```bash
GROUP_ID=$(curl -s -X POST "${OUT}/groups.create" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d '{"name":"New Hires"}' | jq -r '.data.id')

# Resolve a user by name/email, then add to the group
ALICE_ID=$(curl -s -X POST "${OUT}/users.list" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d '{"query":"alice"}' | jq -r '.data[0].id')

curl -s -X POST "${OUT}/groups.add_user" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${GROUP_ID}\",\"userId\":\"${ALICE_ID}\"}" | jq '.data.groupMemberships | length'
```

## 3. Grant the group access to a collection

```bash
curl -s -X POST "${OUT}/collections.add_group" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${COLLECTION_ID}\",\"groupId\":\"${GROUP_ID}\",\"permission\":\"read_write\"}" \
  | jq '.data.collectionGroupMemberships | length'
```
`permission` is `read` or `read_write`. Revoke later with `collections.remove_group`. (→ `collections.md`)

## 4. Grant one user access to a single document

```bash
curl -s -X POST "${OUT}/documents.add_user" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${DOC_ID}\",\"userId\":\"${ALICE_ID}\",\"permission\":\"read_write\"}" \
  | jq '.data.memberships | length'
```
Per-document group access uses `documents.add_group`. (→ `documents.md`)

## 5. Lifecycle: suspend, reactivate, change role

```bash
# Promote to admin (admin only)
curl -s -X POST "${OUT}/users.update_role" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${ALICE_ID}\",\"role\":\"admin\"}" >/dev/null

# Suspend (reversible; preferred over delete). Confirm with the user first.
curl -s -X POST "${OUT}/users.suspend" -H "$H_AUTH" -H "$JSON" -H "$ACC" -d "{\"id\":\"${BOB_ID}\"}" >/dev/null
# Reactivate
curl -s -X POST "${OUT}/users.activate" -H "$H_AUTH" -H "$JSON" -H "$ACC" -d "{\"id\":\"${BOB_ID}\"}" | jq '.data | {id, isSuspended}'
```
Prefer `users.suspend` over `users.delete` — a deleted user can reappear via SSO, and suspension is reversible. Confirm before either.

**Result:** two invited users, a "New Hires" group with collection write access, one user with direct document access, and a demonstrated suspend/activate/role flow.
