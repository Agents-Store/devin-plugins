---
name: api-reference
description: "This skill should be used when making direct HTTP/curl calls to the Dokploy API, looking up endpoint parameters, or building integrations that bypass the MCP server. Triggers: \"dokploy API\", \"curl dokploy\", \"REST endpoint\", \"HTTP request to dokploy\"."
disable-model-invocation: true
---

# Dokploy REST API Reference

API version: **v0.29.14** | **546 endpoints across 50 routers** (OpenAPI 3.1.0). For the **complete, exhaustive operation index** (every endpoint with its params, generated from the schema) see [api-full-index-resources.md](references/api-full-index-resources.md) and [api-full-index-platform.md](references/api-full-index-platform.md). The themed files below give curated usage patterns for the most-used domains.

## Connection
| Setting | Value |
|---------|-------|
| Base URL | `$DOKPLOY_URL` (base server URL, no `/api` suffix) |
| Endpoint path | `$DOKPLOY_URL/api/{tag}.{operationName}` |
| Auth header | `x-api-key: $DOKPLOY_API_KEY` (NOT `Authorization: Bearer`) |
| Content-Type | `application/json` (for POST requests) |

`DOKPLOY_URL` is the Dokploy server's base URL (e.g. `https://dokploy.example.com`). The REST API lives under `/api/…` on that host.

## Endpoint naming convention
All endpoints follow: `{METHOD} /api/{tag}.{operationName}`
- **GET** for read operations (list, fetch, search)
- **POST** for mutations (create, update, delete, deploy)

Tags: `project`, `application`, `compose`, `postgres`, `domain`, `settings`, etc.

## Quick examples

**GET — list all projects:**
```bash
curl -s "$DOKPLOY_URL/api/project.all" \
  -H "x-api-key: $DOKPLOY_API_KEY"
```

**POST — create a project:**
```bash
curl -s -X POST "$DOKPLOY_URL/api/project.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-project", "description": "New project"}'
```

## Reference files

**Complete coverage (100% of all 546 operations, generated from the v0.29.14 schema):**
| File | Coverage |
|------|----------|
| [api-full-index-resources.md](references/api-full-index-resources.md) | EVERY operation for projects, environments, tags, applications, compose, docker, domains, ports, redirects, security, certificates, mounts, registry, all 6 databases, deployments, previews, rollback, schedule, patch, backups, destinations, ai (302 ops) |
| [api-full-index-platform.md](references/api-full-index-platform.md) | EVERY operation for settings, server, cluster, swarm, sshKey, git providers, notifications, users, organizations, custom roles, SSO, forward auth (app SSO gate), SCIM, license, stripe, whitelabeling, audit log, admin (244 ops) |

**Curated usage patterns (the most-used domains, with gotchas and examples):**
| File | Coverage |
|------|----------|
| [api-projects-apps.md](references/api-projects-apps.md) | Projects, Applications, Environments, Deployments |
| [api-databases.md](references/api-databases.md) | Postgres, MySQL, MariaDB, Mongo, Redis, LibSQL |
| [api-domains-certs.md](references/api-domains-certs.md) | Domains, Certificates, Security, Redirects, Ports, Forward Auth |
| [api-compose-docker.md](references/api-compose-docker.md) | Compose, Docker, Mounts, Registry |
| [api-server-settings.md](references/api-server-settings.md) | Server, Settings, Backup, Notifications, Users, Cluster/Swarm |
| [ai-and-debugging.md](references/ai-and-debugging.md) | AI router, log endpoints, Docker introspection, recovery actions, rollback, settings health & cleanup |
| [schedule-patch-previews.md](references/schedule-patch-previews.md) | Schedule, Patch, Volume Backups, Preview Deployments |

## Common patterns
**Pagination:** Most list endpoints return all records. Use client-side filtering.

**Error responses:** `{"error": "Error message string", "statusCode": 400}`

**ID parameters:** All resource IDs are UUIDs. Pass in JSON body for POST, as query parameters for GET.

**GET with parameters:**
```bash
curl -s "$DOKPLOY_URL/api/project.one?projectId=uuid-here" \
  -H "x-api-key: $DOKPLOY_API_KEY"
```
