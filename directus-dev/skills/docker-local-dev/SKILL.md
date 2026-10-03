---
name: docker-local-dev
description: "Run Directus 12 locally with Docker Compose — PostgreSQL, Redis, upload and extension volumes, secrets from .env, /server/ping health check, pinned image tag, first admin, extensions on hardened images, upgrades. This skill should be used when the user asks to \"run Directus locally\", \"Directus Docker Compose\", \"Directus local dev stack\", \"start a local Directus instance\", \"docker-compose.yml for Directus\", or needs a throwaway Directus to develop a frontend, flows or schema against."
---

# Directus Local Development with Docker Compose

Run Directus 12 on your machine with PostgreSQL and Redis, driven by environment variables. Everything below is generic: the compose file contains no values, only `${VAR}` references. Real values live in a gitignored `.env`.

The result is a development stack, not a production deployment. For production, read the Directus self-hosting docs (secrets management, backups, reverse proxy, `IP_TRUST_PROXY`, storage adapter).

## Prerequisites

- Docker Engine 25 or later with Compose 2.20.2 or later (`docker compose version`). The health checks below use `start_interval`, which older versions reject or ignore. On an older setup delete the three `start_interval` lines and the stack still works, only slower to report healthy
- A free host port for Directus (8055 is the usual default, set `LOCAL_DIRECTUS_PORT` when it is taken)

## Files

```
my-project/
├── docker-compose.yml
├── .env                 # real values, gitignored
├── .env.example         # placeholders, committed
├── uploads/             # Directus file storage (bind mount)
├── extensions/          # custom extensions (bind mount)
└── data/database/       # PostgreSQL data (bind mount)
```

### `.env.example`

Commit this file with placeholders. Copy it to `.env` and fill it in.

```bash
# Image: pin an exact version, do not use "latest". Tested up to 12.4.1.
LOCAL_DIRECTUS_VERSION=12.4.1
LOCAL_DIRECTUS_PORT=8055

# Generate once: openssl rand -hex 32
LOCAL_DIRECTUS_SECRET=<random-64-hex-characters>

# First admin account, created on first start
LOCAL_DIRECTUS_ADMIN_EMAIL=admin@example.com
LOCAL_DIRECTUS_ADMIN_PASSWORD=<local-admin-password>
# Optional static token for that admin (for scripts and MCP in local dev only)
LOCAL_DIRECTUS_ADMIN_TOKEN=<local-static-token>

LOCAL_DB_PASSWORD=<local-database-password>

# Origin of your frontend dev server, for CORS (also enforced for WebSockets since 12.1)
LOCAL_FRONTEND_ORIGIN=http://localhost:3000

# Optional: leave empty for the Core tier
LOCAL_DIRECTUS_LICENSE_KEY=
```

Add `.env`, `uploads/`, `data/` to `.gitignore`.

### `docker-compose.yml`

```yaml
services:
  database:
    image: postgis/postgis:17-3.5
    environment:
      POSTGRES_USER: directus
      POSTGRES_PASSWORD: ${LOCAL_DB_PASSWORD:?set LOCAL_DB_PASSWORD in .env}
      POSTGRES_DB: directus
    volumes:
      - ./data/database:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "--host=localhost", "--username=directus"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_interval: 5s
      start_period: 30s

  cache:
    image: redis:7
    healthcheck:
      test: ["CMD-SHELL", "[ $$(redis-cli ping) = 'PONG' ]"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_interval: 5s
      start_period: 30s

  directus:
    image: directus/directus:${LOCAL_DIRECTUS_VERSION:-12.4.1}
    ports:
      - "127.0.0.1:${LOCAL_DIRECTUS_PORT:-8055}:8055"
    volumes:
      - ./uploads:/directus/uploads
      - ./extensions:/directus/extensions
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "wget --spider -q http://127.0.0.1:8055/server/ping || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_interval: 5s
      start_period: 30s
    environment:
      SECRET: ${LOCAL_DIRECTUS_SECRET:?set LOCAL_DIRECTUS_SECRET in .env}

      DB_CLIENT: pg
      DB_HOST: database
      DB_PORT: "5432"
      DB_DATABASE: directus
      DB_USER: directus
      DB_PASSWORD: ${LOCAL_DB_PASSWORD}

      CACHE_ENABLED: "true"
      CACHE_AUTO_PURGE: "true"
      CACHE_STORE: redis
      REDIS: redis://cache:6379

      ADMIN_EMAIL: ${LOCAL_DIRECTUS_ADMIN_EMAIL:?set LOCAL_DIRECTUS_ADMIN_EMAIL in .env}
      ADMIN_PASSWORD: ${LOCAL_DIRECTUS_ADMIN_PASSWORD:?set LOCAL_DIRECTUS_ADMIN_PASSWORD in .env}
      ADMIN_TOKEN: ${LOCAL_DIRECTUS_ADMIN_TOKEN:-}

      PUBLIC_URL: http://localhost:${LOCAL_DIRECTUS_PORT:-8055}
      WEBSOCKETS_ENABLED: "true"
      CORS_ENABLED: "true"
      CORS_ORIGIN: ${LOCAL_FRONTEND_ORIGIN:-http://localhost:3000}
      # Lets the Studio embed your frontend in an iframe (Live Preview)
      CONTENT_SECURITY_POLICY_DIRECTIVES__FRAME_SRC: ${LOCAL_FRONTEND_ORIGIN:-http://localhost:3000}

      LICENSE_KEY: ${LOCAL_DIRECTUS_LICENSE_KEY:-}

      EXTENSIONS_AUTO_RELOAD: "true"
```

