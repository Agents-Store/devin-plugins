# Integrations

Webhooks, slash commands, bots, OAuth apps, and interactive dialogs. Most require the relevant "manage" permission (admin or a role granted it). Base `${MATTERMOST_API_URL%/}/api/v4`.

## Incoming webhooks

Post into a channel by POSTing JSON to the hook URL — no auth token needed on the hook URL itself.

This is the supported way to post under a **custom name and icon**: the hook payload may carry `username`, `icon_url` / `icon_emoji` (and `channel`) when the System Console allows overrides (`ServiceSettings.EnablePostUsernameOverride`, `EnablePostIconOverride`). From **v12.0** it is the *only* way for scripts: a plain `POST /posts` made with a user session or PAT can no longer set `override_username`, `override_icon_url`, `override_icon_emoji`, `webhook_display_name` or any `from_*` prop — the server drops them silently (post still created, author = the authenticating user). Slash commands keep the same override right, and bots post as the bot account.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/hooks/incoming` | Create. Body `{"channel_id","display_name"?,"description"?,"username"?,"icon_url"?}` (`username`/`icon_url` are the hook's default sender identity; honoured only while overrides are enabled). Returns `{id,...}` → hook URL is `${MATTERMOST_API_URL}/hooks/{id}`. |
| GET | `/hooks/incoming` | List. Query `page`, `per_page`, `team_id`. |
| GET | `/hooks/incoming/{hook_id}` | Get one. |
| PUT | `/hooks/incoming/{hook_id}` | Update. |
| DELETE | `/hooks/incoming/{hook_id}` | Delete. |

```bash
# Fire an incoming webhook (note: /hooks/<id>, not /api/v4/...)
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"text":"Deploy finished :rocket:","channel":"alerts","username":"deploy-bot","icon_emoji":":rocket:"}' \
  "${MATTERMOST_API_URL%/}/hooks/${HOOK_ID}"
```

## Outgoing webhooks

Trigger an external URL when a trigger word appears in a channel.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/hooks/outgoing` | Create. Body `{"team_id","channel_id"?,"trigger_words":[],"callback_urls":[],"display_name"}`. |
| GET | `/hooks/outgoing` | List. Query `team_id`, `channel_id`, `page`, `per_page`. |
| GET/PUT/DELETE | `/hooks/outgoing/{hook_id}` | Get / update / delete. |
| POST | `/hooks/outgoing/{hook_id}/regen_token` | Regenerate the token. |

## Slash commands

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/commands` | Create. Body `{"team_id","trigger","url","method":"P"|"G","display_name"?}`. |
| GET | `/commands` | List for a team. Query `team_id`, `custom_only`. |
| PUT | `/commands/{command_id}` | Update. |
| DELETE | `/commands/{command_id}` | Delete. |
| POST | `/commands/{command_id}/regen_token` | Regenerate token. |
| PUT | `/commands/{command_id}/move` | Move to another team. |
| POST | `/commands/execute` | Run a command. Body `{"channel_id","command":"/away"}`. |
| GET | `/teams/{team_id}/commands/autocomplete` | Autocomplete data. |

## Bots

A bot is a non-interactive account that posts as itself (the supported replacement for forged sender props); pair it with a PAT (see `auth-sessions.md`) for automation. Bot-account PATs are exempt from the admin's maximum-lifetime policy.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/bots` | Create. Body `{"username","display_name"?,"description"?}`. |
| GET | `/bots` | List. Query `page`, `per_page`, `include_deleted`, `only_orphaned`. |
| GET | `/bots/{bot_user_id}` | Get one. |
| PUT | `/bots/{bot_user_id}` | Update. |
| POST | `/bots/{bot_user_id}/disable` / `/enable` | Disable / enable. |
| POST | `/bots/{bot_user_id}/assign/{user_id}` | Reassign ownership. |
| POST | `/bots/{bot_user_id}/convert_to_user` | Convert to a normal user. |

## OAuth apps

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/oauth/apps` | Register. Body `{"name","callback_urls":[],"homepage","is_trusted"?}`. |
| GET | `/oauth/apps` | List. Query `page`, `per_page`. |
| GET/PUT/DELETE | `/oauth/apps/{app_id}` | Get / update / delete. |
| POST | `/oauth/apps/{app_id}/regen_secret` | Regenerate client secret. |
| GET | `/oauth/apps/{app_id}/info` | Public info (no secret). |
| POST | `/oauth/apps/register` | **v11.2+.** Dynamic Client Registration (RFC 7591) for external OAuth clients — **no authentication required**, so it is a deliberate admin decision. Body `{"redirect_uris":[],"client_name","client_uri"?}`. Needs `ServiceSettings.EnableOAuthServiceProvider` **and** `EnableDynamicClientRegistration` (default off); redirect URIs are checked against `DCRRedirectURIAllowlist` (matched per URL component since v11.9). |
| GET | `/.well-known/oauth-authorization-server` | **v11.2+.** OAuth authorization-server metadata for clients — served at the server root, not under `/api/v4`; returns `501` while the OAuth service provider is disabled. |

PKCE: `/oauth/authorize` (the user-facing authorization URL, not under `/api/v4`) accepts `code_challenge` and `code_challenge_method` (v11.2+), so public clients — desktop and CLI tools — can use the authorization-code flow without a client secret.

## Interactive dialogs

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/actions/dialogs/open` | Open a dialog. Body `{"trigger_id","url","dialog":{...}}`. |
| POST | `/actions/dialogs/submit` | Submit dialog values. |
