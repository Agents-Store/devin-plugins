# Jira Users & Groups

People, group membership, the current user, and avatars. Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. **Jira identifies users by `accountId`** (GDPR) — never username/email in request bodies.

## User search (resolve a person → accountId)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /user/search?query=` | Find users by name/email (`findUsers`). `query` matches display name or email. Returns `[{accountId, displayName, emailAddress?}]`. |
| `GET /user/assignable/search?project=&query=` | Users assignable on a project (`findAssignableUsers`). |
| `GET /user/permission/search?permissions=&query=` | Users with given permissions (`findUsersWithAllPermissions`). |
| `GET /user/picker?query=` | Picker suggestions (`findUsersForPicker`). |

## Users

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /user?accountId=` | Get a user (`getUser`). `?expand=groups,applicationRoles`. |
| `GET /users/search?startAt=&maxResults=` | List all users (`getAllUsers`). |
| `GET /user/bulk?accountId=…&accountId=…` | Bulk fetch users (`bulkGetUsers`). |
| `GET /user/groups?accountId=` | A user's groups (`getUserGroups`). |
| `GET /user/email?accountId=` | A user's email, if visible (`getUserEmail`). |
| `POST /user` · `DELETE /user?accountId=` | Create / delete a managed user (`createUser`, `removeUser`) — admin, often managed by the org directory instead. **Confirm first.** |
| `GET/PUT/DELETE /user/columns` | The user's default issue-navigator columns. |

## Groups

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /groups/picker?query=` | Find groups (`findGroups`). |
| `GET /group/bulk` | Bulk get groups by name/id (`bulkGetGroups`). |
| `GET /group/member?groupname=|groupId=` | Members of a group (`getUsersFromGroup`), paginated. |
| `POST /group` · `DELETE /group?groupname=` | Create / remove a group (`createGroup`, `removeGroup`). |
| `POST /group/user` · `DELETE /group/user` | Add / remove a user (`addUserToGroup`, `removeUserFromGroup`). Body `{"accountId":"…"}` (+ `?groupId=`). |

## Myself & preferences

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /myself` | The current (token) user (`getCurrentUser`) — confirms auth, returns your `accountId`. |
| `GET/PUT/DELETE /mypreferences` | Get / set / clear a user preference (`getPreference`, `setPreference`). |
| `GET/PUT /mypreferences/locale` | Get / set locale. |

## Avatars

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /avatar/{type}/system` | System avatars for a type (`getAllSystemAvatars`). |
| `GET /universal_avatar/type/{type}/owner/{entityId}` · `POST …` | List / upload avatars for a project/issue-type/user. |

## Notes
- **Always resolve to `accountId` first** with `GET /user/search`, then use `{"accountId":"…"}` in assignee/reporter/actor bodies.
- Email visibility depends on the org's privacy settings — `emailAddress` may be absent.
- Newer Cloud sites manage users via the org admin / SCIM, so `POST/DELETE /user` may be restricted.
- For exact schemas: `grep -n '"operationId": "findUsers"' ../jira-openapi-v3.json`.
