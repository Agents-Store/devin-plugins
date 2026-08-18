# API Reference: Server, Settings, Backup, Notifications, Users

## Contents
- [Server (16 endpoints)](#server-16-endpoints)
- [Settings (49 endpoints)](#settings-49-endpoints)
- [Backup (11 endpoints)](#backup-11-endpoints)
- [Notification (38 endpoints)](#notification-38-endpoints)
- [User (20 endpoints)](#user-20-endpoints)

## Server (16 endpoints)

Manage remote servers connected to Dokploy for multi-server deployments.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/server.all` | server.all | List all registered servers |
| GET | `/server.one` | server.one | Get a server by ID |
| GET | `/server.count` | server.count | Get total server count |
| GET | `/server.buildServers` | server.buildServers | List servers available as build targets |
| GET | `/server.publicIp` | server.publicIp | Get the public IP of a server |
| GET | `/server.security` | server.security | Get server security settings |
| GET | `/server.validate` | server.validate | Validate server SSH connectivity |
| GET | `/server.withSSHKey` | server.withSSHKey | Get server details including SSH key |
| GET | `/server.getDefaultCommand` | server.getDefaultCommand | Get the default setup command for a server |
| GET | `/server.getServerMetrics` | server.getServerMetrics | Get CPU, memory, disk metrics |
| GET | `/server.getServerTime` | server.getServerTime | Get current time on the server |
| POST | `/server.create` | server.create | Register a new remote server |
| POST | `/server.remove` | server.remove | Unregister a server |
| POST | `/server.setup` | server.setup | Run initial setup (install Docker, Traefik) |
| POST | `/server.setupMonitoring` | server.setupMonitoring | Install monitoring stack on server |
| POST | `/server.update` | server.update | Update server configuration |

### Key parameters

**server.create**
```json
{
  "name": "string (required)",
  "ipAddress": "string (required)",
  "port": "number (default: 22)",
  "username": "string (default: root)",
  "sshKeyId": "string (required — SSH key for connection)",
  "description": "string"
}
```

**server.one / server.remove**
- `serverId` (required)

---

## Settings (49 endpoints)

Global Dokploy instance configuration, Traefik management, and system operations.

### Status & info (GET)

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/settings.health` | settings.health | Health check |
| GET | `/settings.getIp` | settings.getIp | Get the Dokploy server's IP address |
| GET | `/settings.getDokployVersion` | settings.getDokployVersion | Get current Dokploy version |
| GET | `/settings.getReleaseTag` | settings.getReleaseTag | Get the current release tag |
| GET | `/settings.getTraefikPorts` | settings.getTraefikPorts | Get Traefik HTTP/HTTPS port config |
| GET | `/settings.checkGPUStatus` | settings.checkGPUStatus | Check if GPU support is available |
| GET | `/settings.getLogCleanupStatus` | settings.getLogCleanupStatus | Get log cleanup schedule status |
| GET | `/settings.getOpenApiDocument` | settings.getOpenApiDocument | Get the full OpenAPI spec |
| GET | `/settings.isCloud` | settings.isCloud | Check if running as Dokploy Cloud |
| GET | `/settings.haveActivateRequests` | settings.haveActivateRequests | Check for pending activation requests |
| GET | `/settings.haveTraefikDashboardPortEnabled` | settings.haveTraefikDashboardPortEnabled | Check if Traefik dashboard port is open |
| GET | `/settings.isUserSubscribed` | settings.isUserSubscribed | Check subscription status (Cloud) |
| GET | `/settings.getDokployCloudIps` | settings.getDokployCloudIps | Get Dokploy Cloud IP allowlist |
| GET | `/settings.getUpdateData` | settings.getUpdateData | Check for available updates |

### Traefik config (GET)

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/settings.readTraefikConfig` | settings.readTraefikConfig | Read main Traefik config file |
| GET | `/settings.readTraefikEnv` | settings.readTraefikEnv | Read Traefik environment variables |
| GET | `/settings.readTraefikFile` | settings.readTraefikFile | Read a specific Traefik config file |
| GET | `/settings.readMiddlewareTraefikConfig` | settings.readMiddlewareTraefikConfig | Read Traefik middleware config |
| GET | `/settings.readWebServerTraefikConfig` | settings.readWebServerTraefikConfig | Read web server Traefik routing |
| GET | `/settings.readDirectories` | settings.readDirectories | List Traefik config directories |
| GET | `/settings.getWebServerSettings` | settings.getWebServerSettings | Get web server configuration |

### Cleanup operations (POST)

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/settings.cleanAll` | settings.cleanAll | Run all cleanup operations |
| POST | `/settings.cleanAllDeploymentQueue` | settings.cleanAllDeploymentQueue | Clear all deployment queues |
| POST | `/settings.cleanDockerBuilder` | settings.cleanDockerBuilder | Remove Docker builder cache |
| POST | `/settings.cleanDockerPrune` | settings.cleanDockerPrune | Docker system prune |
| POST | `/settings.cleanMonitoring` | settings.cleanMonitoring | Remove monitoring data |
| POST | `/settings.cleanRedis` | settings.cleanRedis | Flush Redis cache |
| POST | `/settings.cleanSSHPrivateKey` | settings.cleanSSHPrivateKey | Remove stored SSH keys |
| POST | `/settings.cleanStoppedContainers` | settings.cleanStoppedContainers | Remove all stopped containers |
| POST | `/settings.cleanUnusedImages` | settings.cleanUnusedImages | Remove dangling Docker images |
| POST | `/settings.cleanUnusedVolumes` | settings.cleanUnusedVolumes | Remove unused Docker volumes |

### System operations (POST)

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/settings.reloadRedis` | settings.reloadRedis | Restart Redis connection |
| POST | `/settings.reloadServer` | settings.reloadServer | Reload the Dokploy server process |
| POST | `/settings.reloadTraefik` | settings.reloadTraefik | Reload Traefik configuration |
| POST | `/settings.assignDomainServer` | settings.assignDomainServer | Assign the dashboard domain |
| POST | `/settings.saveSSHPrivateKey` | settings.saveSSHPrivateKey | Store an SSH private key |
| POST | `/settings.setupGPU` | settings.setupGPU | Install GPU drivers and runtime |
| POST | `/settings.toggleDashboard` | settings.toggleDashboard | Enable/disable Traefik dashboard |
| POST | `/settings.toggleRequests` | settings.toggleRequests | Enable/disable activation requests |

### Update config (POST)

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/settings.updateDockerCleanup` | settings.updateDockerCleanup | Configure Docker auto-cleanup schedule |
| POST | `/settings.updateLogCleanup` | settings.updateLogCleanup | Configure log rotation/cleanup |
| POST | `/settings.updateMiddlewareTraefikConfig` | settings.updateMiddlewareTraefikConfig | Update Traefik middleware rules |
| POST | `/settings.updateServer` | settings.updateServer | Update server-level settings |
| POST | `/settings.updateServerIp` | settings.updateServerIp | Change the server's IP address |
| POST | `/settings.updateTraefikConfig` | settings.updateTraefikConfig | Update main Traefik config |
| POST | `/settings.updateTraefikFile` | settings.updateTraefikFile | Write a Traefik config file |
| POST | `/settings.updateTraefikPorts` | settings.updateTraefikPorts | Change HTTP/HTTPS ports |
| POST | `/settings.updateWebServerTraefikConfig` | settings.updateWebServerTraefikConfig | Update web server routing |
| POST | `/settings.writeTraefikEnv` | settings.writeTraefikEnv | Write Traefik environment variables |

---

## Backup (11 endpoints)

Database backup management and manual backup triggers.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/backup.one` | backup.one | Get a backup configuration |
| GET | `/backup.listBackupFiles` | backup.listBackupFiles | List backup files for a config |
| POST | `/backup.create` | backup.create | Create a scheduled backup configuration |
| POST | `/backup.update` | backup.update | Update backup schedule/settings |
| POST | `/backup.remove` | backup.remove | Remove a backup configuration |
| POST | `/backup.manualBackupPostgres` | backup.manualBackupPostgres | Trigger immediate PostgreSQL backup |
| POST | `/backup.manualBackupMySql` | backup.manualBackupMySql | Trigger immediate MySQL backup |
| POST | `/backup.manualBackupMariadb` | backup.manualBackupMariadb | Trigger immediate MariaDB backup |
| POST | `/backup.manualBackupMongo` | backup.manualBackupMongo | Trigger immediate MongoDB backup |
| POST | `/backup.manualBackupCompose` | backup.manualBackupCompose | Trigger immediate compose service backup |
| POST | `/backup.manualBackupWebServer` | backup.manualBackupWebServer | Trigger immediate web server backup |

### Key parameters

**backup.create**
```json
{
  "schedule": "string (required — cron expression, e.g. '0 2 * * *')",
  "prefix": "string (backup file prefix)",
  "destination": "string (required — s3 | local)",
  "enabled": "boolean (default: true)",
  "postgresId": "string (for Postgres backups)",
  "mysqlId": "string (for MySQL backups)",
  "mariadbId": "string (for MariaDB backups)",
  "mongoId": "string (for MongoDB backups)"
}
```

**backup.manualBackupPostgres**
```json
{
  "postgresId": "string (required)"
}
```

---

## Notification (38 endpoints)

Notification provider management. Dokploy supports 12 notification channels, each with create, update, remove, and test operations.

### Global

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/notification.all` | notification.all | List all notification providers |
| GET | `/notification.one` | notification.one | Get a notification provider by ID |
| GET | `/notification.getEmailProviders` | notification.getEmailProviders | List configured email providers |
| POST | `/notification.receiveNotification` | notification.receiveNotification | Webhook endpoint for incoming notifications |

### Per-provider operations

Each provider has 4 endpoints: `create`, `update`, `remove`, `test`. The path pattern is:

```
POST /notification.create{Provider}
POST /notification.update{Provider}
POST /notification.remove{Provider}
POST /notification.test{Provider}
```

| Provider | create | update | remove | test |
|----------|--------|--------|--------|------|
| Discord | `createDiscord` | `updateDiscord` | `removeDiscord` | `testDiscord` |
| Email | `createEmail` | `updateEmail` | `removeEmail` | `testEmail` |
| Slack | `createSlack` | `updateSlack` | `removeSlack` | `testSlack` |
| Telegram | `createTelegram` | `updateTelegram` | `removeTelegram` | `testTelegram` |
| Teams | `createTeams` | `updateTeams` | `removeTeams` | `testTeams` |
| Gotify | `createGotify` | `updateGotify` | `removeGotify` | `testGotify` |
| Ntfy | `createNtfy` | `updateNtfy` | `removeNtfy` | `testNtfy` |
| Pushover | `createPushover` | `updatePushover` | `removePushover` | `testPushover` |
| Resend | `createResend` | `updateResend` | `removeResend` | `testResend` |
| Lark | `createLark` | `updateLark` | `removeLark` | `testLark` |
| Custom | `createCustom` | `updateCustom` | `removeCustom` | `testCustom` |

### Key parameters by provider

**Discord / Slack / Teams / Lark**
```json
{
  "name": "string (required)",
  "webhookUrl": "string (required)",
  "channel": "string (optional)"
}
```

**Telegram**
```json
{
  "name": "string (required)",
  "botToken": "string (required)",
  "chatId": "string (required)"
}
```

**Email**
```json
{
  "name": "string (required)",
  "smtpServer": "string (required)",
  "smtpPort": "number (required)",
  "username": "string",
  "password": "string",
  "fromAddress": "string (required)",
  "toAddresses": ["string"]
}
```

**Custom**
```json
{
  "name": "string (required)",
  "webhookUrl": "string (required)",
  "method": "POST | GET",
  "headers": "object (optional)",
  "body": "string (optional — template)"
}
```

---

## User (20 endpoints)

User management, API keys, permissions, and metrics.

### Read operations

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/user.all` | user.all | List all users |
| GET | `/user.get` | user.get | Get current authenticated user |
| GET | `/user.one` | user.one | Get a user by ID |
| GET | `/user.session` | user.session | Get current session info |
| GET | `/user.haveRootAccess` | user.haveRootAccess | Check if current user is admin |
| GET | `/user.getPermissions` | user.getPermissions | Get permissions for current user |
| GET | `/user.getInvitations` | user.getInvitations | List pending invitations |
| GET | `/user.checkUserOrganizations` | user.checkUserOrganizations | Check organization memberships |
| GET | `/user.getBackups` | user.getBackups | List user's backup configs |
| GET | `/user.getContainerMetrics` | user.getContainerMetrics | Get container-level metrics |
| GET | `/user.getServerMetrics` | user.getServerMetrics | Get server-level metrics for user |
| GET | `/user.getMetricsToken` | user.getMetricsToken | Get the metrics authentication token |
| GET | `/user.getUserByToken` | user.getUserByToken | Look up user by API token |

### Mutations

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| POST | `/user.createApiKey` | user.createApiKey | Generate a new API key |
| POST | `/user.deleteApiKey` | user.deleteApiKey | Revoke an API key |
| POST | `/user.generateToken` | user.generateToken | Generate an auth token |
| POST | `/user.assignPermissions` | user.assignPermissions | Assign project permissions to a user |
| POST | `/user.sendInvitation` | user.sendInvitation | Invite a new user |
| POST | `/user.update` | user.update | Update user profile |
| POST | `/user.remove` | user.remove | Delete a user |

### Key parameters

**user.createApiKey**
```json
{
  "name": "string (required — descriptive label)",
  "expiresAt": "string (optional — ISO date)"
}
```

**user.assignPermissions**
```json
{
  "userId": "string (required)",
  "projectId": "string (required)",
  "permissions": ["create", "deploy", "delete", "update"]
}
```

**user.sendInvitation**
```json
{
  "email": "string (required)",
  "role": "admin | user"
}
```

**user.update**
```json
{
  "userId": "string (required)",
  "email": "string",
  "password": "string",
  "role": "string"
}
```
