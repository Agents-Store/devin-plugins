# API Reference: Compose, Docker, Mounts, Registry

## Contents
- [Compose (28 endpoints)](#compose-28-endpoints)
- [Docker (7 endpoints)](#docker-7-endpoints)
- [Mounts (6 endpoints)](#mounts-6-endpoints)
- [Registry (7 endpoints)](#registry-7-endpoints)

## Compose (28 endpoints)

Compose services deploy multi-container apps from docker-compose.yml files.

### Read operations

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/compose.one` | compose.one | Get a compose service by ID |
| GET | `/compose.search` | compose.search | Search compose services by name |
| GET | `/compose.templates` | compose.templates | List available compose templates |
| GET | `/compose.getTags` | compose.getTags | Get available template tags |
| GET | `/compose.loadServices` | compose.loadServices | Parse and list services from a compose file |
| GET | `/compose.loadMountsByService` | compose.loadMountsByService | List mounts for a specific compose service |
| GET | `/compose.getConvertedCompose` | compose.getConvertedCompose | Get the resolved/converted compose YAML |
| GET | `/compose.getDefaultCommand` | compose.getDefaultCommand | Get the default docker compose command |
| GET | `/compose.fetchSourceType` | compose.fetchSourceType | Detect the source type (git, raw, etc.) |

### Create & delete

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/compose.create` | compose.create | Create a new compose service |
| POST | `/compose.delete` | compose.delete | Delete a compose service |
| POST | `/compose.import` | compose.import | Import a compose file from raw YAML |

### Lifecycle

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/compose.deploy` | compose.deploy | Deploy the compose stack |
| POST | `/compose.redeploy` | compose.redeploy | Force redeploy from scratch |
| POST | `/compose.start` | compose.start | Start all compose containers |
| POST | `/compose.stop` | compose.stop | Stop all compose containers |
| POST | `/compose.cancelDeployment` | compose.cancelDeployment | Cancel an in-progress deployment |
| POST | `/compose.killBuild` | compose.killBuild | Kill a running build |
| POST | `/compose.cleanQueues` | compose.cleanQueues | Clear the deployment queue |
| POST | `/compose.clearDeployments` | compose.clearDeployments | Remove all deployment history |
| POST | `/compose.isolatedDeployment` | compose.isolatedDeployment | Deploy a single service in isolation |

### Update & configuration

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/compose.update` | compose.update | Update compose configuration |
| POST | `/compose.move` | compose.move | Move to a different project |
| POST | `/compose.randomizeCompose` | compose.randomizeCompose | Randomize ports/names to avoid conflicts |

### Templates

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/compose.deployTemplate` | compose.deployTemplate | Deploy from a predefined template |
| POST | `/compose.processTemplate` | compose.processTemplate | Process template variables |

### Git provider

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/compose.disconnectGitProvider` | compose.disconnectGitProvider | Disconnect git source |
| POST | `/compose.refreshToken` | compose.refreshToken | Refresh git provider OAuth token |

### Key parameters

**compose.create**
```json
{
  "name": "string (required)",
  "projectId": "string (required)",
  "description": "string",
  "composeFile": "string (raw docker-compose.yml content)",
  "serverId": "string"
}
```

**compose.deploy / compose.redeploy**
```json
{
  "composeId": "string (required)"
}
```

**compose.import**
```json
{
  "projectId": "string (required)",
  "name": "string (required)",
  "composeFile": "string (required — raw YAML)"
}
```

**compose.deployTemplate**
```json
{
  "projectId": "string (required)",
  "templateId": "string (required)"
}
```

---

## Docker (7 endpoints)

Direct Docker container inspection and management.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/docker.getConfig` | docker.getConfig | Get Docker daemon configuration |
| GET | `/docker.getContainers` | docker.getContainers | List all containers on the host |
| GET | `/docker.getContainersByAppLabel` | docker.getContainersByAppLabel | Find containers by Dokploy app label |
| GET | `/docker.getContainersByAppNameMatch` | docker.getContainersByAppNameMatch | Find containers matching an app name |
| GET | `/docker.getServiceContainersByAppName` | docker.getServiceContainersByAppName | Get service containers for a specific app |
| GET | `/docker.getStackContainersByAppName` | docker.getStackContainersByAppName | Get all stack containers for an app |
| POST | `/docker.restartContainer` | docker.restartContainer | Restart a specific container |

### Key parameters

**docker.getContainersByAppNameMatch**
- Query: `appName` (required)

**docker.restartContainer**
```json
{
  "containerId": "string (required)",
  "serverId": "string (optional)"
}
```

---

## Mounts (6 endpoints)

Volume and bind mounts for applications and compose services.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/mounts.allNamedByApplicationId` | mounts.allNamedByApplicationId | List named volumes for an application |
| GET | `/mounts.listByServiceId` | mounts.listByServiceId | List mounts for a compose service |
| GET | `/mounts.one` | mounts.one | Get a single mount by ID |
| POST | `/mounts.create` | mounts.create | Create a new mount |
| POST | `/mounts.remove` | mounts.remove | Remove a mount |
| POST | `/mounts.update` | mounts.update | Update mount configuration |

### Key parameters

**mounts.create**
```json
{
  "mountPath": "string (required — path inside container)",
  "hostPath": "string (for bind mounts)",
  "volumeName": "string (for named volumes)",
  "type": "bind | volume | file",
  "content": "string (for file mounts — file content)",
  "applicationId": "string",
  "composeId": "string",
  "serviceType": "application | compose"
}
```

---

## Registry (7 endpoints)

Docker registry connections for pulling private images.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/registry.all` | registry.all | List all configured registries |
| GET | `/registry.one` | registry.one | Get a single registry |
| POST | `/registry.create` | registry.create | Add a new registry |
| POST | `/registry.remove` | registry.remove | Remove a registry |
| POST | `/registry.update` | registry.update | Update registry credentials |
| POST | `/registry.testRegistry` | registry.testRegistry | Test registry connection with credentials |
| POST | `/registry.testRegistryById` | registry.testRegistryById | Test an existing registry connection |

### Key parameters

**registry.create**
```json
{
  "registryName": "string (required)",
  "registryType": "selfHosted | dockerHub | gcr | ghcr | ecr | digitalocean | azure",
  "registryUrl": "string (required for selfHosted)",
  "username": "string (required)",
  "password": "string (required)",
  "imagePrefix": "string (optional — e.g. my-org)"
}
```
