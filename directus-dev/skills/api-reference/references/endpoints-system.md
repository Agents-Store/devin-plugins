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
    "role": "<role-uuid>",
    "status": "active"
  }'
```

A user has at most one direct role. Policies can also be attached to the user directly (see [Access](#access-policy-assignments)).

### User Status Values

`active`, `invited`, `draft`, `unverified`, `suspended`, `archived`

Only `active` users can authenticate.

## Access Control Model (Directus 11+)

Permissions are held by **policies**, never by roles. A user's effective permissions are the aggregate of every policy attached to the user directly, to the user's role, and to that role's parent roles. Policies are additive: each one can add access, none can take it away (the one subtractive control is a policy's IP allowlist, which removes the whole policy for non-matching clients).

| Object | Endpoint | System collection | Holds |
|--------|----------|-------------------|-------|
| Policy | `/policies` | `directus_policies` | `admin_access`, `app_access`, `enforce_tfa`, `ip_access`, and its permissions |
| Permission | `/permissions` | `directus_permissions` | One rule for one collection and action, attached to a **policy** |
| Role | `/roles` | `directus_roles` | `name`, `icon`, `description`, `parent`, `children`, `policies`, `users` (organization only) |
| Access | `/access` | `directus_access` | Junction rows that attach a policy to a role or to a user |

The system collection names matter in two places: permission rules that target them (`collection: 'directus_policies'`), and the SDK, which refuses `readItems('directus_policies')` and the other generic item commands on a `directus_*` collection. Use the typed commands instead (`readPolicies()`, `readRoles()`, `readPermissions()`).

Build order: policy, then its permissions, then role, then the access row that attaches the policy, then assign users to the role.

## Policies

| Method | Path | Description |
|--------|------|-------------|
| GET | `/policies` | List policies |
| POST | `/policies` | Create policy |
| GET | `/policies/{id}` | Get policy |
| PATCH | `/policies/{id}` | Update policy |
| DELETE | `/policies/{id}` | Delete policy |

### Create Policy

```bash
curl -X POST "${DIRECTUS_URL}/policies" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Content Editor",
    "icon": "edit",
    "description": "Edit posts in the Data Studio",
    "admin_access": false,
    "app_access": true,
    "enforce_tfa": false,
    "ip_access": null
  }'
```

- `admin_access`: full permissions on everything. Use sparingly.
- `app_access`: may use the Data Studio. Leave `false` for API-only users (they do not count against the seat limit).
- `enforce_tfa`: require two-factor authentication.
- `ip_access`: allowlist of IPs, ranges or CIDR blocks (typed `string[]` in `@directus/sdk` 26). `null` or empty means no restriction. A request from a non-matching IP loses the whole policy, not just the IP-restricted part.

Policies created with `app_access: true` only receive read access to a narrow set of `directus_settings` fields since 12.2.0. Policies created earlier keep reading the whole settings collection, including provider API keys: audit them.

## Roles

| Method | Path | Description |
|--------|------|-------------|
| GET | `/roles` | List roles |
| POST | `/roles` | Create role |
| GET | `/roles/{id}` | Get role |
| PATCH | `/roles/{id}` | Update role |
| DELETE | `/roles/{id}` | Delete role |

A role no longer carries `admin_access`, `app_access`, `enforce_tfa` or `ip_access`. Those fields moved to policies in Directus 11. A role payload that still contains them is not rejected: the role is created and the flags are silently dropped, so it grants nothing. Check the response, not just the status code. A role is an organizational unit: it has `name`, `icon`, `description`, an optional `parent` (children inherit the parent's policies), `children`, `policies` and `users`.

### Create Role

```bash
curl -X POST "${DIRECTUS_URL}/roles" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Content Editor",
    "icon": "edit",
    "description": "Editors of the blog",
    "parent": null
  }'
