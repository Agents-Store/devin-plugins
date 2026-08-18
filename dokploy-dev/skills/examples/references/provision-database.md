# Scenario: Provision a Database

Create, configure, and expose a PostgreSQL database with external access and automated backups.

This scenario uses PostgreSQL as the example. The same pattern applies to MySQL, MariaDB, MongoDB, and Redis — substitute the tool prefix (e.g. `postgres` becomes `mysql`, `mariadb`, `mongo`, or `redis`).

## Contents
- [Prerequisites](#prerequisites)
- [Step 1: Create a Project (or use an existing one)](#step-1-create-a-project-or-use-an-existing-one)
- [Step 2: Create the PostgreSQL Database](#step-2-create-the-postgresql-database)
- [Step 3: Deploy the Database](#step-3-deploy-the-database)
- [Step 4: Set External Port (for external access)](#step-4-set-external-port-for-external-access)
- [Step 5: Set Up Automated Backups](#step-5-set-up-automated-backups)
- [Step 6: Verify the Database](#step-6-verify-the-database)
- [Connection String Reference](#connection-string-reference)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Dokploy MCP connection verified (run the `setup` skill if not confirmed)
- `$DOKPLOY_URL` and `$DOKPLOY_API_KEY` configured
- A project to host the database (create one in Step 1 if needed)

---

## Step 1: Create a Project (or use an existing one)

If a project already exists, skip this step and use its `projectId`.

**MCP:**

```
mcp__dokploy__project-create
```

Parameters:
```json
{
  "name": "database-services",
  "description": "Databases for production applications"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/project.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "database-services", "description": "Databases for production applications"}'
```

Save the returned `projectId`.

**Resolve the target environment** — databases are created inside a project *environment* (default `production`):

```
mcp__dokploy__project-one { "projectId": "<projectId>" }
   → environments[0].environmentId
```

Save the `environmentId`.

---

## Step 2: Create the PostgreSQL Database

**MCP:**

```
mcp__dokploy__postgres-create
```

Parameters (`databaseName` and `databaseUser` are **required** for postgres):
```json
{
  "name": "main-db",
  "environmentId": "<environmentId>",
  "databaseName": "main",
  "databaseUser": "postgres",
  "databasePassword": "secure-password-here",
  "dockerImage": "postgres:16-alpine"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/postgres.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "main-db", "environmentId": "<environmentId>", "databaseName": "main", "databaseUser": "postgres", "databasePassword": "secure-password-here", "dockerImage": "postgres:16-alpine"}'
```

Save the returned `postgresId`.

### Recommended Docker images

| Use case | Image |
|----------|-------|
| Production | `postgres:16-alpine` |
| With PostGIS | `postgis/postgis:16-3.4-alpine` |
| Latest stable | `postgres:latest` |
| Lightweight testing | `postgres:16-alpine` |

---

## Step 3: Deploy the Database

Start the PostgreSQL container.

**MCP:**

```
mcp__dokploy__postgres-deploy
```

Parameters:
```json
{
  "postgresId": "<postgresId>"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/postgres.deploy" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"postgresId": "<postgresId>"}'
```

---

## Step 4: Set External Port (for external access)

By default, the database is only accessible from other containers on the same Docker network. To connect from outside the server (e.g. from a local machine or external service), expose an external port.

**MCP:**

```
mcp__dokploy__postgres-saveExternalPort
```

Parameters:
```json
{
  "postgresId": "<postgresId>",
  "externalPort": 5433
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/postgres.saveExternalPort" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"postgresId": "<postgresId>", "externalPort": 5433}'
```

Use a non-default port (not 5432) to avoid conflicts with any host PostgreSQL instance.

---

## Step 5: Set Up Automated Backups

Create a backup schedule using the backup API.

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/backup.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "postgresId": "<postgresId>",
    "schedule": "0 2 * * *",
    "prefix": "main-db-backup",
    "enabled": true,
    "destinationId": "<destinationId>"
  }'
```

### Schedule format (cron)

| Schedule | Meaning |
|----------|---------|
| `0 2 * * *` | Daily at 2:00 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 2 * * 0` | Weekly on Sunday at 2:00 AM |
| `0 2 1 * *` | Monthly on the 1st at 2:00 AM |

### Backup destinations

List available destinations:

```bash
curl -s "$DOKPLOY_URL/api/destination.all" \
  -H "x-api-key: $DOKPLOY_API_KEY"
```

Destinations can be S3-compatible storage (AWS S3, MinIO, etc.) configured in the Dokploy dashboard under **Settings > Destinations**.

---

## Step 6: Verify the Database

### Check database status

**MCP:**

```
mcp__dokploy__postgres-one
```

Parameters:
```json
{
  "postgresId": "<postgresId>"
}
```

Look for `"databaseStatus": "done"` in the response.

### Test the connection

**Internal connection** (from another Dokploy app on the same network):

```
postgresql://postgres:secure-password-here@main-db:5432/postgres
```

**External connection** (from outside the server):

```
postgresql://postgres:secure-password-here@<server-ip>:5433/postgres
```

Get the server IP with:

```
mcp__dokploy__server-publicIp
```

### Test with psql

```bash
psql "postgresql://postgres:secure-password-here@<server-ip>:5433/postgres"
```

---

## Connection String Reference

After provisioning, construct the connection string for your application:

| Component | Internal value | External value |
|-----------|---------------|----------------|
| Host | Container name (e.g. `main-db`) | Server IP |
| Port | `5432` (default) | External port (e.g. `5433`) |
| User | `postgres` (default) | `postgres` |
| Password | Set in Step 2 | Set in Step 2 |
| Database | `postgres` (default) | `postgres` |

### Full connection string

```
postgresql://postgres:<password>@<host>:<port>/postgres
```

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Connection refused externally | No external port set | Complete Step 4 |
| Connection refused internally | Database not deployed | Complete Step 3 |
| Authentication failed | Wrong password | Check password with `mcp__dokploy__postgres-one` |
| Backup not running | Destination not configured | Create a destination in **Settings > Destinations** first |
| Container keeps restarting | Corrupted data volume | Check container logs, consider recreating the database |

See the `troubleshoot` skill for detailed diagnostic procedures.
