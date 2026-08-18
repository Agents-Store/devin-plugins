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

Long-lived tokens for unattended integrations — used identically to a session token (`Authorization: Bearer <pat>`). A system admin must enable PATs in the System Console first.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users/{user_id}/tokens` | Create a PAT. Body `{"description"}`. Response includes the one-time `token` value. |
| GET | `/users/{user_id}/tokens` | List a user's PAT metadata (not the secret). |
| GET | `/users/tokens/{token_id}` | Get one PAT's metadata. |
| POST | `/users/tokens/revoke` | Revoke a PAT. Body `{"token_id"}`. |
| POST | `/users/tokens/disable` / `/users/tokens/enable` | Disable / re-enable a PAT. Body `{"token_id"}`. |
| POST | `/users/tokens/search` | Search PATs (admin). |

## Terms of service

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/terms_of_service` | Get the latest custom terms of service. |
| POST | `/terms_of_service` | (Admin) Create a new terms-of-service text. |
| GET | `/users/{user_id}/terms_of_service` | Get a user's latest acceptance. |
| POST | `/users/{user_id}/terms_of_service` | Record acceptance/decline. Body `{"serviceTermsId","accepted"}`. |
