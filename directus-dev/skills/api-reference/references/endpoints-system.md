# System API — Detailed Reference

## Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Login (email + password → JWT) |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout / invalidate session |
| POST | `/auth/password/request` | Request password reset email |
| POST | `/auth/password/reset` | Reset password with token |
| GET | `/auth/oauth` | List OAuth providers |
| GET | `/auth/oauth/{provider}` | Initiate OAuth flow |

### Login

```bash
curl -X POST "${DIRECTUS_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

Response:
```json
{
  "data": {
    "access_token": "eyJ...",
    "expires": 900000,
    "refresh_token": "abc..."
  }
}
```

### Login Modes

```bash
# JSON mode (default) — tokens in response body
-d '{"email": "...", "password": "...", "mode": "json"}'

# Cookie mode — tokens in httpOnly cookies
-d '{"email": "...", "password": "...", "mode": "cookie"}'

# Session mode — server-side session
-d '{"email": "...", "password": "...", "mode": "session"}'
```

## Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | List users |
| POST | `/users` | Create user |
| GET | `/users/{id}` | Get user |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |
| GET | `/users/me` | Get current user |
| PATCH | `/users/me` | Update current user |

### Create User

```bash
curl -X POST "${DIRECTUS_URL}/users" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "secure-password",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "role-uuid",
    "status": "active"
  }'
```

### User Status Values

`active`, `invited`, `draft`, `suspended`, `deleted`

## Roles

| Method | Path | Description |
|--------|------|-------------|
| GET | `/roles` | List roles |
| POST | `/roles` | Create role |
| GET | `/roles/{id}` | Get role |
| PATCH | `/roles/{id}` | Update role |
| DELETE | `/roles/{id}` | Delete role |

### Create Role

```bash
curl -X POST "${DIRECTUS_URL}/roles" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Content Editor",
    "icon": "edit",
    "admin_access": false,
    "app_access": true
  }'
```

## Permissions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/permissions` | List permissions |
| POST | `/permissions` | Create permission |
| GET | `/permissions/{id}` | Get permission |
| PATCH | `/permissions/{id}` | Update permission |
| DELETE | `/permissions/{id}` | Delete permission |

### Create Permission

```bash
curl -X POST "${DIRECTUS_URL}/permissions" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "role-uuid",
    "collection": "posts",
    "action": "read",
    "fields": ["*"],
    "permissions": {},
    "validation": {}
  }'
```

### Permission Actions

`create`, `read`, `update`, `delete`

## Activity & Revisions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/activity` | List activity log (read-only) |
| GET | `/activity/{id}` | Get activity entry |
| GET | `/revisions` | List revisions |
| GET | `/revisions/{id}` | Get revision with delta |

### List Recent Activity

```bash
curl "${DIRECTUS_URL}/activity?sort=-timestamp&limit=25&filter[action][_eq]=update" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

## Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings` | Get global settings |
| PATCH | `/settings` | Update settings |

### Key Settings Fields

`project_name`, `project_color`, `project_logo`, `public_foreground`, `public_background`, `auth_login_attempts`, `auth_password_policy`, `storage_asset_transform`, `custom_css`, `default_language`, `basemaps`

## Notifications

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notifications` | List notifications |
| POST | `/notifications` | Create notification |
| PATCH | `/notifications/{id}` | Mark as read |
| DELETE | `/notifications/{id}` | Delete notification |

## Flows (REST API)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/flows` | List flows |
| POST | `/flows` | Create flow |
| GET | `/flows/{id}` | Get flow |
| PATCH | `/flows/{id}` | Update flow |
| DELETE | `/flows/{id}` | Delete flow |
| POST | `/flows/trigger/{id}` | Trigger a flow |

## Server

```bash
# Health check
curl "${DIRECTUS_URL}/server/ping"
# Returns: "pong"

# Detailed health
curl "${DIRECTUS_URL}/server/health" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"

# Server info
curl "${DIRECTUS_URL}/server/info" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

## Content Versions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/versions` | List versions |
| POST | `/versions` | Create version |
| GET | `/versions/{id}` | Get version |
| PATCH | `/versions/{id}` | Update version |
| DELETE | `/versions/{id}` | Delete version |
| POST | `/versions/{id}/promote` | Promote version to main |
