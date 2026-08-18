---
name: examples
description: "This skill should be used when learning how to deploy apps, provision databases, set up Docker Compose stacks, or debug a failed deployment on Dokploy. Provides end-to-end workflow walkthroughs. Triggers: \"dokploy example\", \"how to deploy on dokploy\", \"dokploy tutorial\", \"dokploy walkthrough\", \"show me how to use dokploy\", \"dokploy debug example\"."
---

# Dokploy Examples

Step-by-step walkthroughs covering the most common Dokploy workflows. Each scenario uses MCP tools as the primary method, with equivalent curl commands shown alongside where relevant.

---

## Scenario 1: Deploy a Web Application

Deploy a web app from a GitHub repository to a running application with a custom domain and HTTPS.

Covers: project creation, application setup, GitHub integration, environment variables, domain configuration, and deployment.

See full walkthrough: [references/deploy-app.md](references/deploy-app.md)

---

## Scenario 2: Provision a Database

Create, configure, and expose a PostgreSQL database with external access and automated backups.

Covers: database creation, deployment, external port configuration, connection string construction, and backup scheduling.

See full walkthrough: [references/provision-database.md](references/provision-database.md)

---

## Scenario 3: Deploy a Docker Compose Stack

Deploy a multi-container application using a docker-compose.yml file with service-level domain routing.

Covers: compose service creation, compose file content, environment variables, deployment, and per-service domain assignment.

See full walkthrough: [references/compose-stack.md](references/compose-stack.md)

---

## Scenario 4: Debug a Failed Deployment

Diagnose and recover from a failed deployment end-to-end — locate the failed run, read the build log, inspect the container, check Traefik, optionally AI-summarise, apply the fix, and verify.

Covers: `deployment-all` filtering, reading runtime + build logs over MCP (`application-readLogs` / per-container `compose-readLogs` / `deployment-readLogs`, v0.29.0+ (current v0.29.14)), `docker-getContainersByAppLabel` + `docker-getConfig` introspection, `ai-analyzeLogs { aiId, logs, context }` integration, and choosing the right recovery action.

See full walkthrough: [references/debug-failed-deploy.md](references/debug-failed-deploy.md)
