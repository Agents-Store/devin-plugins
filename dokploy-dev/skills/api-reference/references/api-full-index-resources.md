# Dokploy API — Complete Operation Index: Resources

Auto-generated from the Dokploy v0.29.14 OpenAPI schema — the **exhaustive** list of resource/deployment operations. Every row maps 1:1 to an MCP tool `mcp__dokploy__<operation>` and a REST endpoint `{METHOD} /api/<operation-with-dots>` (`x-api-key` auth). `*` marks required params. For curated usage patterns and gotchas see the `mcp-patterns` skill and the themed `api-*` references; this file is the complete coverage index.

## Contents
- [project](#project) — Projects (top-level grouping) (9)
- [environment](#environment) — Per-project environments (7)
- [tag](#tag) — Resource tags (8)
- [application](#application) — Applications (31)
- [compose](#compose) — Docker Compose stacks (31)
- [docker](#docker) — Raw Docker introspection/control (12)
- [domain](#domain) — Domains / Traefik routing (9)
- [port](#port) — Exposed host ports (4)
- [redirects](#redirects) — HTTP redirect rules (4)
- [security](#security) — Per-app security / basic-auth (4)
- [certificates](#certificates) — Custom TLS certificates (5)
- [mounts](#mounts) — File/volume mounts (6)
- [registry](#registry) — Private Docker registry credentials (7)
- [postgres](#postgres) — PostgreSQL (16)
- [mysql](#mysql) — MySQL (16)
- [mariadb](#mariadb) — MariaDB (16)
- [mongo](#mongo) — MongoDB (16)
- [redis](#redis) — Redis (16)
- [libsql](#libsql) — LibSQL (14)
- [deployment](#deployment) — Deployment history (9)
- [previewDeployment](#previewDeployment) — Preview (per-PR) deployments (4)
- [rollback](#rollback) — Rollback to a previous image (2)
- [schedule](#schedule) — Cron schedules (6)
- [patch](#patch) — Deploy-time file patches (12)
- [backup](#backup) — Resource-aware (DB-dump) backups (12)
- [volumeBackups](#volumeBackups) — Raw volume backups (6)
- [destination](#destination) — S3/R2 backup destinations (6)
- [ai](#ai) — AI router (log analysis) (14)

## project
_Projects (top-level grouping) — 9 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `project-all` | — |
| GET | `project-allForPermissions` | — |
| POST | `project-create` | name*, description, env |
| POST | `project-duplicate` | sourceEnvironmentId*, name*, description, includeServices, selectedServices, duplicateInSameProject |
| GET | `project-homeStats` | — |
| GET | `project-one` | projectId* |
| POST | `project-remove` | projectId* |
| GET | `project-search` | q, name, description, limit, offset |
| POST | `project-update` | projectId*, name, description, createdAt, organizationId, env |

## environment
_Per-project environments — 7 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `environment-byProjectId` | projectId* |
| POST | `environment-create` | name*, description, projectId* |
| POST | `environment-duplicate` | environmentId*, name*, description |
| GET | `environment-one` | environmentId* |
| POST | `environment-remove` | environmentId* |
| GET | `environment-search` | q, name, description, projectId, limit, offset |
| POST | `environment-update` | environmentId*, name, description, projectId, env |

## tag
_Resource tags — 8 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `tag-all` | — |
| POST | `tag-assignToProject` | projectId*, tagId* |
| POST | `tag-bulkAssign` | projectId*, tagIds* |
| POST | `tag-create` | name*, color |
| GET | `tag-one` | tagId* |
| POST | `tag-remove` | tagId* |
| POST | `tag-removeFromProject` | projectId*, tagId* |
| POST | `tag-update` | tagId*, name, color, createdAt, organizationId |

## application
_Applications — 31 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `application-cancelDeployment` | applicationId* |
| POST | `application-cleanQueues` | applicationId* |
| POST | `application-clearDeployments` | applicationId* |
| POST | `application-create` | name*, appName, description, environmentId*, serverId |
| POST | `application-delete` | applicationId* |
| POST | `application-deploy` | applicationId*, title, description |
| POST | `application-disconnectGitProvider` | applicationId* |
| POST | `application-dropDeployment` | — |
| POST | `application-killBuild` | applicationId* |
| POST | `application-markRunning` | applicationId* |
| POST | `application-move` | applicationId*, targetEnvironmentId* |
| GET | `application-one` | applicationId* |
| GET | `application-readAppMonitoring` | appName* |
| GET | `application-readLogs` | applicationId*, tail, since, search |
| GET | `application-readTraefikConfig` | applicationId* |
| POST | `application-redeploy` | applicationId*, title, description |
| POST | `application-refreshToken` | applicationId* |
| POST | `application-reload` | appName*, applicationId* |
| POST | `application-saveBitbucketProvider` | bitbucketBuildPath*, bitbucketOwner*, bitbucketRepository*, bitbucketRepositorySlug*, bitbucketId*, applicationId*, bitbucketBranch*, enableSubmodules, watchPaths |
| POST | `application-saveBuildType` | applicationId*, buildType*, dockerfile*, dockerContextPath*, dockerBuildStage*, herokuVersion*, railpackVersion*, publishDirectory, isStaticSpa |
| POST | `application-saveDockerProvider` | dockerImage*, applicationId*, username*, password*, registryUrl* |
| POST | `application-saveEnvironment` | applicationId*, env*, buildArgs*, buildSecrets*, createEnvFile* |
| POST | `application-saveGitProvider` | applicationId*, customGitBuildPath*, customGitUrl*, watchPaths*, enableSubmodules, customGitBranch*, customGitSSHKeyId |
| POST | `application-saveGiteaProvider` | applicationId*, giteaBuildPath*, giteaOwner*, giteaRepository*, giteaId*, giteaBranch*, enableSubmodules, watchPaths |
| POST | `application-saveGithubProvider` | applicationId*, repository*, owner*, buildPath*, githubId*, branch*, triggerType*, enableSubmodules, watchPaths |
| POST | `application-saveGitlabProvider` | applicationId*, gitlabBuildPath*, gitlabOwner*, gitlabRepository*, gitlabId*, gitlabProjectId*, gitlabPathNamespace*, gitlabBranch*, enableSubmodules, watchPaths |
| GET | `application-search` | q, name, appName, description, repository, owner, dockerImage, projectId, environmentId, limit, offset |
| POST | `application-start` | applicationId* |
| POST | `application-stop` | applicationId* |
| POST | `application-update` | applicationId*, name, appName, description, env, previewEnv, watchPaths, previewBuildArgs, previewBuildSecrets, previewLabels, previewWildcard, previewPort, previewHttps, previewPath, …(+84) |
| POST | `application-updateTraefikConfig` | applicationId*, traefikConfig* |

## compose
_Docker Compose stacks — 31 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `compose-cancelDeployment` | composeId* |
| POST | `compose-cleanQueues` | composeId* |
| POST | `compose-clearDeployments` | composeId* |
| POST | `compose-create` | name*, description, environmentId*, composeType, appName, serverId, composeFile |
| POST | `compose-delete` | composeId*, deleteVolumes* |
| POST | `compose-deploy` | composeId*, title, description |
| POST | `compose-deployTemplate` | environmentId*, serverId, id*, baseUrl |
| POST | `compose-disconnectGitProvider` | composeId* |
| POST | `compose-fetchSourceType` | composeId* |
| GET | `compose-getConvertedCompose` | composeId* |
| GET | `compose-getDefaultCommand` | composeId* |
| GET | `compose-getTags` | baseUrl |
| POST | `compose-import` | base64*, composeId* |
| POST | `compose-isolatedDeployment` | composeId*, suffix |
| POST | `compose-killBuild` | composeId* |
| GET | `compose-loadMountsByService` | composeId*, serviceName* |
| GET | `compose-loadServices` | composeId*, type |
| POST | `compose-move` | composeId*, targetEnvironmentId* |
| GET | `compose-one` | composeId* |
| POST | `compose-previewTemplate` | base64*, appName*, serverId |
| POST | `compose-processTemplate` | base64*, composeId* |
| POST | `compose-randomizeCompose` | composeId*, suffix |
| GET | `compose-readLogs` | composeId*, containerId*, tail, since, search |
| POST | `compose-redeploy` | composeId*, title, description |
| POST | `compose-refreshToken` | composeId* |
| POST | `compose-saveEnvironment` | composeId*, env* |
| GET | `compose-search` | q, name, appName, description, projectId, environmentId, limit, offset |
| POST | `compose-start` | composeId* |
| POST | `compose-stop` | composeId* |
| GET | `compose-templates` | baseUrl |
| POST | `compose-update` | composeId*, name, appName, description, env, composeFile, refreshToken, sourceType, composeType, repository, owner, branch, autoDeploy, gitlabProjectId, …(+30) |

## docker
_Raw Docker introspection/control — 12 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `docker-getConfig` | containerId*, serverId |
| GET | `docker-getContainers` | serverId |
| GET | `docker-getContainersByAppLabel` | appName*, serverId, type* |
| GET | `docker-getContainersByAppNameMatch` | appType, appName*, serverId |
| GET | `docker-getServiceContainersByAppName` | appName*, serverId |
| GET | `docker-getStackContainersByAppName` | appName*, serverId |
| POST | `docker-killContainer` | containerId*, serverId |
| POST | `docker-removeContainer` | containerId*, serverId |
| POST | `docker-restartContainer` | containerId*, serverId |
| POST | `docker-startContainer` | containerId*, serverId |
| POST | `docker-stopContainer` | containerId*, serverId |
| POST | `docker-uploadFileToContainer` | — |

## domain
_Domains / Traefik routing — 9 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `domain-byApplicationId` | applicationId* |
| GET | `domain-byComposeId` | composeId* |
| GET | `domain-canGenerateTraefikMeDomains` | serverId* |
| POST | `domain-create` | host*, path, port, customEntrypoint, https, applicationId, certificateType, customCertResolver, composeId, serviceName, domainType, previewDeploymentId, internalPath, stripPath, middlewares, forwardAuthEnabled |
| POST | `domain-delete` | domainId* |
| POST | `domain-generateDomain` | appName*, serverId |
| GET | `domain-one` | domainId* |
| POST | `domain-update` | host*, path, port, customEntrypoint, https, certificateType, customCertResolver, serviceName, domainType, internalPath, stripPath, middlewares, forwardAuthEnabled, domainId* |
| POST | `domain-validateDomain` | domain*, serverIp |

## port
_Exposed host ports — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `port-create` | publishedPort*, publishMode*, targetPort*, protocol*, applicationId* |
| POST | `port-delete` | portId* |
| GET | `port-one` | portId* |
| POST | `port-update` | portId*, publishedPort*, publishMode*, targetPort*, protocol* |

## redirects
_HTTP redirect rules — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `redirects-create` | regex*, replacement*, permanent*, applicationId* |
| POST | `redirects-delete` | redirectId* |
| GET | `redirects-one` | redirectId* |
| POST | `redirects-update` | redirectId*, regex*, replacement*, permanent* |

## security
_Per-app security / basic-auth — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `security-create` | applicationId*, username*, password* |
| POST | `security-delete` | securityId* |
| GET | `security-one` | securityId* |
| POST | `security-update` | securityId*, username*, password* |

## certificates
_Custom TLS certificates — 5 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `certificates-all` | — |
| POST | `certificates-create` | certificateId, name*, certificateData*, privateKey*, certificatePath, autoRenew, organizationId*, serverId |
| GET | `certificates-one` | certificateId* |
| POST | `certificates-remove` | certificateId* |
| POST | `certificates-update` | certificateId*, name, certificateData, privateKey |

## mounts
_File/volume mounts — 6 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `mounts-allNamedByApplicationId` | applicationId* |
| POST | `mounts-create` | type*, hostPath, volumeName, content, mountPath*, filePath, serviceType, serviceId* |
| GET | `mounts-listByServiceId` | serviceType*, serviceId* |
| GET | `mounts-one` | mountId* |
| POST | `mounts-remove` | mountId* |
| POST | `mounts-update` | mountId*, type, hostPath, volumeName, filePath, content, serviceType, mountPath, applicationId, composeId, libsqlId, mariadbId, mongoId, mysqlId, …(+2) |

## registry
_Private Docker registry credentials — 7 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `registry-all` | — |
| POST | `registry-create` | registryName*, username*, password*, registryUrl*, registryType*, imagePrefix*, serverId |
| GET | `registry-one` | registryId* |
| POST | `registry-remove` | registryId* |
| POST | `registry-testRegistry` | registryName, username*, password*, registryUrl*, registryType*, imagePrefix, serverId |
| POST | `registry-testRegistryById` | registryId, serverId |
| POST | `registry-update` | registryId*, registryName, imagePrefix, username, password, registryUrl, createdAt, registryType, organizationId, serverId |

## postgres
_PostgreSQL — 16 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `postgres-changePassword` | postgresId*, password* |
| POST | `postgres-changeStatus` | postgresId*, applicationStatus* |
| POST | `postgres-create` | name*, appName, databaseName*, databaseUser*, databasePassword*, dockerImage, environmentId*, description, serverId |
| POST | `postgres-deploy` | postgresId* |
| POST | `postgres-move` | postgresId*, targetEnvironmentId* |
| GET | `postgres-one` | postgresId* |
| GET | `postgres-readLogs` | postgresId*, tail, since, search |
| POST | `postgres-rebuild` | postgresId* |
| POST | `postgres-reload` | postgresId*, appName* |
| POST | `postgres-remove` | postgresId* |
| POST | `postgres-saveEnvironment` | postgresId*, env* |
| POST | `postgres-saveExternalPort` | postgresId*, externalPort* |
| GET | `postgres-search` | q, name, appName, description, projectId, environmentId, limit, offset |
| POST | `postgres-start` | postgresId* |
| POST | `postgres-stop` | postgresId* |
| POST | `postgres-update` | postgresId*, name, appName, databaseName, databaseUser, databasePassword, description, dockerImage, command, args, env, memoryReservation, externalPort, memoryLimit, …(+17) |

## mysql
_MySQL — 16 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `mysql-changePassword` | mysqlId*, password*, type |
| POST | `mysql-changeStatus` | mysqlId*, applicationStatus* |
| POST | `mysql-create` | name*, appName, dockerImage, environmentId*, description, databaseName*, databaseUser*, databasePassword*, databaseRootPassword, serverId |
| POST | `mysql-deploy` | mysqlId* |
| POST | `mysql-move` | mysqlId*, targetEnvironmentId* |
| GET | `mysql-one` | mysqlId* |
| GET | `mysql-readLogs` | mysqlId*, tail, since, search |
| POST | `mysql-rebuild` | mysqlId* |
| POST | `mysql-reload` | mysqlId*, appName* |
| POST | `mysql-remove` | mysqlId* |
| POST | `mysql-saveEnvironment` | mysqlId*, env* |
| POST | `mysql-saveExternalPort` | mysqlId*, externalPort* |
| GET | `mysql-search` | q, name, appName, description, projectId, environmentId, limit, offset |
| POST | `mysql-start` | mysqlId* |
| POST | `mysql-stop` | mysqlId* |
| POST | `mysql-update` | mysqlId*, name, appName, description, databaseName, databaseUser, databasePassword, databaseRootPassword, dockerImage, command, args, env, memoryReservation, memoryLimit, …(+18) |

## mariadb
_MariaDB — 16 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `mariadb-changePassword` | mariadbId*, password*, type |
| POST | `mariadb-changeStatus` | mariadbId*, applicationStatus* |
| POST | `mariadb-create` | name*, appName, dockerImage, databaseRootPassword, environmentId*, description, databaseName*, databaseUser*, databasePassword*, serverId |
| POST | `mariadb-deploy` | mariadbId* |
| POST | `mariadb-move` | mariadbId*, targetEnvironmentId* |
| GET | `mariadb-one` | mariadbId* |
| GET | `mariadb-readLogs` | mariadbId*, tail, since, search |
| POST | `mariadb-rebuild` | mariadbId* |
| POST | `mariadb-reload` | mariadbId*, appName* |
| POST | `mariadb-remove` | mariadbId* |
| POST | `mariadb-saveEnvironment` | mariadbId*, env* |
| POST | `mariadb-saveExternalPort` | mariadbId*, externalPort* |
| GET | `mariadb-search` | q, name, appName, description, projectId, environmentId, limit, offset |
| POST | `mariadb-start` | mariadbId* |
| POST | `mariadb-stop` | mariadbId* |
| POST | `mariadb-update` | mariadbId*, name, appName, description, databaseName, databaseUser, databasePassword, databaseRootPassword, dockerImage, command, args, env, memoryReservation, memoryLimit, …(+18) |

## mongo
_MongoDB — 16 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `mongo-changePassword` | mongoId*, password* |
| POST | `mongo-changeStatus` | mongoId*, applicationStatus* |
| POST | `mongo-create` | name*, appName, dockerImage, environmentId*, description, databaseUser*, databasePassword*, serverId, replicaSets |
| POST | `mongo-deploy` | mongoId* |
| POST | `mongo-move` | mongoId*, targetEnvironmentId* |
| GET | `mongo-one` | mongoId* |
| GET | `mongo-readLogs` | mongoId*, tail, since, search |
| POST | `mongo-rebuild` | mongoId* |
| POST | `mongo-reload` | mongoId*, appName* |
| POST | `mongo-remove` | mongoId* |
| POST | `mongo-saveEnvironment` | mongoId*, env* |
| POST | `mongo-saveExternalPort` | mongoId*, externalPort* |
| GET | `mongo-search` | q, name, appName, description, projectId, environmentId, limit, offset |
| POST | `mongo-start` | mongoId* |
| POST | `mongo-stop` | mongoId* |
| POST | `mongo-update` | mongoId*, name, appName, description, databaseUser, databasePassword, dockerImage, command, args, env, memoryReservation, memoryLimit, cpuReservation, cpuLimit, …(+17) |

## redis
_Redis — 16 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `redis-changePassword` | redisId*, password* |
| POST | `redis-changeStatus` | redisId*, applicationStatus* |
| POST | `redis-create` | name*, appName, databasePassword*, dockerImage, environmentId*, description, serverId |
| POST | `redis-deploy` | redisId* |
| POST | `redis-move` | redisId*, targetEnvironmentId* |
| GET | `redis-one` | redisId* |
| GET | `redis-readLogs` | redisId*, tail, since, search |
| POST | `redis-rebuild` | redisId* |
| POST | `redis-reload` | redisId*, appName* |
| POST | `redis-remove` | redisId* |
| POST | `redis-saveEnvironment` | redisId*, env* |
| POST | `redis-saveExternalPort` | redisId*, externalPort* |
| GET | `redis-search` | q, name, appName, description, projectId, environmentId, limit, offset |
| POST | `redis-start` | redisId* |
| POST | `redis-stop` | redisId* |
| POST | `redis-update` | redisId*, name, appName, description, databasePassword, dockerImage, command, args, env, memoryReservation, memoryLimit, cpuReservation, cpuLimit, externalPort, …(+15) |

## libsql
_LibSQL — 14 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `libsql-changeStatus` | libsqlId*, applicationStatus* |
| POST | `libsql-create` | name*, appName*, dockerImage*, environmentId*, description*, databaseUser*, databasePassword*, sqldNode*, sqldPrimaryUrl*, enableNamespaces*, serverId* |
| POST | `libsql-deploy` | libsqlId* |
| POST | `libsql-move` | libsqlId*, targetEnvironmentId* |
| GET | `libsql-one` | libsqlId* |
| GET | `libsql-readLogs` | libsqlId*, tail, since, search |
| POST | `libsql-rebuild` | libsqlId* |
| POST | `libsql-reload` | libsqlId*, appName* |
| POST | `libsql-remove` | libsqlId* |
| POST | `libsql-saveEnvironment` | libsqlId*, env* |
| POST | `libsql-saveExternalPorts` | libsqlId*, externalPort, externalGRPCPort, externalAdminPort |
| POST | `libsql-start` | libsqlId* |
| POST | `libsql-stop` | libsqlId* |
| POST | `libsql-update` | libsqlId*, name, appName, description, databaseUser, databasePassword, sqldNode, sqldPrimaryUrl, enableNamespaces, dockerImage, command, env, memoryReservation, memoryLimit, …(+19) |

## deployment
_Deployment history — 9 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `deployment-all` | applicationId* |
| GET | `deployment-allByCompose` | composeId* |
| GET | `deployment-allByServer` | serverId* |
| GET | `deployment-allByType` | id*, type* |
| GET | `deployment-allCentralized` | — |
| POST | `deployment-killProcess` | deploymentId* |
| GET | `deployment-queueList` | — |
| GET | `deployment-readLogs` | deploymentId*, tail |
| POST | `deployment-removeDeployment` | deploymentId* |

## previewDeployment
_Preview (per-PR) deployments — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `previewDeployment-all` | applicationId* |
| POST | `previewDeployment-delete` | previewDeploymentId* |
| GET | `previewDeployment-one` | previewDeploymentId* |
| POST | `previewDeployment-redeploy` | previewDeploymentId*, title, description |

## rollback
_Rollback to a previous image — 2 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `rollback-delete` | rollbackId* |
| POST | `rollback-rollback` | rollbackId* |

## schedule
_Cron schedules — 6 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `schedule-create` | scheduleId, name*, description, cronExpression*, appName, serviceName, shellType, scheduleType, command*, script, applicationId, composeId, serverId, organizationId, timezone, …(+2) |
| POST | `schedule-delete` | scheduleId* |
| GET | `schedule-list` | id*, scheduleType* |
| GET | `schedule-one` | scheduleId* |
| POST | `schedule-runManually` | scheduleId* |
| POST | `schedule-update` | scheduleId*, name*, description, cronExpression*, appName, serviceName, shellType, scheduleType, command*, script, applicationId, composeId, serverId, organizationId, timezone, …(+2) |

_v0.29.8 rescoped Dokploy-host schedules from user to organization (`organizationId`, formerly `userId`) and added a `timezone` field._

## patch
_Deploy-time file patches — 12 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `patch-byEntityId` | id*, type* |
| POST | `patch-cleanPatchRepos` | serverId |
| POST | `patch-create` | filePath*, content*, type, enabled, applicationId, composeId |
| POST | `patch-delete` | patchId* |
| POST | `patch-ensureRepo` | id*, type* |
| POST | `patch-markFileForDeletion` | id*, type*, filePath* |
| GET | `patch-one` | patchId* |
| GET | `patch-readRepoDirectories` | id*, type*, repoPath* |
| GET | `patch-readRepoFile` | id*, type*, filePath* |
| POST | `patch-saveFileAsPatch` | id*, type*, filePath*, content*, patchType |
| POST | `patch-toggleEnabled` | patchId*, enabled* |
| POST | `patch-update` | patchId*, type, filePath, enabled, content, createdAt, updatedAt |

## backup
_Resource-aware (DB-dump) backups — 12 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `backup-create` | schedule*, enabled, prefix*, destinationId*, keepLatestCount, database*, mariadbId, mysqlId, postgresId, mongoId, libsqlId, databaseType*, userId, backupType, …(+3) |
| GET | `backup-listBackupFiles` | destinationId*, search*, serverId |
| POST | `backup-manualBackupCompose` | backupId* |
| POST | `backup-manualBackupLibsql` | backupId* |
| POST | `backup-manualBackupMariadb` | backupId* |
| POST | `backup-manualBackupMongo` | backupId* |
| POST | `backup-manualBackupMySql` | backupId* |
| POST | `backup-manualBackupPostgres` | backupId* |
| POST | `backup-manualBackupWebServer` | backupId* |
| GET | `backup-one` | backupId* |
| POST | `backup-remove` | backupId* |
| POST | `backup-update` | schedule*, enabled*, prefix*, backupId*, destinationId*, database*, keepLatestCount*, serviceName*, metadata*, databaseType* |

## volumeBackups
_Raw volume backups — 6 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `volumeBackups-create` | name*, volumeName*, prefix*, serviceType, appName, serviceName, turnOff, cronExpression*, keepLatestCount, enabled, applicationId, postgresId, mariadbId, mongoId, …(+6) |
| POST | `volumeBackups-delete` | volumeBackupId* |
| GET | `volumeBackups-list` | id*, volumeBackupType* |
| GET | `volumeBackups-one` | volumeBackupId* |
| POST | `volumeBackups-runManually` | volumeBackupId* |
| POST | `volumeBackups-update` | name*, volumeName*, prefix*, serviceType, appName, serviceName, turnOff, cronExpression*, keepLatestCount, enabled, applicationId, postgresId, mariadbId, mongoId, …(+7) |

## destination
_S3/R2 backup destinations — 6 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `destination-all` | — |
| POST | `destination-create` | name*, provider*, accessKey*, bucket*, region*, endpoint*, secretAccessKey*, additionalFlags*, serverId |
| GET | `destination-one` | destinationId* |
| POST | `destination-remove` | destinationId* |
| POST | `destination-testConnection` | name*, provider*, accessKey*, bucket*, region*, endpoint*, secretAccessKey*, additionalFlags*, serverId |
| POST | `destination-update` | name*, accessKey*, bucket*, region*, endpoint*, secretAccessKey*, destinationId*, provider*, additionalFlags*, serverId |

## ai
_AI router (log analysis) — 14 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `ai-analyzeLogs` | aiId*, logs*, context* |
| POST | `ai-create` | name*, apiUrl*, apiKey*, model*, isEnabled* |
| POST | `ai-delete` | aiId* |
| POST | `ai-deploy` | environmentId*, id*, dockerCompose*, envVariables*, serverId, name*, description*, domains, configFiles |
| GET | `ai-get` | aiId* |
| GET | `ai-getAll` | — |
| GET | `ai-getCustomProviders` | — |
| GET | `ai-getEnabledProviders` | — |
| GET | `ai-getModels` | apiUrl*, apiKey* |
| GET | `ai-one` | aiId* |
| POST | `ai-saveCustomProviders` | providers* |
| POST | `ai-suggest` | aiId*, input*, serverId |
| POST | `ai-testConnection` | apiUrl*, apiKey*, model* |
| POST | `ai-update` | aiId*, name, apiUrl, apiKey, model, isEnabled, createdAt |

