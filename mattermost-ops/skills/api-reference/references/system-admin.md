# System Administration

Server-wide operations. **All require the System Admin role** — a `403` means the account lacks it. Base `${MATTERMOST_API_URL%/}/api/v4`. Treat config writes, license changes, and data-retention/compliance jobs as high-impact: confirm before running.

## Health & info

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/system/ping` | Health check (no auth needed). Query `get_server_status=true` for DB/filestore status. |
| GET | `/system/timezones` | Supported timezones. |
| GET | `/latest_version` | Latest public server release info. |
| GET | `/cluster/status` | High-availability cluster node status. |
| GET | `/usage/posts` / `/usage/storage` / `/usage/teams` | Current usage counters. |

## Configuration

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/config` | Full server config (sanitized). |
| PUT | `/config` | Replace the whole config. |
| PUT | `/config/patch` | Patch only the fields you send (preferred). |
| POST | `/config/reload` | Reload config from disk. |
| GET | `/config/client?format=old` | Client-visible config (no admin needed). |
| GET | `/config/environment` | Settings set via env vars (read-only). |

## Analytics, audits, logs

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/analytics/old` | Aggregate analytics. Query `name` (e.g. `standard`, `post_counts_day`, `user_counts_with_posts_day`), `team_id`. |
| GET | `/audits` | System audit records. Query `page`, `per_page`. |
| GET | `/logs` | Server logs. Query `page`, `per_page`. |
| POST | `/logs` | Append a client log line. |
| GET | `/reports/users` | Paged/sorted users for admin reporting. |
| POST | `/reports/users/export` | Start a job exporting users to a report file. |

## License

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/license` | Upload a license file — multipart `-F "license=@mattermost.mattermost-license"`. |
| DELETE | `/license` | Remove the license (revert to Team Edition). |
| GET | `/license/client?format=old` | Client license info. |
| POST | `/trial-license` | Request a trial license. |

## Jobs (async server tasks)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/jobs` | List jobs. Query `page`, `per_page`. |
| POST | `/jobs` | Create a job. Body `{"type":"data_retention"|"elasticsearch_post_indexing"|"export_delete"|...}`. |
| GET | `/jobs/{job_id}` | Job status. |
| GET | `/jobs/type/{type}` | Jobs of a type. |
| POST | `/jobs/{job_id}/cancel` | Cancel a job. |
| GET | `/jobs/{job_id}/download` | Download job results (e.g. an export). |

## Plugins

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/plugins` | Upload a plugin bundle — multipart `-F "plugin=@plugin.tar.gz"`. Add `-F "force=true"` to overwrite. |
| GET | `/plugins` | List active + inactive plugins. |
| POST | `/plugins/install_from_url` | Install from a URL. Query `plugin_download_url`, `force`. |
| DELETE | `/plugins/{plugin_id}` | Remove a plugin. |
| POST | `/plugins/{plugin_id}/enable` / `/disable` | Enable / disable. |
| GET | `/plugins/statuses` | Per-node plugin status. |
| GET | `/plugins/marketplace` | List marketplace plugins. |
| POST | `/plugins/marketplace` | Install a marketplace plugin. Body `{"id","version"}`. |

## Compliance & data retention (Enterprise)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/compliance/reports` | Create a compliance export. Body `{"desc","emails"?,"keywords"?,"start_at","end_at"}`. |
| GET | `/compliance/reports` | List reports. |
| GET | `/compliance/reports/{report_id}` | Report metadata. |
| GET | `/compliance/reports/{report_id}/download` | Download (binary). |
| GET | `/data_retention/policy` | Global retention policy. |
| GET | `/data_retention/policies` | Granular policies. Query `page`, `per_page`. |
| POST | `/data_retention/policies` | Create a granular policy. |
| GET/PATCH/DELETE | `/data_retention/policies/{policy_id}` | Get / patch / delete. |
| GET/POST/DELETE | `/data_retention/policies/{policy_id}/teams` and `/channels` | Manage policy scope. |

## Authentication backends

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/ldap/sync` | Trigger an LDAP sync. |
| POST | `/ldap/test` | Test the LDAP connection. |
| GET | `/ldap/groups` | List LDAP groups available to link. |
| POST | `/saml/metadatafromidp` | Build SAML config from IdP metadata. |
| GET | `/saml/metadata` | Get this server's SP metadata. |
| POST | `/saml/reset_auth_data` | Reset SAML AuthData to email. |
| POST | `/elasticsearch/test` | Test the Elasticsearch config. |
| POST | `/elasticsearch/purge_indexes` | Purge all ES indexes. |

## Exports & imports

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/exports` | List bulk-export files. |
| GET | `/exports/{export_name}` | Download an export. |
| DELETE | `/exports/{export_name}` | Delete an export. |
| GET | `/imports` | List import files. |

> Many admin actions (recycle DB connections `POST /database/recycle`, invalidate caches `POST /caches/invalidate`, test email `POST /email/test`, S3 test `POST /file/s3_test`) exist too — grep the bundled OpenAPI spec under the `system` tag for the full list.
