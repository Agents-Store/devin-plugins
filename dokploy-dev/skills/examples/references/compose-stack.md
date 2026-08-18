# Scenario: Deploy a Docker Compose Stack

Deploy a multi-container application using a docker-compose.yml file with service-level domain routing.

This scenario walks through deploying a typical web app stack: a web server, an API backend, and a database, all defined in a single docker-compose.yml.

## Contents
- [Prerequisites](#prerequisites)
- [Step 1: Create a Project](#step-1-create-a-project)
- [Step 2: Create the Compose Service](#step-2-create-the-compose-service)
- [Step 3: Set the docker-compose.yml Content](#step-3-set-the-docker-composeyml-content)
- [Step 4: Set Environment Variables (optional)](#step-4-set-environment-variables-optional)
- [Step 5: Deploy the Stack](#step-5-deploy-the-stack)
- [Step 6: Add Domains for Services](#step-6-add-domains-for-services)
- [Step 7: Verify the Deployment](#step-7-verify-the-deployment)
- [Example docker-compose.yml Templates](#example-docker-composeyml-templates)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Dokploy MCP connection verified (run the `setup` skill if not confirmed)
- `$DOKPLOY_URL` and `$DOKPLOY_API_KEY` configured
- A docker-compose.yml file (inline or from a Git repository)

---

## Step 1: Create a Project

**MCP:**

```
mcp__dokploy__project-create
```

Parameters:
```json
{
  "name": "my-stack",
  "description": "Multi-container application stack"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/project.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-stack", "description": "Multi-container application stack"}'
```

Save the returned `projectId`.

**Resolve the target environment** — compose stacks are created inside a project *environment* (default `production`):

```
mcp__dokploy__project-one { "projectId": "<projectId>" }
   → environments[0].environmentId
```

Save the `environmentId`.

---

## Step 2: Create the Compose Service

**MCP:**

```
mcp__dokploy__compose-create
```

Parameters:
```json
{
  "environmentId": "<environmentId>",
  "name": "my-stack",
  "appName": "my-stack"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/compose.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"environmentId": "<environmentId>", "name": "my-stack", "appName": "my-stack"}'
```

Save the returned `composeId`.

---

## Step 3: Set the docker-compose.yml Content

Upload the compose file content. Pass the full YAML as a string.

**MCP:**

```
mcp__dokploy__compose-update
```

Parameters:
```json
{
  "composeId": "<composeId>",
  "composeFile": "version: '3.8'\n\nservices:\n  web:\n    image: nginx:alpine\n    ports:\n      - \"80\"\n    depends_on:\n      - api\n    volumes:\n      - ../files/nginx.conf:/etc/nginx/nginx.conf:ro\n\n  api:\n    image: node:20-alpine\n    working_dir: /app\n    command: node server.js\n    ports:\n      - \"3000\"\n    environment:\n      - DATABASE_URL=postgresql://postgres:secret@db:5432/mydb\n      - NODE_ENV=production\n    depends_on:\n      - db\n    volumes:\n      - ../files/app:/app\n\n  db:\n    image: postgres:16-alpine\n    environment:\n      - POSTGRES_PASSWORD=secret\n      - POSTGRES_DB=mydb\n    volumes:\n      - ../files/pgdata:/var/lib/postgresql/data\n    ports:\n      - \"5432\""
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/compose.update" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"composeId": "<composeId>", "composeFile": "version: '\''3.8'\''\n\nservices:\n  web:\n    image: nginx:alpine\n    ports:\n      - \"80\"\n    depends_on:\n      - api\n\n  api:\n    image: node:20-alpine\n    ports:\n      - \"3000\"\n    environment:\n      - DATABASE_URL=postgresql://postgres:secret@db:5432/mydb\n    depends_on:\n      - db\n\n  db:\n    image: postgres:16-alpine\n    environment:\n      - POSTGRES_PASSWORD=secret\n      - POSTGRES_DB=mydb\n    volumes:\n      - ../files/pgdata:/var/lib/postgresql/data"}'
```

### Important volume path convention

In Dokploy, compose volume paths use `../files/` as the base for persistent data:

```yaml
volumes:
  - ../files/pgdata:/var/lib/postgresql/data
  - ../files/app:/app
  - ../files/nginx.conf:/etc/nginx/nginx.conf:ro
```

Do NOT use named volumes or absolute host paths. Dokploy manages the file storage location.

---

## Step 4: Set Environment Variables (optional)

If the compose file references environment variables with `${VAR}` syntax, set them at the compose level.

**MCP:**

```
mcp__dokploy__compose-saveEnvironment
```

Parameters:
```json
{
  "composeId": "<composeId>",
  "env": "POSTGRES_PASSWORD=secret\nAPP_SECRET=my-secret-key"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/compose.saveEnvironment" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"composeId": "<composeId>", "env": "POSTGRES_PASSWORD=secret\nAPP_SECRET=my-secret-key"}'
```

---

## Step 5: Deploy the Stack

**MCP:**

```
mcp__dokploy__compose-deploy
```

Parameters:
```json
{
  "composeId": "<composeId>"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/compose.deploy" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"composeId": "<composeId>"}'
```

This pulls images, creates containers, and starts all services defined in the compose file.

---

## Step 6: Add Domains for Services

Add a domain for each publicly accessible service. In a compose stack, specify the `composeId` and the target service name.

### Domain for the web service

**MCP:**

```
mcp__dokploy__domain-create
```

Parameters:
```json
{
  "composeId": "<composeId>",
  "host": "app.example.com",
  "port": 80,
  "https": true,
  "serviceName": "web"
}
```

### Domain for the API service (optional)

```json
{
  "composeId": "<composeId>",
  "host": "api.example.com",
  "port": 3000,
  "https": true,
  "serviceName": "api"
}
```

**curl (web service):**

```bash
curl -s -X POST "$DOKPLOY_URL/api/domain.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"composeId": "<composeId>", "host": "app.example.com", "port": 80, "https": true, "serviceName": "web"}'
```

### Key points

- The `port` must match the port the service exposes internally (not the host port).
- The `serviceName` must match the service name in the docker-compose.yml.
- Each service can have its own domain.
- The database service (`db`) typically does NOT need a domain — it is accessed internally by other services.

---

## Step 7: Verify the Deployment

### Check running services

**MCP:**

```
mcp__dokploy__compose-loadServices
```

Parameters:
```json
{
  "composeId": "<composeId>"
}
```

This returns the list of services defined in the compose file and their status.

### Read every container's logs

`compose-loadServices` lists the *defined* services; to see the *running* containers and their logs, enumerate then loop (a stack has many containers — `compose-readLogs` is per-container):

```
mcp__dokploy__compose-one { composeId }
   → appName (e.g. "my-stack-ab12cd"), composeType ("docker-compose")

mcp__dokploy__docker-getContainersByAppNameMatch
   → { appName: "my-stack-ab12cd", appType: "docker-compose" }
   → [ { containerId, name, state, status }, ... ]   # web, api, db

for each container:
  mcp__dokploy__compose-readLogs
    → { composeId, containerId: "<containerId>", tail: 200, search: "error" }
```

Read **all** of them — a crashed `db` container shows up as `ECONNREFUSED` in `api`, so the lowest-level failing container is the real root cause. `/dokploy-dev:compose-logs my-stack` runs this whole loop and highlights errors per container.

### Validate the compose file

**MCP:**

```
mcp__dokploy__compose-getConvertedCompose
```

Parameters:
```json
{
  "composeId": "<composeId>"
}
```

This returns the processed compose file with Dokploy's modifications applied. Use it to verify the final configuration.

### Test the endpoints

```bash
# Test web service
curl -s -o /dev/null -w "%{http_code}" https://app.example.com

# Test API service
curl -s -o /dev/null -w "%{http_code}" https://api.example.com
```

---

## Example docker-compose.yml Templates

### Minimal web app + database

```yaml
version: '3.8'

services:
  app:
    image: node:20-alpine
    working_dir: /app
    command: node server.js
    ports:
      - "3000"
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/mydb
    depends_on:
      - db
    volumes:
      - ../files/app:/app

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=mydb
    volumes:
      - ../files/pgdata:/var/lib/postgresql/data
```

### WordPress

```yaml
version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    ports:
      - "80"
    environment:
      - WORDPRESS_DB_HOST=db
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=${DB_PASSWORD}
      - WORDPRESS_DB_NAME=wordpress
    depends_on:
      - db
    volumes:
      - ../files/wp-content:/var/www/html/wp-content

  db:
    image: mariadb:10
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_PASSWORD}
      - MYSQL_DATABASE=wordpress
      - MYSQL_USER=wordpress
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - ../files/mysql:/var/lib/mysql
```

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Deploy fails | Invalid docker-compose.yml | Call `mcp__dokploy__compose-getConvertedCompose` to validate the file |
| Service not starting | Image pull failure or crash | Read that container's logs: `docker-getContainersByAppNameMatch { appName, appType: "docker-compose" }` → `compose-readLogs { composeId, containerId }` (or `/dokploy-dev:compose-logs`). Verify the image name and tag exist |
| 502 on domain | Wrong port or service name | Verify `port` and `serviceName` match the compose file |
| Volume data lost | Wrong volume path | Use `../files/` prefix for all persistent volumes |
| Services cannot communicate | Network misconfiguration | Compose services share a network by default. Reference services by their compose service name |
| Environment variables not resolving | Vars not set at compose level | Set vars with `mcp__dokploy__compose-saveEnvironment` (Step 4) |

See the `troubleshoot` skill for detailed diagnostic procedures.
