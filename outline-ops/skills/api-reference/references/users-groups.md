# Users & Groups

People in the workspace and the groups that bundle them for permissions. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header. Role-changing and lifecycle actions require admin authorization.

## Users

`role` is one of `admin`, `member`, `viewer`, `guest` (the `UserRole` enum).

| Method | Purpose & key fields |
|--------|----------------------|
| `users.invite` | Email-invite people. `{"invites":[{"email","name","role"}], "suppressEmail"?}` → `{sent, users}`. |
| `users.info` | Retrieve a user. `{"id"}`. |
| `users.list` | List/filter users. Pagination + sorting + `{"query"?,"filters"?}` (structured filter, see **Filters** below). The older `{"emails"?[],"filter":"all"|"invited"|"active"|"suspended","role"?}` still work but are **deprecated** and cannot be combined with `filters`. |
| `users.update` | Update name/avatar/language/preferences. `{"name"?(≤255),"avatarUrl"?,"language"?,"preferences"?}` (no `id` → updates the current user). `preferences` is merged — only the fields you send change (currently `sidebarSectionOrder`: ordering of `starred`/`shared`/`collections`). |
| `users.updateEmail` | Start an email change. `{"email"(required),"id"?}` (`id` omitted → the current user; changing someone else's email needs admin). The address is **not** changed immediately: a confirmation link goes to the new address and the change applies only once it is followed. |
| `users.resendInvite` | Re-send the invitation email to a user still in the *invited* state (never signed in). `{"id"}`. |
| `users.update_role` | Change a user's role (admin only). `{"id","role":"admin"|"member"|"viewer"|"guest"}`. |
| `users.suspend` | Prevent sign-in (reversible; suspended users don't count toward hosted billing). `{"id"}`. **Confirm first.** |
| `users.activate` | Re-enable a suspended user. `{"id"}`. |
| `users.delete` | Permanently remove the user object. `{"id"}`. Prefer `users.suspend` — a deleted user can re-appear via SSO. **Confirm first.** |

## Groups

A group is a named set of users that can be granted collection/document access as a unit.

| Method | Purpose & key fields |
|--------|----------------------|
| `groups.info` | Retrieve a group (name + member count). `{"id"}`. |
| `groups.list` | List groups. Pagination + sorting + `{"userId"?,"externalId"?,"query"?}` → `{groups, groupMemberships}` (membership preview). |
| `groups.create` | `{"name"(required, ≤255),"description"?(≤2000, nullable)}`. |
| `groups.update` | Rename. `{"id","name"}`. |
| `groups.delete` | Delete the group; members lose any access granted through it — irreversible. `{"id"}`. **Confirm first.** |
| `groups.memberships` | List/filter members of a group. `{"id","query"?}` + pagination → `{users, groupMemberships}`. |
| `groups.add_user` | Add a user to the group. `{"id","userId"}` → `{users, groups, groupMemberships}`. |
| `groups.update_user` | Change a member's role inside the group. `{"id","userId","permission":"member"|"admin"}` (all required) — promote to group admin or demote back to member. |
| `groups.remove_user` | Remove a user from the group. `{"id","userId"}`. |

## Direct and group document shares (the current user's view)

What has been shared **with the authenticated user** — useful for "what can I see because someone shared it with me".

| Method | Purpose & key fields |
|--------|----------------------|
| `userMemberships.list` | Documents shared **directly** with the current user, with the membership records. Pagination → `{memberships, documents}`. |
| `userMemberships.update` | Reorder a shared document in the user's sidebar. `{"id"(membership id),"index"(required, fractional index)}`. |
| `groupMemberships.list` | Documents shared with the **groups the current user belongs to**, with the group-membership records. Pagination + `{"groupId"?}` to restrict to one group → `{groupMemberships, groups, documents}`. |

(To manage who a document is shared *with*, use `documents.add_user` / `documents.add_group` and the `*.memberships` listings → `documents.md`.)

## Filters (`users.list`)

`filters` is an array of nodes, ANDed together. A leaf is `{"field","operator","value"}`; a group is `{"operator":"AND"|"OR","filters":[…]}` and may nest.

- `field`: `id`, `name`, `email`, `role`, `createdAt`, `updatedAt`, `lastActiveAt`, `suspendedAt` (`id` and `role` accept only `eq`, `neq`, `in`, `notIn`).
- `operator`: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `contains`, `startsWith`, `endsWith`, `containsStrict`, `startsWithStrict`, `endsWithStrict`, `in`, `notIn`, `isNull`, `isNotNull`.
- `value`: string, number, boolean or an array (for `in`/`notIn`); date fields take an ISO 8601 date **or** an ISO 8601 duration (relative to now); `role` takes a `UserRole` value; omit for `isNull`/`isNotNull`.

```json
{"filters":[{"field":"role","operator":"eq","value":"member"},{"field":"suspendedAt","operator":"isNull"}]}
```

## Notes

- To grant a group access to content, create the group here, then use `collections.add_group` / `documents.add_group` (→ `collections.md`, `documents.md`).
- Notification preferences for the current user (`users.notificationsSubscribe`/`Unsubscribe`) live in `comments-stars-views.md`.
- `users.update` with no `id` is the "update myself" path; changing another user (or a role) requires admin rights and will `403` otherwise.
- For exact schemas, search `operationId: users…` / `groups…` in `outline-openapi.yml`.
