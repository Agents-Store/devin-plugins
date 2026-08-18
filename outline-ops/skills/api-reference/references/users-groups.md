# Users & Groups

People in the workspace and the groups that bundle them for permissions. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header. Role-changing and lifecycle actions require admin authorization.

## Users

`role` is one of `admin`, `member`, `viewer` (the `UserRole` enum).

| Method | Purpose & key fields |
|--------|----------------------|
| `users.invite` | Email-invite people. `{"invites":[{"email","name","role"}], "suppressEmail"?}` → `{sent, users}`. |
| `users.info` | Retrieve a user. `{"id"}`. |
| `users.list` | List/filter users. Pagination + sorting + `{"query"?,"emails"?[],"filter":"all"|"invited"|"active"|"suspended","role"?}`. |
| `users.update` | Update name/avatar/language. `{"name"?,"avatarUrl"?,"language"?}` (no `id` → updates the current user). |
| `users.update_role` | Change a user's role (admin only). `{"id","role":"admin"|"member"|"viewer"}`. |
| `users.suspend` | Prevent sign-in (reversible; suspended users don't count toward hosted billing). `{"id"}`. **Confirm first.** |
| `users.activate` | Re-enable a suspended user. `{"id"}`. |
| `users.delete` | Permanently remove the user object. `{"id"}`. Prefer `users.suspend` — a deleted user can re-appear via SSO. **Confirm first.** |

## Groups

A group is a named set of users that can be granted collection/document access as a unit.

| Method | Purpose & key fields |
|--------|----------------------|
| `groups.info` | Retrieve a group (name + member count). `{"id"}`. |
| `groups.list` | List groups. Pagination + sorting + `{"userId"?,"externalId"?,"query"?}` → `{groups, groupMemberships}` (membership preview). |
| `groups.create` | `{"name"}`. |
| `groups.update` | Rename. `{"id","name"}`. |
| `groups.delete` | Delete the group; members lose any access granted through it — irreversible. `{"id"}`. **Confirm first.** |
| `groups.memberships` | List/filter members of a group. `{"id","query"?}` + pagination → `{users, groupMemberships}`. |
| `groups.add_user` | Add a user to the group. `{"id","userId"}` → `{users, groups, groupMemberships}`. |
| `groups.remove_user` | Remove a user from the group. `{"id","userId"}`. |

## Notes

- To grant a group access to content, create the group here, then use `collections.add_group` / `documents.add_group` (→ `collections.md`, `documents.md`).
- `users.update` with no `id` is the "update myself" path; changing another user (or a role) requires admin rights and will `403` otherwise.
- For exact schemas, search `operationId: users…` / `groups…` in `outline-openapi.yml`.
