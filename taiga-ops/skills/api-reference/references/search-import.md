# Search, Resolver, Stats & Import/Export — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`.

## Search

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/search?project=<id>&text=<q>` | Full-text search within one project | `project` (required), `text` |

Returns matching `userstories`, `tasks`, `issues`, `wikipages`, `epics` with counts.

```bash
curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/search?project=7&text=password%20reset" | jq '{count, userstories: (.userstories|length), issues: (.issues|length)}'
```

## Resolver (slug/ref → numeric ID)

| Method | Path | Resolves |
|--------|------|----------|
| GET | `/resolver?project=<slug>` | project → `{project}` |
| GET | `/resolver?project=<slug>&us=<ref>` | + user story → `{project, us}` |
| GET | `/resolver?project=<slug>&task=<ref>` | + task |
| GET | `/resolver?project=<slug>&issue=<ref>` | + issue |
| GET | `/resolver?project=<slug>&epic=<ref>` | + epic |
| GET | `/resolver?project=<slug>&milestone=<slug>` | + sprint |
| GET | `/resolver?project=<slug>&wikipage=<slug>` | + wiki page |
| GET | `/resolver?project=<slug>&ref=<ref>` | auto-detect US/task/issue by ref (do not combine with `us`/`task`/`issue`) |

```bash
# What numeric IDs back project "apollo" and its story #42?
curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/resolver?project=apollo&us=42" | jq .
```

## Stats

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/stats/discover` | Discover/featured project metrics | optional |
| GET | `/stats/system` | Instance-wide stats (users, projects) | admin |

Project-level metrics live on the project resource: `GET /projects/{id}/stats` and `GET /projects/{id}/issues_stats` (see `projects.md`); sprint metrics on `GET /milestones/{id}/stats` (see `milestones-wiki.md`).

## Export / import (project dumps)

| Method | Path | Purpose | Notes |
|--------|------|---------|-------|
| GET | `/exporter/{projectId}` | Export a full project dump | Async — returns a `url` to the generated dump (poll it). Add `?dump=...` per docs. |
| POST | `/importer/load_dump` | Import a project from a dump | Multipart `dump` (file). Creates a new project. Async; returns a task to poll. |

```bash
# Kick off an export and read the dump URL
curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/exporter/7" | jq '{url, export_id}'
```

## Importers (Trello / GitHub / Jira)

Each external importer follows the same 3-phase OAuth + import flow. Replace `{svc}` with `trello`, `github`, or `jira`.

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/importers/{svc}/auth_url` | Get the OAuth authorization URL | — |
| POST | `/importers/{svc}/authorize` | Exchange OAuth `code` for a token | `code` → `token` |
| POST | `/importers/{svc}/list_projects` | List importable boards/repos/projects | `token` |
| POST | `/importers/{svc}/list_users` | List users on a source board (for mapping) | `token`, `project`/`board`/`repo` id |
| POST | `/importers/{svc}/import_project` | Run the import into a new Taiga project | `token`, source id, `name`, `description`, `users` mapping |

Imports are long-running; poll the returned task for completion.
