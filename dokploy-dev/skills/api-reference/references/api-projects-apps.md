# API Reference: Projects, Applications, Environments, Deployments

## Contents
- [Project (8 endpoints)](#project-8-endpoints)
- [Application (31 endpoints)](#application-31-endpoints)
- [Environment (7 endpoints)](#environment-7-endpoints)
- [Deployment (8 endpoints)](#deployment-8-endpoints)

## Project (8 endpoints)

Projects are top-level containers that hold applications, compose services, and databases.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/project.all` | project.all | List all projects with their services |
| GET | `/project.one` | project.one | Get a single project by ID |
| GET | `/project.search` | project.search | Search projects by name/description |
| GET | `/project.allForPermissions` | project.allForPermissions | List projects the current user has access to |
| POST | `/project.create` | project.create | Create a new project |
| POST | `/project.update` | project.update | Update project name/description |
| POST | `/project.duplicate` | project.duplicate | Duplicate an existing project and its services |
| POST | `/project.remove` | project.remove | Delete a project and all its services |

### Key parameters

**project.create**
```json
{
  "name": "string (required)",
  "description": "string",
  "serverId": "string (optional — target server)"
}
```

**project.one / project.remove**
```json
{
  "projectId": "string (required)"
}
```

---

## Application (31 endpoints)

Applications are deployable services within a project — Docker images, GitHub repos, or raw Dockerfiles.

### Read operations

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/application.one` | application.one | Get application by ID with full config |
| GET | `/application.search` | application.search | Search applications by name |
| GET | `/application.readAppMonitoring` | application.readAppMonitoring | Get monitoring data (CPU, memory, network) |
| GET | `/application.readTraefikConfig` | application.readTraefikConfig | Read the Traefik routing config for this app |

### Create & delete

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/application.create` | application.create | Create a new application in a project |
| POST | `/application.delete` | application.delete | Delete an application |

### Lifecycle

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/application.deploy` | application.deploy | Trigger a deployment |
| POST | `/application.redeploy` | application.redeploy | Force redeploy (rebuild from scratch) |
| POST | `/application.start` | application.start | Start a stopped application |
| POST | `/application.stop` | application.stop | Stop a running application |
| POST | `/application.reload` | application.reload | Reload the application container |
| POST | `/application.markRunning` | application.markRunning | Manually mark app as running |
| POST | `/application.cancelDeployment` | application.cancelDeployment | Cancel an in-progress deployment |
| POST | `/application.killBuild` | application.killBuild | Kill a running build process |
| POST | `/application.cleanQueues` | application.cleanQueues | Clear the deployment queue |
| POST | `/application.clearDeployments` | application.clearDeployments | Remove all deployment history |

### Update & move

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/application.update` | application.update | Update application configuration |
| POST | `/application.move` | application.move | Move application to a different project |

### Build & source providers

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/application.saveBuildType` | application.saveBuildType | Set build type (dockerfile, nixpacks, buildpack, heroku) |
| POST | `/application.saveEnvironment` | application.saveEnvironment | Save environment variables |
| POST | `/application.saveDockerProvider` | application.saveDockerProvider | Configure Docker image source |
| POST | `/application.saveGithubProvider` | application.saveGithubProvider | Configure GitHub repo source |
| POST | `/application.saveGitlabProvider` | application.saveGitlabProvider | Configure GitLab repo source |
| POST | `/application.saveBitbucketProvider` | application.saveBitbucketProvider | Configure Bitbucket repo source |
| POST | `/application.saveGiteaProvider` | application.saveGiteaProvider | Configure Gitea repo source |
| POST | `/application.saveGitProvider` | application.saveGitProvider | Configure generic Git repo source |
| POST | `/application.disconnectGitProvider` | application.disconnectGitProvider | Disconnect current git provider |
| POST | `/application.refreshToken` | application.refreshToken | Refresh the git provider OAuth token |

### Traefik

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/application.updateTraefikConfig` | application.updateTraefikConfig | Update custom Traefik routing rules |

### Key parameters

**application.create**
```json
{
  "name": "string (required)",
  "environmentId": "string (required — resources live under a project environment)",
  "appName": "string",
  "description": "string",
  "serverId": "string"
}
```

**application.deploy / application.redeploy**
```json
{
  "applicationId": "string (required)"
}
```

**application.saveBuildType**
```json
{
  "applicationId": "string (required)",
  "buildType": "dockerfile | nixpacks | buildpack | heroku"
}
```

**application.saveGithubProvider**
```json
{
  "applicationId": "string (required)",
  "repository": "string (required — repo name only, NOT full URL)",
  "branch": "string (required)",
  "owner": "string (required)",
  "githubId": "string (required — from gitProvider.getAll)",
  "triggerType": "string (required, default: push)",
  "buildPath": "string (required, default: /)"
}
```

---

## Environment (7 endpoints)

Environments partition a project (default: `production`); applications, databases and compose stacks are created **inside an environment** (`environmentId`) — resolve it via `environment.byProjectId` or the `environments` array on `project.one`.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/environment.byProjectId` | environment.byProjectId | List environments for a project |
| GET | `/environment.one` | environment.one | Get a single environment |
| GET | `/environment.search` | environment.search | Search environments by name |
| POST | `/environment.create` | environment.create | Create a new environment |
| POST | `/environment.duplicate` | environment.duplicate | Duplicate an environment |
| POST | `/environment.remove` | environment.remove | Delete an environment |
| POST | `/environment.update` | environment.update | Update environment name/description |

### Key parameters

**environment.create**
```json
{
  "name": "string (required)",
  "projectId": "string (required)",
  "description": "string"
}
```

---

## Deployment (8 endpoints)

Deployments track build and deploy history across all services.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/deployment.all` | deployment.all | List all deployments for an application (`applicationId` only) |
| GET | `/deployment.allByCompose` | deployment.allByCompose | List deployments for a compose service |
| GET | `/deployment.allByServer` | deployment.allByServer | List deployments on a specific server |
| GET | `/deployment.allByType` | deployment.allByType | List deployments filtered by service type |
| GET | `/deployment.allCentralized` | deployment.allCentralized | List all deployments across all services |
| GET | `/deployment.queueList` | deployment.queueList | List pending deployments in the queue |
| POST | `/deployment.killProcess` | deployment.killProcess | Kill a running deployment process |
| POST | `/deployment.removeDeployment` | deployment.removeDeployment | Remove a deployment record |

### Key parameters

**deployment.all**
- Query: `applicationId` (required)

**deployment.allByCompose**
- Query: `composeId` (required)

**deployment.allByServer**
- Query: `serverId` (required)

**deployment.killProcess / deployment.removeDeployment**
```json
{
  "deploymentId": "string (required)"
}
```
