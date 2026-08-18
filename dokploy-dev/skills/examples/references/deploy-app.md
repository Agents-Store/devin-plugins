# Scenario: Deploy a Web Application

Deploy a web app from a GitHub repository to a running application with a custom domain and HTTPS.

## Contents
- [Prerequisites](#prerequisites)
- [Step 1: Create a Project](#step-1-create-a-project)
- [Step 2: Create an Application](#step-2-create-an-application)
- [Step 3: Connect GitHub Repository](#step-3-connect-github-repository)
- [Step 4: Set Build Type](#step-4-set-build-type)
- [Step 5: Set Environment Variables](#step-5-set-environment-variables)
- [Step 6: Add a Domain](#step-6-add-a-domain)
- [Step 7: Deploy](#step-7-deploy)
- [Step 8: Verify](#step-8-verify)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Dokploy MCP connection verified (run the `setup` skill if not confirmed)
- A GitHub repository with the application source code
- A domain name with DNS pointed to the Dokploy server IP
- `$DOKPLOY_URL` and `$DOKPLOY_API_KEY` configured

---

## Step 1: Create a Project

Every application in Dokploy lives inside a project. Create one first.

**MCP:**

```
mcp__dokploy__project-create
```

Parameters:
```json
{
  "name": "my-web-app",
  "description": "Production web application"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/project.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-web-app", "description": "Production web application"}'
```

Save the returned `projectId` for the next steps.

**Resolve the target environment** — resources live under a project *environment* (default `production`), not the project itself:

```
mcp__dokploy__project-one { "projectId": "<projectId>" }
   → environments[0].environmentId
```

(Or `environment-byProjectId { projectId }`.) Save the `environmentId`.

---

## Step 2: Create an Application

Create an application resource within the project's environment.

**MCP:**

```
mcp__dokploy__application-create
```

Parameters:
```json
{
  "environmentId": "<environmentId from Step 1>",
  "name": "my-web-app",
  "appName": "my-web-app"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"environmentId": "<environmentId>", "name": "my-web-app", "appName": "my-web-app"}'
```

Save the returned `applicationId`.

---

## Step 3: Connect GitHub Repository

Link the application to a GitHub repository.

**MCP:**

```
mcp__dokploy__application-saveGithubProvider
```

Parameters (`repository` is the repo **name only** — NOT the full URL; get `githubId` from `gitProvider-getAll`):
```json
{
  "applicationId": "<applicationId from Step 2>",
  "repository": "repo",
  "branch": "main",
  "owner": "owner",
  "githubId": "<githubId>",
  "triggerType": "push",
  "buildPath": "/"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.saveGithubProvider" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"applicationId": "<applicationId>", "repository": "repo", "branch": "main", "owner": "owner", "githubId": "<githubId>", "triggerType": "push", "buildPath": "/"}'
```

---

## Step 4: Set Build Type

Choose the build method. Nixpacks auto-detects the language and framework. Use Dockerfile if the repo contains a Dockerfile.

**MCP:**

```
mcp__dokploy__application-saveBuildType
```

Parameters:
```json
{
  "applicationId": "<applicationId>",
  "buildType": "nixpacks"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.saveBuildType" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"applicationId": "<applicationId>", "buildType": "nixpacks"}'
```

Valid build types: `nixpacks`, `dockerfile`, `heroku_buildpacks`, `paketo_buildpacks`, `static`.

---

## Step 5: Set Environment Variables

Pass environment variables to the application. Use the `KEY=VALUE\nKEY2=VALUE2` format (newline-separated).

**MCP:**

```
mcp__dokploy__application-saveEnvironment
```

Parameters:
```json
{
  "applicationId": "<applicationId>",
  "env": "NODE_ENV=production\nDATABASE_URL=postgresql://user:pass@db:5432/mydb\nPORT=3000"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.saveEnvironment" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"applicationId": "<applicationId>", "env": "NODE_ENV=production\nDATABASE_URL=postgresql://user:pass@db:5432/mydb\nPORT=3000"}'
```

---

## Step 6: Add a Domain

Configure a custom domain with HTTPS. The app must listen on the port specified here.

**MCP:**

```
mcp__dokploy__domain-create
```

Parameters:
```json
{
  "applicationId": "<applicationId>",
  "host": "app.example.com",
  "port": 3000,
  "https": true
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/domain.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"applicationId": "<applicationId>", "host": "app.example.com", "port": 3000, "https": true}'
```

**Important:** The port must match the port the application listens on internally. Common defaults:
- Next.js / Node.js: `3000`
- Laravel / PHP: `8000`
- Django / Python: `8000`
- Go: `8080`
- Static sites: `80`

---

## Step 7: Deploy

Trigger the deployment. Dokploy will clone the repo, build the image, and start the container.

**MCP:**

```
mcp__dokploy__application-deploy
```

Parameters:
```json
{
  "applicationId": "<applicationId>"
}
```

**curl:**

```bash
curl -s -X POST "$DOKPLOY_URL/api/application.deploy" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"applicationId": "<applicationId>"}'
```

---

## Step 8: Verify

Check that the deployment succeeded and the domain is working.

### Check application status

**MCP:**

```
mcp__dokploy__application-one
```

Parameters:
```json
{
  "applicationId": "<applicationId>"
}
```

Look for `"applicationStatus": "done"` in the response.

### Validate domain

**MCP:**

```
mcp__dokploy__domain-validateDomain
```

Parameters (the **hostname string**, not the domainId):
```json
{
  "domain": "app.example.com"
}
```

### Test the endpoint

```bash
curl -s -o /dev/null -w "%{http_code}" https://app.example.com
```

Expected: `200`.

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Build fails | Wrong build type or missing dependencies | Check build logs, switch to Dockerfile if Nixpacks fails |
| 502 Bad Gateway | App not listening on 0.0.0.0 | Set `HOST=0.0.0.0` in env vars |
| Domain not resolving | DNS not configured | Add an A record pointing to the server IP |
| SSL error | Certificate not issued yet | Wait a few minutes for Let's Encrypt to issue the certificate |
| App crashes on start | Missing env vars | Compare required env vars with what is set in Step 5 |

See the `troubleshoot` skill for detailed diagnostic procedures.
