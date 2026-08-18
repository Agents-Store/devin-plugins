---
name: dify-docker-architecture
description: >
  Dify Docker Compose deployment architecture — services, container naming, directory layout,
  .env.example structure, and Docker project name conventions. Use when working with Dify Docker
  setup, understanding container services, debugging container issues, or needing to know the
  Dify directory structure. Triggers on "dify docker", "dify containers", "dify services",
  "dify architecture", "dify compose".
---

## Directory Layout

Dify is cloned from `https://github.com/langgenius/dify`. The Docker deployment lives in the `docker/` subdirectory:

```
dify/                          # Git repo root (DIFY_ROOT)
├── api/                       # Backend API source
├── web/                       # Frontend source
├── docker/                    # Docker deployment (DOCKER_DIR)
│   ├── docker-compose.yaml    # Main compose file
│   ├── .env.example           # Configuration template (150+ vars)
│   ├── .env                   # User's configuration (gitignored)
│   ├── dify-env-sync.sh       # Optional: official env sync script
│   ├── nginx/
│   │   └── conf.d/default.conf
│   ├── ssrf_proxy/
│   │   └── squid.conf
│   ├── volumes/               # Persistent data (created at runtime)
│   │   ├── postgres/
│   │   ├── redis/
│   │   ├── weaviate/
│   │   └── storage/
│   └── env-backup/            # Timestamped .env backups
├── .github/
└── ...
```

**Working directory detection:** Before any operation, detect whether the user is in:
- `dify/` root — has `docker/` subdirectory with `docker-compose.yaml`
- `dify/docker/` — has `docker-compose.yaml` and `.env.example` directly

Git operations run from `dify/` root. Docker and .env operations run from `dify/docker/`.

## Docker Compose Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `api` | `langgenius/dify-api` | 5001 (internal) | Backend REST API, webhooks |
| `worker` | `langgenius/dify-api` | — | Celery async task worker |
| `worker_beat` | `langgenius/dify-api` | — | Celery Beat scheduler |
| `web` | `langgenius/dify-web` | 3000 (internal) | Next.js frontend UI |
| `plugin_daemon` | `langgenius/dify-plugin-daemon` | 5003 | Plugin execution service |
| `db_postgres` | `postgres:15-alpine` | 5432 (internal) | PostgreSQL database |
| `redis` | `redis:6-alpine` | 6379 (internal) | Cache + Celery broker |
| `weaviate` | `semitechnologies/weaviate` | 8080 (internal) | Vector database (default) |
| `nginx` | `nginx:latest` | 80, 443 | Reverse proxy, SSL |
| `ssrf_proxy` | `ubuntu/squid:latest` | 3128 (internal) | SSRF protection proxy |
| `sandbox` | `langgenius/dify-sandbox` | 8194 (internal) | Code execution sandbox |

**Notes:**
- `api` and `worker` use the **same image** — different startup mode
- `COMPOSE_PROFILES` controls which vector DB service starts (default: weaviate)
- `db_postgres` has a health check enabled

## Container Naming Convention

Docker Compose derives the project name from the parent directory:
- If compose file is in `/opt/dify/docker/`, project name = `docker`
- Containers are named `{project}-{service}-1` (e.g., `docker-api-1`, `docker-web-1`)
- If using `-p custom`, then `custom-api-1`
- Network: `{project}_default`

To detect the project name from running containers:
```bash
docker ps --format '{{.Names}}' | grep -E '-(api|web|worker)-' | head -1 | sed 's/-\(api\|web\|worker\|nginx\|redis\|db_postgres\|sandbox\|ssrf_proxy\|plugin_daemon\|weaviate\|worker_beat\)-[0-9]*$//'
```

## .env.example Structure

The file has 150+ variables organized in sections:

| Section | Key Variables | Notes |
|---------|--------------|-------|
| **Security** | `SECRET_KEY`, `INIT_PASSWORD` | SECRET_KEY must be changed from default |
| **Server** | `LOG_LEVEL`, `MIGRATION_ENABLED`, `DEPLOY_ENV` | MIGRATION_ENABLED=true by default |
| **Database** | `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_DATABASE` | Default: postgres/difyai123456 |
| **Redis** | `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` | DB 0: cache, DB 1: Celery |
| **Storage** | `STORAGE_TYPE`, `S3_*`, `AZURE_BLOB_*` | Default: local |
| **Vector DB** | `VECTOR_STORE`, `WEAVIATE_*`, `QDRANT_*` | Default: weaviate |
| **Mail** | `MAIL_TYPE`, `SMTP_*` | Optional |
| **URLs** | `CONSOLE_API_URL`, `CONSOLE_WEB_URL`, `SERVICE_API_URL` | Leave empty for same-domain |
| **Compose** | `COMPOSE_PROFILES` | Auto-set from VECTOR_STORE and DB_TYPE |
| **Plugin Daemon** | Various plugin config vars | Added in newer versions |

## Database Migrations

- `MIGRATION_ENABLED=true` (default) — Dify auto-runs DB migrations on startup
- Manual: `docker compose exec api uv run flask db upgrade`
- **No downgrade support** — once upgraded, rolling back requires database backup/restore
- Always backup before updating: `docker compose exec db_postgres pg_dump -U postgres dify > backup.sql`

## Critical Facts

1. **Forward-only updates** — Dify does not support version downgrades due to migration incompatibilities
2. **Volume mounts** — `api` and `worker` must share the same storage volume for file uploads
3. **COMPOSE_PROFILES** — controls which services start; invalid profiles silently skip services
4. **Weaviate v4** — requires Client v4 and Server 1.27+, not backwards compatible
5. **Nginx** — may need config updates if API ports change between versions
