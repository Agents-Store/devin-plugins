# Channels

Channels live inside a team. Types: `O` public (open), `P` private, `D` direct message, `G` group message. Base `${MATTERMOST_API_URL%/}/api/v4`.

## CRUD & lookup

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/channels` | Create a channel. Body `{"team_id","name","display_name","type":"O"}` (`O` or `P`). |
| GET | `/channels` | (Admin) List all channels across teams. Query `page`, `per_page`, `not_associated_to_group`, `exclude_default_channels`. |
| GET | `/channels/{channel_id}` | Get one channel. |
| PUT | `/channels/{channel_id}` | Full update. |
| PUT | `/channels/{channel_id}/patch` | Partial update — `display_name`, `header`, `purpose` (preferred). |
| DELETE | `/channels/{channel_id}` | Archive the channel. `?permanent=true` to hard-delete. |
| GET | `/teams/{team_id}/channels/name/{channel_name}` | Look up by name within a team. |
| GET | `/teams/name/{team_name}/channels/name/{channel_name}` | Look up by team slug + channel name. |
| PUT | `/channels/{channel_id}/privacy` | Convert `O`↔`P`. Body `{"privacy":"P"}`. |
| POST | `/channels/{channel_id}/restore` | Restore an archived channel. |
| POST | `/channels/{channel_id}/move` | Move to another team. Body `{"team_id","force"?}`. |

## Direct & group messages

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/channels/direct` | Create/get a DM channel. Body = `["userId1","userId2"]`. |
| POST | `/channels/group` | Create/get a group message. Body = `["id1","id2","id3"]` (3–8 users). |
| POST | `/channels/group/{channel_id}/convert_to_channel` | Convert a GM into a private channel of a team. |

## Listing within a team

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/teams/{team_id}/channels` | Public channels in a team. Query `page`, `per_page`. |
| GET | `/teams/{team_id}/channels/private` | (Admin) Private channels in a team. |
| GET | `/teams/{team_id}/channels/deleted` | Archived channels. |
| GET | `/users/{user_id}/teams/{team_id}/channels` | Channels a user is a member of. |
| POST | `/teams/{team_id}/channels/search` | Search within a team. Body `{"term"}`. |
| POST | `/channels/search` | (Admin) Search all channels across teams. |

## Members

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/channels/{channel_id}/members` | List members. Query `page`, `per_page`. |
| POST | `/channels/{channel_id}/members` | Add a user. Body `{"user_id"}`. |
| GET | `/channels/{channel_id}/members/{user_id}` | One membership. |
| DELETE | `/channels/{channel_id}/members/{user_id}` | Remove a user. |
| POST | `/channels/{channel_id}/members/ids` | Bulk get members by ids. |
| PUT | `/channels/{channel_id}/members/{user_id}/roles` | Set channel roles. Body `{"roles":"channel_user channel_admin"}`. |
| PUT | `/channels/{channel_id}/members/{user_id}/notify_props` | Per-user notification props. |
| POST | `/channels/members/{user_id}/view` | Mark channel(s) viewed. Body `{"channel_id"}`. |

## Stats, pinned, moderation

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/channels/{channel_id}/stats` | Member count, guest count, pinned count. |
| GET | `/channels/{channel_id}/pinned` | List pinned posts. |
| GET | `/channels/{channel_id}/moderations` | Get moderation settings. |
| PUT | `/channels/{channel_id}/moderations/patch` | Update moderation (e.g. disable posting for members). |

## Bookmarks

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/channels/{channel_id}/bookmarks` | List channel bookmarks. |
| POST | `/channels/{channel_id}/bookmarks` | Create. Body `{"display_name","type":"link"|"file","link_url"?,"file_id"?}`. |
| PATCH | `/channels/{channel_id}/bookmarks/{bookmark_id}` | Update. |
| DELETE | `/channels/{channel_id}/bookmarks/{bookmark_id}` | Delete. |
| POST | `/channels/{channel_id}/bookmarks/{bookmark_id}/sort_order` | Reorder. |

## Sidebar categories (per user, per team)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/{user_id}/teams/{team_id}/channels/categories` | Get categories + order. |
| POST | `/users/{user_id}/teams/{team_id}/channels/categories` | Create a category. |
| PUT | `/users/{user_id}/teams/{team_id}/channels/categories` | Update categories. |
| PUT | `/users/{user_id}/teams/{team_id}/channels/categories/order` | Reorder categories. |