Notes on the file:

- **`LOCAL_` prefix.** Compose gives variables exported in your shell precedence over `.env`, silently. A shell that already exports `DIRECTUS_*` for your app (a `DIRECTUS_ADMIN_TOKEN`, say) would override the stack's value with no warning, and a real credential could end up in a throwaway container. The prefix keeps the stack's variables apart from the app's `DIRECTUS_URL` and `DIRECTUS_TOKEN`.
- **Loopback port.** `127.0.0.1:` in the port mapping keeps the stack off your network: the local admin password and static token are throwaway values, and a plain `8055:8055` would publish them on every interface of the machine. Remove the prefix only when another device has to reach the instance.
- **Pinned tag.** `directus/directus:${LOCAL_DIRECTUS_VERSION}` keeps restarts from silently upgrading. Directus 12 enforces licensing and has breaking changes between minor versions, so upgrades must be deliberate.
- **`:?` guards.** Compose stops with the message if a required variable is missing, instead of starting Directus with an empty `SECRET`.
- **Health check** calls `127.0.0.1`, not `localhost`: the image's `wget` tries the IPv6 address for `localhost` first and Directus listens on IPv4 only, so a `localhost` probe reports the container as unhealthy while it works fine.
- **`CONTENT_SECURITY_POLICY_DIRECTIVES__FRAME_SRC`** is what lets Live Preview show your frontend inside the Studio. Without it the browser refuses the iframe. Your frontend must allow the Studio origin as well (`Content-Security-Policy: frame-ancestors 'self' <studio-origin>`), see the Directus Live Preview guide.
- **`ADMIN_*`** create the first admin on an empty database, so the onboarding screen is skipped. They are ignored once the database already has users.
- **`PUBLIC_URL`** must match the address you open in the browser. Licensing binds to it on first use and OAuth redirects use it.
- **PostGIS image** is the one the Directus docs use, so geometry field types work. A plain `postgres` image also works if you do not need them.
- **`LICENSE_KEY`** stays empty for local development (Core tier). A license key binds to the project and `PUBLIC_URL` on first use. Deleting a stack that holds a key without deactivating the license first (Settings → License) strands the activation against the license's activation limit, so never test a production key in a throwaway stack.
- **Redis** is optional for one instance. It is included to match production behavior (cache, rate limits).

## Start and Verify

Compose reads `.env` by itself. Your shell does not, so the `curl` commands below need the values loaded first: `set -a; . ./.env; set +a`.

```bash
mkdir -p uploads extensions data/database
sudo chown 1000:1000 uploads extensions   # Linux: the container user "node" is uid 1000
cp .env.example .env        # then edit .env
docker compose up -d
docker compose ps           # wait until directus is "healthy"

# Liveness: public, answers "pong" once the HTTP server runs
curl -sS "http://localhost:${LOCAL_DIRECTUS_PORT:-8055}/server/ping"
```

`/server/ping` is the right probe. `/server/health` checks the database, Redis, storage and email, but Directus 12 answers `403` to it without a token.

Dependency check with the admin token (`200` with `"status": "ok"` when the database, Redis, storage and email checks pass):

```bash
curl -sS "http://localhost:${LOCAL_DIRECTUS_PORT:-8055}/server/health" \
  -H "Authorization: Bearer ${LOCAL_DIRECTUS_ADMIN_TOKEN}"
```

Then open the Studio in the browser at the `PUBLIC_URL` and sign in with the admin account.

The Directus container runs as the unprivileged `node` user (uid 1000). On Linux the bind-mounted `uploads/` and `extensions/` directories must be writable by that uid, which the `chown` above does. When they are owned by another user, uploads fail with `EACCES`, and `/server/health` returns `503` with a `storage:local` error (health results are cached for `HEALTHCHECK_CACHE_TTL`, five minutes by default, so a fix can take that long to show). Docker Desktop on macOS and Windows usually needs no change.

## Connect Your Tools

```bash
# App .env (a .env file does not expand variables: write the literal address and token)
DIRECTUS_URL=http://localhost:8055         # the port you put in LOCAL_DIRECTUS_PORT
DIRECTUS_TOKEN=<value of LOCAL_DIRECTUS_ADMIN_TOKEN>   # local dev only
```

