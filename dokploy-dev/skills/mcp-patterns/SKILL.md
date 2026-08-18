---
name: mcp-patterns
description: "This skill should be used when deploying applications, managing projects, provisioning databases, configuring domains, working with Docker Compose, or performing any Dokploy operation via MCP tools. Triggers: \"deploy app\", \"create project\", \"add domain\", \"provision database\", \"dokploy compose\", \"manage dokploy\"."
---

# Dokploy MCP Tool Patterns

The official `@dokploy/mcp` server exposes **546 tools across 50 categories (v0.29.14)**. Each tool is prefixed with `mcp__dokploy__`. This skill covers every category developers and operators use day-to-day: projects, applications, domains, compose, six database types, deployment history, the cross-cutting recovery chain, the AI router (new in v0.29), Docker introspection, settings/cleanup/health, schedules, patches, volume backups, and preview deployments. Categories not fully tabled here are listed at the end with a pointer to the matching reference file.

To reduce the exposed tool surface, set `DOKPLOY_ENABLED_TAGS` in `.mcp.json` `env` to a comma-separated list of categories (e.g. `project,application,domain,compose,postgres,settings,deployment,docker,ai,rollback,schedule`).

---

## Project Management (9 tools)

Projects are the top-level container. Every application, database, and compose stack belongs to a project. Always create or identify a project before creating resources.

| Tool | Description | Parameters |
|---|---|---|
| `mcp__dokploy__project-all` | List all projects | None |
| `mcp__dokploy__project-allForPermissions` | List projects the current token can access | None |
| `mcp__dokploy__project-one` | Get a single project by ID | `projectId` (string, required) |
| `mcp__dokploy__project-create` | Create a new project | `name` (string, required), `description` (string, optional) |
| `mcp__dokploy__project-update` | Update project metadata | `projectId` (string, required), `name` (string), `description` (string) |
| `mcp__dokploy__project-duplicate` | Duplicate an environment's resources | `sourceEnvironmentId` (required), `name` (required), `description`, `includeServices`, `selectedServices`, `duplicateInSameProject` |
| `mcp__dokploy__project-remove` | Delete a project and all its resources | `projectId` (string, required) |
| `mcp__dokploy__project-search` | Search projects by name | `query` (string) |
| `mcp__dokploy__project-homeStats` | Aggregate dashboard/home stats across projects | None |

### Usage notes

- `project-all` returns an array of project objects, each containing `projectId`, `name`, `description`, and nested arrays of applications, databases, and compose stacks.
- `project-remove` is destructive — it deletes all applications, databases, and compose stacks within the project. Confirm with the user before calling.
- `project-duplicate` creates a full copy including all nested resources. Use it for staging/production environment cloning.

---

## Application Management (31 tools)

Applications are the primary deployment unit. They support multiple source types (GitHub, GitLab, Bitbucket, Gitea, generic Git, Docker image) and build types (Nixpacks, Dockerfile, Buildpacks, Docker image).

### Core CRUD + Search (5 tools)

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__application-one` | Get application details | `applicationId` |
| `mcp__dokploy__application-create` | Create a new application | `environmentId` (required), `name` (required), `appName` (unique slug) |
| `mcp__dokploy__application-update` | Update application settings | `applicationId`, plus any updatable fields |
| `mcp__dokploy__application-delete` | Delete an application | `applicationId` |
| `mcp__dokploy__application-search` | Search applications by name | `query` |

### Lifecycle (5 tools)

| Tool | Description | Parameters |
|---|---|---|
| `mcp__dokploy__application-deploy` | Trigger a new deployment | `applicationId` |
| `mcp__dokploy__application-redeploy` | Redeploy with latest config | `applicationId` |
| `mcp__dokploy__application-start` | Start a stopped application | `applicationId` |
| `mcp__dokploy__application-stop` | Stop a running application | `applicationId` |
| `mcp__dokploy__application-reload` | Reload application (zero-downtime) | `applicationId`, `appName` (both required) |

**Key distinction:** `deploy` builds from source and deploys. `redeploy` re-runs the last deployment with current config. `reload` restarts the running container without rebuilding.

### Git Provider Configuration (6 tools)

Connect an application to a Git source. Only one provider can be active at a time.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__application-saveGithubProvider` | Connect to GitHub | `applicationId`, `repository` (repo name only — NOT full URL), `branch`, `owner`, `githubId`, `enableSubmodules` |
| `mcp__dokploy__application-saveGitlabProvider` | Connect to GitLab | `applicationId`, `repository`, `branch`, `gitlabProjectId` |
| `mcp__dokploy__application-saveBitbucketProvider` | Connect to Bitbucket | `applicationId`, `repository`, `branch`, `owner` |
| `mcp__dokploy__application-saveGiteaProvider` | Connect to Gitea | `applicationId`, `repository`, `branch`, `owner` |
| `mcp__dokploy__application-saveGitProvider` | Connect to any Git URL | `applicationId`, `customGitUrl`, `customGitBranch`, `customGitBuildPath`, `enableSubmodules`, `watchPaths` |
| `mcp__dokploy__application-disconnectGitProvider` | Remove Git connection | `applicationId` |

**GitHub provider critical note:** The `repository` parameter for `saveGithubProvider` must be the **repository name only** (e.g. `"my-repo"`), NOT the full URL. Dokploy constructs the clone URL as `github.com/{owner}/{repository}` — passing a full URL like `https://github.com/org/repo` causes a broken double-URL (`github.com/org/https://github.com/org/repo`). You also need the `githubId` — get it from `gitProvider-getAll` (then filter by type `github`). Required fields: `applicationId`, `repository`, `branch`, `owner`, `githubId`, `enableSubmodules`, `triggerType` (default `"push"`), `watchPaths` (array, use `[]` if none), `buildPath` (default `"/"`).

**Generic Git provider note:** `saveGitProvider` requires ALL of: `applicationId`, `customGitUrl` (full SSH/HTTPS URL), `customGitBranch`, `customGitBuildPath` (e.g. `"/"`), `enableSubmodules` (boolean), `watchPaths` (array). Optionally `customGitSSHKeyId` for private repos. Omitting any required field causes a 400 validation error.

