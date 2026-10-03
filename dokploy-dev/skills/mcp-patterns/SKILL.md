---
name: mcp-patterns
description: "This skill should be used when deploying applications, managing projects, provisioning databases, configuring domains, working with Docker Compose, or performing any Dokploy operation via MCP tools. Triggers: \"deploy app\", \"create project\", \"add domain\", \"provision database\", \"dokploy compose\", \"manage dokploy\"."
---

# Dokploy MCP Tool Patterns

The official `@dokploy/mcp` server exposes **604 tools across 57 categories (Dokploy v0.30.7, `@dokploy/mcp` 0.30.7)**. Each tool is prefixed with `mcp__plugin_dokploy-dev_dokploy__`. This skill covers every category developers and operators use day-to-day: projects, applications, domains, compose, six database types, deployment history, the cross-cutting recovery chain, the AI router, Docker introspection and host diagnostics, networks, vault and DNS providers, settings/cleanup/health, schedules, patches, volume backups, and preview deployments. **Responses are redacted by default (`DOKPLOY_REDACT_ENV=true` since `@dokploy/mcp` 0.30.0) — read "Redaction" below before diagnosing env or credential problems.** Categories not fully tabled here are listed at the end with a pointer to the matching reference file.

To reduce the exposed tool surface, set these in the `.mcp.json` `env` block (a category is the operation prefix, matched case-insensitively — `previewDeployment`, `volumeBackups`, `dockerVolume` …):

- `DOKPLOY_TOOL_PRESET` (≥ 0.30.0): `all` (default), `minimal` = project + application, `core` = project + server + application, `deploy` = project + environment + server + application + compose + domain + deployment, `databases` = the six database categories, `git` = github + gitlab + bitbucket + gitea + gitProvider + registry + sshKey.
- `DOKPLOY_ENABLED_TAGS`: explicit comma-separated list (e.g. `project,application,domain,compose,postgres,settings,deployment,docker,ai,rollback,schedule`); wins over the preset.
- `DOKPLOY_DISABLED_TAGS` (≥ 0.30.0): categories to drop afterwards, applied last.

No preset contains `docker`, `ai`, `settings`, `rollback` or `schedule`, which `/dokploy-dev:debug` uses — list them in `DOKPLOY_ENABLED_TAGS` when you trim the toolset.

---

## Redaction (`DOKPLOY_REDACT_ENV`, on by default since 0.30.0)

The MCP server rewrites every response (and its own log lines) before the model sees it: a field whose name **ends with** an entry of the redaction list becomes the string `[REDACTED]`. Matching is case-insensitive, at any depth, on the key only. The default list: `env`, `buildArgs`, `buildSecrets`, `previewBuildSecrets`, `composeFile`, `dockerCompose`, `environment`, `password` and the `*Password` fields, `token` and the `*Token` fields, `secret`, `clientSecret`, `apiKey`, `secretAccessKey`, `accessKey`, `licenseKey`, `privateKey`, `sshKey`, `customGitSSHKey`, `dockerAuth`.

| You call | You get |
|---|---|
| `application-one`, `compose-one`, `{db}-one` | `env`, `buildArgs`, `composeFile`, passwords = `[REDACTED]` — not even the variable **names**. A `null` stays `null` (`env: null` = never set); `[REDACTED]` means *a string, possibly empty* |
| `docker-getConfig` | the container's `Env` = `[REDACTED]` |
| `settings-getOpenApiDocument` | 27 operations (every `*-saveEnvironment`, `*-changePassword`, `*-refreshToken`, `user-createApiKey`, …) come back as bare `[REDACTED]`, and secret-named request fields lose their schema in 73 more — regenerate API indexes over REST, never through MCP |
| any create/update tool | **arguments are not redacted** — writes work normally; only the response echo is redacted |
| `docker-readContainerFile`, `dockerVolume-readVolumeFile` | the file body is an opaque string, so it is **not** redacted — do not read `.env`-style files through these tools unless you want the values in context |

Rules that follow:

1. **Diagnose from names and logs first.** A stack trace or `getaddrinfo ENOTFOUND db` shows the failing host without exposing a secret; `docker-getContainersByAppLabel`, `application-readLogs` and `deployment-readLogs` are unaffected.
2. **Never write `[REDACTED]` back.** `application-saveEnvironment` / `compose-saveEnvironment` replace the *whole* `env` string (and, for applications, `buildArgs`/`buildSecrets`), so a read-modify-write through MCP would overwrite every variable with the placeholder. Change one variable with the REST recipe below, or supply the complete new value yourself.
3. **Reading values on purpose** = set `DOKPLOY_REDACT_ENV=false` in `.mcp.json` and reconnect the `dokploy` server, or call REST/CLI (never redacted). Anything printed lands in the model context, so prefer pipes that do not print values:

```bash
# variable NAMES only (values never printed)
curl -s -G "$DOKPLOY_URL/api/application.one" -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode "applicationId=<id>" \
  | jq -r '(.env // "") | split("\n")[] | select(test("^[A-Za-z_][A-Za-z0-9_]*=")) | split("=")[0]'

# change ONE variable, keep the rest (env + companion fields are sent as a unit)
NEW='<new-value>'
curl -s -G "$DOKPLOY_URL/api/application.one" -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode "applicationId=<id>" \
  | jq --arg v "DATABASE_URL=$NEW" '{applicationId, buildArgs, buildSecrets, createEnvFile,
      env: ((.env // "") | sub("(?m)^DATABASE_URL=.*"; $v))}' \
  | curl -s -X POST "$DOKPLOY_URL/api/application.saveEnvironment" \
      -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" -d @-
```

`DOKPLOY_REDACT_FIELDS` **replaces** the default list (it is not additive) — set it only to narrow or widen on purpose.

For secrets that should never be pasted at all, v0.30 can resolve them at deploy time from an external manager — see "Vault providers" below.

---

## Project Management (11 tools)

Projects are the top-level container. Every application, database, and compose stack belongs to a project. Always create or identify a project before creating resources.

| Tool | Description | Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__project-all` | List all projects | None |
| `mcp__plugin_dokploy-dev_dokploy__project-allForPermissions` | List projects the current token can access | None |
| `mcp__plugin_dokploy-dev_dokploy__project-one` | Get a single project by ID | `projectId` (string, required) |
| `mcp__plugin_dokploy-dev_dokploy__project-create` | Create a new project | `name` (string, required), `description` (string, optional) |
| `mcp__plugin_dokploy-dev_dokploy__project-update` | Update project metadata | `projectId` (string, required), `name` (string), `description` (string) |
| `mcp__plugin_dokploy-dev_dokploy__project-duplicate` | Duplicate an environment's resources | `sourceEnvironmentId` (required), `name` (required), `description`, `includeServices`, `selectedServices`, `duplicateInSameProject` |
| `mcp__plugin_dokploy-dev_dokploy__project-remove` | Delete a project and all its resources | `projectId` (string, required) |
| `mcp__plugin_dokploy-dev_dokploy__project-search` | Search projects (free-text key is `q`; default `limit` 20) | `q`, `name`, `description`, `limit`, `offset` |
| `mcp__plugin_dokploy-dev_dokploy__project-homeStats` | Aggregate dashboard/home stats across projects (counts and running/error/idle status) | None |
| `mcp__plugin_dokploy-dev_dokploy__project-onboardingStatus` | Dokploy Cloud onboarding-wizard state (trial, plan, project count) | None |
| `mcp__plugin_dokploy-dev_dokploy__project-completeOnboarding` | Mark the onboarding wizard as done | None |

### Usage notes

- `project-all` returns an array of project objects, each containing `projectId`, `name`, `description`, and nested arrays of applications, databases, and compose stacks.
- `project-remove` is destructive — it deletes all applications, databases, and compose stacks within the project. Confirm with the user before calling.
- `project-duplicate` creates a full copy including all nested resources. Use it for staging/production environment cloning.

---

## Overview Dashboard (3 tools + `server-getServices`, v0.30.0+)

The project Overview page (Services, Backups, Domains at a glance) is available as three parameter-less reads; use them for `/dokploy-dev:status`-style summaries instead of walking `project-all` → `project-one`.

| Tool | Description | Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__overview-services` | Services (applications, compose stacks, databases) with their status | None |
| `mcp__plugin_dokploy-dev_dokploy__overview-backups` | Configured backups and their state | None |
| `mcp__plugin_dokploy-dev_dokploy__overview-domains` | Domains across projects | None |
| `mcp__plugin_dokploy-dev_dokploy__server-getServices` | Services deployed on one remote server | `serverId` (required) |