- **SDK.** See the `sdk-patterns` skill: static token on the server, `authentication('json')` for a login in Node, `authentication('session', { credentials: 'include' })` in the browser.
- **MCP.** Enable it once in the Studio under Settings → AI → Model Context Protocol, then register `${DIRECTUS_URL}/mcp` with your client (see `mcp-tools`). For a local instance a static token is the simplest start. Create a dedicated user with its own policy for AI work rather than reusing the admin account.
- **Frontend dev server** on another origin: set `LOCAL_FRONTEND_ORIGIN` to it. The origin must be listed in `CORS_ORIGIN` for both REST and WebSockets.

## Daily Commands

```bash
docker compose logs -f directus          # follow logs
docker compose restart directus          # after changing .env or extensions
docker compose down                      # stop, keep data
```

To start over, stop the stack and delete the `data/` and `uploads/` directories. The next `up` bootstraps a fresh database and recreates the admin from `.env`.

## Moving a Schema Between Instances

Snapshot the local schema, diff it against another instance and apply (admin token, see `api-reference` for the pipeline):

```bash
curl -s -H "Authorization: Bearer ${LOCAL_DIRECTUS_ADMIN_TOKEN}" \
  "http://localhost:${LOCAL_DIRECTUS_PORT:-8055}/schema/snapshot" > schema-snapshot.json
```

Snapshots are capped by `IMPORT_MAX_FILE_SIZE` (default `50mb`) when uploaded to `/schema/diff` or `/schema/apply`.

## Extensions

Mount extensions into `./extensions` and keep `EXTENSIONS_AUTO_RELOAD: "true"` for local development. The published Directus 12 images are hardened: `npm` and `npx` are removed from the runtime, and the `-dhi` variant (for example `directus/directus:12.4.1-dhi`) is distroless with no shell at all. So you cannot install extensions or run `npx directus ...` inside the container.

- **Build outside, copy in.** Install and build the extension on your machine or in a build stage, then mount the finished directory (it needs a `package.json` and a `dist/` folder) into `extensions/`.
- **Bake into an image** with a multi-stage Dockerfile and copy with `--chown=node:node`:

```dockerfile
FROM node:22-alpine AS build
WORKDIR /extension-build
RUN corepack enable && pnpm init && pnpm add <extension-package>

FROM directus/directus:12.4.1
COPY --from=build --chown=node:node /extension-build/node_modules/<extension-package> /directus/extensions/<extension-name>
```

Keep the Alpine version of the build stage in line with the Directus image when an extension has native dependencies. The `-dhi` image has no `wget`, so the compose health check above does not work with it: probe `/server/ping` from outside the container instead.

- **Directus CLI** is still there, call it with `node`:

```bash
docker compose exec directus node /directus/cli.js database migrate:latest
```

## Upgrading

1. Read the breaking changes for every version you skip (Directus docs, Releases, Breaking changes). Directus 12 notes: `/server/health` needs a token, `IP_TRUST_PROXY` defaults to `false`, the Studio shows published items of versioned collections read-only, update and delete flow operations without a target return `null`. 12.4.0 has a bug reading `directus_folders` as a non-admin, so go to 12.4.1 or later.
2. Back up first: `docker compose exec database pg_dump --username=directus directus > backup.sql`, plus the `uploads/` directory.
3. Change `LOCAL_DIRECTUS_VERSION` in `.env`, then `docker compose pull directus && docker compose up -d`. Migrations run automatically on start.
4. Check `docker compose logs directus` and `/server/ping`.

To go back to an older version, restore the backup taken before the upgrade. Changing the image tag back alone leaves a database that was already migrated by the newer version.

## Troubleshooting

| Symptom | Cause and fix |
|---------|---------------|
| `required variable ... is missing a value` | A `${VAR:?...}` guard fired. Set the variable in `.env` |
| A value in the running container is not the one in `.env` | A variable with the same name is exported in your shell and wins over `.env`. Unset it, or run `docker compose` from a clean environment with `env -i PATH="$PATH" HOME="$HOME" docker compose up -d` |
| Port already in use | Another process owns the host port. Set `LOCAL_DIRECTUS_PORT` to a free one and update `PUBLIC_URL` consumers |
| Directus restarts in a loop, logs show database connection errors | Wrong `LOCAL_DB_PASSWORD`. The database directory keeps the first password: delete `data/database` to re-initialize, or change the password inside PostgreSQL |
| Login works, but the browser app gets CORS errors | `LOCAL_FRONTEND_ORIGIN` does not match the app origin exactly (scheme, host and port) |
| `503` from `/server/health` with a `storage:local` error, uploads fail with `EACCES` | `uploads/` is not writable for uid 1000, see the `chown` in Start and Verify |
| `403` from `/server/health` | Expected without a token in Directus 12. Use `/server/ping` |
| Cannot sign in with SSO | Directus 12 needs a licensed tier for SSO. Use an email/password user locally |
| Assets return `403` for anonymous requests | Files are private by default. Grant the Public policy read on `directus_files`, or serve them through a server route that adds the token. Never put `?access_token=` in a URL a browser sees (see `troubleshoot`) |
