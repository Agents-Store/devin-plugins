# Vaultwarden Config Keys an Operator Touches

Source: the `make_config!` table in `src/config.rs` (Vaultwarden `main`, 2026-10-07). Environment variable = key in UPPER_CASE; `config.json` / `POST /admin/config` key = snake_case. Any key also accepts a `_FILE` suffix in the environment (`SMTP_PASSWORD_FILE=<secret-file>`).

**Precedence:** built-in defaults → `.env` / `ENV_FILE` → process environment → `config.json` (written by the admin page) wins. A value that "does not change" after editing the environment is usually overridden in `config.json`.

**Editable** = can be changed live in the admin page / `POST /admin/config`. **Restart-only** = environment variable plus container restart.

## Editable live

| Key | Default | Notes |
|---|---|---|
| `domain` | `http://localhost` | external URL incl. scheme and optional path; wrong value breaks links, WebAuthn, attachments |
| `signups_allowed` | `true` | open registration |
| `signups_verify` | `false` | require email verification before login |
| `signups_domains_whitelist` | empty | comma list; overrides `signups_allowed=false` for these domains |
| `invitations_allowed` | `true` | org admins may invite non-registered emails |
| `invitation_org_name` | `Vaultwarden` | name in invite mails |
| `org_creation_users` | empty | comma list of emails allowed to create orgs; empty or `all` = everyone, `none` = nobody |
| `emergency_access_allowed` | `true` | |
| `sends_allowed` | `true` | |
| `password_iterations` | `600000` | server-side PBKDF2 rounds on the received hash |
| `password_hints_allowed`, `show_password_hint` | `true`, `false` | |
| `require_device_email` | `false` | fail login if the new-device mail cannot be sent |
| `disable_2fa_remember` | `false` | |
| `trash_auto_delete_days` | unset | purge trash after N days |
| `user_attachment_limit`, `org_attachment_limit` | unset | KB |
| `ip_header` | `X-Real-IP` | must match the reverse proxy, or every client shares one IP for rate limits |
| `ip_header_trusted_proxies` | `local` | with `X-Forwarded-For`, rightmost untrusted hop is the client (1.37.4+) |
| `admin_token` | unset | plain or `$argon2id$...` |
| `admin_session_lifetime` | `20` | minutes |
| `smtp_host`, `smtp_from`, `smtp_from_name`, `smtp_port`, `smtp_security`, `smtp_username`, `smtp_password` | unset | mail disabled until `smtp_host` + `smtp_from` are set; `smtp_security` = `starttls` / `force_tls` / `off` |
| `sso_enabled`, `sso_only`, `sso_authority`, `sso_client_id`, `sso_client_secret`, `sso_pkce`, `sso_signups_allowed`, `sso_signups_match_email` | off | OpenID Connect login |

## Restart-only

| Key | Default | Notes |
|---|---|---|
| `data_folder` | `data` | |
| `database_url` | `sqlite://<data_folder>/db.sqlite3` | `mysql://` and `postgresql://` also supported |
| `enable_db_wal` | `true` | SQLite WAL |
| `database_max_conns` | `10` | |
| `web_vault_enabled` | `true` | |
| `enable_websocket` | `true` | live sync over `/notifications/hub` |
| `push_enabled`, `push_installation_id`, `push_installation_key` | off | mobile push needs an id/key from bitwarden.com/host |
| `org_events_enabled` | `false` | event log |
| `events_days_retain` | unset | |
| `org_groups_enabled` | `false` | groups + directory-import groups |
| `invitation_expiration_hours` | `120` | |
| `login_ratelimit_seconds`, `login_ratelimit_max_burst` | `60`, `10` | |
| `admin_ratelimit_seconds`, `admin_ratelimit_max_burst` | `300`, `3` | |
| `disable_admin_token` | `false` | |
| `log_level` | `info` | `trace`/`debug` for diagnosis — they log request details |
| `log_file`, `use_syslog`, `extended_logging` | | |
| `icon_service` | `internal` | `bitwarden`, `duckduckgo`, `google`, or a URL template |

## Data folder — what to back up

| Path | Why |
|---|---|
| `db.sqlite3` (+ `-wal`, `-shm`) | everything; copy with `sqlite3 db.sqlite3 ".backup '<dest>'"`, `vaultwarden backup`, or `POST /admin/config/backup_db` — never `cp` a live WAL database |
| `attachments/` | item attachments |
| `sends/` | file Sends (short-lived) |
| `config.json` | admin-page settings — contains the admin token and SMTP password in plain text |
| `rsa_key.pem` (older installs also `rsa_key.pub.pem` / `.der`) | signs all tokens; losing it logs everyone out and invalidates pending invites |
| `icon_cache/` | optional |

MySQL/PostgreSQL deployments need `mysqldump` / `pg_dump`; `backup_db` and `vaultwarden backup` are SQLite-only. Restore: stop the container, replace the files, remove a stale `db.sqlite3-wal`, start.