### Build & Environment Configuration (3 tools)

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__application-saveBuildType` | Set build method | `applicationId`, `buildType` (`nixpacks`, `dockerfile`, `docker`, `buildpacks`) |
| `mcp__dokploy__application-saveEnvironment` | Set environment variables | `applicationId`, `env` (newline-separated KEY=VALUE string) |
| `mcp__dokploy__application-saveDockerProvider` | Set Docker image source | `applicationId`, `dockerImage`, `dockerTag` |

### Monitoring, Logs & Config (4 tools)

| Tool | Description | Parameters |
|---|---|---|
| `mcp__dokploy__application-readAppMonitoring` | Read monitoring metrics (CPU, memory, network) | `applicationId` |
| `mcp__dokploy__application-readLogs` | Read the app container's runtime stdout/stderr (v0.29.0+) | `applicationId` (required), `tail` (1–10000, default 100), `since` (`all` or `<n>{s\|m\|h\|d}`), `search` (substring) |
| `mcp__dokploy__application-readTraefikConfig` | Read current Traefik routing config | `applicationId` |
| `mcp__dokploy__application-updateTraefikConfig` | Update Traefik routing rules | `applicationId`, `traefikConfig` (YAML string) |

### Deployment & Queue Management (8 tools)

| Tool | Description | Parameters |
|---|---|---|
| `mcp__dokploy__application-move` | Move application to another environment | `applicationId`, `targetEnvironmentId` |
| `mcp__dokploy__application-markRunning` | Force-mark application as running | `applicationId` |
| `mcp__dokploy__application-cancelDeployment` | Cancel an in-progress deployment | `applicationId` |
| `mcp__dokploy__application-killBuild` | Kill the currently-running build process | `applicationId` |
| `mcp__dokploy__application-refreshToken` | Regenerate application webhook token | `applicationId` |
| `mcp__dokploy__application-cleanQueues` | Clear stuck deployment queues | `applicationId` |
| `mcp__dokploy__application-clearDeployments` | Purge historical deployment records | `applicationId` |
| `mcp__dokploy__application-dropDeployment` | Drop a specific deployment | `deploymentId` |

### Application usage notes

- `application-create` requires `environmentId` and `name`. The `appName` parameter becomes the container name and must be unique across the server.
- **Resources live under a project's ENVIRONMENT** (default `production`) — applications, databases, and compose stacks are created with an `environmentId`, not a `projectId`. Resolve it via `project-one { projectId }` → `environments[]` or `environment-byProjectId { projectId }`.
- `application-saveEnvironment` expects **all** of these parameters: `applicationId`, `env` (newline-separated KEY=VALUE string), `buildArgs` (newline-separated KEY=VALUE string for Docker build args — use empty string if none), `buildSecrets` (empty string if none), `createEnvFile` (boolean). Omitting any parameter causes a 400 validation error. Build args are critical for frameworks like Next.js where env vars (e.g. `NEXT_PUBLIC_*`) must be available during `docker build`.
- `application-saveBuildType` requires **all** of these parameters: `applicationId`, `buildType` (`nixpacks`, `dockerfile`, `docker`, `buildpacks`), `dockerfile` (filename, e.g. `"Dockerfile"`), `dockerContextPath` (e.g. `"."`), `dockerBuildStage` (empty string if none), `herokuVersion` (empty string if N/A), `railpackVersion` (empty string if N/A). Omitting any parameter causes a 400 validation error. When a project has a `Dockerfile`, default to `buildType: "dockerfile"` — ask the user to confirm.
- After calling `application-deploy`, the deployment runs asynchronously. Check deployment status via `deployment-all` filtered by `applicationId` to confirm completion. On failure, read logs with `application-readLogs` and iterate.
- `application-markRunning` is a manual override for stuck states. Use only when the container is running but Dokploy shows it as stopped.
- `application-cleanQueues` clears the deployment queue. Use when deployments are stuck in "queued" state. `application-killBuild` aborts a running build immediately.

---

## Domain Management (9 tools)

Domains map hostnames to applications or compose services. Dokploy uses Traefik as the reverse proxy.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__domain-byApplicationId` | List domains for an application | `applicationId` |
| `mcp__dokploy__domain-byComposeId` | List domains for a compose stack | `composeId` |
| `mcp__dokploy__domain-one` | Get a single domain by ID | `domainId` |
| `mcp__dokploy__domain-create` | Create a domain mapping | See below |
| `mcp__dokploy__domain-update` | Update domain settings | `domainId`, plus updatable fields |
| `mcp__dokploy__domain-delete` | Delete a domain | `domainId` |
| `mcp__dokploy__domain-validateDomain` | Check DNS resolution for a domain | `domain` (required — the hostname string, NOT domainId), `serverIp` (optional) |
| `mcp__dokploy__domain-generateDomain` | Auto-generate a subdomain | `appName` (required), `serverId` |
| `mcp__dokploy__domain-canGenerateTraefikMeDomains` | Check if .traefik.me domains are available | None |

