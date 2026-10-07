# Scenario: Onboard an Employee

Goal: `new.person@example.com` gets a Vaultwarden account, joins the organization as a User and can read the "Infra" collection.

Needs: admin token (step 1, only if signups are closed), an Admin/Owner of the org with a personal API key and master password (steps 2–4).

## 1. Check whether the account already exists — admin panel

Skip if `SIGNUPS_ALLOWED=true` or `INVITATIONS_ALLOWED=true` (an org invite then lets the person register).

```bash
JAR="$(mktemp)"
read -r -s -p "admin token: " VW_ADMIN_TOKEN && echo
printf '%s' "$VW_ADMIN_TOKEN" | curl -sS -c "$JAR" -o /dev/null -w '%{http_code}\n' --data-urlencode 'token@-' "$VW_URL/admin"
unset VW_ADMIN_TOKEN
curl -fsS -b "$JAR" "$VW_URL/admin/users/by-mail/new.person@example.com" -o /dev/null -w '%{http_code}\n' || true   # 404 = no account yet
```

## 2. Find the org and the collection — bw

```bash
bw sync
bw list organizations | jq -r '.[] | [.id, .name] | @tsv'
bw list org-collections --organizationid <org-uuid> | jq -r '.[] | [.id, .name] | @tsv'
```

Collection names are encrypted on the server, so look them up with `bw`, not with the raw API.

## 3. Invite into the org with collection access — client API

```bash
VW_TOKEN="$(printf '%s' "$BW_CLIENTSECRET" | curl -fsS "$VW_URL/identity/connect/token" \
  --data-urlencode grant_type=client_credentials --data-urlencode scope=api \
  --data-urlencode "client_id=$BW_CLIENTID" --data-urlencode 'client_secret@-' \
  --data-urlencode device_type=14 --data-urlencode "device_identifier=$VW_DEVICE_ID" \
  --data-urlencode device_name=vw-onboarding | jq -r .access_token)"

jq -n --arg col "<infra-collection-id>" '{
  emails: ["new.person@example.com"], type: 2, groups: [],
  collections: [{id: $col, readOnly: true, hidePasswords: false, manage: false}],
  permissions: {}
}' | curl -fsS -X POST "$VW_URL/api/organizations/<org-uuid>/users/invite" \
  -H "Authorization: Bearer $VW_TOKEN" -H 'Content-Type: application/json' -d @-
```

Check: the member list shows the email with `status` `0` (Invited).

```bash
curl -fsS -H "Authorization: Bearer $VW_TOKEN" "$VW_URL/api/organizations/<org-uuid>/users" \
  | jq -r '.data[] | select(.email == "new.person@example.com") | [.id, .status, .type] | @tsv'
```

No SMTP? The invitation is still recorded; tell the person to register at `$VW_URL` with exactly that email.

## 4. Confirm after they accept — bw

The person registers and accepts → `status` becomes `1` (Accepted). Confirmation hands them the organization key and needs client crypto:

```bash
bw list org-members --organizationid <org-uuid> | jq -r '.[] | select(.status == 1) | [.id, .email] | @tsv'
bw confirm org-member <member-id> --organizationid <org-uuid>
```

Check: `status` `2` (Confirmed). The person now sees the Infra collection after a sync.

## 5. Recommend to the person

- enable 2FA (an org policy `0` TwoFactorAuthentication can enforce it);
- create their own personal API key only if they automate.

Clean up: `rm -f "$JAR"; unset VW_TOKEN`.
