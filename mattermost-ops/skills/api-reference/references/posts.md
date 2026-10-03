# Posts

Messages and threads. A reply sets `root_id` to the thread's root post id. Base `${MATTERMOST_API_URL%/}/api/v4`.

> **v12.0 (October 2026) — identity props are stripped.** On a post sent with a user session or PAT, the server drops `from_webhook`, `from_bot`, `from_oauth_app`, `from_plugin`, `override_username`, `override_icon_url`, `override_icon_emoji` and `webhook_display_name` from `props` — **silently**: the post is created, no error comes back, and the author is the authenticating user. Do not use `props` to fake a sender. To post under a custom name/icon use an incoming webhook (`username`/`icon_url`, when overrides are enabled in the System Console), a slash-command response, or a bot account (see `integrations.md`). Other `props` (for example attachments) are unaffected. On v11 the old behaviour still works but is going away.

## CRUD

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/posts` | Create a post. Body `{"channel_id","message","root_id"?,"file_ids"?,"props"?}`. `root_id` makes it a thread reply. `props` cannot set sender identity from v12.0 (see the note above). |
| GET | `/posts/{post_id}` | Get one post. |
| PUT | `/posts/{post_id}` | Full update. |
| PUT | `/posts/{post_id}/patch` | Partial update — `message`, `file_ids`, `props` (preferred; same v12.0 identity-props rule). |
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

> **Removed:** the bulk call `POST /posts/ids/reactions` ("get reactions for many posts") is gone — dropped in v11.11 and backported to the 11.9.2, 11.10.2 and 11.7.11 patch releases. Read reactions per post with `GET /posts/{post_id}/reactions` (or from the `metadata.reactions` of a fetched post/thread).

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

## AI helpers (Mattermost Agents plugin, server v11.2+)

Available only where the Agents plugin is installed; any authenticated user may call them.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/posts/rewrite` | Rewrite text with an AI agent. Body `{"agent_id","message","action","custom_prompt"?}`; `action` is `shorten`, `elaborate`, `improve_writing`, `fix_spelling`, `simplify`, `summarize` or `custom` (`custom` needs `custom_prompt`). |
| GET | `/agents` | AI agents the caller may use (get `agent_id` here). |
| GET | `/llmservices` | LLM services the caller may use. |
