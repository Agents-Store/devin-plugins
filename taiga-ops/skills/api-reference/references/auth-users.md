# Auth, Users & Account — API Reference

All paths are under `${TAIGA_API_URL%/}/api/v1`. Authenticated calls send `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`. See `setup` for the login flow.

## Auth

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| POST | `/auth` | Normal login (username/password → token) | `type:"normal"`, `username`, `password` |
| POST | `/auth` | Login via GitHub | `type:"github"`, `code` |
| POST | `/auth/register` | Public self-registration | `type:"public"`, `username`, `password`, `email`, `full_name`, `accepted_terms` |
| POST | `/auth/register` | Register via invitation | `type:"private"`, `existing`, `token`, `username`, `email`, `full_name`, `password` |
| POST | `/auth/refresh` | Exchange a refresh token for a new auth token | `refresh` |

```bash
# Normal login
curl -s -X POST "${TAIGA_API_URL%/}/api/v1/auth" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"normal\",\"username\":\"${TAIGA_ADMIN_USERNAME}\",\"password\":\"${TAIGA_ADMIN_PASSWORD}\"}" | jq '{auth_token, refresh, id, username}'
```

## Applications & Application tokens

Application tokens authenticate external apps. They are sent as `Authorization: Application <token>` (not `Bearer`).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/applications/{applicationId}` | Get application metadata |
| GET | `/applications/{applicationId}/token` | Get the current user's token for an application |
| GET | `/application-tokens` | List the authenticated user's application tokens |
| GET | `/application-tokens/{id}` | Get one application token |
| DELETE | `/application-tokens/{id}` | Revoke an application token |
| POST | `/application-tokens/authorize` | Request an auth code. Body: `application` (UUID), `state` (CSRF string) → returns `auth_code` |
| POST | `/application-tokens/validate` | Validate the code. Body: `application`, `auth_code`, `state` → returns `cyphered_token` (JWE, A128KW + A256GCM — decipher with the application secret) |

## Users

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/users` | List users (filter `?project=<id>` for project members) | — |
| GET | `/users/me` | Current authenticated user | — |
| GET | `/users/{userId}` | Get a user | — |
| PATCH | `/users/{userId}` | Edit profile (partial) | `username`, `full_name`, `email`, `bio`, `lang`, `theme` |
| PUT | `/users/{userId}` | Replace profile | full object |
| DELETE | `/users/{userId}` | Delete a user | — |
| POST | `/users/cancel` | Cancel (deactivate) own account | `cancel_token` |
| POST | `/users/change_password` | Change password | `current_password`, `new_password` |
| POST | `/users/password_recovery` | Request a reset email | `username` (or email) |
| POST | `/users/change_password_from_recovery` | Reset via recovery token | `token`, `password` |
| POST | `/users/change_avatar` | Upload avatar (multipart) | `avatar` (file) |
| POST | `/users/remove_avatar` | Remove avatar | — |
| POST | `/users/change_email` | Confirm a new email | `email_token` |
| GET | `/users/{userId}/stats` | User statistics | — |
| GET | `/users/{userId}/contacts` | User's contacts | — |
| GET | `/users/{userId}/liked` | Items the user liked (filter `?type=`, `?q=`) | — |
| GET | `/users/{userId}/voted` | Items the user voted | — |
| GET | `/users/{userId}/watched` | Items the user watches | — |

```bash
# Edit your display name
ME=$(curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" "${TAIGA_API_URL%/}/api/v1/users/me")
UID=$(echo "$ME" | jq -r .id)
curl -s -X PATCH -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"full_name":"New Name"}' "${TAIGA_API_URL%/}/api/v1/users/${UID}" | jq '{id, full_name}'
```

## User storage (per-user key/value)

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/user-storage` | List all keys for the user | — |
| POST | `/user-storage` | Create an entry | `key`, `value` |
| GET | `/user-storage/{key}` | Get one entry | — |
| PATCH | `/user-storage/{key}` | Update an entry (partial) | `value` |
| PUT | `/user-storage/{key}` | Replace an entry | `value` |
| DELETE | `/user-storage/{key}` | Delete an entry | — |

## Locales, feedback, contact

| Method | Path | Purpose | Key fields | Auth |
|--------|------|---------|-----------|------|
| GET | `/locales` | List supported locales | — | no |
| POST | `/feedback` | Submit product feedback | `comment`, `full_name?`, `email?` | yes |
| POST | `/contact` | Message a project's admins | `project`, `comment` | yes |
