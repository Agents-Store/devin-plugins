# Auth & Sessions

Login, sessions, MFA, personal access tokens. All paths are under `${MATTERMOST_API_URL%/}/api/v4`. See `setup` for the Token-header login flow and conventions.

## Login / logout

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users/login` | Log in. Body `{"login_id","password","token"?}` (`token` = MFA code). **Session token returned in the `Token` response header**, body = user object. |
| POST | `/users/logout` | End the current session (revokes the token). |
| POST | `/users/login/switch` | Switch a user's login method (email↔LDAP↔SAML↔OAuth). Admin/self. |

```bash
# Capture the token from the header (the #1 gotcha)
MATTERMOST_TOKEN=$(curl -si -X POST "${MATTERMOST_API_URL%/}/api/v4/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"login_id\":\"${MATTERMOST_ADMIN_USERNAME}\",\"password\":\"${MATTERMOST_ADMIN_PASSWORD}\"}" \
  | awk 'tolower($1)=="token:"{print $2}' | tr -d '\r'); export MATTERMOST_TOKEN
```

## Sessions

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/{user_id}/sessions` | List a user's active sessions (`user_id` may be `me`). |
| POST | `/users/{user_id}/sessions/revoke` | Revoke one session. Body `{"session_id"}`. |
| POST | `/users/{user_id}/sessions/revoke/all` | Revoke all of a user's sessions. |
| POST | `/users/sessions/revoke/all` | (Admin) Revoke all sessions for all users. |
| PUT | `/users/sessions/device` | Attach a mobile device id to the session. |

## Multi-factor authentication (MFA)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users/{user_id}/mfa` | Enable/disable MFA. Body `{"activate":true,"code":"<totp>"}`. |
| POST | `/users/{user_id}/mfa/generate` | Generate a new MFA secret + QR code. |
| POST | `/users/mfa` | Check a user's MFA requirement by `login_id`. |

## Personal access tokens (PAT)

Tokens for unattended integrations — used identically to a session token (`Authorization: Bearer <pat>`). A system admin must enable PATs in the System Console first (`ServiceSettings.EnableUserAccessTokens`). **Since v11.9 a PAT can expire**: pass `expires_at` (Unix **milliseconds**) when creating it; omitted or `0` = non-expiring (every PAT created before v11.9 is). An expired PAT is rejected with HTTP `401`.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users/{user_id}/tokens` | Create a PAT. Body `{"description","expires_at"?}` (`expires_at` in v11.9+, Unix ms). Response includes the one-time `token` value. Needs `create_user_access_token` (plus `edit_other_users` for someone else). |
| GET | `/users/{user_id}/tokens` | List a user's PAT metadata (not the secret): `id`, `description`, `is_active`, `expires_at` (Unix ms; `0` = no expiry). |
| GET | `/users/tokens` | (Admin, `manage_system`) Page through all PATs on the server. |
| GET | `/users/tokens/{token_id}` | Get one PAT's metadata. |
| POST | `/users/tokens/rotate` | **v11.10+.** Rotate a PAT: body `{"token_id","expires_at"?}`; returns the new secret (shown once) and **invalidates the old secret and its sessions immediately**. Needs `create_user_access_token`; rotating someone else's token also needs `edit_other_users`, and a system admin's token also `manage_system`; OAuth sessions cannot call it; a **disabled** token cannot be rotated (`400` — enable it first). |
| POST | `/users/tokens/revoke` | Revoke a PAT. Body `{"token_id"}`. |
| POST | `/users/tokens/disable` / `/users/tokens/enable` | Disable / re-enable a PAT. Body `{"token_id"}`. |
| POST | `/users/tokens/search` | Search PATs (admin). |
| GET | `/users/tokens/non_compliant/count` | **v11.10+.** (`manage_system`) Count active PATs that break the admin's maximum-lifetime policy (never expire, or expire beyond the cap). Returns `{"count":n}`; `0` when no policy is set. |
| POST | `/users/tokens/non_compliant/revoke` | **v11.10+.** (`manage_system`) **Irreversibly** delete every non-compliant PAT and its sessions; returns `{"count":n}`; `400` when no policy is set. Always run the `count` call first and confirm with the user. |

```bash
# PAT that expires in 90 days (Unix milliseconds)
EXPIRES_AT=$(( ($(date +%s) + 90*86400) * 1000 ))
curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"description\":\"ci\",\"expires_at\":${EXPIRES_AT}}" \
  "${MATTERMOST_API_URL%/}/api/v4/users/me/tokens" | jq '{id, token}'

# Rotate before it lapses (old secret stops working at once)
curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"token_id\":\"${TOKEN_ID}\",\"expires_at\":${EXPIRES_AT}}" \
  "${MATTERMOST_API_URL%/}/api/v4/users/tokens/rotate" | jq '{id, token}'
```

Admin policy and notifications (v11.9 / v11.10 changelog):

- `ServiceSettings.MaximumPersonalAccessTokenLifetimeDays` — `0` (default) imposes no policy; non-zero means a **new** PAT must expire within that many days. Bot-account tokens are exempt; existing tokens are not touched until an admin runs the non-compliant revoke above (also in System Console → Integrations → Integration Management).
- The server reaps expired PATs hourly (job `cleanup_expired_access_tokens`). From v11.10 the owner gets a system-bot direct message 7, 3 and 1 days before expiry and when an expired token is removed. Admins can run the notifier on demand through the jobs API: `POST /jobs` with `{"type":"notify_expiring_access_tokens"}` (the changelog calls it the `pat_expiry_notify` job, but that string is **not** the job type and returns `400 incorrect_job_type`).
- `mmctl user token generate` accepts `--expires-in` (for example `90d`).

## Terms of service

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/terms_of_service` | Get the latest custom terms of service. |
| POST | `/terms_of_service` | (Admin) Create a new terms-of-service text. |
| GET | `/users/{user_id}/terms_of_service` | Get a user's latest acceptance. |
| POST | `/users/{user_id}/terms_of_service` | Record acceptance/decline. Body `{"serviceTermsId","accepted"}`. |
