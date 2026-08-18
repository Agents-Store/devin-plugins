# Roles, Schemes & Groups

Access control: RBAC roles and their permissions, permission schemes (per-team/channel role overrides), and groups (custom + LDAP/SAML synced). Mostly System-Admin scoped. Base `${MATTERMOST_API_URL%/}/api/v4`.

## Roles

A role is a named set of permissions (e.g. `system_admin`, `team_admin`, `channel_user`). You can't create system roles, but you can patch the permission list of existing ones.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/roles` | List all roles. |
| GET | `/roles/{role_id}` | Get a role by id. |
| GET | `/roles/name/{role_name}` | Get a role by name (e.g. `channel_admin`). |
| PUT | `/roles/{role_id}/patch` | Change a role's permissions. Body `{"permissions":["create_post","add_reaction",...]}`. |
| POST | `/roles/names` | Bulk get roles by name. Body `["team_user","channel_user"]`. |

> Assign system roles to a user with `PUT /users/{user_id}/roles` (see `users.md`); team/channel roles with the membership `*/roles` endpoints (see `teams.md`, `channels.md`).

## Schemes (permission schemes)

A scheme bundles role overrides you can attach to teams or channels for custom permission models (Enterprise).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/schemes` | List schemes. Query `scope` (`team`/`channel`), `page`, `per_page`. |
| POST | `/schemes` | Create. Body `{"name","scope":"team","description"?}`. |
| GET | `/schemes/{scheme_id}` | Get one. |
| PUT | `/schemes/{scheme_id}/patch` | Update name/description. |
| DELETE | `/schemes/{scheme_id}` | Delete. |
| GET | `/schemes/{scheme_id}/teams` | Teams using the scheme. |
| GET | `/schemes/{scheme_id}/channels` | Channels using the scheme. |

> Attach a scheme with `PUT /teams/{team_id}/scheme` or `PUT /channels/{channel_id}/scheme`.

## Groups

Two kinds: **custom** groups you create via API, and **LDAP/SAML** groups synced from your directory. Groups can be linked to teams/channels so membership auto-syncs.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/groups` | List groups. Query `filter_allow_reference`, `q`, `page`, `per_page`, `since`. |
| POST | `/groups` | Create a custom group. Body `{"name","display_name","allow_reference"?}`. |
| GET | `/groups/{group_id}` | Get one. |
| PUT | `/groups/{group_id}/patch` | Update. |
| DELETE | `/groups/{group_id}` | Delete a custom group. |
| GET | `/groups/{group_id}/members` | List members. |
| POST | `/groups/{group_id}/members` | Add members. Body `{"user_ids":[]}`. |
| DELETE | `/groups/{group_id}/members` | Remove members. Body `{"user_ids":[]}`. |
| GET | `/groups/{group_id}/stats` | Member count. |

### Linking groups to teams / channels

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/groups/{group_id}/teams/{team_id}/link` | Link a group to a team (auto-add members). |
| DELETE | `/groups/{group_id}/teams/{team_id}/link` | Unlink. |
| POST | `/groups/{group_id}/channels/{channel_id}/link` | Link a group to a channel. |
| DELETE | `/groups/{group_id}/channels/{channel_id}/link` | Unlink. |
| GET | `/teams/{team_id}/groups` | Groups linked to a team. |
| GET | `/channels/{channel_id}/groups` | Groups linked to a channel. |

### LDAP groups

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/ldap/groups` | List LDAP groups discovered by sync. |
| POST | `/ldap/groups/{remote_id}/link` | Make an LDAP group available as a Mattermost group. |
| DELETE | `/ldap/groups/{remote_id}/link` | Unlink. |

## Permissions reference

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/permissions/ancillary` | Return ancillary (System-Console subsection) permissions for given base permissions. |