### `domain-create` parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `host` | string | Yes | Domain hostname (e.g. `app.example.com`) |
| `path` | string | No | URL path prefix (default: `/`) |
| `port` | number | No | Container port to route to (default: application's exposed port) |
| `applicationId` | string | Conditional | Application to attach to (mutually exclusive with `composeId`) |
| `composeId` | string | Conditional | Compose stack to attach to (mutually exclusive with `applicationId`) |
| `https` | boolean | No | Enable HTTPS with auto-cert (default: `false`) |
| `certificateType` | string | No | Certificate type: `letsencrypt`, `none` (default: `none`) |
| `forwardAuthEnabled` | boolean | No | (v0.29.8+, enterprise) gate this domain behind the server's forward-auth SSO — see the `forwardAuth-*` tools |

### Domain usage notes

- Always call `domain-validateDomain` after creating a domain to confirm DNS is pointing to the server.
- `domain-generateDomain` creates a `.traefik.me` wildcard subdomain that resolves to the server's IP. Useful for development/testing without DNS setup.
- To enable HTTPS with Let's Encrypt, set `https: true` and `certificateType: "letsencrypt"`. The domain must have valid DNS pointing to the server for certificate issuance to succeed.
- A single application can have multiple domains. Use this for aliases or www/non-www setups.
- To list domains attached to a compose stack, use `domain-byComposeId` (the old `compose-fetchDomains` tool was removed — this is its direct replacement).

---

## Compose Management (31 tools)

Docker Compose stacks deploy multi-container applications defined by a `docker-compose.yml` file.

### Core CRUD & Lifecycle

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__compose-one` | Get compose stack details | `composeId` |
| `mcp__dokploy__compose-create` | Create a compose stack | `environmentId` (required), `name` (required), `appName` |
| `mcp__dokploy__compose-update` | Update compose settings + source (see note below) | `composeId`, updatable fields |
| `mcp__dokploy__compose-delete` | Delete a compose stack | `composeId` |
| `mcp__dokploy__compose-deploy` | Deploy the compose stack | `composeId` |
| `mcp__dokploy__compose-redeploy` | Redeploy with current config | `composeId` |
| `mcp__dokploy__compose-start` | Start compose services | `composeId` |
| `mcp__dokploy__compose-stop` | Stop all compose services | `composeId` |
| `mcp__dokploy__compose-move` | Move compose stack to another environment | `composeId`, `targetEnvironmentId` |
| `mcp__dokploy__compose-search` | Search compose stacks by name | `query` |

### Source / Git Configuration

Unlike applications, compose git source is set **via `compose-update`**, not a separate `saveGithubProvider` call. Pass `sourceType` (`github` / `gitlab` / `bitbucket` / `gitea` / `git`), `repository`, `branch`, `owner`, `composePath`, and provider-specific IDs (`githubId`, `gitlabProjectId`, etc.) in a single update.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__compose-disconnectGitProvider` | Remove Git connection | `composeId` |
| `mcp__dokploy__compose-fetchSourceType` | Detect source type from repo | `composeId` |
| `mcp__dokploy__compose-import` | Import compose stack from external source | per-source fields |

### Templates

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__compose-templates` | List available compose templates | None |
| `mcp__dokploy__compose-deployTemplate` | Deploy a compose template | `id` (template id), `environmentId`, `serverId` |
| `mcp__dokploy__compose-processTemplate` | Render a template with variables | `templateId`, variables |
| `mcp__dokploy__compose-previewTemplate` | Preview a rendered template before deploying | `base64` (required), `appName` (required), `serverId` |

### Build, Config & Logs

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__compose-getDefaultCommand` | Get default docker compose command | `composeId` |
| `mcp__dokploy__compose-getConvertedCompose` | Validate and render the compose file | `composeId` |
| `mcp__dokploy__compose-loadServices` | List services defined in the stack | `composeId` |
| `mcp__dokploy__compose-loadMountsByService` | Inspect mounts per service | `composeId`, `serviceName` |
| `mcp__dokploy__compose-getTags` | List image tags used | `composeId` |
| `mcp__dokploy__compose-randomizeCompose` | Generate random ports for services | `composeId` |
| `mcp__dokploy__compose-saveEnvironment` | Set environment variables | `composeId`, `env` |
| `mcp__dokploy__compose-readLogs` | Read ONE container's runtime logs. `containerId` is **required** — a stack has many containers, so enumerate first (see note) and call once per container | `composeId` (required), `containerId` (required), `tail`, `since`, `search` |

### Deployment Management

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__compose-cancelDeployment` | Cancel in-progress deployment | `composeId` |
| `mcp__dokploy__compose-killBuild` | Kill the running build | `composeId` |
| `mcp__dokploy__compose-cleanQueues` | Clear stuck deployment queue | `composeId` |
| `mcp__dokploy__compose-clearDeployments` | Purge deployment history | `composeId` |
| `mcp__dokploy__compose-refreshToken` | Regenerate webhook token | `composeId` |
| `mcp__dokploy__compose-isolatedDeployment` | Toggle isolated deployment mode | `composeId`, boolean |

### Compose usage notes

- `compose-create` creates the stack record. After creation, set git source / compose file content via `compose-update`, then call `compose-deploy`.
- **Setting a git source for compose:** Use `compose-update` with `sourceType` and the matching provider fields. The old `compose-saveGithubProvider` / `compose-saveGitlabProvider` tools were consolidated into `compose-update` in the official MCP server.
- **Listing domains for a compose stack:** Use `domain-byComposeId` (not the removed `compose-fetchDomains`).
- `compose-saveEnvironment` works the same as the application equivalent — newline-separated `KEY=VALUE` string.
- `compose-getConvertedCompose` validates the compose file by rendering it with current env vars. Call this before `compose-deploy` to catch YAML errors early.
- **Reading logs for a stack = read every container.** `compose-readLogs` is per-container and requires `containerId`. To read all of them: `compose-one { composeId }` → `appName`/`composeType`; then `docker-getContainersByAppNameMatch { appName, appType: "docker-compose" }` (compose) or `docker-getStackContainersByAppName { appName }` (swarm) to list containers (`{ containerId, name, state, status }`); then loop `compose-readLogs { composeId, containerId, tail, since, search }` for each. The `read-logs` skill and `/dokploy-dev:compose-logs` automate this.

---

## Database Management (5 types × 16 tools; LibSQL has 14)

Dokploy supports six managed database types. Five of them (postgres, mysql, mariadb, mongo, redis) have an identical set of 16 tools following the same naming pattern (the official server adds `changePassword`, `readLogs`, and `search` on top of the 13 core tools). **LibSQL has only 14**: there is no `libsql-changePassword` and no `libsql-search`, and its port tool is `libsql-saveExternalPorts` (plural) taking three port fields (`externalPort`, `externalGRPCPort`, `externalAdminPort`).

### Tool pattern per database type

Replace `{type}` with `postgres`, `mysql`, `mariadb`, `mongo`, `redis`, or `libsql`:

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__{type}-create` | Provision a new database | `environmentId` (required), `name` (required), plus per-type required fields (see notes) |
| `mcp__dokploy__{type}-one` | Get database details | `{type}Id` |
| `mcp__dokploy__{type}-update` | Update database config | `{type}Id`, updatable fields |
| `mcp__dokploy__{type}-remove` | Delete a database | `{type}Id` |
| `mcp__dokploy__{type}-move` | Move to another environment | `{type}Id`, `targetEnvironmentId` |
| `mcp__dokploy__{type}-search` | Search databases by name (**not libsql**) | `query` |
| `mcp__dokploy__{type}-deploy` | Deploy/start the database container | `{type}Id` |
| `mcp__dokploy__{type}-start` | Start a stopped database | `{type}Id` |
| `mcp__dokploy__{type}-stop` | Stop a running database | `{type}Id` |
| `mcp__dokploy__{type}-reload` | Reload database container | `{type}Id` |
| `mcp__dokploy__{type}-rebuild` | Rebuild database container from scratch | `{type}Id` |
| `mcp__dokploy__{type}-changeStatus` | Force status change | `{type}Id`, `applicationStatus` |
| `mcp__dokploy__{type}-changePassword` | Rotate the database password (**not libsql**) | `{type}Id`, `newPassword` |
| `mcp__dokploy__{type}-saveExternalPort` | Expose database on a host port (libsql: `libsql-saveExternalPorts`, plural) | `{type}Id`, `externalPort` (libsql also `externalGRPCPort`, `externalAdminPort`) |
| `mcp__dokploy__{type}-saveEnvironment` | Set database environment variables | `{type}Id`, `env` |
| `mcp__dokploy__{type}-readLogs` | Read the DB container's runtime logs | `{type}Id` (required), `tail`, `since`, `search` |

### Supported types

- **PostgreSQL** (`postgres-*`)
- **MySQL** (`mysql-*`)
- **MariaDB** (`mariadb-*`)
- **MongoDB** (`mongo-*`)
- **Redis** (`redis-*`)
- **LibSQL** (`libsql-*`) — new in the official server; embedded-SQL / SQLite-compatible managed service. Only 14 tools: no `changePassword`/`search`; port exposure via `libsql-saveExternalPorts` (`externalPort`, `externalGRPCPort`, `externalAdminPort`)

### Database usage notes

- `{type}-create` requires `environmentId` and `name`, plus per-type required fields: postgres/mysql/mariadb → `databaseName`, `databaseUser`, `databasePassword` (mysql/mariadb also accept optional `databaseRootPassword`); mongo → `databaseUser`, `databasePassword`; redis → `databasePassword`; libsql → `databaseUser`, `databasePassword`, `sqldNode`, `enableNamespaces` (and more — see the full index).
- After `{type}-create`, call `{type}-deploy` to start the container. Creation only registers the resource.
- `{type}-saveExternalPort` exposes the database on the host network. Set `externalPort` to the desired port number. Set to `null` to remove external access. For LibSQL the tool is `libsql-saveExternalPorts` (plural) with `externalPort`, `externalGRPCPort`, and `externalAdminPort`.
- `{type}-rebuild` destroys and recreates the container. Data persists only if volumes are configured.
- `{type}-changeStatus` is a manual override. Use only when the actual container state differs from what Dokploy reports.
- `{type}-changePassword` rotates credentials without destroying data (not available for libsql). Follow up by updating connection strings in dependent applications.

---

## Deployment History (9 tools)

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__deployment-all` | List deployments for an application | `applicationId` (required) |
| `mcp__dokploy__deployment-allByCompose` | List deployments for a compose stack | `composeId` |
| `mcp__dokploy__deployment-allByServer` | List deployments for a server | `serverId` |
| `mcp__dokploy__deployment-allByType` | Filter by resource id + type | `id` (required), `type` (required) |
| `mcp__dokploy__deployment-allCentralized` | List deployments across all resources | None |
| `mcp__dokploy__deployment-queueList` | Inspect the deployment queue | None |
| `mcp__dokploy__deployment-killProcess` | Kill a running deployment process | `deploymentId` |
| `mcp__dokploy__deployment-removeDeployment` | Remove a deployment record | `deploymentId` |
| `mcp__dokploy__deployment-readLogs` | Read a deployment's **build log** (central to debugging failed builds) | `deploymentId` (required), `tail` |

`deployment-all` takes ONLY `applicationId`. For a compose stack use `deployment-allByCompose { composeId }`; for a server use `deployment-allByServer { serverId }`; `deployment-allByType` takes `id` + `type`.

---

## Recovery Chain (cross-cutting)

When a deploy is misbehaving, recovery actions live across `application-*`, `compose-*`, `deployment-*`, `docker-*`, `settings-*`, and `rollback-*`. The canonical order from least-destructive to most:

| Step | Tool | When to use |
|---|---|---|
| 1 | `application-killBuild` / `compose-killBuild` | Abort an in-progress builder process |
| 2 | `application-cancelDeployment` / `compose-cancelDeployment` | Cancel a queued/in-flight deploy and free the queue slot |
| 3 | `deployment-killProcess` | Kill the underlying deployment process by `deploymentId` (use when 1+2 don't free it) |
| 4 | `application-cleanQueues` / `compose-cleanQueues` / `settings-cleanAllDeploymentQueue` | Clear stuck queued state for one resource or globally |
| 5 | `application-dropDeployment` / `deployment-removeDeployment` | Remove a single bad deployment record |
| 6 | `application-clearDeployments` / `compose-clearDeployments` | Wipe deployment history (destroys audit trail — confirm) |
| 7 | `docker-killContainer` → `application-redeploy` | Force-kill a wedged runtime container and rebuild |
| 8 | `rollback-rollback { rollbackId }` | Switch back to a previously-successful image (no rebuild) |
| 9 | `application-markRunning` | Force the status field when Dokploy lost track but the container is actually fine (cosmetic) |

See the `debug-deploy` skill for the diagnostic chain that produces the `deploymentId`/`rollbackId` you need to pass here.

---

## AI Router (14 tools)

Provider-agnostic LLM integration for log analysis and recommendations. The AI router calls run on the Dokploy server, not the client.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__ai-getEnabledProviders` | List enabled providers; empty means AI is not available | None |
| `mcp__dokploy__ai-getAll` | List all configured providers (enabled and disabled) | None |
| `mcp__dokploy__ai-one` / `mcp__dokploy__ai-get` | Read one provider's config | `aiId` |
| `mcp__dokploy__ai-getModels` | List models a candidate endpoint advertises | `apiUrl`, `apiKey` (NOT aiId) |
| `mcp__dokploy__ai-create` | Add a provider | `name`, `apiKey`, `apiUrl`, `model`, `isEnabled` |
| `mcp__dokploy__ai-update` | Update a provider's config | `aiId`, updatable fields |
| `mcp__dokploy__ai-delete` | Remove a provider | `aiId` |
| `mcp__dokploy__ai-testConnection` | Validate credentials and reachability | `apiUrl`, `apiKey`, `model` (tests a candidate payload BEFORE saving — does NOT take aiId) |
| `mcp__dokploy__ai-getCustomProviders` | List org-defined custom provider presets (v0.29.13+) | None |
| `mcp__dokploy__ai-saveCustomProviders` | Save org custom provider presets | `providers` (array, required) |
| `mcp__dokploy__ai-deploy` | Deploy the AI orchestrator side-service (admin-only) | none / admin params |
| `mcp__dokploy__ai-analyzeLogs` | **Headline:** AI-summarise log text you fetched | `aiId` (enabled provider), `logs` (the log text from a `*-readLogs` call), `context` (`"build"` for `deployment-readLogs`, `"runtime"` for app/compose/db logs) — NOT `deploymentId` |
| `mcp__dokploy__ai-suggest` | Ask the LLM for next-step recommendations | `aiId` (required), `input` (required — the question/state text), `serverId` (optional) |

`apiUrl` is OpenAI-compatible. Common providers: OpenAI (`https://api.openai.com/v1`), OpenRouter (`https://openrouter.ai/api/v1`), Groq (`https://api.groq.com/openai/v1`), Gemini (`https://generativelanguage.googleapis.com/v1beta/openai`), Ollama (`http://host:11434/v1`). See the `ai-assist` skill for the full setup workflow.

---

## Docker Introspection (12 tools)

Raw Docker container operations on the Dokploy host. Essential for runtime debugging.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__docker-getContainers` | List all containers on the host (each `{ containerId, name, state, status }`) | optional `serverId` |
| `mcp__dokploy__docker-getContainersByAppLabel` | List containers tagged with a specific Dokploy app label | `appName`, `type` (**required**: `"standalone"` \| `"swarm"`), optional `serverId` |
| `mcp__dokploy__docker-getContainersByAppNameMatch` | Match containers by app name — use for compose stacks | `appName`, `appType` (`"stack"` \| `"docker-compose"`), optional `serverId` |
| `mcp__dokploy__docker-getServiceContainersByAppName` | Swarm service containers across nodes | `appName`, optional `serverId` |
| `mcp__dokploy__docker-getStackContainersByAppName` | Compose/Swarm stack service containers | `appName`, optional `serverId` |
| `mcp__dokploy__docker-getConfig` | Inspect a container's full config (env, command, mounts, network, restart policy) | `containerId` |
| `mcp__dokploy__docker-startContainer` | Start a stopped container | `containerId` |
| `mcp__dokploy__docker-stopContainer` | Gracefully stop a running container | `containerId` |
| `mcp__dokploy__docker-restartContainer` | Restart in place (no rebuild) — first try for transient failures | `containerId` |
| `mcp__dokploy__docker-killContainer` | Force-kill (SIGKILL) a wedged container | `containerId` |
| `mcp__dokploy__docker-removeContainer` | Hard-delete; Dokploy recreates on next `deploy` | `containerId` |
| `mcp__dokploy__docker-uploadFileToContainer` | Push a one-off file into a container without rebuilding — does NOT survive redeploy | `containerId`, `path`, `content` |

Choosing the discovery tool: for a **standalone application** use `getContainersByAppLabel { appName, type: "standalone" }` (most reliable — Dokploy stamps a known label). For a **compose stack** use `getContainersByAppNameMatch { appName, appType: "docker-compose" }` (or `getStackContainersByAppName` for swarm) — these return every service container. All return `{ containerId, name, state, status }`; feed each `containerId` into `compose-readLogs` to read that container's logs.

---

## Settings, Health & Cleanup (selected)

The `settings-*` namespace is the catch-all for server-wide operations. Highest-leverage subset for dev/debug:

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__settings-health` | Liveness probe (no auth required) | None |
| `mcp__dokploy__settings-checkInfrastructureHealth` | Combined check: Docker daemon, Traefik, network, disk | None |
| `mcp__dokploy__settings-getDockerDiskUsage` | Per-category disk usage (images, containers, volumes, build cache) | None |
| `mcp__dokploy__settings-checkGPUStatus` | GPU availability and current usage | None |
| `mcp__dokploy__settings-getDokployVersion` | Server version string | None |
| `mcp__dokploy__settings-getReleaseTag` | Image tag currently running | None |
| `mcp__dokploy__settings-getUpdateData` | Available update info | None |
| `mcp__dokploy__settings-getIp` | Server outbound IP | None |
| `mcp__dokploy__settings-getDokployCloudIps` | Static IP ranges for Dokploy Cloud egress | None |
| `mcp__dokploy__settings-getTraefikPorts` | Currently-bound Traefik ports | None |
| `mcp__dokploy__settings-haveTraefikDashboardPortEnabled` | Is the 8080 dashboard exposed? | None |
| `mcp__dokploy__settings-getLogCleanupStatus` | Log rotation schedule + last run | None |
| `mcp__dokploy__settings-updateLogCleanup` | Tune log rotation | retention fields |
| `mcp__dokploy__settings-updateBuildsConcurrency` | Set concurrent builds for the Dokploy host queue (per-server queues since v0.29.9; the OSS max-2 clamp existed only in v0.29.9–v0.29.10 — since v0.29.11 concurrency is a full OSS feature, 1–100 per server, default 1) | `buildsConcurrency` |
| `mcp__dokploy__settings-updateEnforceSSO` | Toggle enforce-SSO restriction | `enforceSSO` |
| `mcp__dokploy__settings-updateRemoteServersOnly` | Toggle remote-servers-only mode | `remoteServersOnly` |
| `mcp__dokploy__settings-cleanDockerBuilder` | Clear BuildKit cache | None |
| `mcp__dokploy__settings-cleanDockerPrune` | `docker system prune` equivalent | None |
| `mcp__dokploy__settings-cleanStoppedContainers` | Remove exited containers | None |
| `mcp__dokploy__settings-cleanUnusedImages` | Remove dangling/untagged images | None |
| `mcp__dokploy__settings-cleanUnusedVolumes` | **Destroys orphan volumes** — risky | None |
| `mcp__dokploy__settings-cleanMonitoring` | Reset monitoring data | None |
| `mcp__dokploy__settings-cleanRedis` | Flush Dokploy's internal Redis cache | None |
| `mcp__dokploy__settings-cleanAll` | Aggressive: combines builder + prune + monitoring + redis | None |
| `mcp__dokploy__settings-cleanAllDeploymentQueue` | Force-clear every stuck deploy across all resources | None |
| `mcp__dokploy__settings-readTraefikConfig` | Top-level Traefik static config | None |
| `mcp__dokploy__settings-readMiddlewareTraefikConfig` | Middlewares config | None |
| `mcp__dokploy__settings-readWebServerTraefikConfig` | Per-webserver dynamic config | None |
| `mcp__dokploy__settings-reloadTraefik` | Reload Traefik to apply config changes | None |
| `mcp__dokploy__settings-reloadServer` / `reloadRedis` | Bounce the Dokploy server / Redis | None |
| `mcp__dokploy__settings-toggleDashboard` | Show/hide the Traefik dashboard | None |

For the cleanup chain run in order, use the `/dokploy-dev:cleanup` command — it confirms each destructive step and reports reclaimed space.

---

## Schedule Router (6 tools)

Cron-like scheduled tasks scoped to a resource. Each schedule fires a command inside the target container.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__schedule-list` | List schedules for a resource | `id` (required — the target resource id), `scheduleType` (required: `application`\|`compose`\|`server`\|`dokploy-server`) |
| `mcp__dokploy__schedule-one` | Get one schedule | `scheduleId` |
| `mcp__dokploy__schedule-create` | Create a scheduled task | `name`, `cronExpression`, target binding (`applicationId` / `composeId` / `serverId` / `dokployServer`), `command`, `serviceName` (for compose), `enabled`, optional `timezone`. Host schedules are organization-scoped since v0.29.8 (`organizationId`, formerly `userId`) |
| `mcp__dokploy__schedule-update` | Edit a schedule | `scheduleId`, updatable fields |
| `mcp__dokploy__schedule-delete` | Remove a schedule | `scheduleId` |
| `mcp__dokploy__schedule-runManually` | Trigger the schedule immediately, ignoring cron | `scheduleId` |

Schedule targets:

- `applicationId` — runs `command` inside the app container at every tick
- `composeId` + `serviceName` — runs inside that specific compose service
- `serverId` — runs on the host (for remote servers)
- `dokployServer: true` — runs on the Dokploy host itself

`cronExpression` is a standard 5-field cron (e.g. `"0 3 * * *"` = daily at 03:00).

---

## Patch Router (12 tools)

File-level overlays applied at deploy time. Useful when you can't / don't want to modify the source repo (e.g. tweaking a config file in an upstream image).

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__patch-byEntityId` | List patches for an entity | `id` (required — applicationId/composeId), `type` (required: `application`/`compose`) |
| `mcp__dokploy__patch-one` | Get one patch record | `patchId` |
| `mcp__dokploy__patch-create` | Create a patch | `filePath` (required), `content` (required), `type`, `enabled`, `applicationId`/`composeId` |
| `mcp__dokploy__patch-update` | Update patch metadata | `patchId`, updatable fields |
| `mcp__dokploy__patch-delete` | Remove a patch | `patchId` |
| `mcp__dokploy__patch-toggleEnabled` | Enable/disable without deleting | `patchId`, `enabled` |
| `mcp__dokploy__patch-ensureRepo` | Ensure the patch's git repo workspace is materialised | `id`, `type` |
| `mcp__dokploy__patch-cleanPatchRepos` | Garbage-collect orphan patch repos | optional `serverId` |
| `mcp__dokploy__patch-readRepoDirectories` | List directories inside the patch workspace | `id`, `type`, `repoPath` |
| `mcp__dokploy__patch-readRepoFile` | Read a file from the patch workspace | `id`, `type`, `filePath` |
| `mcp__dokploy__patch-saveFileAsPatch` | Save a modified file as a patch overlay | `id`, `type`, `filePath`, `content`, `patchType` |
| `mcp__dokploy__patch-markFileForDeletion` | Mark a file for deletion during patch apply | `id`, `type`, `filePath` |

Patches apply during the deploy step, after the source is cloned but before the build. Use for per-environment config overrides without forking the upstream repo.

---

## Volume Backups (6 tools)

Distinct from the resource-aware `backup` namespace — `volumeBackups` snapshot raw Docker volumes as-is (no DB-specific dump tooling).

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__volumeBackups-list` | List volume backup configs for a resource | `id` (required), `volumeBackupType` (required) |
| `mcp__dokploy__volumeBackups-one` | Get one backup config | `volumeBackupId` |
| `mcp__dokploy__volumeBackups-create` | Configure a recurring volume backup | resource binding, `volumeName`, `destinationId`, `cronExpression`, `enabled` |
| `mcp__dokploy__volumeBackups-update` | Update config | `volumeBackupId`, updatable fields |
| `mcp__dokploy__volumeBackups-delete` | Remove a backup config | `volumeBackupId` |
| `mcp__dokploy__volumeBackups-runManually` | Trigger a one-off backup outside the schedule | `volumeBackupId` |

Pair with the `destination-*` namespace to point at S3, R2, or another remote. Use for non-database persistent state (uploads, ML model files, caches).

---

## Preview Deployments (4 tools)

Ephemeral per-PR / per-branch deploys spun up alongside the main application.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__dokploy__previewDeployment-all` | List preview deployments | `applicationId` (required) |
| `mcp__dokploy__previewDeployment-one` | Get one preview deployment | `previewDeploymentId` |
| `mcp__dokploy__previewDeployment-redeploy` | Force a fresh build of a preview | `previewDeploymentId` |
| `mcp__dokploy__previewDeployment-delete` | Tear down a preview environment | `previewDeploymentId` |

Preview deployments are typically triggered by webhook (PR opened/synced). The MCP surface above is for inspection and manual lifecycle control.

---

## Common Workflow Patterns

### 1. Deploy a new application from GitHub

Execute these tools in sequence:

```
1. mcp__dokploy__project-create
   → { name: "my-project", description: "Production app" }
   → Returns: { projectId: "abc123" }

1b. mcp__dokploy__project-one
   → { projectId: "abc123" }
   → Returns environments[] — take environments[0].environmentId (default environment "production")

2. mcp__dokploy__application-create
   → { environmentId: "env123", name: "My App", appName: "my-app" }
   → Returns: { applicationId: "def456" }

3. mcp__dokploy__application-saveGithubProvider
   → { applicationId: "def456", repository: "my-repo", branch: "main", owner: "my-org" }

4. mcp__dokploy__application-saveBuildType
   → { applicationId: "def456", buildType: "dockerfile", dockerfile: "Dockerfile", dockerContextPath: ".", dockerBuildStage: "", herokuVersion: "", railpackVersion: "" }
   (Use "nixpacks" if no Dockerfile exists. Ask user which to use.)

5. mcp__dokploy__application-saveEnvironment
   → { applicationId: "def456", env: "DATABASE_URL=postgres://...\nNODE_ENV=production\nPORT=3000", buildArgs: "", buildSecrets: "", createEnvFile: false }

6. mcp__dokploy__domain-create
   → { applicationId: "def456", host: "app.example.com", https: true, certificateType: "letsencrypt", port: 3000 }

7. mcp__dokploy__application-deploy
   → { applicationId: "def456" }
```

After step 7, check the application status with `application-one` and deployment history with `deployment-all` filtered by `applicationId` to confirm the deployment succeeded. Stream logs with `application-readLogs` if it fails.

### 2. Provision a PostgreSQL database with external access

```
1. mcp__dokploy__project-create
   → { name: "databases" }
   → Returns: { projectId: "proj789" }
   (Or use project-all to find an existing project)
   Then resolve the environment: project-one { projectId } → environments[0].environmentId

2. mcp__dokploy__postgres-create
   → { environmentId: "env789", name: "Main DB", appName: "main-db", databaseName: "main", databaseUser: "postgres", databasePassword: "secure-password-here" }
   → Returns: { postgresId: "pg123" }

3. mcp__dokploy__postgres-deploy
   → { postgresId: "pg123" }

4. mcp__dokploy__postgres-saveExternalPort
   → { postgresId: "pg123", externalPort: 5432 }
```

The database is now accessible at `server-ip:5432`. Use the connection string: `postgres://postgres:secure-password-here@server-ip:5432/postgres`.

### 3. Add a domain with HTTPS to an existing application

```
1. mcp__dokploy__domain-create
   → { applicationId: "def456", host: "api.example.com", https: true, certificateType: "letsencrypt", port: 8080 }
   → Returns: { domainId: "dom789" }

2. mcp__dokploy__domain-validateDomain
   → { domain: "api.example.com" }        # the hostname string (optionally serverIp) — NOT the domainId
```

If validation fails, the DNS A record for `api.example.com` is not pointing to the server's IP. Fix DNS and re-validate.

### 4. Deploy a Docker Compose stack

```
1. mcp__dokploy__project-create
   → { name: "compose-stack" }
   → Returns: { projectId: "proj456" }
   Then resolve the environment: project-one { projectId } → environments[0].environmentId

2. mcp__dokploy__compose-create
   → { environmentId: "env456", name: "My Stack", appName: "my-stack" }
   → Returns: { composeId: "comp789" }

3. mcp__dokploy__compose-update
   → { composeId: "comp789", composeFile: "version: '3.8'\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - '80:80'" }

   (If sourcing compose from a git repo instead, pass sourceType/repository/branch/owner/composePath here too.)

4. mcp__dokploy__compose-saveEnvironment
   → { composeId: "comp789", env: "NGINX_HOST=example.com" }

5. mcp__dokploy__compose-getConvertedCompose
   → { composeId: "comp789" }   // validate the file before deploy

6. mcp__dokploy__compose-deploy
   → { composeId: "comp789" }
```

### 5. Read the logs of every container in a compose stack

```
1. mcp__dokploy__compose-one
   → { composeId: "comp789" }
   → read appName (e.g. "my-stack-ab12cd") and composeType (e.g. "docker-compose")

2. mcp__dokploy__docker-getContainersByAppNameMatch          // swarm → docker-getStackContainersByAppName
   → { appName: "my-stack-ab12cd", appType: "docker-compose" }
   → [ { containerId, name, state, status }, ... ]   // every service container

3. for each container:
   mcp__dokploy__compose-readLogs
     → { composeId: "comp789", containerId: "<containerId>", tail: 200, since: "1h", search: "error" }
     → .data is a newline-joined, timestamp-prefixed log string

4. Aggregate per container; the lowest-level failing service (e.g. a crashed db) is usually the root cause of
   ECONNREFUSED-style errors in the others.
```

The `read-logs` skill and `/dokploy-dev:compose-logs <name>` command run this loop for you. For build (not runtime) failures, use `deployment-readLogs { deploymentId, tail }` instead.

---

## Best Practices

### Project organization

- Create one project per logical application or environment (e.g. `production`, `staging`, `databases`).
- Use descriptive project names. Projects are the primary grouping mechanism in the Dokploy dashboard.
- Use `project-all` to find existing projects before creating new ones. Avoid duplicate projects.

### Application deployment

- Always call `application-saveBuildType` before the first deployment. The default may not match your application.
- Use `application-redeploy` for subsequent deployments after config changes. Do not delete and recreate.
- Use `application-reload` for zero-downtime restarts when only environment variables changed.
- Set environment variables with `application-saveEnvironment` before deploying. Deploying first and then setting env vars requires a redeploy.
- Check deployment status after calling `application-deploy` — the call is asynchronous and returns immediately. Use `deployment-all` with `applicationId` filter and `application-readLogs` for failure diagnosis.

### Domain management

- Always call `domain-validateDomain` after creating a domain. Do not assume DNS is configured.
- For HTTPS, ensure DNS is pointing to the server before creating the domain with `certificateType: "letsencrypt"`. Let's Encrypt validation will fail otherwise.
- Use `domain-generateDomain` for quick testing without DNS setup. These `.traefik.me` domains resolve to the server IP automatically.

### Database operations

- All six database types follow the same tool pattern. Learn one, and you know all six.
- Always call `{type}-deploy` after `{type}-create`. Creation only registers the resource in Dokploy.
- Use `{type}-saveExternalPort` only when external access is needed (e.g. for development tools). In production, prefer internal Docker networking.
- Never use `{type}-rebuild` in production without confirming volume persistence. Rebuild destroys the container.
- Rotate credentials with `{type}-changePassword` rather than recreating the database.

### General

- Use `project-all` and `application-one` to inspect current state before making changes.
- Prefer `redeploy` over `deploy` for updates — `deploy` may trigger a full rebuild from source.
- Always confirm destructive operations (`project-remove`, `application-delete`, `{type}-remove`) with the user before executing.

---

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| `"Project not found"` | Invalid `projectId` | Call `project-all` to get valid IDs |
| `"Application not found"` | Invalid `applicationId` | Call `project-one` with the project ID to list its applications |
| `"appName already exists"` | Duplicate `appName` | Choose a unique `appName` — it must be unique across the entire server |
| `"Build failed"` | Source code or Dockerfile error | Check application logs with `application-readLogs`; fix source and redeploy |
| `"Deploy timeout"` | Container takes too long to start | Check health check config; increase timeout or fix startup |
| `"Port already in use"` | Another container uses the same port | Choose a different `externalPort` or stop the conflicting container |
| `"Certificate issuance failed"` | DNS not pointing to server | Verify DNS A record, then retry. Remove and recreate the domain if needed |
| `"Provider not configured"` | No Git source set on application | Call `application-saveGithubProvider` (or another provider) before deploying |
| `"Queue is full"` | Too many pending deployments | Call `application-cleanQueues` to clear stuck deployments |
| `"Database connection refused"` | Database not deployed or port not exposed | Call `{type}-deploy` first, then `{type}-saveExternalPort` if external access is needed |
| MCP timeout | Network issue or Dokploy server overloaded | Retry the call; check server health with `curl $DOKPLOY_URL/api/settings.health` |
| `"Unauthorized"` | Invalid or expired API key | Regenerate the API key in the Dokploy dashboard and update `userConfig` |
| `"UNAUTHORIZED"` from REST API | Wrong auth header format | Dokploy uses `x-api-key: <token>` header, NOT `Authorization: Bearer <token>`. This applies to both trpc endpoints and direct REST calls |

---

## Tool Count Summary

The official `@dokploy/mcp` server exposes **546 tools across 50 categories**. Categories covered by this skill in detail:

| Category | Approx Count | Prefix |
|---|---|---|
| Project Management | 9 | `project-` |
| Application Management | 31 | `application-` |
| Domain Management | 9 | `domain-` |
| Compose Management | 31 | `compose-` |
| PostgreSQL | 16 | `postgres-` |
| MySQL | 16 | `mysql-` |
| MariaDB | 16 | `mariadb-` |
| MongoDB | 16 | `mongo-` |
| Redis | 16 | `redis-` |
| LibSQL | 14 | `libsql-` |
| Deployment History | 9 | `deployment-` |
| AI Router | 14 | `ai-` |
| Docker Introspection | 12 | `docker-` |
| Settings / Cleanup / Health | ~30 | `settings-` |
| Schedule | 6 | `schedule-` |
| Patch | 12 | `patch-` |
| Volume Backups | 6 | `volumeBackups-` |
| Preview Deployments | 4 | `previewDeployment-` |

Use `DOKPLOY_ENABLED_TAGS` in `.mcp.json` to restrict exposure to a subset of categories.

---

## Other categories (reference only)

The remaining categories use the same `mcp__dokploy__<category>-<op>` pattern. **Every one of these — and every operation in every category above — is enumerated with its exact params in the complete index:** [`api-reference/references/api-full-index-resources.md`](../api-reference/references/api-full-index-resources.md) and [`api-full-index-platform.md`](../api-reference/references/api-full-index-platform.md) (all 546 operations, v0.29.14 schema). The themed files below add curated usage notes for some of them.

| Category | Prefix | Purpose | Reference |
|---|---|---|---|
| Environments | `environment-` | Per-project environments | `api-projects-apps.md` |
| Rollback | `rollback-` | Roll a resource back to a previous deployment | `ai-and-debugging.md` |
| Backups | `backup-` | Resource-aware backups (DB-aware dumps) | `api-server-settings.md` |
| Registries | `registry-` | Private Docker registry credentials | `api-compose-docker.md` |
| Destinations | `destination-` | S3 / R2 / remote destinations for backups | `api-server-settings.md` |
| Mounts | `mounts-` | File/volume mounts | `api-compose-docker.md` |
| Ports | `port-` | Exposed host ports | `api-domains-certs.md` |
| Redirects | `redirects-` | HTTP redirect rules | `api-domains-certs.md` |
| Security | `security-` | Per-app security rules / basic auth | `api-domains-certs.md` |
| Certificates | `certificates-` | Custom TLS certificates | `api-domains-certs.md` |
| Notifications | `notification-` | Discord, Slack, Telegram, Email, Gotify, Ntfy, Mattermost, Teams, Pushover, Resend, Lark, custom webhooks | `api-server-settings.md` |
| Servers | `server-` | Managed remote servers (add, setup, metrics, security, SSH) | `api-server-settings.md` |
| Clusters / Swarm | `cluster-` / `swarm-` | Docker Swarm cluster nodes, stats, container inspection | `api-server-settings.md` |
| SSH Keys | `sshKey-` | Manage SSH keys used for git or server access | `api-server-settings.md` |
| Git Providers | `gitProvider-` / `github-` / `gitlab-` / `bitbucket-` / `gitea-` | Per-provider CRUD, branches, repos, test connection | `api-projects-apps.md` |
| Organizations | `organization-` | Multi-tenant orgs, invitations, members | `api-server-settings.md` |
| Users | `user-` | Users, API keys, permissions, invitations, bookmarks | `api-server-settings.md` |
| Custom Roles | `customRole-` | Fine-grained role definitions | `api-server-settings.md` |
| SSO | `sso-` | Single sign-on providers + trusted origins | `api-server-settings.md` |
| Forward Auth | `forwardAuth-` | SSO login gate (oauth2-proxy + Traefik) in front of app domains — enterprise | `api-domains-certs.md` |
| SCIM | `scim-` | SCIM 2.0 user provisioning — enterprise | `api-full-index-platform.md` |
| Tags | `tag-` | Tag resources for grouping | `api-projects-apps.md` |
| Audit Log | `auditLog-` | Read audit log entries | `api-server-settings.md` |
| License Key | `licenseKey-` | Enterprise license + feature toggles | `api-server-settings.md` |
| Whitelabeling | `whitelabeling-` | Branding customization | `api-server-settings.md` |
| Stripe | `stripe-` | Cloud billing integration | `api-server-settings.md` |
| Admin | `admin-` | Admin-only operations (e.g. monitoring setup) | `api-server-settings.md` |

For the authoritative tool list, see https://github.com/Dokploy/mcp.

---

## REST API Fallback

If MCP tools fail (e.g. "Resource not found" errors), use the Dokploy trpc REST API directly via `curl`. Dokploy uses **`x-api-key`** header for authentication (NOT `Authorization: Bearer`). API paths live at `/api/…` under the base `$DOKPLOY_URL`.

### Authentication

```bash
# Correct — use x-api-key header and /api path
curl -s "$DOKPLOY_URL/api/project.all" \
  -H "x-api-key: $DOKPLOY_API_KEY"

# Wrong — Bearer auth returns 401
curl -s "$DOKPLOY_URL/api/project.all" \
  -H "Authorization: Bearer $DOKPLOY_API_KEY"
```

### Read operations (GET with input)

URL-encode the JSON input as a query parameter:

```bash
curl -s "$DOKPLOY_URL/api/application.one?input=%7B%22json%22%3A%7B%22applicationId%22%3A%22abc123%22%7D%7D" \
  -H "x-api-key: $DOKPLOY_API_KEY"
```

### Write operations (POST with JSON body)

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.deploy" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"json":{"applicationId":"abc123"}}'
```

### Health check (no auth required)

```bash
curl -s "$DOKPLOY_URL/api/settings.health"
```