---

## Application Management (32 tools)

Applications are the primary deployment unit. They support multiple source types (GitHub, GitLab, Bitbucket, Gitea, generic Git, Docker image) and build types (Nixpacks, Dockerfile, Buildpacks, Docker image).

### Core CRUD + Search (5 tools)

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__application-one` | Get application details | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-create` | Create a new application | `environmentId` (required), `name` (required), `appName` (unique slug), `serverId`, `sourceType` (`github` \| `docker` \| `git` \| `gitlab` \| `bitbucket` \| `gitea` \| `drop`) |
| `mcp__plugin_dokploy-dev_dokploy__application-update` | Update application settings (also per-service networks: `networkIds`, `detachDokployNetwork`, `networkSwarm` — see "Docker Networks") | `applicationId`, plus any updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__application-delete` | Delete an application | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-search` | Search applications (all filters optional, AND-combined). **The free-text key is `q`; an unknown key such as `query` is silently stripped and the call returns unfiltered rows** (default `limit` 20, max 100) | `q`, `name`, `appName`, `description`, `repository`, `owner`, `dockerImage`, `projectId`, `environmentId`, `limit`, `offset` |

### Lifecycle (5 tools)

| Tool | Description | Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__application-deploy` | Trigger a new deployment | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-redeploy` | Redeploy with latest config | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-start` | Start a stopped application | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-stop` | Stop a running application | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-reload` | Reload application (zero-downtime) | `applicationId`, `appName` (both required) |

**Key distinction:** `deploy` builds from source and deploys. `redeploy` re-runs the last deployment with current config. `reload` restarts the running container without rebuilding.

### Git Provider Configuration (6 tools)

Connect an application to a Git source. Only one provider can be active at a time.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__application-saveGithubProvider` | Connect to GitHub | `applicationId`, `repository` (repo name only — NOT full URL), `branch`, `owner`, `githubId`, `enableSubmodules` |
| `mcp__plugin_dokploy-dev_dokploy__application-saveGitlabProvider` | Connect to GitLab | `applicationId`, `repository`, `branch`, `gitlabProjectId` |
| `mcp__plugin_dokploy-dev_dokploy__application-saveBitbucketProvider` | Connect to Bitbucket | `applicationId`, `repository`, `branch`, `owner` |
| `mcp__plugin_dokploy-dev_dokploy__application-saveGiteaProvider` | Connect to Gitea | `applicationId`, `repository`, `branch`, `owner` |
| `mcp__plugin_dokploy-dev_dokploy__application-saveGitProvider` | Connect to any Git URL | `applicationId`, `customGitUrl`, `customGitBranch`, `customGitBuildPath`, `enableSubmodules`, `watchPaths` |
| `mcp__plugin_dokploy-dev_dokploy__application-disconnectGitProvider` | Remove Git connection | `applicationId` |

**GitHub provider critical note:** The `repository` parameter for `saveGithubProvider` must be the **repository name only** (e.g. `"my-repo"`), NOT the full URL. Dokploy constructs the clone URL as `github.com/{owner}/{repository}` — passing a full URL like `https://github.com/org/repo` causes a broken double-URL (`github.com/org/https://github.com/org/repo`). You also need the `githubId` — get it from `gitProvider-getAll` (then filter by type `github`). Required fields: `applicationId`, `repository`, `branch`, `owner`, `githubId`, `enableSubmodules`, `triggerType` (default `"push"`), `watchPaths` (array, use `[]` if none), `buildPath` (default `"/"`).

**Generic Git provider note:** `saveGitProvider` requires ALL of: `applicationId`, `customGitUrl` (full SSH/HTTPS URL), `customGitBranch`, `customGitBuildPath` (e.g. `"/"`), `enableSubmodules` (boolean), `watchPaths` (array). Optionally `customGitSSHKeyId` for private repos. Omitting any required field causes a 400 validation error.

