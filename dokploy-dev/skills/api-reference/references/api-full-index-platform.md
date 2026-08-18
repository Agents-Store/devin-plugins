# Dokploy API — Complete Operation Index: Platform & Admin

Auto-generated from the Dokploy v0.29.14 OpenAPI schema — the **exhaustive** list of server, settings, git-provider, and tenancy/admin operations. Every row maps 1:1 to an MCP tool `mcp__dokploy__<operation>` and a REST endpoint `{METHOD} /api/<operation-with-dots>` (`x-api-key` auth). `*` marks required params. Many of these are ops/admin surfaces outside the day-to-day dev flow — included for completeness.

## Contents
- [settings](#settings) — Server settings / health / cleanup (54)
- [server](#server) — Managed remote servers (18)
- [cluster](#cluster) — Docker Swarm cluster (4)
- [swarm](#swarm) — Swarm node/container stats (4)
- [sshKey](#sshKey) — SSH keys (7)
- [gitProvider](#gitProvider) — Git providers (shared) (4)
- [github](#github) — GitHub provider (6)
- [gitlab](#gitlab) — GitLab provider (7)
- [bitbucket](#bitbucket) — Bitbucket provider (7)
- [gitea](#gitea) — Gitea provider (8)
- [notification](#notification) — Notifications (Slack/Discord/Telegram/Email/…) (41)
- [user](#user) — Users / API keys / permissions (23)
- [organization](#organization) — Organizations / members / invitations (11)
- [customRole](#customRole) — Custom roles (6)
- [sso](#sso) — Single sign-on (11)
- [forwardAuth](#forwardauth) — Traefik forward-auth SSO gate for app domains (10)
- [scim](#scim) — SCIM 2.0 user provisioning (enterprise) (3)
- [licenseKey](#licenseKey) — Enterprise license (6)
- [stripe](#stripe) — Cloud billing (8)
- [whitelabeling](#whitelabeling) — Branding (4)
- [auditLog](#auditLog) — Audit log (1)
- [admin](#admin) — Admin-only ops (1)

## settings
_Server settings / health / cleanup — 54 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `settings-assignDomainServer` | host*, certificateType*, letsEncryptEmail, https |
| GET | `settings-checkGPUStatus` | serverId |
| GET | `settings-checkInfrastructureHealth` | — |
| POST | `settings-cleanAll` | serverId |
| POST | `settings-cleanAllDeploymentQueue` | — |
| POST | `settings-cleanDockerBuilder` | serverId |
| POST | `settings-cleanDockerPrune` | serverId |
| POST | `settings-cleanMonitoring` | — |
| POST | `settings-cleanRedis` | — |
| POST | `settings-cleanSSHPrivateKey` | — |
| POST | `settings-cleanStoppedContainers` | serverId |
| POST | `settings-cleanUnusedImages` | serverId |
| POST | `settings-cleanUnusedVolumes` | serverId |
| GET | `settings-getDockerDiskUsage` | — |
| GET | `settings-getDokployCloudIps` | — |
| GET | `settings-getDokployVersion` | — |
| GET | `settings-getIp` | — |
| GET | `settings-getLogCleanupStatus` | — |
| GET | `settings-getOpenApiDocument` | — |
| GET | `settings-getReleaseTag` | — |
| GET | `settings-getTraefikPorts` | serverId |
| POST | `settings-getUpdateData` | — |
| GET | `settings-getWebServerSettings` | — |
| GET | `settings-haveActivateRequests` | — |
| GET | `settings-haveTraefikDashboardPortEnabled` | serverId |
| GET | `settings-health` | — |
| GET | `settings-isCloud` | — |
| GET | `settings-isUserSubscribed` | — |
| GET | `settings-readDirectories` | serverId |
| GET | `settings-readMiddlewareTraefikConfig` | — |
| GET | `settings-readTraefikConfig` | — |
| GET | `settings-readTraefikEnv` | serverId |
| GET | `settings-readTraefikFile` | path*, serverId |
| GET | `settings-readWebServerTraefikConfig` | — |
| POST | `settings-reloadRedis` | — |
| POST | `settings-reloadServer` | — |
| POST | `settings-reloadTraefik` | serverId |
| POST | `settings-saveSSHPrivateKey` | sshPrivateKey* |
| POST | `settings-setupGPU` | serverId |
| POST | `settings-toggleDashboard` | enableDashboard, serverId |
| POST | `settings-toggleRequests` | enable* |
| POST | `settings-updateBuildsConcurrency` | buildsConcurrency* |
| POST | `settings-updateDockerCleanup` | enableDockerCleanup*, serverId |
| POST | `settings-updateEnforceSSO` | enforceSSO* |
| POST | `settings-updateLogCleanup` | cronExpression* |
| POST | `settings-updateMiddlewareTraefikConfig` | traefikConfig* |
| POST | `settings-updateRemoteServersOnly` | remoteServersOnly* |
| POST | `settings-updateServer` | — |
| POST | `settings-updateServerIp` | serverIp* |
| POST | `settings-updateTraefikConfig` | traefikConfig* |
| POST | `settings-updateTraefikFile` | path*, traefikConfig*, serverId |
| POST | `settings-updateTraefikPorts` | serverId, additionalPorts* |
| POST | `settings-updateWebServerTraefikConfig` | traefikConfig* |
| POST | `settings-writeTraefikEnv` | env*, serverId |

## server
_Managed remote servers — 18 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `server-all` | — |
| GET | `server-allForPermissions` | — |
| GET | `server-buildServers` | — |
| GET | `server-count` | — |
| POST | `server-create` | name*, description*, ipAddress*, port*, username*, sshKeyId*, serverType* |
| GET | `server-getDefaultCommand` | serverId* |
| GET | `server-getServerMetrics` | url*, token*, dataPoints* |
| GET | `server-getServerTime` | — |
| GET | `server-one` | serverId* |
| GET | `server-publicIp` | — |
| POST | `server-remove` | serverId* |
| GET | `server-security` | serverId* |
| POST | `server-setup` | serverId* |
| POST | `server-setupMonitoring` | serverId*, metricsConfig* |
| POST | `server-update` | name*, description*, serverId*, ipAddress*, port*, username*, sshKeyId*, serverType*, command |
| POST | `server-updateBuildsConcurrency` | serverId*, buildsConcurrency* |
| GET | `server-validate` | serverId* |
| GET | `server-withSSHKey` | — |

## cluster
_Docker Swarm cluster — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `cluster-addManager` | serverId |
| GET | `cluster-addWorker` | serverId |
| GET | `cluster-getNodes` | serverId |
| POST | `cluster-removeWorker` | nodeId*, serverId |

## swarm
_Swarm node/container stats — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `swarm-getContainerStats` | serverId |
| GET | `swarm-getNodeApps` | serverId |
| GET | `swarm-getNodeInfo` | nodeId*, serverId |
| GET | `swarm-getNodes` | serverId |

## sshKey
_SSH keys — 7 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `sshKey-all` | — |
| GET | `sshKey-allForApps` | — |
| POST | `sshKey-create` | name*, description, privateKey*, publicKey*, organizationId* |
| POST | `sshKey-generate` | type |
| GET | `sshKey-one` | sshKeyId* |
| POST | `sshKey-remove` | sshKeyId* |
| POST | `sshKey-update` | name, description, lastUsedAt, sshKeyId* |

## gitProvider
_Git providers (shared) — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `gitProvider-allForPermissions` | — |
| GET | `gitProvider-getAll` | — |
| POST | `gitProvider-remove` | gitProviderId* |
| POST | `gitProvider-toggleShare` | gitProviderId*, sharedWithOrganization* |

## github
_GitHub provider — 6 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `github-getGithubBranches` | repo*, owner*, githubId |
| GET | `github-getGithubRepositories` | githubId* |
| GET | `github-githubProviders` | — |
| GET | `github-one` | githubId* |
| POST | `github-testConnection` | githubId* |
| POST | `github-update` | githubId*, name*, gitProviderId*, githubAppName* |

## gitlab
_GitLab provider — 7 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `gitlab-create` | applicationId, secret, groupName, gitProviderId, redirectUri, authId*, name*, gitlabUrl*, gitlabInternalUrl |
| GET | `gitlab-getGitlabBranches` | id, owner*, repo*, gitlabId |
| GET | `gitlab-getGitlabRepositories` | gitlabId* |
| GET | `gitlab-gitlabProviders` | — |
| GET | `gitlab-one` | gitlabId* |
| POST | `gitlab-testConnection` | gitlabId*, groupName |
| POST | `gitlab-update` | applicationId, secret, groupName, redirectUri, name*, gitlabId*, gitlabUrl*, gitProviderId*, gitlabInternalUrl |

## bitbucket
_Bitbucket provider — 7 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `bitbucket-bitbucketProviders` | — |
| POST | `bitbucket-create` | bitbucketId, bitbucketUsername, bitbucketEmail, appPassword, apiToken, bitbucketWorkspaceName, gitProviderId, authId*, name* |
| GET | `bitbucket-getBitbucketBranches` | owner*, repo*, bitbucketId |
| GET | `bitbucket-getBitbucketRepositories` | bitbucketId* |
| GET | `bitbucket-one` | bitbucketId* |
| POST | `bitbucket-testConnection` | bitbucketId*, bitbucketUsername, bitbucketEmail, workspaceName, apiToken, appPassword |
| POST | `bitbucket-update` | bitbucketId*, bitbucketUsername, bitbucketEmail, appPassword, apiToken, bitbucketWorkspaceName, gitProviderId*, name*, organizationId |

## gitea
_Gitea provider — 8 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `gitea-create` | giteaId, giteaUrl*, giteaInternalUrl, redirectUri, clientId, clientSecret, gitProviderId, accessToken, refreshToken, expiresAt, scopes, lastAuthenticatedAt, name*, giteaUsername, …(+1) |
| GET | `gitea-getGiteaBranches` | owner*, repositoryName*, giteaId |
| GET | `gitea-getGiteaRepositories` | giteaId* |
| GET | `gitea-getGiteaUrl` | giteaId* |
| GET | `gitea-giteaProviders` | — |
| GET | `gitea-one` | giteaId* |
| POST | `gitea-testConnection` | giteaId, organizationName |
| POST | `gitea-update` | giteaId*, giteaUrl*, giteaInternalUrl, redirectUri, clientId, clientSecret, gitProviderId*, accessToken, refreshToken, expiresAt, scopes, lastAuthenticatedAt, name*, giteaUsername, …(+1) |

## notification
_Notifications (Slack/Discord/Telegram/Email/…) — 41 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `notification-all` | — |
| POST | `notification-createCustom` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name*, appDeploy, dockerCleanup, serverThreshold, endpoint*, headers |
| POST | `notification-createDiscord` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, webhookUrl*, decoration* |
| POST | `notification-createEmail` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, smtpServer*, smtpPort*, username*, password*, fromAddress*, …(+1) |
| POST | `notification-createGotify` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverUrl*, appToken*, priority*, decoration* |
| POST | `notification-createLark` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, webhookUrl* |
| POST | `notification-createMattermost` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, webhookUrl*, channel, username |
| POST | `notification-createNtfy` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverUrl*, topic*, accessToken*, priority* |
| POST | `notification-createPushover` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name*, appDeploy, dockerCleanup, serverThreshold, userKey*, apiToken*, priority, retry, expire |
| POST | `notification-createResend` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, apiKey*, fromAddress*, toAddresses* |
| POST | `notification-createSlack` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, webhookUrl*, channel* |
| POST | `notification-createTeams` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, webhookUrl* |
| POST | `notification-createTelegram` | appBuildError*, databaseBackup*, dokployBackup*, volumeBackup*, dokployRestart*, name*, appDeploy*, dockerCleanup*, serverThreshold*, botToken*, chatId*, messageThreadId* |
| GET | `notification-getEmailProviders` | — |
| GET | `notification-one` | notificationId* |
| POST | `notification-receiveNotification` | ServerType, Type*, Value*, Threshold*, Message*, Timestamp*, Token* |
| POST | `notification-remove` | notificationId* |
| POST | `notification-testCustomConnection` | endpoint*, headers |
| POST | `notification-testDiscordConnection` | webhookUrl*, decoration |
| POST | `notification-testEmailConnection` | smtpServer*, smtpPort*, username*, password*, toAddresses*, fromAddress* |
| POST | `notification-testGotifyConnection` | serverUrl*, appToken*, priority*, decoration |
| POST | `notification-testLarkConnection` | webhookUrl* |
| POST | `notification-testMattermostConnection` | webhookUrl*, channel, username |
| POST | `notification-testNtfyConnection` | serverUrl*, topic*, accessToken*, priority* |
| POST | `notification-testPushoverConnection` | userKey*, apiToken*, priority*, retry, expire |
| POST | `notification-testResendConnection` | apiKey*, fromAddress*, toAddresses* |
| POST | `notification-testSlackConnection` | webhookUrl*, channel* |
| POST | `notification-testTeamsConnection` | webhookUrl* |
| POST | `notification-testTelegramConnection` | botToken*, chatId*, messageThreadId* |
| POST | `notification-updateCustom` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, endpoint, headers, notificationId*, customId*, organizationId |
| POST | `notification-updateDiscord` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, webhookUrl, decoration, notificationId*, discordId*, organizationId |
| POST | `notification-updateEmail` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, smtpServer, smtpPort, username, password, fromAddress, …(+4) |
| POST | `notification-updateGotify` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverUrl, appToken, priority, decoration, notificationId*, gotifyId*, …(+1) |
| POST | `notification-updateLark` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, webhookUrl, notificationId*, larkId*, organizationId |
| POST | `notification-updateMattermost` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, webhookUrl, channel, username, notificationId*, mattermostId*, …(+1) |
| POST | `notification-updateNtfy` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverUrl, topic, accessToken, priority, notificationId*, ntfyId*, …(+1) |
| POST | `notification-updatePushover` | notificationId*, pushoverId*, organizationId, userKey, apiToken, priority, retry, expire, appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, …(+3) |
| POST | `notification-updateResend` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, apiKey, fromAddress, toAddresses, notificationId*, resendId*, …(+1) |
| POST | `notification-updateSlack` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, webhookUrl, channel, notificationId*, slackId*, organizationId |
| POST | `notification-updateTeams` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, webhookUrl, notificationId*, teamsId*, organizationId |
| POST | `notification-updateTelegram` | appBuildError, databaseBackup, dokployBackup, volumeBackup, dokployRestart, name, appDeploy, dockerCleanup, serverThreshold, botToken, chatId, messageThreadId, notificationId*, telegramId*, …(+1) |

## user
_Users / API keys / permissions — 23 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `user-all` | — |
| POST | `user-assignPermissions` | id*, accessedProjects*, accessedEnvironments*, accessedServices*, accessedGitProviders*, accessedServers*, canCreateProjects*, canCreateServices*, canDeleteProjects*, canDeleteServices*, canAccessToDocker*, canAccessToTraefikFiles*, canAccessToAPI*, canAccessToSSHKeys*, …(+3) |
| GET | `user-checkUserOrganizations` | userId* |
| POST | `user-createApiKey` | name*, prefix, expiresIn, metadata*, rateLimitEnabled, rateLimitTimeWindow, rateLimitMax, remaining, refillAmount, refillInterval |
| POST | `user-createUserWithCredentials` | email*, password*, role* |
| POST | `user-deleteApiKey` | apiKeyId* |
| POST | `user-generateToken` | — |
| GET | `user-get` | — |
| GET | `user-getBackups` | — |
| GET | `user-getBookmarkedTemplates` | — |
| GET | `user-getContainerMetrics` | url*, token*, appName*, dataPoints* |
| GET | `user-getInvitations` | — |
| GET | `user-getMetricsToken` | — |
| GET | `user-getPermissions` | — |
| GET | `user-getServerMetrics` | — |
| GET | `user-getUserByToken` | token* |
| GET | `user-haveRootAccess` | — |
| GET | `user-one` | userId* |
| POST | `user-remove` | userId* |
| POST | `user-sendInvitation` | invitationId*, notificationId* |
| GET | `user-session` | — |
| POST | `user-toggleTemplateBookmark` | templateId* |
| POST | `user-update` | id, firstName, lastName, isRegistered, expirationDate, createdAt2, createdAt, twoFactorEnabled, email, emailVerified, image, banned, banReason, banExpires, …(+11) |

## organization
_Organizations / members / invitations — 11 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `organization-active` | — |
| GET | `organization-all` | — |
| GET | `organization-allInvitations` | — |
| POST | `organization-create` | name*, logo |
| POST | `organization-delete` | organizationId* |
| POST | `organization-inviteMember` | email*, role* |
| GET | `organization-one` | organizationId* |
| POST | `organization-removeInvitation` | invitationId* |
| POST | `organization-setDefault` | organizationId* |
| POST | `organization-update` | organizationId*, name*, logo |
| POST | `organization-updateMemberRole` | memberId*, role* |

## customRole
_Custom roles — 6 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `customRole-all` | — |
| POST | `customRole-create` | roleName*, permissions* |
| GET | `customRole-getStatements` | — |
| GET | `customRole-membersByRole` | roleName* |
| POST | `customRole-remove` | roleName* |
| POST | `customRole-update` | roleName*, newRoleName, permissions* |

## sso
_Single sign-on — 11 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `sso-addTrustedOrigin` | origin* |
| POST | `sso-deleteProvider` | providerId* |
| GET | `sso-enforceSSO` | — |
| GET | `sso-getTrustedOrigins` | — |
| GET | `sso-listProviders` | — |
| GET | `sso-one` | providerId* |
| POST | `sso-register` | providerId*, issuer*, domains*, oidcConfig, samlConfig, organizationId, overrideUserInfo |
| POST | `sso-removeTrustedOrigin` | origin* |
| GET | `sso-showSignInWithSSO` | — |
| POST | `sso-update` | providerId*, issuer*, domains*, oidcConfig, samlConfig, organizationId, overrideUserInfo |
| POST | `sso-updateTrustedOrigin` | oldOrigin*, newOrigin* |

## forwardAuth
_Traefik forward-auth "Application Authentication" — SSO login gate in front of app domains, powered by oauth2-proxy (enterprise, v0.29.8+). 10 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `forwardAuth-deployOnServer` | serverId*, providerId* |
| POST | `forwardAuth-disable` | domainId* |
| POST | `forwardAuth-enable` | domainId* |
| GET | `forwardAuth-getAuthDomain` | serverId* |
| GET | `forwardAuth-listProviders` | — |
| POST | `forwardAuth-removeAuthDomain` | serverId* |
| POST | `forwardAuth-removeOnServer` | serverId* |
| GET | `forwardAuth-serverStatus` | — |
| POST | `forwardAuth-setAuthDomain` | serverId*, authDomain*, https, certificateType, customCertResolver |
| GET | `forwardAuth-status` | domainId* |

## scim
_SCIM 2.0 provisioning — IdP-driven user create/update/deactivate (enterprise, v0.29.11+). 3 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `scim-deleteProvider` | providerId* |
| POST | `scim-generateToken` | providerId* |
| GET | `scim-listProviders` | — |

## licenseKey
_Enterprise license — 6 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `licenseKey-activate` | licenseKey* |
| POST | `licenseKey-deactivate` | — |
| GET | `licenseKey-getEnterpriseSettings` | — |
| GET | `licenseKey-haveValidLicenseKey` | — |
| POST | `licenseKey-updateEnterpriseSettings` | enableEnterpriseFeatures |
| POST | `licenseKey-validate` | — |

## stripe
_Cloud billing — 8 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `stripe-canCreateMoreServers` | — |
| POST | `stripe-createCheckoutSession` | tier*, productId*, serverQuantity*, isAnnual* |
| POST | `stripe-createCustomerPortalSession` | — |
| GET | `stripe-getCurrentPlan` | — |
| GET | `stripe-getInvoices` | — |
| GET | `stripe-getProducts` | — |
| POST | `stripe-updateInvoiceNotifications` | enabled* |
| POST | `stripe-upgradeSubscription` | tier*, serverQuantity*, isAnnual* |

## whitelabeling
_Branding — 4 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `whitelabeling-get` | — |
| GET | `whitelabeling-getPublic` | — |
| POST | `whitelabeling-reset` | — |
| POST | `whitelabeling-update` | whitelabelingConfig* |

## auditLog
_Audit log — 1 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| GET | `auditLog-all` | userId, userEmail, resourceName, action, resourceType, from, to, limit, offset |

## admin
_Admin-only ops — 1 operations._

| Method | Operation | Params (`*`=required) |
|---|---|---|
| POST | `admin-setupMonitoring` | metricsConfig* |

