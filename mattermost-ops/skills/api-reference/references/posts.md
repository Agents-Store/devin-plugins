# Posts

Messages and threads. A reply sets `root_id` to the thread's root post id. Base `${MATTERMOST_API_URL%/}/api/v4`.

## CRUD

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/posts` | Create a post. Body `{"channel_id","message","root_id"?,"file_ids"?,"props"?}`. `root_id` makes it a thread reply. |
| GET | `/posts/{post_id}` | Get one post. |
| PUT | `/posts/{post_id}` | Full update. |
| PUT | `/posts/{post_id}/patch` | Partial update — `message`, `file_ids`, `props` (preferred). |
| DELETE | `/posts/{post_id}` | Delete a post (soft). |
| POST | `/posts/ephemeral` | Send an ephemeral post visible only to one user. Body `{"user_id","post":{"channel_id","message"}}` (admin/bot). |
| POST | `/posts/ids` | Bulk get posts by ids. |

## Reading channel posts & threads

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/channels/{channel_id}/posts` | Posts in a channel. Query `page`, `per_page`, `since`, `before`, `after`. Returns `{order, posts}`. |
| GET | `/posts/{post_id}/thread` | The full thread (root + replies). |
| GET | `/users/{user_id}/channels/{channel_id}/posts/unread` | Posts around the oldest unread. |
| GET | `/users/{user_id}/posts/flagged` | A user's flagged posts. |
| POST | `/users/{user_id}/posts/{post_id}/set_unread` | Mark unread from this post. |

## Pinning

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/posts/{post_id}/pin` | Pin to its channel. |
| POST | `/posts/{post_id}/unpin` | Unpin. |

## Search

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/teams/{team_id}/posts/search` | Search within a team. Body `{"terms","is_or_search"?,"time_zone_offset"?,"page"?,"per_page"?}`. Supports modifiers like `from:`, `in:`, `on:`, `before:`, `after:`. |
| POST | `/posts/search` | Search across all the current user's teams. |

## Reactions

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/reactions` | Add a reaction. Body `{"user_id","post_id","emoji_name"}`. |
| GET | `/posts/{post_id}/reactions` | List a post's reactions. |
| DELETE | `/users/{user_id}/posts/{post_id}/reactions/{emoji_name}` | Remove a reaction. |
| POST | `/posts/ids/reactions` | Bulk get reactions for many posts. |

## Drafts & scheduled posts

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/me/teams/{team_id}/drafts` | List your drafts in a team. |
| POST | `/drafts` | Upsert a draft. Body `{"channel_id","message","root_id"?}`. |
| DELETE | `/users/me/channels/{channel_id}/drafts` | Delete a channel draft. |
| POST | `/posts/schedule` | Create a scheduled post. Body `{"channel_id","message","scheduled_at":<epoch_ms>}`. |
| GET | `/posts/scheduled/team/{team_id}` | List scheduled posts for a team. |
| PUT/DELETE | `/posts/schedule/{scheduled_post_id}` | Update / delete a scheduled post. |

## Acknowledgements & reminders

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/posts/{post_id}/ack` | Acknowledge a post (priority feature). |
| DELETE | `/posts/{post_id}/ack` | Remove acknowledgement. |
| POST | `/users/{user_id}/posts/{post_id}/reminder` | Set a reminder. Body `{"target_time":<epoch>}`. |
