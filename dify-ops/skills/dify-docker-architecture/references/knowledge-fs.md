# KnowledgeFS integration (opt-in, since Dify 1.18.0)

KnowledgeFS backs the Agent Knowledge Base (beta): knowledge spaces for agents, with document processing, metadata, retrieval traces and quality evaluation. Classic Knowledge stays available and is the default. KnowledgeFS is a separate service with its own database, so a default install does not need any of this and an update never turns it on by itself.

Checked against the `1.20.0` tag (`docker/README.md`, `docker-compose.yaml`, `envs/core-services/knowledge-fs.env.example`) and the 1.18.0 release notes, upgrade guide step 7. Source: https://github.com/langgenius/dify/releases/tag/1.18.0 and https://github.com/langgenius/dify/blob/1.20.0/docker/README.md (section "Enable the KnowledgeFS integration").

## What the profiles start

| Profile | Services | Notes |
|---------|----------|-------|
| `knowledge-fs` | `knowledge_fs` (internal port 8787, no host port, no nginx route), `worker_knowledge_fs_upgrade` | The API image is `KNOWLEDGE_FS_API_IMAGE`, default `langgenius/dify-knowledge-fs-api`, published for linux/amd64 only. The upgrade worker (Classic dataset to KnowledgeFS) must run with `CELERY_WORKER_POOL=prefork`; do not change its task limits |
| `knowledge-fs-unstructured` | `knowledge_fs_unstructured` | Isolated document parser used only by KnowledgeFS, separate from the `unstructured` profile of Classic ETL |
| `knowledge-fs-celery` | five `knowledge_fs_*_worker` services | Engine workers; they need a worker image that bundles the KnowledgeFS engine, which the standard `langgenius/dify-api` image does not |

Add the profiles you want to `COMPOSE_PROFILES` in the root `.env`. Without `envs/core-services/knowledge-fs.env` the service cannot start.

## Enable it deliberately

1. Create a dedicated database for KnowledgeFS. Never point its `DATABASE_URL` at Dify's application database, and run its migrations as a separate, controlled step.
2. Copy the template and fill the operator-owned inputs: `cp envs/core-services/knowledge-fs.env.example envs/core-services/knowledge-fs.env`. Those inputs are the database, the Capability v2 public verification material (public JWKS only) and an optional Unstructured endpoint. Dify's inner API connection is injected by Compose; do not copy storage endpoints or credentials into this file, because KnowledgeFS stores its objects through Dify's own `STORAGE_TYPE` (the verified backends are S3 and OpenDAL local).
3. Validate and pull before starting: `docker compose --profile knowledge-fs config --quiet`, then `docker compose --profile knowledge-fs pull knowledge_fs`, then `docker compose --profile knowledge-fs up -d`.
4. Wait for `/ready` to return 200, not only `/health`: the container reports healthy while `/ready` stays 503 until the verifier and the other durable dependencies exist. Only when it does, and the migration and per-workspace cutover gates of the README are complete, set `KNOWLEDGE_FS_ENABLED=true` in the root `.env`; it is `false` by default, so a running container carries no product traffic.
5. A deployment that overrides `CELERY_QUEUES` or `CELERY_WORKER_QUEUES` must add the `knowledge_fs_lifecycle` queue to one worker pool.

## Updates and backups

- The 1.18.0 release added the KnowledgeFS tables to Dify's own database through Dify's normal migration chain; the KnowledgeFS engine database is separate and has its own migration process.
- A backup that should cover KnowledgeFS has to include its own database as well; the `update-workflow` backup archives `volumes/` only. The release notes also say that a downgrade which would leave KnowledgeFS-only API keys unrestricted is blocked until those keys are revoked through the API, so keep a backup before you enable it.
- The 1.18.0 notes say the older KnowledgeFS implementation was replaced: do not reuse its `KNOWLEDGE_FS_JWT_SECRET` or SSE timeout settings. `KNOWLEDGE_FS_ENABLED`, `KNOWLEDGE_FS_BASE_URL` and `KNOWLEDGE_FS_TIMEOUT_SECONDS` still apply.
