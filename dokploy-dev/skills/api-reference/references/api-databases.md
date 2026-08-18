# API Reference: Databases

## Contents
- [Common endpoint pattern](#common-endpoint-pattern)
- [Database type prefixes](#database-type-prefixes)
- [Key parameters](#key-parameters)
- [Full endpoint count](#full-endpoint-count)

Dokploy supports 5 managed database types. Each has an identical set of 14 endpoints following the same pattern.

## Common endpoint pattern

All database types share the same operations. Replace `{db}` with the database prefix:

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/{db}.one` | {db}.one | Get database service by ID |
| GET | `/{db}.search` | {db}.search | Search database services by name |
| POST | `/{db}.create` | {db}.create | Create a new database service |
| POST | `/{db}.update` | {db}.update | Update database configuration |
| POST | `/{db}.remove` | {db}.remove | Delete a database service |
| POST | `/{db}.move` | {db}.move | Move database to another environment |
| POST | `/{db}.deploy` | {db}.deploy | Deploy/redeploy the database container |
| POST | `/{db}.start` | {db}.start | Start a stopped database |
| POST | `/{db}.stop` | {db}.stop | Stop a running database |
| POST | `/{db}.reload` | {db}.reload | Reload the database container |
| POST | `/{db}.rebuild` | {db}.rebuild | Rebuild the database from scratch |
| POST | `/{db}.changeStatus` | {db}.changeStatus | Change the application status |
| POST | `/{db}.saveExternalPort` | {db}.saveExternalPort | Expose database on a host port |
| POST | `/{db}.saveEnvironment` | {db}.saveEnvironment | Set environment variables |

## Database type prefixes

| Prefix | Database | Default image |
|--------|----------|---------------|
| `postgres` | PostgreSQL | `postgres:15` |
| `mysql` | MySQL | `mysql:8` |
| `mariadb` | MariaDB | `mariadb:11` |
| `mongo` | MongoDB | `mongo:6` |
| `redis` | Redis | `redis:7` |

### Endpoint examples by type

```
GET  /postgres.one?postgresId=uuid
POST /mysql.create
POST /mariadb.deploy
POST /mongo.stop
POST /redis.saveExternalPort
```

## Key parameters

### create (all types)

```json
{
  "name": "string (required)",
  "environmentId": "string (required — resources live under a project environment)",
  "databasePassword": "string (REQUIRED for all types)",
  "dockerImage": "string (default: type-specific, e.g. postgres:15)",
  "description": "string",
  "serverId": "string (optional — target server)"
}
```

Type-specific create fields:

| Type | Extra fields |
|------|-------------|
| postgres | `databaseName` (REQUIRED), `databaseUser` (REQUIRED) |
| mysql | `databaseName` (REQUIRED), `databaseUser` (REQUIRED), `databaseRootPassword` (optional) |
| mariadb | `databaseName` (REQUIRED), `databaseUser` (REQUIRED), `databaseRootPassword` (optional) |
| mongo | `databaseUser` (REQUIRED) |
| redis | _(none — `databasePassword` only, required)_ |

### one (all types)

Uses the type-specific ID parameter:

| Type | ID parameter |
|------|-------------|
| postgres | `postgresId` |
| mysql | `mysqlId` |
| mariadb | `mariadbId` |
| mongo | `mongoId` |
| redis | `redisId` |

### update

```json
{
  "{type}Id": "string (required)",
  "name": "string",
  "dockerImage": "string",
  "description": "string",
  "memoryLimit": "number",
  "cpuLimit": "number",
  "command": "string",
  "env": "string"
}
```

### deploy / start / stop / reload / rebuild

```json
{
  "{type}Id": "string (required)"
}
```

### saveExternalPort

```json
{
  "{type}Id": "string (required)",
  "externalPort": "number | null (null to remove)"
}
```

### saveEnvironment

```json
{
  "{type}Id": "string (required)",
  "env": "string (KEY=VALUE format, newline-separated)"
}
```

### move

```json
{
  "{type}Id": "string (required)",
  "targetEnvironmentId": "string (required — target environment)"
}
```

## Full endpoint count

5 database types x 14 endpoints each = **70 endpoints total**