### Build & Environment Configuration (3 tools)

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__application-saveBuildType` | Set build method | `applicationId`, `buildType` (`nixpacks`, `dockerfile`, `docker`, `buildpacks`) |
| `mcp__plugin_dokploy-dev_dokploy__application-saveEnvironment` | Set environment variables | `applicationId`, `env` (newline-separated KEY=VALUE string) |
| `mcp__plugin_dokploy-dev_dokploy__application-saveDockerProvider` | Set Docker image source (the tag is part of `dockerImage`, e.g. `nginx:1.27`) | `applicationId`, `dockerImage`, `username`, `password`, `registryUrl` (all required — empty strings for a public image) |

### Monitoring, Logs & Config (4 tools)

| Tool | Description | Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__application-readAppMonitoring` | Read monitoring metrics (CPU, memory, network) | `appName` (required — the app's container/service name, not `applicationId`) |
| `mcp__plugin_dokploy-dev_dokploy__application-readLogs` | Read the app container's runtime stdout/stderr (v0.29.0+) | `applicationId` (required), `tail` (1–10000, default 100), `since` (`all` or `<n>{s\|m\|h\|d}`), `search` (substring) |
| `mcp__plugin_dokploy-dev_dokploy__application-readTraefikConfig` | Read current Traefik routing config | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-updateTraefikConfig` | Update Traefik routing rules | `applicationId`, `traefikConfig` (YAML string) |

### Deployment & Queue Management (8 tools)

| Tool | Description | Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__application-move` | Move application to another environment | `applicationId`, `targetEnvironmentId` |
| `mcp__plugin_dokploy-dev_dokploy__application-markRunning` | Force-mark application as running | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-cancelDeployment` | Cancel an in-progress deployment | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-killBuild` | Kill the currently-running build process | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-refreshToken` | Regenerate application webhook token | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-cleanQueues` | Clear stuck deployment queues | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-clearDeployments` | Purge historical deployment records | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__application-dropDeployment` | Deploy an uploaded zip (the `drop` source type) — multipart, not a history cleanup. **The MCP tool has an empty schema and cannot send the file; use REST `curl -F`** (below). The CLI command declares no options either | `applicationId`, `zip` (file), `dropBuildPath` |

`application-deployNginxQuickstart { environmentId, serverId? }` creates and deploys the "Hello World" nginx demo application the Cloud onboarding wizard uses (on Dokploy Cloud a `serverId` is required) — a smoke test for a fresh environment, not a deploy tool for your own app.

### Application usage notes

- `application-create` requires `environmentId` and `name`. The `appName` parameter becomes the container name and must be unique across the server.
- **Resources live under a project's ENVIRONMENT** (default `production`) — applications, databases, and compose stacks are created with an `environmentId`, not a `projectId`. Resolve it via `project-one { projectId }` → `environments[]` or `environment-byProjectId { projectId }`.
- `application-saveEnvironment` expects **all** of these parameters: `applicationId`, `env` (newline-separated KEY=VALUE string), `buildArgs` (newline-separated KEY=VALUE string for Docker build args — use empty string if none), `buildSecrets` (empty string if none), `createEnvFile` (boolean). Omitting any parameter causes a 400 validation error. Build args are critical for frameworks like Next.js where env vars (e.g. `NEXT_PUBLIC_*`) must be available during `docker build`.
- `application-saveBuildType` requires **all** of these parameters: `applicationId`, `buildType` (`nixpacks`, `dockerfile`, `docker`, `buildpacks`), `dockerfile` (filename, e.g. `"Dockerfile"`), `dockerContextPath` (e.g. `"."`), `dockerBuildStage` (empty string if none), `herokuVersion` (empty string if N/A), `railpackVersion` (empty string if N/A). Omitting any parameter causes a 400 validation error. When a project has a `Dockerfile`, default to `buildType: "dockerfile"` — ask the user to confirm.
- After calling `application-deploy`, the deployment runs asynchronously. Check deployment status via `deployment-all` filtered by `applicationId` to confirm completion. On failure, read logs with `application-readLogs` and iterate.
- `application-markRunning` is a manual override for stuck states. Use only when the container is running but Dokploy shows it as stopped.
- `application-cleanQueues` clears the deployment queue. Use when deployments are stuck in "queued" state. `application-killBuild` aborts a running build immediately.

---

## Domain Management (10 tools)

Domains map hostnames to applications or compose services. Dokploy uses Traefik as the reverse proxy.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__domain-byApplicationId` | List domains for an application | `applicationId` |
| `mcp__plugin_dokploy-dev_dokploy__domain-byComposeId` | List domains for a compose stack | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__domain-one` | Get a single domain by ID | `domainId` |
| `mcp__plugin_dokploy-dev_dokploy__domain-create` | Create a domain mapping | See below |
| `mcp__plugin_dokploy-dev_dokploy__domain-update` | Update domain settings (v0.30.0+: `enabled`) | `domainId`, plus updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__domain-toggleEnable` | **Flip** a domain's `enabled` flag (v0.30.0+): the route leaves Traefik but certificate, path and middleware settings stay. Applications change instantly; compose domains are labels and only change on the next deploy | `domainId` |
| `mcp__plugin_dokploy-dev_dokploy__domain-delete` | Delete a domain | `domainId` |
| `mcp__plugin_dokploy-dev_dokploy__domain-validateDomain` | Check DNS resolution for a domain | `domain` (required — the hostname string, NOT domainId), `serverId` (optional — validate against that remote server's IPs instead of the Dokploy host; `serverIp` was replaced by `serverId` in v0.30) |
| `mcp__plugin_dokploy-dev_dokploy__domain-generateDomain` | Auto-generate a subdomain | `appName` (required), `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__domain-canGenerateTraefikMeDomains` | Check if .traefik.me domains are available | None |

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
| `enabled` | boolean | No | (v0.30.0+, `domain-update`) `false` takes the route out of Traefik without deleting the domain |

### Domain usage notes

- Always call `domain-validateDomain` after creating a domain to confirm DNS is pointing to the server.
- `domain-generateDomain` creates a `.traefik.me` wildcard subdomain that resolves to the server's IP. Useful for development/testing without DNS setup.
- To enable HTTPS with Let's Encrypt, set `https: true` and `certificateType: "letsencrypt"`. The domain must have valid DNS pointing to the server for certificate issuance to succeed.
- A single application can have multiple domains. Use this for aliases or www/non-www setups.
- To list domains attached to a compose stack, use `domain-byComposeId` (the old `compose-fetchDomains` tool was removed — this is its direct replacement).
- **DNS records:** `domain-create` does not create the DNS record. v0.30 can manage records at Cloudflare, Route 53, Porkbun, Infomaniak or OVHcloud through the `dnsProvider-*` tools (see "DNS Providers") — Dokploy's docs describe that integration as standalone, not wired into the add-domain flow, so create the record first (or in parallel) and then `domain-create` + `domain-validateDomain`.

---

## Compose Management (31 tools)

Docker Compose stacks deploy multi-container applications defined by a `docker-compose.yml` file.

### Core CRUD & Lifecycle

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__compose-one` | Get compose stack details | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-create` | Create a compose stack | `environmentId` (required), `name` (required), `appName`, `composeType`, `composeFile`, `serverId`, `sourceType` (`git` \| `github` \| `gitlab` \| `bitbucket` \| `gitea` \| `raw`) |
| `mcp__plugin_dokploy-dev_dokploy__compose-update` | Update compose settings + source (see note below); per-service networks via `serviceNetworks` (see "Docker Networks") | `composeId`, updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__compose-delete` | Delete a compose stack | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-deploy` | Deploy the compose stack | `composeId`, optional `title`, `description`, `freshVolumes` (v0.30.5+, "Deploy with Fresh Volumes": runs `docker compose down --volumes` first — **permanently deletes the stack's volumes**; `docker-compose` type only, not swarm stacks; confirm and back up first) |
| `mcp__plugin_dokploy-dev_dokploy__compose-redeploy` | Redeploy with current config | `composeId`, optional `title`, `description`, `freshVolumes` (same warning) |
| `mcp__plugin_dokploy-dev_dokploy__compose-start` | Start compose services | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-stop` | Stop all compose services | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-move` | Move compose stack to another environment | `composeId`, `targetEnvironmentId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-search` | Search compose stacks (free-text key is `q`, not `query`; default `limit` 20) | `q`, `name`, `appName`, `description`, `projectId`, `environmentId`, `limit`, `offset` |

### Source / Git Configuration

Unlike applications, compose git source is set **via `compose-update`**, not a separate `saveGithubProvider` call. Pass `sourceType` (`github` / `gitlab` / `bitbucket` / `gitea` / `git` / `raw` for an inline compose file), `repository`, `branch`, `owner`, `composePath`, and provider-specific IDs (`githubId`, `gitlabProjectId`, etc.) in a single update.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__compose-disconnectGitProvider` | Remove Git connection | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-fetchSourceType` | Detect source type from repo | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-import` | Import compose stack from external source | per-source fields |

### Templates

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__compose-templates` | List available compose templates | None |
| `mcp__plugin_dokploy-dev_dokploy__compose-deployTemplate` | Deploy a compose template | `id` (template id), `environmentId`, `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-processTemplate` | Render a template with variables | `base64` (required — the encoded template), `composeId` (required) |
| `mcp__plugin_dokploy-dev_dokploy__compose-previewTemplate` | Preview a rendered template before deploying | `base64` (required), `appName` (required), `serverId` |

### Build, Config & Logs

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__compose-getDefaultCommand` | Get default docker compose command | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-getConvertedCompose` | Validate and render the compose file | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-loadServices` | List services defined in the stack | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-loadMountsByService` | Inspect mounts per service | `composeId`, `serviceName` |
| `mcp__plugin_dokploy-dev_dokploy__compose-getTags` | List the template tags of the template registry | optional `baseUrl` |
| `mcp__plugin_dokploy-dev_dokploy__compose-randomizeCompose` | Generate random ports for services | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-saveEnvironment` | Set environment variables (replaces the whole `env` string) | `composeId`, `env`, `createEnvFile` |
| `mcp__plugin_dokploy-dev_dokploy__compose-readLogs` | Read ONE container's runtime logs. `containerId` is **required** — a stack has many containers, so enumerate first (see note) and call once per container | `composeId` (required), `containerId` (required), `tail`, `since`, `search` |

### Deployment Management

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__compose-cancelDeployment` | Cancel in-progress deployment | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-killBuild` | Kill the running build | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-cleanQueues` | Clear stuck deployment queue | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-clearDeployments` | Purge deployment history | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-refreshToken` | Regenerate webhook token | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__compose-isolatedDeployment` | **DEPRECATED (v0.30.0)** — clones the stack's source and returns the compose file; it rewrites it with a name suffix only when the stack's `isolatedDeployment` flag is already on (otherwise the cloned file comes back unmodified), the default suffix being the compose `appName`. It does **not** toggle anything; the mode itself is `compose-update { isolatedDeployment }`, still in Compose's advanced settings. Attaching/detaching networks per service (`serviceNetworks`, "Docker Networks") replaces the feature | `composeId`, optional `suffix` |

### Compose usage notes

- `compose-create` creates the stack record. After creation, set git source / compose file content via `compose-update`, then call `compose-deploy`.
- **Setting a git source for compose:** Use `compose-update` with `sourceType` and the matching provider fields. The old `compose-saveGithubProvider` / `compose-saveGitlabProvider` tools were consolidated into `compose-update` in the official MCP server.
- **Listing domains for a compose stack:** Use `domain-byComposeId` (not the removed `compose-fetchDomains`).
- `compose-saveEnvironment` works the same as the application equivalent — newline-separated `KEY=VALUE` string; it **replaces** the whole `env`, so see "Redaction" before editing one variable. Since v0.30.2/v0.30.3 values written to the stack's `.env` are not quoted and `${VAR}` interpolation is preserved.
- `compose-getConvertedCompose` validates the compose file by rendering it with current env vars. Call this before `compose-deploy` to catch YAML errors early.
- **Reading logs for a stack = read every container.** `compose-readLogs` is per-container and requires `containerId`. To read all of them: `compose-one { composeId }` → `appName`/`composeType`; then `docker-getContainersByAppNameMatch { appName, appType: "docker-compose" }` (compose) or `docker-getStackContainersByAppName { appName }` (swarm) to list containers (`{ containerId, name, state, status }`); then loop `compose-readLogs { composeId, containerId, tail, since, search }` for each. The `read-logs` skill and `/dokploy-dev:compose-logs` automate this.

---

## Database Management (5 types × 16 tools; LibSQL has 14)

Dokploy supports six managed database types. Five of them (postgres, mysql, mariadb, mongo, redis) have an identical set of 16 tools following the same naming pattern (the official server adds `changePassword`, `readLogs`, and `search` on top of the 13 core tools). **LibSQL has only 14**: there is no `libsql-changePassword` and no `libsql-search`, and its port tool is `libsql-saveExternalPorts` (plural) taking three port fields (`externalPort`, `externalGRPCPort`, `externalAdminPort`).

### Tool pattern per database type

Replace `{type}` with `postgres`, `mysql`, `mariadb`, `mongo`, `redis`, or `libsql`:

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__{type}-create` | Provision a new database | `environmentId` (required), `name` (required), plus per-type required fields (see notes) |
| `mcp__plugin_dokploy-dev_dokploy__{type}-one` | Get database details | `{type}Id` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-update` | Update database config (also per-service networks: `networkIds`, `detachDokployNetwork`, `networkSwarm` — see "Docker Networks") | `{type}Id`, updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__{type}-remove` | Delete a database | `{type}Id` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-move` | Move to another environment | `{type}Id`, `targetEnvironmentId` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-search` | Search databases (**not libsql**; free-text key is `q`, not `query`; default `limit` 20) | `q`, `name`, `appName`, `description`, `projectId`, `environmentId`, `limit`, `offset` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-deploy` | Deploy/start the database container | `{type}Id` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-start` | Start a stopped database | `{type}Id` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-stop` | Stop a running database | `{type}Id` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-reload` | Reload database container | `{type}Id` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-rebuild` | Rebuild database container from scratch | `{type}Id` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-changeStatus` | Force status change | `{type}Id`, `applicationStatus` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-changePassword` | Rotate the database password (**not libsql**) | `{type}Id`, `password` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-saveExternalPort` | Expose database on a host port (libsql: `libsql-saveExternalPorts`, plural) | `{type}Id`, `externalPort` (libsql also `externalGRPCPort`, `externalAdminPort`) |
| `mcp__plugin_dokploy-dev_dokploy__{type}-saveEnvironment` | Set database environment variables | `{type}Id`, `env` |
| `mcp__plugin_dokploy-dev_dokploy__{type}-readLogs` | Read the DB container's runtime logs | `{type}Id` (required), `tail`, `since`, `search` |

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
| `mcp__plugin_dokploy-dev_dokploy__deployment-all` | List deployments for an application | `applicationId` (required) |
| `mcp__plugin_dokploy-dev_dokploy__deployment-allByCompose` | List deployments for a compose stack | `composeId` |
| `mcp__plugin_dokploy-dev_dokploy__deployment-allByServer` | List deployments for a server | `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__deployment-allByType` | Filter by resource id + type | `id` (required), `type` (required) |
| `mcp__plugin_dokploy-dev_dokploy__deployment-allCentralized` | List deployments across all resources | None |
| `mcp__plugin_dokploy-dev_dokploy__deployment-queueList` | Inspect the deployment queue | None |
| `mcp__plugin_dokploy-dev_dokploy__deployment-killProcess` | Kill a running deployment process | `deploymentId` |
| `mcp__plugin_dokploy-dev_dokploy__deployment-removeDeployment` | Remove a deployment record | `deploymentId` |
| `mcp__plugin_dokploy-dev_dokploy__deployment-readLogs` | Read a deployment's **build log** (central to debugging failed builds) | `deploymentId` (required), `tail` |

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
| 5 | `deployment-removeDeployment` | Remove a single bad deployment record (do NOT use `application-dropDeployment` — that tool uploads a zip and deploys it) |
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
| `mcp__plugin_dokploy-dev_dokploy__ai-getEnabledProviders` | List enabled providers; empty means AI is not available | None |
| `mcp__plugin_dokploy-dev_dokploy__ai-getAll` | List all configured providers (enabled and disabled) | None |
| `mcp__plugin_dokploy-dev_dokploy__ai-one` / `mcp__plugin_dokploy-dev_dokploy__ai-get` | Read one provider's config | `aiId` |
| `mcp__plugin_dokploy-dev_dokploy__ai-getModels` | List models a candidate endpoint advertises | `apiUrl`, `apiKey` (NOT aiId) |
| `mcp__plugin_dokploy-dev_dokploy__ai-create` | Add a provider | `name`, `apiKey`, `apiUrl`, `model`, `isEnabled` |
| `mcp__plugin_dokploy-dev_dokploy__ai-update` | Update a provider's config | `aiId`, updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__ai-delete` | Remove a provider | `aiId` |
| `mcp__plugin_dokploy-dev_dokploy__ai-testConnection` | Validate credentials and reachability | `apiUrl`, `apiKey`, `model` (tests a candidate payload BEFORE saving — does NOT take aiId) |
| `mcp__plugin_dokploy-dev_dokploy__ai-getCustomProviders` | List org-defined custom provider presets (v0.29.13+) | None |
| `mcp__plugin_dokploy-dev_dokploy__ai-saveCustomProviders` | Save org custom provider presets | `providers` (array, required) |
| `mcp__plugin_dokploy-dev_dokploy__ai-deploy` | Deploy the AI orchestrator side-service (admin-only) | none / admin params |
| `mcp__plugin_dokploy-dev_dokploy__ai-analyzeLogs` | **Headline:** AI-summarise log text you fetched | `aiId` (enabled provider), `logs` (the log text from a `*-readLogs` call), `context` (`"build"` for `deployment-readLogs`, `"runtime"` for app/compose/db logs) — NOT `deploymentId` |
| `mcp__plugin_dokploy-dev_dokploy__ai-suggest` | Ask the LLM for next-step recommendations | `aiId` (required), `input` (required — the question/state text), `serverId` (optional) |

`apiUrl` is OpenAI-compatible. Common providers: OpenAI (`https://api.openai.com/v1`), OpenRouter (`https://openrouter.ai/api/v1`), Groq (`https://api.groq.com/openai/v1`), Gemini (`https://generativelanguage.googleapis.com/v1beta/openai`), Ollama (`http://host:11434/v1`). See the `ai-assist` skill for the full setup workflow.

---

## Docker Introspection (18 tools)

Raw Docker container operations on the Dokploy host. Essential for runtime debugging.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__docker-getContainers` | List all containers on the host (each `{ containerId, name, state, status }`) | optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-getContainersByAppLabel` | List containers tagged with a specific Dokploy app label | `appName`, `type` (**required**: `"standalone"` \| `"swarm"`), optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-getContainersByAppNameMatch` | Match containers by app name — use for compose stacks | `appName`, `appType` (`"stack"` \| `"docker-compose"`), optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-getServiceContainersByAppName` | Swarm service containers across nodes | `appName`, optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-getStackContainersByAppName` | Compose/Swarm stack service containers | `appName`, optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-getConfig` | Inspect a container's full config (command, mounts, network, restart policy; its `Env` is `[REDACTED]` by default — see "Redaction") | `containerId`, optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-startContainer` | Start a stopped container | `containerId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-stopContainer` | Gracefully stop a running container | `containerId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-restartContainer` | Restart in place (no rebuild) — first try for transient failures | `containerId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-killContainer` | Force-kill (SIGKILL) a wedged container | `containerId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-removeContainer` | Hard-delete; Dokploy recreates on next `deploy` | `containerId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-uploadFileToContainer` | Push a one-off file into a container without rebuilding — does NOT survive redeploy. Multipart upload: **the MCP tool has an empty schema and cannot send the file; use REST `curl -F`** (below). The CLI command declares no options either | `containerId`, `file` (the file), `destinationPath`, optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-getServerHealth` | **Host diagnostics (v0.30.0+, read-only, over SSH):** container/service counts, memory and CPU, disk used/total, inotify limits, per-network IP-pool usage, recent daemon errors, memory/CPU reservations | optional `serverId`, `sinceHours` (1–168) |
| `mcp__plugin_dokploy-dev_dokploy__docker-getEvents` | Docker daemon events (container start/stop, image pull, network connect) as `{ events[], fetchedAt }` | optional `serverId`, `minutes` (1–1440, default 15) |
| `mcp__plugin_dokploy-dev_dokploy__docker-listContainerFiles` | List a directory inside a running container (read-only) | `containerId`, `path` (absolute), optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-readContainerFile` | Read a file inside a running container (read-only; the body is **not** redacted) | `containerId`, `path` (absolute), optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-writeContainerFile` | Overwrite a file inside a running container — lost on redeploy; confirm first | `containerId`, `path`, `content`, optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__docker-deleteContainerFile` | Delete a path inside a running container — destructive; confirm first | `containerId`, `path`, optional `serverId` |

### Host diagnostics (v0.30.0+)

Use these read-only tools in `debug-deploy` Step 0 and when a deploy "mysteriously stalls" — they replace the manual SSH checks:

| Question | Tool |
|---|---|
| Is the host short on disk, memory, inotify watches, or Docker network address pools? | `docker-getServerHealth` (also returns `daemonErrors[]` and memory/CPU `reservation`) |
| What did the daemon do in the last N minutes (OOM kills, restarts, image pulls)? | `docker-getEvents { minutes }` |
| What is eating disk — images, volumes, build cache? | `dockerDiskUsage-getDiskUsage` (rows `{ type, totalCount, active, size, reclaimable, sizeBytes }`; accepts `serverId`, unlike `settings-getDockerDiskUsage`), `dockerDiskUsage-getBuildCache` |
| Which images / volumes exist and how big? | `dockerImage-getImages`, `dockerImage-getImageConfig { imageRef }`, `dockerVolume-getVolumes`, `dockerVolume-getVolumesSize`, `dockerVolume-getVolumeConfig { volumeName }` |
| What is inside a volume (no SSH)? | `dockerVolume-listVolumeFiles { volumeName, path }` → `dockerVolume-readVolumeFile { volumeName, path }` |

Mutating siblings — confirm each: `dockerDiskUsage-pruneBuildCache`, `dockerImage-removeImage { repository, tag, id, force? }`, `dockerVolume-removeVolume { volumeName }` (**data loss**), `dockerVolume-writeVolumeFile { volumeName, path, content }`, `dockerVolume-deleteVolumeFile { volumeName, path }`. `dockerVolume-*` and `dockerImage-*` take an optional `serverId` for remote servers.

Choosing the discovery tool: for a **standalone application** use `getContainersByAppLabel { appName, type: "standalone" }` (most reliable — Dokploy stamps a known label). For a **compose stack** use `getContainersByAppNameMatch { appName, appType: "docker-compose" }` (or `getStackContainersByAppName` for swarm) — these return every service container. All return `{ containerId, name, state, status }`; feed each `containerId` into `compose-readLogs` to read that container's logs.

---

## Docker Networks (9 tools + per-service attachment, v0.30.0+)

Dokploy now tracks Docker networks (bridge or overlay, per server) and attaches them **per service**. Every application and compose service still joins the shared `dokploy-network` by default (that is how Traefik reaches it); a service can detach it and join only the networks it needs. Changes apply on the next deploy. This declarative model **replaces Isolated Deployment** (the `isolatedDeployment` flag of `compose-update` and the `compose-isolatedDeployment` rewrite tool, both deprecated).

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__network-all` | List tracked networks | optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__network-one` | One tracked network | `networkId` |
| `mcp__plugin_dokploy-dev_dokploy__network-inspect` | Live `docker network inspect` data for a tracked network | `networkId` |
| `mcp__plugin_dokploy-dev_dokploy__network-create` | Create a network | `name` (required), `driver` (`bridge` \| `overlay`), `internal`, `attachable`, `enableIPv4`, `enableIPv6`, `mtu` (68–65535), `ipam` (`{ driver, config: [{ subnet, gateway, ipRange }] }`), optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__network-networksToSync` | Docker networks that exist on the host but are not tracked yet | optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__network-import` | Start tracking existing Docker networks | `names` (array, required), optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__network-resync` | Re-read Docker state for a tracked network (detects delete/recreate by Docker ID) | `networkId` |
| `mcp__plugin_dokploy-dev_dokploy__network-recreate` | Remove and recreate the network — disrupts attached services; confirm | `networkId` |
| `mcp__plugin_dokploy-dev_dokploy__network-remove` | Delete the network record and the Docker network; confirm | `networkId` |

Attach per service by passing these fields to the update tool of the service type:

| Service | Tool | Fields |
|---|---|---|
| Application, each database (`postgres`/`mysql`/`mariadb`/`mongo`/`redis`/`libsql`) | `{type}-update` | `networkIds` (array of tracked `networkId`s, or `null`), `detachDokployNetwork` (boolean), `networkSwarm` (raw swarm attachment objects `{ Target, Aliases, DriverOpts }`) |
| Compose stack | `compose-update` | `serviceNetworks`: array of `{ serviceName, networkIds, detachDokployNetwork }` (all three required per entry) |

Example — attach a tracked network to an application (REST; the CLI cannot send array fields):

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.update" \
  -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" \
  -d '{"applicationId":"<id>","networkIds":["<networkId>"],"detachDokployNetwork":false}'
```

Detaching `dokploy-network` from a public-facing service makes it unreachable from Traefik — only do it for backends (databases, workers) that should be reachable solely over a private network. Symptom → cause table: `troubleshoot` ("Docker / Compose Issues").

---

## Vault Providers (7 tools, v0.30.0+)

External secret managers resolve environment values **at deploy time**; the value is never stored in Dokploy and members see only the reference. Reference syntax in any env editor (service, project-level or environment-level variables, build args and build secrets):

```
DATABASE_URL=postgres://app:${{vault.prod-vault.myapp/prod:DB_PASSWORD}}@db:5432/app
API_KEY=${{vault.doppler-prod.API_KEY}}
```

`${{vault.<provider-name>.<ref>}}` — `<provider-name>` is the unique name given at creation (letters, digits, `-`, `_`); `<ref>` is provider-specific (HashiCorp Vault / OpenBao: `path:field`; Infisical, Doppler: the secret name; AWS Secrets Manager: `name` or `name:field`; Azure Key Vault: the secret name; Scaleway: `[folder/]name[:field]`). Vault references resolve **before** `${{project.X}}` / `${{environment.X}}` interpolation. Rotating a secret takes effect on the next deployment.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__vaultProvider-all` / `vaultProvider-one` | List / read providers (credentials are masked) | `vaultProviderId` for `one` |
| `mcp__plugin_dokploy-dev_dokploy__vaultProvider-create` | Add a provider | `name`, `config` (`providerType` + its fields), `assignments` (`[{ projectId, environmentIds? }]`) — all required |
| `mcp__plugin_dokploy-dev_dokploy__vaultProvider-update` | Edit a provider (an untouched masked credential keeps its stored value) | `vaultProviderId`, `name`, `config`, `assignments` |
| `mcp__plugin_dokploy-dev_dokploy__vaultProvider-testConnection` | Validate credentials before or after saving | `vaultProviderId` or `config` |
| `mcp__plugin_dokploy-dev_dokploy__vaultProvider-listSecretNames` | Secret **names** the provider exposes (what the editor autocompletes; never values) | `vaultProviderId`, `projectId` (required), `environmentId` |
| `mcp__plugin_dokploy-dev_dokploy__vaultProvider-remove` | Delete a provider — deployments that reference it will fail | `vaultProviderId` |

`config.providerType` is one of `hashicorp` (HashiCorp Vault / OpenBao KV v2: `url`, `token`, `namespace`, `mount`), `infisical` (`siteUrl`, `clientId`, `clientSecret`, `projectId`, `environmentSlug`, `secretPath`), `aws` (Secrets Manager: `region`, `accessKeyId`, `secretAccessKey`, `endpoint`), `aws-parameter-store` (plus `parameterPath`), `doppler` (`serviceToken`, `project`, `config`), `azure` (`vaultUri`, `tenantId`, `clientId`, `clientSecret`), `scaleway` (`projectId`, `secretKey`, `region`, `apiUrl`) or `phase` (`token`, `appId`, `env`, `path`, `apiUrl`). A provider with no `assignments` is usable nowhere; an assignment without `environmentIds` covers every environment of that project (including future ones). Project-level shared variables are evaluated by **every** environment of the project, so do not reference an environment-restricted provider there. Managing providers needs owner/admin (or a custom role with the `vaultProvider` permission); members only see names. Keep the credentials you give a vault provider in your own secret manager — never in the repository or in chat.

---

## DNS Providers (11 tools, v0.30.0+)

Connect a DNS account to browse zones and manage records without leaving Dokploy (enterprise feature: owner/admin or a custom role with the `dnsProvider` permission; every change is audit-logged).

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__dnsProvider-all` / `dnsProvider-one` | List / read providers | `dnsProviderId` for `one` |
| `mcp__plugin_dokploy-dev_dokploy__dnsProvider-create` / `dnsProvider-update` / `dnsProvider-remove` | Manage a provider; `config.providerType` is `cloudflare` (`apiToken`), `route53` (`accessKeyId`, `secretAccessKey`), `porkbun` (`apiKey`, `secretApiKey`), `infomaniak` (`apiToken`) or `ovh` (`endpoint`, `applicationKey`, `applicationSecret`, `consumerKey`); the type is locked after creation | `name`, `config` (+ `dnsProviderId` for update/remove) |
| `mcp__plugin_dokploy-dev_dokploy__dnsProvider-testConnection` | Validate credentials | `dnsProviderId` or `config` |
| `mcp__plugin_dokploy-dev_dokploy__dnsProvider-listZones` | Zones the credentials can see | `dnsProviderId` |
| `mcp__plugin_dokploy-dev_dokploy__dnsProvider-listRecords` | Records of one zone | `dnsProviderId`, `zoneId` |
| `mcp__plugin_dokploy-dev_dokploy__dnsProvider-createRecord` / `dnsProvider-updateRecord` | Add / change a record (`type` A, AAAA, CNAME, MX, TXT, NS, SRV, CAA or PTR; `name` — `@` is the zone apex; `content`; optional `ttl`, `proxied`) | `dnsProviderId`, `zoneId`, `type`, `name`, `content` (+ `recordId` for update) |
| `mcp__plugin_dokploy-dev_dokploy__dnsProvider-deleteRecord` | Delete a record **at the DNS provider** — not just in Dokploy; confirm | `dnsProviderId`, `zoneId`, `recordId` |

**Client gotcha:** `dnsProvider-createRecord` and `dnsProvider-updateRecord` publish `ttl` with a numeric `exclusiveMinimum`, which some MCP clients reject while loading tools (Claude Code drops these two). If they are missing from your session, call REST instead: `POST $DOKPLOY_URL/api/dnsProvider.createRecord` with the same JSON body. The docs describe the DNS integration as standalone (Settings → DNS Providers), not wired into `domain-create`; so the record must exist (create it here or at the provider) before `domain-validateDomain` can succeed. Sequence: `dnsProvider-listZones` → `dnsProvider-createRecord { type: "A", name, content: <server public IP from server-publicIp / settings-getIp> }` → `domain-create` → `domain-validateDomain`.

---

## Settings, Health & Cleanup (selected)

The `settings-*` namespace is the catch-all for server-wide operations. Highest-leverage subset for dev/debug:

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__settings-health` | Liveness probe (`{ status: "ok" }`; the REST route needs the API key, only `/api/trpc/settings.health` is open) | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-checkInfrastructureHealth` | Core service check: returns `{ postgres: { status }, traefik: { status } }` (Redis was removed in v0.30.0). For Docker daemon, disk, inotify and network pools use `docker-getServerHealth` | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getDockerDiskUsage` | Per-category disk usage on the Dokploy host (images, containers, volumes, build cache) — for a remote server use `dockerDiskUsage-getDiskUsage { serverId }` | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-checkGPUStatus` | GPU availability and current usage | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getDokployVersion` | Server version string | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getReleaseTag` | Image tag currently running | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getUpdateData` | Available update info | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getIp` | Server outbound IP | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getDokployCloudIps` | Static IP ranges for Dokploy Cloud egress | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getTraefikPorts` | Currently-bound Traefik ports | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-haveTraefikDashboardPortEnabled` | Is the 8080 dashboard exposed? | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-getLogCleanupStatus` | Log rotation schedule + last run | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-updateLogCleanup` | Tune log rotation | retention fields |
| `mcp__plugin_dokploy-dev_dokploy__settings-updateBuildsConcurrency` | Set concurrent builds for the Dokploy host queue (per-server queues since v0.29.9; the OSS max-2 clamp existed only in v0.29.9–v0.29.10 — since v0.29.11 concurrency is a full OSS feature, 1–100 per server, default 1) | `buildsConcurrency` |
| `mcp__plugin_dokploy-dev_dokploy__settings-updateEnforceSSO` | Toggle enforce-SSO restriction | `enforceSSO` |
| `mcp__plugin_dokploy-dev_dokploy__settings-updateRemoteServersOnly` | Toggle remote-servers-only mode | `remoteServersOnly` |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanDockerBuilder` | Clear BuildKit cache | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanDockerPrune` | `docker system prune` equivalent | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanStoppedContainers` | Remove exited containers | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanUnusedImages` | Remove dangling/untagged images | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanUnusedVolumes` | **Destroys orphan volumes** — risky | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanMonitoring` | Reset monitoring data | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanAll` | Aggressive. Admin-only; **runs in the background** and returns `{ status: "scheduled", message }` immediately (check the effect with `dockerDiskUsage-getDiskUsage` afterwards). It runs `docker container prune`, `docker image prune --all`, `docker builder prune --all` and `docker system prune --all`; volumes are excluded and monitoring data is untouched (`settings-cleanMonitoring` is separate) | optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__settings-cleanAllDeploymentQueue` | Force-clear every stuck deploy across all resources | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-readTraefikConfig` | Top-level Traefik static config | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-readMiddlewareTraefikConfig` | Middlewares config | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-readWebServerTraefikConfig` | Per-webserver dynamic config | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-reloadTraefik` | Reload Traefik to apply config changes | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-reloadServer` | Bounce the Dokploy server | None |
| `mcp__plugin_dokploy-dev_dokploy__settings-toggleDashboard` | Show/hide the Traefik dashboard | None |

For the cleanup chain run in order, use the `/dokploy-dev:cleanup` command — it confirms each destructive step and reports reclaimed space.

---

## Schedule Router (6 tools)

Cron-like scheduled tasks scoped to a resource. Each schedule fires a command inside the target container.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__schedule-list` | List schedules for a resource | `id` (required — the target resource id), `scheduleType` (required: `application`\|`compose`\|`server`\|`dokploy-server`) |
| `mcp__plugin_dokploy-dev_dokploy__schedule-one` | Get one schedule | `scheduleId` |
| `mcp__plugin_dokploy-dev_dokploy__schedule-create` | Create a scheduled task | `name`, `cronExpression`, `command` (required), `scheduleType` (`application` \| `compose` \| `server` \| `dokploy-server`), target binding (`applicationId` / `composeId` / `serverId`), `serviceName` (for compose), `shellType` (`bash` \| `sh`), `enabled`, optional `timezone`. Dokploy-host schedules (`scheduleType: "dokploy-server"`) are organization-scoped since v0.29.8 — the server fills `organizationId` from your session |
| `mcp__plugin_dokploy-dev_dokploy__schedule-update` | Edit a schedule | `scheduleId`, updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__schedule-delete` | Remove a schedule | `scheduleId` |
| `mcp__plugin_dokploy-dev_dokploy__schedule-runManually` | Trigger the schedule immediately, ignoring cron | `scheduleId` |

Schedule targets:

- `applicationId` — runs `command` inside the app container at every tick
- `composeId` + `serviceName` — runs inside that specific compose service
- `serverId` — runs on the host (for remote servers)
- `scheduleType: "dokploy-server"` — runs on the Dokploy host itself

`cronExpression` is a standard 5-field cron (e.g. `"0 3 * * *"` = daily at 03:00).

---

## Patch Router (12 tools)

File-level overlays applied at deploy time. Useful when you can't / don't want to modify the source repo (e.g. tweaking a config file in an upstream image).

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__patch-byEntityId` | List patches for an entity | `id` (required — applicationId/composeId), `type` (required: `application`/`compose`) |
| `mcp__plugin_dokploy-dev_dokploy__patch-one` | Get one patch record | `patchId` |
| `mcp__plugin_dokploy-dev_dokploy__patch-create` | Create a patch | `filePath` (required), `content` (required), `type`, `enabled`, `applicationId`/`composeId` |
| `mcp__plugin_dokploy-dev_dokploy__patch-update` | Update patch metadata | `patchId`, updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__patch-delete` | Remove a patch | `patchId` |
| `mcp__plugin_dokploy-dev_dokploy__patch-toggleEnabled` | Enable/disable without deleting | `patchId`, `enabled` |
| `mcp__plugin_dokploy-dev_dokploy__patch-ensureRepo` | Ensure the patch's git repo workspace is materialised | `id`, `type` |
| `mcp__plugin_dokploy-dev_dokploy__patch-cleanPatchRepos` | Garbage-collect orphan patch repos | optional `serverId` |
| `mcp__plugin_dokploy-dev_dokploy__patch-readRepoDirectories` | List directories inside the patch workspace | `id`, `type`, `repoPath` |
| `mcp__plugin_dokploy-dev_dokploy__patch-readRepoFile` | Read a file from the patch workspace | `id`, `type`, `filePath` |
| `mcp__plugin_dokploy-dev_dokploy__patch-saveFileAsPatch` | Save a modified file as a patch overlay | `id`, `type`, `filePath`, `content`, `patchType` |
| `mcp__plugin_dokploy-dev_dokploy__patch-markFileForDeletion` | Mark a file for deletion during patch apply | `id`, `type`, `filePath` |

Patches apply during the deploy step, after the source is cloned but before the build. Use for per-environment config overrides without forking the upstream repo.

---

## Volume Backups (6 tools)

Distinct from the resource-aware `backup` namespace — `volumeBackups` snapshot raw Docker volumes as-is (no DB-specific dump tooling).

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__volumeBackups-list` | List volume backup configs for a resource | `id` (required), `volumeBackupType` (required) |
| `mcp__plugin_dokploy-dev_dokploy__volumeBackups-one` | Get one backup config | `volumeBackupId` |
| `mcp__plugin_dokploy-dev_dokploy__volumeBackups-create` | Configure a recurring volume backup | resource binding, `volumeName`, `destinationId`, `cronExpression`, `enabled` |
| `mcp__plugin_dokploy-dev_dokploy__volumeBackups-update` | Update config | `volumeBackupId`, updatable fields |
| `mcp__plugin_dokploy-dev_dokploy__volumeBackups-delete` | Remove a backup config | `volumeBackupId` |
| `mcp__plugin_dokploy-dev_dokploy__volumeBackups-runManually` | Trigger a one-off backup outside the schedule | `volumeBackupId` |

Pair with the `destination-*` namespace to point at S3, R2, or another remote. Use for non-database persistent state (uploads, ML model files, caches).

---

## Preview Deployments (4 tools)

Ephemeral per-PR / per-branch deploys spun up alongside the main application.

| Tool | Description | Key Parameters |
|---|---|---|
| `mcp__plugin_dokploy-dev_dokploy__previewDeployment-all` | List preview deployments | `applicationId` (required) |
| `mcp__plugin_dokploy-dev_dokploy__previewDeployment-one` | Get one preview deployment | `previewDeploymentId` |
| `mcp__plugin_dokploy-dev_dokploy__previewDeployment-redeploy` | Force a fresh build of a preview | `previewDeploymentId` |
| `mcp__plugin_dokploy-dev_dokploy__previewDeployment-delete` | Tear down a preview environment | `previewDeploymentId` |

Preview deployments are typically triggered by webhook (PR opened/synced). The MCP surface above is for inspection and manual lifecycle control.

---

## Common Workflow Patterns

### 1. Deploy a new application from GitHub

Execute these tools in sequence:

```
1. mcp__plugin_dokploy-dev_dokploy__project-create
   → { name: "my-project", description: "Production app" }
   → Returns: { projectId: "abc123" }

1b. mcp__plugin_dokploy-dev_dokploy__project-one
   → { projectId: "abc123" }
   → Returns environments[] — take environments[0].environmentId (default environment "production")

2. mcp__plugin_dokploy-dev_dokploy__application-create
   → { environmentId: "env123", name: "My App", appName: "my-app" }
   → Returns: { applicationId: "def456" }

3. mcp__plugin_dokploy-dev_dokploy__application-saveGithubProvider
   → { applicationId: "def456", repository: "my-repo", branch: "main", owner: "my-org" }

4. mcp__plugin_dokploy-dev_dokploy__application-saveBuildType
   → { applicationId: "def456", buildType: "dockerfile", dockerfile: "Dockerfile", dockerContextPath: ".", dockerBuildStage: "", herokuVersion: "", railpackVersion: "" }
   (Use "nixpacks" if no Dockerfile exists. Ask user which to use.)

5. mcp__plugin_dokploy-dev_dokploy__application-saveEnvironment
   → { applicationId: "def456", env: "DATABASE_URL=postgres://...\nNODE_ENV=production\nPORT=3000", buildArgs: "", buildSecrets: "", createEnvFile: false }

6. mcp__plugin_dokploy-dev_dokploy__domain-create
   → { applicationId: "def456", host: "app.example.com", https: true, certificateType: "letsencrypt", port: 3000 }

7. mcp__plugin_dokploy-dev_dokploy__application-deploy
   → { applicationId: "def456" }
```

After step 7, check the application status with `application-one` and deployment history with `deployment-all` filtered by `applicationId` to confirm the deployment succeeded. Stream logs with `application-readLogs` if it fails.

### 2. Provision a PostgreSQL database with external access

```
1. mcp__plugin_dokploy-dev_dokploy__project-create
   → { name: "databases" }
   → Returns: { projectId: "proj789" }
   (Or use project-all to find an existing project)
   Then resolve the environment: project-one { projectId } → environments[0].environmentId

2. mcp__plugin_dokploy-dev_dokploy__postgres-create
   → { environmentId: "env789", name: "Main DB", appName: "main-db", databaseName: "main", databaseUser: "postgres", databasePassword: "secure-password-here" }
   → Returns: { postgresId: "pg123" }

3. mcp__plugin_dokploy-dev_dokploy__postgres-deploy
   → { postgresId: "pg123" }

4. mcp__plugin_dokploy-dev_dokploy__postgres-saveExternalPort
   → { postgresId: "pg123", externalPort: 5432 }
```

The database is now accessible at `server-ip:5432`. Use the connection string: `postgres://postgres:secure-password-here@server-ip:5432/postgres`.

### 3. Add a domain with HTTPS to an existing application

```
1. mcp__plugin_dokploy-dev_dokploy__domain-create
   → { applicationId: "def456", host: "api.example.com", https: true, certificateType: "letsencrypt", port: 8080 }
   → Returns: { domainId: "dom789" }

2. mcp__plugin_dokploy-dev_dokploy__domain-validateDomain
   → { domain: "api.example.com" }        # the hostname string (optionally serverId) — NOT the domainId
```

If validation fails, the DNS A record for `api.example.com` is not pointing to the server's IP. Fix DNS and re-validate.

### 4. Deploy a Docker Compose stack

```
1. mcp__plugin_dokploy-dev_dokploy__project-create
   → { name: "compose-stack" }
   → Returns: { projectId: "proj456" }
   Then resolve the environment: project-one { projectId } → environments[0].environmentId

2. mcp__plugin_dokploy-dev_dokploy__compose-create
   → { environmentId: "env456", name: "My Stack", appName: "my-stack" }
   → Returns: { composeId: "comp789" }

3. mcp__plugin_dokploy-dev_dokploy__compose-update
   → { composeId: "comp789", composeFile: "version: '3.8'\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - '80:80'" }

   (If sourcing compose from a git repo instead, pass sourceType/repository/branch/owner/composePath here too.)

4. mcp__plugin_dokploy-dev_dokploy__compose-saveEnvironment
   → { composeId: "comp789", env: "NGINX_HOST=example.com" }

5. mcp__plugin_dokploy-dev_dokploy__compose-getConvertedCompose
   → { composeId: "comp789" }   // validate the file before deploy

6. mcp__plugin_dokploy-dev_dokploy__compose-deploy
   → { composeId: "comp789" }
```

### 5. Read the logs of every container in a compose stack

```
1. mcp__plugin_dokploy-dev_dokploy__compose-one
   → { composeId: "comp789" }
   → read appName (e.g. "my-stack-ab12cd") and composeType (e.g. "docker-compose")

2. mcp__plugin_dokploy-dev_dokploy__docker-getContainersByAppNameMatch          // swarm → docker-getStackContainersByAppName
   → { appName: "my-stack-ab12cd", appType: "docker-compose" }
   → [ { containerId, name, state, status }, ... ]   // every service container

3. for each container:
   mcp__plugin_dokploy-dev_dokploy__compose-readLogs
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

The official `@dokploy/mcp` server exposes **604 tools across 57 categories** (v0.30.7; the same set as the REST operations). Categories covered by this skill in detail:

| Category | Count | Prefix |
|---|---|---|
| Project Management | 11 | `project-` |
| Overview Dashboard | 3 | `overview-` |
| Application Management | 32 | `application-` |
| Domain Management | 10 | `domain-` |
| Compose Management | 31 | `compose-` |
| PostgreSQL | 16 | `postgres-` |
| MySQL | 16 | `mysql-` |
| MariaDB | 16 | `mariadb-` |
| MongoDB | 16 | `mongo-` |
| Redis | 16 | `redis-` |
| LibSQL | 14 | `libsql-` |
| Deployment History | 9 | `deployment-` |
| AI Router | 14 | `ai-` |
| Docker Introspection | 18 | `docker-` |
| Docker Volumes / Images / Disk Usage | 8 / 3 / 3 | `dockerVolume-` / `dockerImage-` / `dockerDiskUsage-` |
| Docker Networks | 9 | `network-` |
| Vault Providers | 7 | `vaultProvider-` |
| DNS Providers | 11 | `dnsProvider-` |
| Settings / Cleanup / Health | 52 (selected above) | `settings-` |
| Schedule | 6 | `schedule-` |
| Patch | 12 | `patch-` |
| Volume Backups | 6 | `volumeBackups-` |
| Preview Deployments | 4 | `previewDeployment-` |

Use `DOKPLOY_TOOL_PRESET` / `DOKPLOY_ENABLED_TAGS` / `DOKPLOY_DISABLED_TAGS` in `.mcp.json` to restrict exposure to a subset of categories.

---

## Other categories (reference only)

The remaining categories use the same `mcp__plugin_dokploy-dev_dokploy__<category>-<op>` pattern. **Every one of these — and every operation in every category above — is enumerated with its exact params in the complete index:** [`api-reference/references/api-full-index-resources.md`](../api-reference/references/api-full-index-resources.md) and [`api-full-index-platform.md`](../api-reference/references/api-full-index-platform.md) (all 604 operations, v0.30.7 schema). The themed files below add curated usage notes for some of them.

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
| Servers | `server-` | Managed remote servers (add, setup, metrics, security, SSH, `getServices`) | `api-server-settings.md` |
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

If MCP tools fail or are missing from your session (e.g. a client that drops `dnsProvider-createRecord`), call the Dokploy REST API directly via `curl`. Dokploy uses **`x-api-key`** header for authentication (NOT `Authorization: Bearer`). Operations live at `/api/<tag>.<operation>` under the base `$DOKPLOY_URL`; the exact parameters of each are in the `api-reference` indexes. REST calls are **not** redacted (see "Redaction").

### Authentication

```bash
# Correct — use x-api-key header and /api path
curl -s "$DOKPLOY_URL/api/project.all" \
  -H "x-api-key: $DOKPLOY_API_KEY"

# Wrong — Bearer auth returns 401
curl -s "$DOKPLOY_URL/api/project.all" \
  -H "Authorization: Bearer $DOKPLOY_API_KEY"
```

### Read operations (GET with query parameters)

Pass the parameters as plain query-string fields:

```bash
curl -s -G "$DOKPLOY_URL/api/application.one" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode "applicationId=abc123"
```

(The tRPC wire format `?input={"json":{...}}` is rejected on `/api/<tag>.<operation>` with `400 Input validation failed`.)

### Write operations (POST with a flat JSON body)

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.deploy" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"applicationId":"abc123"}'
```

### Health check

```bash
curl -s "$DOKPLOY_URL/api/settings.health" -H "x-api-key: $DOKPLOY_API_KEY"
```

Without the key `/api/settings.health` answers 401 on v0.30; the tRPC route `GET /api/trpc/settings.health` is the unauthenticated liveness probe.

### Multipart operations (`curl -F`)

`application-dropDeployment` and `docker-uploadFileToContainer` take a file upload; their MCP tools expose an empty schema, so call REST:

```bash
# deploy a zip as the application's "drop" source
curl -s -X POST "$DOKPLOY_URL/api/application.dropDeployment" -H "x-api-key: $DOKPLOY_API_KEY" \
  -F "applicationId=<id>" -F "zip=@build.zip" -F "dropBuildPath=<optional-subdir>"

# one-off file into a running container (lost on redeploy)
curl -s -X POST "$DOKPLOY_URL/api/docker.uploadFileToContainer" -H "x-api-key: $DOKPLOY_API_KEY" \
  -F "containerId=<id>" -F "destinationPath=/app/config.json" -F "file=@config.json" -F "serverId=<optional>"
```

