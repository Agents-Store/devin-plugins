# Teams

Teams are the top-level workspaces that contain channels. Base `${MATTERMOST_API_URL%/}/api/v4`. A team `id` is 26 chars; `name` is the URL slug.

## CRUD & lookup

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/teams` | Create a team. Body `{"name","display_name","type":"O"}` — `O`=open (anyone joins), `I`=invite-only. |
| GET | `/teams` | List teams. Query `page`, `per_page`, `include_total_count`, `exclude_policy_constrained`. |
| GET | `/teams/{team_id}` | Get one team. |
| PUT | `/teams/{team_id}` | Full update. |
| PUT | `/teams/{team_id}/patch` | Partial update (preferred) — `display_name`, `description`, `allow_open_invite`, etc. |
| DELETE | `/teams/{team_id}` | Soft-delete (archive). Add `?permanent=true` to hard-delete. |
| GET | `/teams/name/{name}` | Look up by slug. |
| PUT | `/teams/{team_id}/privacy` | Change `O`↔`I`. Body `{"privacy":"I"}`. |
| POST | `/teams/{team_id}/restore` | Restore an archived team. |
| GET | `/teams/{team_id}/exists` | Check if a team name is taken (use `/teams/name/{name}/exists`). |
| POST | `/teams/search` | Search teams. Body `{"term"}`. |

## Members

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/teams/{team_id}/members` | List members. Query `page`, `per_page`. |
| POST | `/teams/{team_id}/members` | Add a member. Body `{"team_id","user_id"}`. |
| POST | `/teams/{team_id}/members/batch` | Add many members at once (array). |
| GET | `/teams/{team_id}/members/{user_id}` | Get one membership. |
| DELETE | `/teams/{team_id}/members/{user_id}` | Remove a member. |
| POST | `/teams/members/ids` | Get memberships for listed team IDs (current user). |
| GET | `/users/{user_id}/teams` | Teams a user belongs to. |
| GET | `/users/{user_id}/teams/members` | A user's memberships. |
| GET | `/users/{user_id}/teams/unread` | Unread counts per team. |
| PUT | `/teams/{team_id}/members/{user_id}/roles` | Set team roles. Body `{"roles":"team_user team_admin"}`. |
| PUT | `/teams/{team_id}/members/{user_id}/schemeRoles` | Set scheme-based admin/user flags. |

## Invites

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/teams/{team_id}/invite/email` | Email-invite members. Body = array of emails. |
| POST | `/teams/{team_id}/invite-guests/email` | Invite guests with channel scope. Body `{"emails":[],"channels":[],"message"?}`. |
| GET | `/teams/{team_id}/invite/{invite_id}` | Get invite info from an invite id. |
| POST | `/teams/{team_id}/regenerate_invite_id` | Rotate the open-invite id. |
| POST | `/teams/members/invite` | Join a team via invite id (`?invite_id=`). |

## Stats, icon, scheme, import

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/teams/{team_id}/stats` | Member + active-member counts. |
| GET | `/teams/{team_id}/image` | Get team icon. |
| POST | `/teams/{team_id}/image` | Set icon — multipart `-F "image=@icon.png"`. |
| DELETE | `/teams/{team_id}/image` | Remove icon. |
| PUT | `/teams/{team_id}/scheme` | Assign a permission scheme. Body `{"scheme_id"}`. |
| POST | `/teams/{team_id}/import` | Import a team archive (Slack export) — multipart. |