```

### Access (Policy Assignments)

Attach a policy to a role (or to a user) by creating a row in `directus_access`:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/access` | List policy assignments |
| POST | `/access` | Attach a policy to a role or user |
| PATCH | `/access/{id}` | Update an assignment (for example `sort`) |
| DELETE | `/access/{id}` | Detach a policy |

```bash
# Attach a policy to a role
curl -X POST "${DIRECTUS_URL}/access" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"role": "<role-uuid>", "policy": "<policy-uuid>"}'

# Attach a policy to a single user
curl -X POST "${DIRECTUS_URL}/access" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"user": "<user-uuid>", "policy": "<policy-uuid>"}'
```

Inspect what a role grants:

```bash
curl "${DIRECTUS_URL}/roles/<role-uuid>?fields=name,parent,policies.policy.name,policies.policy.app_access" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

## Permissions

A permission belongs to a **policy**. It is not attached to a role.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/permissions` | List permissions |
| POST | `/permissions` | Create permission |
| GET | `/permissions/{id}` | Get permission |
| PATCH | `/permissions/{id}` | Update permission |
| DELETE | `/permissions/{id}` | Delete permission |
| GET | `/permissions/me` | Effective permissions of the current user (all collections) |
| GET | `/permissions/me/{collection}/{id}` | Permissions of the current user on one item |

### Create Permission

```bash
curl -X POST "${DIRECTUS_URL}/permissions" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "<policy-uuid>",
    "collection": "posts",
    "action": "read",
    "fields": ["*"],
    "permissions": {},
    "validation": {}
  }'
```

`permissions` is the item rule (a filter), `validation` is checked on create and update, `presets` sets defaults, `fields` lists the allowed fields. A payload that carries `role` instead of `policy` fails with `400 FAILED_VALIDATION` (`policy` is required).

### List Permissions of a Policy

```bash
curl "${DIRECTUS_URL}/permissions?filter[policy][_eq]=<policy-uuid>&limit=-1" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

### Check What the Current User Can Do

```bash
curl "${DIRECTUS_URL}/permissions/me" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

The response has one entry per collection with an `access` level per action: `none`, `partial` (some items) or `full`.

### Permission Actions

`create`, `read`, `update`, `delete`, `share`

Since 12.4.0, an update or delete request that selects items by `query` also needs read access to the collection's primary key, and only touches items the policy can read.

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
# Liveness: public, no token, answers once the HTTP server runs
curl "${DIRECTUS_URL}/server/ping"
# Returns: "pong"

# Dependency health: requires a token since Directus 12 (403 without one)
curl "${DIRECTUS_URL}/server/health" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"

# Server info
curl "${DIRECTUS_URL}/server/info" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

Use `/server/ping` for load balancer probes and container health checks. `/server/health` checks the database, Redis, storage and email; admin tokens get every check, other users only the overall `status`. Results are cached for `HEALTHCHECK_CACHE_TTL` (default `5m`).

## Content Versions

Collections with versioning enabled (`meta.versioning: true`) keep drafts in `directus_versions`. The published item is addressed by the reserved key `published` (`main` still works as an alias); `draft` is a reserved global version. Read a version with `?version=<key>` on the item endpoints.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/versions` | List versions |
| POST | `/versions` | Create version |
| GET | `/versions/{id}` | Get version |
| PATCH | `/versions/{id}` | Update version |
| DELETE | `/versions/{id}` | Delete version |
| POST | `/versions/{id}/save` | Save changes into a version |
| GET | `/versions/{id}/compare` | Compare a version with the published item |
| POST | `/versions/{id}/promote` | Publish a version (promote it to the published item) |

In the Studio the published view of a versioned collection is read-only since Directus 12.0.0: edits go to a version (the draft by default), which is then published. Direct API writes to the item itself still work when the policy allows them, so use versions on purpose for review workflows. The keys `published`, `main` and `draft` cannot be used for custom versions. Reading a version key that does not exist (also `draft` before a draft was saved) answers `403 FORBIDDEN`.
