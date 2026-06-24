# Dokploy MCP Tool Catalog

Generated from the official Dokploy MCP OpenAPI spec.

- Total tools: 524
- Categories: 48
- Source: https://raw.githubusercontent.com/Dokploy/mcp/main/src/generated/openapi.json
- Generated: 2026-06-24T15:17:46Z

## Categories

- [admin](#admin) (1 tools)
- [ai](#ai) (12 tools)
- [application](#application) (31 tools)
- [auditLog](#auditlog) (1 tools)
- [backup](#backup) (12 tools)
- [bitbucket](#bitbucket) (7 tools)
- [certificates](#certificates) (5 tools)
- [cluster](#cluster) (4 tools)
- [compose](#compose) (30 tools)
- [customRole](#customrole) (6 tools)
- [deployment](#deployment) (8 tools)
- [destination](#destination) (6 tools)
- [docker](#docker) (12 tools)
- [domain](#domain) (9 tools)
- [environment](#environment) (7 tools)
- [gitProvider](#gitprovider) (4 tools)
- [gitea](#gitea) (8 tools)
- [github](#github) (6 tools)
- [gitlab](#gitlab) (7 tools)
- [libsql](#libsql) (14 tools)
- [licenseKey](#licensekey) (6 tools)
- [mariadb](#mariadb) (16 tools)
- [mongo](#mongo) (16 tools)
- [mounts](#mounts) (6 tools)
- [mysql](#mysql) (16 tools)
- [notification](#notification) (41 tools)
- [organization](#organization) (11 tools)
- [patch](#patch) (12 tools)
- [port](#port) (4 tools)
- [postgres](#postgres) (16 tools)
- [previewDeployment](#previewdeployment) (4 tools)
- [project](#project) (9 tools)
- [redirects](#redirects) (4 tools)
- [redis](#redis) (16 tools)
- [registry](#registry) (7 tools)
- [rollback](#rollback) (2 tools)
- [schedule](#schedule) (6 tools)
- [security](#security) (4 tools)
- [server](#server) (17 tools)
- [settings](#settings) (51 tools)
- [sshKey](#sshkey) (7 tools)
- [sso](#sso) (10 tools)
- [stripe](#stripe) (8 tools)
- [swarm](#swarm) (4 tools)
- [tag](#tag) (8 tools)
- [user](#user) (23 tools)
- [volumeBackups](#volumebackups) (6 tools)
- [whitelabeling](#whitelabeling) (4 tools)

## admin

| Tool | Method | Parameters |
|------|--------|------------|
| `admin-setupMonitoring` | POST | `metricsConfig` (object) |

## ai

| Tool | Method | Parameters |
|------|--------|------------|
| `ai-analyzeLogs` | POST | `aiId` (string), `logs` (string), `context` ("build" | "runtime") |
| `ai-create` | POST | `name` (string), `apiUrl` (string), `apiKey` (string), `model` (string), `isEnabled` (boolean) |
| `ai-delete` | POST | `aiId` (string) |
| `ai-deploy` | POST | `environmentId` (string), `id` (string), `dockerCompose` (string), `envVariables` (string), `name` (string), `description` (string), `serverId`?, `domains`?, `configFiles`? |
| `ai-get` | GET | `aiId` (string) |
| `ai-getAll` | GET | None |
| `ai-getEnabledProviders` | GET | None |
| `ai-getModels` | GET | `apiUrl` (string), `apiKey` (string) |
| `ai-one` | GET | `aiId` (string) |
| `ai-suggest` | POST | `aiId` (string), `input` (string), `serverId`? |
| `ai-testConnection` | POST | `apiUrl` (string), `apiKey` (string), `model` (string) |
| `ai-update` | POST | `aiId` (string), +6 optional |

## application

| Tool | Method | Parameters |
|------|--------|------------|
| `application-cancelDeployment` | POST | `applicationId` (string) |
| `application-cleanQueues` | POST | `applicationId` (string) |
| `application-clearDeployments` | POST | `applicationId` (string) |
| `application-create` | POST | `name` (string), `environmentId` (string), `appName`?, `description`?, `serverId`? |
| `application-delete` | POST | `applicationId` (string) |
| `application-deploy` | POST | `applicationId` (string), `title`?, `description`? |
| `application-disconnectGitProvider` | POST | `applicationId` (string) |
| `application-dropDeployment` | POST | None |
| `application-killBuild` | POST | `applicationId` (string) |
| `application-markRunning` | POST | `applicationId` (string) |
| `application-move` | POST | `applicationId` (string), `targetEnvironmentId` (string) |
| `application-one` | GET | `applicationId` (string) |
| `application-readAppMonitoring` | GET | `appName` (string) |
| `application-readLogs` | GET | `applicationId` (string), `tail`?, `since`?, `search`? |
| `application-readTraefikConfig` | GET | `applicationId` (string) |
| `application-redeploy` | POST | `applicationId` (string), `title`?, `description`? |
| `application-refreshToken` | POST | `applicationId` (string) |
| `application-reload` | POST | `appName` (string), `applicationId` (string) |
| `application-saveBitbucketProvider` | POST | `bitbucketBranch` (string | null), `bitbucketBuildPath` (string | null), `bitbucketOwner` (string | null), `bitbucketRepository` (string | null), `bitbucketRepositorySlug` (string | null), `bitbucketId` (string | null), `applicationId` (string), `enableSubmodules`?, `watchPaths`? |
| `application-saveBuildType` | POST | `applicationId` (string), `buildType` ("dockerfile" | "heroku_buildpacks" | "paketo_buildpacks" | "nixpacks" | "static" | "railpack"), `dockerfile` (string | null), `dockerContextPath` (string | null), `dockerBuildStage` (string | null), `herokuVersion` (string | null), `railpackVersion` (string | null), `publishDirectory`?, `isStaticSpa`? |
| `application-saveDockerProvider` | POST | `dockerImage` (string | null), `applicationId` (string), `username` (string | null), `password` (string | null), `registryUrl` (string | null) |
| `application-saveEnvironment` | POST | `applicationId` (string), `env` (string | null), `buildArgs` (string | null), `buildSecrets` (string | null), `createEnvFile` (boolean) |
| `application-saveGitProvider` | POST | `customGitBranch` (string | null), `applicationId` (string), `customGitBuildPath` (string | null), `customGitUrl` (string | null), `watchPaths` (string[] | null), `enableSubmodules`?, `customGitSSHKeyId`? |
| `application-saveGiteaProvider` | POST | `applicationId` (string), `giteaBranch` (string | null), `giteaBuildPath` (string | null), `giteaOwner` (string | null), `giteaRepository` (string | null), `giteaId` (string | null), `enableSubmodules`?, `watchPaths`? |
| `application-saveGithubProvider` | POST | `applicationId` (string), `repository` (string | null), `branch` (string | null), `owner` (string | null), `buildPath` (string | null), `githubId` (string | null), `triggerType` ("push" | "tag"), `enableSubmodules`?, `watchPaths`? |
| `application-saveGitlabProvider` | POST | `applicationId` (string), `gitlabBranch` (string | null), `gitlabBuildPath` (string | null), `gitlabOwner` (string | null), `gitlabRepository` (string | null), `gitlabId` (string | null), `gitlabProjectId` (number | null), `gitlabPathNamespace` (string | null), `enableSubmodules`?, `watchPaths`? |
| `application-search` | GET | +11 optional |
| `application-start` | POST | `applicationId` (string) |
| `application-stop` | POST | `applicationId` (string) |
| `application-update` | POST | `applicationId` (string), +97 optional |
| `application-updateTraefikConfig` | POST | `applicationId` (string), `traefikConfig` (string) |

## auditLog

| Tool | Method | Parameters |
|------|--------|------------|
| `auditLog-all` | GET | +9 optional |

## backup

| Tool | Method | Parameters |
|------|--------|------------|
| `backup-create` | POST | `schedule` (string), `prefix` (string), `destinationId` (string), `database` (string), `databaseType` ("postgres" | "mariadb" | "mysql" | "mongo" | "web-server" | "libsql"), +12 optional |
| `backup-listBackupFiles` | GET | `destinationId` (string), `search` (string), `serverId`? |
| `backup-manualBackupCompose` | POST | `backupId` (string) |
| `backup-manualBackupLibsql` | POST | `backupId` (string) |
| `backup-manualBackupMariadb` | POST | `backupId` (string) |
| `backup-manualBackupMongo` | POST | `backupId` (string) |
| `backup-manualBackupMySql` | POST | `backupId` (string) |
| `backup-manualBackupPostgres` | POST | `backupId` (string) |
| `backup-manualBackupWebServer` | POST | `backupId` (string) |
| `backup-one` | GET | `backupId` (string) |
| `backup-remove` | POST | `backupId` (string) |
| `backup-update` | POST | `schedule` (string), `enabled` (boolean | null), `prefix` (string), `backupId` (string), `destinationId` (string), `database` (string), `keepLatestCount` (number | null), `serviceName` (string | null), `metadata` (unknown | null), `databaseType` ("postgres" | "mariadb" | "mysql" | "mongo" | "web-server" | "libsql") |

## bitbucket

| Tool | Method | Parameters |
|------|--------|------------|
| `bitbucket-bitbucketProviders` | GET | None |
| `bitbucket-create` | POST | `authId` (string), `name` (string), +7 optional |
| `bitbucket-getBitbucketBranches` | GET | `owner` (string), `repo` (string), `bitbucketId`? |
| `bitbucket-getBitbucketRepositories` | GET | `bitbucketId` (string) |
| `bitbucket-one` | GET | `bitbucketId` (string) |
| `bitbucket-testConnection` | POST | `bitbucketId` (string), +5 optional |
| `bitbucket-update` | POST | `bitbucketId` (string), `gitProviderId` (string), `name` (string), +6 optional |

## certificates

| Tool | Method | Parameters |
|------|--------|------------|
| `certificates-all` | GET | None |
| `certificates-create` | POST | `name` (string), `certificateData` (string), `privateKey` (string), `organizationId` (string), +4 optional |
| `certificates-one` | GET | `certificateId` (string) |
| `certificates-remove` | POST | `certificateId` (string) |
| `certificates-update` | POST | `certificateId` (string), `name`?, `certificateData`?, `privateKey`? |

## cluster

| Tool | Method | Parameters |
|------|--------|------------|
| `cluster-addManager` | GET | `serverId`? |
| `cluster-addWorker` | GET | `serverId`? |
| `cluster-getNodes` | GET | `serverId`? |
| `cluster-removeWorker` | POST | `nodeId` (string), `serverId`? |

## compose

| Tool | Method | Parameters |
|------|--------|------------|
| `compose-cancelDeployment` | POST | `composeId` (string) |
| `compose-cleanQueues` | POST | `composeId` (string) |
| `compose-clearDeployments` | POST | `composeId` (string) |
| `compose-create` | POST | `name` (string), `environmentId` (string), +5 optional |
| `compose-delete` | POST | `composeId` (string), `deleteVolumes` (boolean) |
| `compose-deploy` | POST | `composeId` (string), `title`?, `description`? |
| `compose-deployTemplate` | POST | `environmentId` (string), `id` (string), `serverId`?, `baseUrl`? |
| `compose-disconnectGitProvider` | POST | `composeId` (string) |
| `compose-fetchSourceType` | POST | `composeId` (string) |
| `compose-getConvertedCompose` | GET | `composeId` (string) |
| `compose-getDefaultCommand` | GET | `composeId` (string) |
| `compose-getTags` | GET | `baseUrl`? |
| `compose-import` | POST | `base64` (string), `composeId` (string) |
| `compose-isolatedDeployment` | POST | `composeId` (string), `suffix`? |
| `compose-killBuild` | POST | `composeId` (string) |
| `compose-loadMountsByService` | GET | `composeId` (string), `serviceName` (string) |
| `compose-loadServices` | GET | `composeId` (string), `type`? |
| `compose-move` | POST | `composeId` (string), `targetEnvironmentId` (string) |
| `compose-one` | GET | `composeId` (string) |
| `compose-processTemplate` | POST | `base64` (string), `composeId` (string) |
| `compose-randomizeCompose` | POST | `composeId` (string), `suffix`? |
| `compose-readLogs` | GET | `composeId` (string), `containerId` (string), `tail`?, `since`?, `search`? |
| `compose-redeploy` | POST | `composeId` (string), `title`?, `description`? |
| `compose-refreshToken` | POST | `composeId` (string) |
| `compose-saveEnvironment` | POST | `composeId` (string), `env` (string | null) |
| `compose-search` | GET | +8 optional |
| `compose-start` | POST | `composeId` (string) |
| `compose-stop` | POST | `composeId` (string) |
| `compose-templates` | GET | `baseUrl`? |
| `compose-update` | POST | `composeId` (string), +43 optional |

## customRole

| Tool | Method | Parameters |
|------|--------|------------|
| `customRole-all` | GET | None |
| `customRole-create` | POST | `roleName` (string), `permissions` (object) |
| `customRole-getStatements` | GET | None |
| `customRole-membersByRole` | GET | `roleName` (string) |
| `customRole-remove` | POST | `roleName` (string) |
| `customRole-update` | POST | `roleName` (string), `permissions` (object), `newRoleName`? |

## deployment

| Tool | Method | Parameters |
|------|--------|------------|
| `deployment-all` | GET | `applicationId` (string) |
| `deployment-allByCompose` | GET | `composeId` (string) |
| `deployment-allByServer` | GET | `serverId` (string) |
| `deployment-allByType` | GET | `id` (string), `type` ("application" | "compose" | "server" | "schedule" | "previewDeployment" | "backup" | "volumeBackup") |
| `deployment-allCentralized` | GET | None |
| `deployment-killProcess` | POST | `deploymentId` (string) |
| `deployment-queueList` | GET | None |
| `deployment-removeDeployment` | POST | `deploymentId` (string) |

## destination

| Tool | Method | Parameters |
|------|--------|------------|
| `destination-all` | GET | None |
| `destination-create` | POST | `name` (string), `provider` (string | null), `accessKey` (string), `bucket` (string), `region` (string), `endpoint` (string), `secretAccessKey` (string), `additionalFlags` (string[] | null), `serverId`? |
| `destination-one` | GET | `destinationId` (string) |
| `destination-remove` | POST | `destinationId` (string) |
| `destination-testConnection` | POST | `name` (string), `provider` (string | null), `accessKey` (string), `bucket` (string), `region` (string), `endpoint` (string), `secretAccessKey` (string), `additionalFlags` (string[] | null), `serverId`? |
| `destination-update` | POST | `name` (string), `accessKey` (string), `bucket` (string), `region` (string), `endpoint` (string), `secretAccessKey` (string), `destinationId` (string), `provider` (string | null), `additionalFlags` (string[] | null), `serverId`? |

## docker

| Tool | Method | Parameters |
|------|--------|------------|
| `docker-getConfig` | GET | `containerId` (string), `serverId`? |
| `docker-getContainers` | GET | `serverId`? |
| `docker-getContainersByAppLabel` | GET | `appName` (string), `type` ("standalone" | "swarm"), `serverId`? |
| `docker-getContainersByAppNameMatch` | GET | `appName` (string), `appType`?, `serverId`? |
| `docker-getServiceContainersByAppName` | GET | `appName` (string), `serverId`? |
| `docker-getStackContainersByAppName` | GET | `appName` (string), `serverId`? |
| `docker-killContainer` | POST | `containerId` (string), `serverId`? |
| `docker-removeContainer` | POST | `containerId` (string), `serverId`? |
| `docker-restartContainer` | POST | `containerId` (string), `serverId`? |
| `docker-startContainer` | POST | `containerId` (string), `serverId`? |
| `docker-stopContainer` | POST | `containerId` (string), `serverId`? |
| `docker-uploadFileToContainer` | POST | None |

## domain

| Tool | Method | Parameters |
|------|--------|------------|
| `domain-byApplicationId` | GET | `applicationId` (string) |
| `domain-byComposeId` | GET | `composeId` (string) |
| `domain-canGenerateTraefikMeDomains` | GET | `serverId` (string) |
| `domain-create` | POST | `host` (string), +14 optional |
| `domain-delete` | POST | `domainId` (string) |
| `domain-generateDomain` | POST | `appName` (string), `serverId`? |
| `domain-one` | GET | `domainId` (string) |
| `domain-update` | POST | `host` (string), `domainId` (string), +11 optional |
| `domain-validateDomain` | POST | `domain` (string), `serverIp`? |

## environment

| Tool | Method | Parameters |
|------|--------|------------|
| `environment-byProjectId` | GET | `projectId` (string) |
| `environment-create` | POST | `name` (string), `projectId` (string), `description`? |
| `environment-duplicate` | POST | `environmentId` (string), `name` (string), `description`? |
| `environment-one` | GET | `environmentId` (string) |
| `environment-remove` | POST | `environmentId` (string) |
| `environment-search` | GET | +6 optional |
| `environment-update` | POST | `environmentId` (string), +4 optional |

## gitProvider

| Tool | Method | Parameters |
|------|--------|------------|
| `gitProvider-allForPermissions` | GET | None |
| `gitProvider-getAll` | GET | None |
| `gitProvider-remove` | POST | `gitProviderId` (string) |
| `gitProvider-toggleShare` | POST | `gitProviderId` (string), `sharedWithOrganization` (boolean) |

## gitea

| Tool | Method | Parameters |
|------|--------|------------|
| `gitea-create` | POST | `giteaUrl` (string), `name` (string), +13 optional |
| `gitea-getGiteaBranches` | GET | `owner` (string), `repositoryName` (string), `giteaId`? |
| `gitea-getGiteaRepositories` | GET | `giteaId` (string) |
| `gitea-getGiteaUrl` | GET | `giteaId` (string) |
| `gitea-giteaProviders` | GET | None |
| `gitea-one` | GET | `giteaId` (string) |
| `gitea-testConnection` | POST | `giteaId`?, `organizationName`? |
| `gitea-update` | POST | `giteaId` (string), `giteaUrl` (string), `gitProviderId` (string), `name` (string), +11 optional |

## github

| Tool | Method | Parameters |
|------|--------|------------|
| `github-getGithubBranches` | GET | `repo` (string), `owner` (string), `githubId`? |
| `github-getGithubRepositories` | GET | `githubId` (string) |
| `github-githubProviders` | GET | None |
| `github-one` | GET | `githubId` (string) |
| `github-testConnection` | POST | `githubId` (string) |
| `github-update` | POST | `githubId` (string), `name` (string), `gitProviderId` (string), `githubAppName` (string) |

## gitlab

| Tool | Method | Parameters |
|------|--------|------------|
| `gitlab-create` | POST | `authId` (string), `name` (string), `gitlabUrl` (string), +6 optional |
| `gitlab-getGitlabBranches` | GET | `owner` (string), `repo` (string), `id`?, `gitlabId`? |
| `gitlab-getGitlabRepositories` | GET | `gitlabId` (string) |
| `gitlab-gitlabProviders` | GET | None |
| `gitlab-one` | GET | `gitlabId` (string) |
| `gitlab-testConnection` | POST | `gitlabId` (string), `groupName`? |
| `gitlab-update` | POST | `name` (string), `gitlabId` (string), `gitlabUrl` (string), `gitProviderId` (string), +5 optional |

## libsql

| Tool | Method | Parameters |
|------|--------|------------|
| `libsql-changeStatus` | POST | `libsqlId` (string), `applicationStatus` ("idle" | "running" | "done" | "error") |
| `libsql-create` | POST | `name` (string), `appName` (string), `dockerImage` (string), `environmentId` (string), `description` (string | null), `databaseUser` (string), `databasePassword` (string), `sqldNode` ("primary" | "replica"), `sqldPrimaryUrl` (string | null | null), `enableNamespaces` (boolean), `serverId` (string | null) |
| `libsql-deploy` | POST | `libsqlId` (string) |
| `libsql-move` | POST | `libsqlId` (string), `targetEnvironmentId` (string) |
| `libsql-one` | GET | `libsqlId` (string) |
| `libsql-readLogs` | GET | `libsqlId` (string), `tail`?, `since`?, `search`? |
| `libsql-rebuild` | POST | `libsqlId` (string) |
| `libsql-reload` | POST | `libsqlId` (string), `appName` (string) |
| `libsql-remove` | POST | `libsqlId` (string) |
| `libsql-saveEnvironment` | POST | `libsqlId` (string), `env` (string | null) |
| `libsql-saveExternalPorts` | POST | `libsqlId` (string), `externalPort`?, `externalGRPCPort`?, `externalAdminPort`? |
| `libsql-start` | POST | `libsqlId` (string) |
| `libsql-stop` | POST | `libsqlId` (string) |
| `libsql-update` | POST | `libsqlId` (string), +32 optional |

## licenseKey

| Tool | Method | Parameters |
|------|--------|------------|
| `licenseKey-activate` | POST | `licenseKey` (string) |
| `licenseKey-deactivate` | POST | None |
| `licenseKey-getEnterpriseSettings` | GET | None |
| `licenseKey-haveValidLicenseKey` | GET | None |
| `licenseKey-updateEnterpriseSettings` | POST | `enableEnterpriseFeatures`? |
| `licenseKey-validate` | POST | None |

## mariadb

| Tool | Method | Parameters |
|------|--------|------------|
| `mariadb-changePassword` | POST | `mariadbId` (string), `password` (string), `type`? |
| `mariadb-changeStatus` | POST | `mariadbId` (string), `applicationStatus` ("idle" | "running" | "done" | "error") |
| `mariadb-create` | POST | `name` (string), `environmentId` (string), `databaseName` (string), `databaseUser` (string), `databasePassword` (string), +5 optional |
| `mariadb-deploy` | POST | `mariadbId` (string) |
| `mariadb-move` | POST | `mariadbId` (string), `targetEnvironmentId` (string) |
| `mariadb-one` | GET | `mariadbId` (string) |
| `mariadb-readLogs` | GET | `mariadbId` (string), `tail`?, `since`?, `search`? |
| `mariadb-rebuild` | POST | `mariadbId` (string) |
| `mariadb-reload` | POST | `mariadbId` (string), `appName` (string) |
| `mariadb-remove` | POST | `mariadbId` (string) |
| `mariadb-saveEnvironment` | POST | `mariadbId` (string), `env` (string | null) |
| `mariadb-saveExternalPort` | POST | `mariadbId` (string), `externalPort` (number | null) |
| `mariadb-search` | GET | +8 optional |
| `mariadb-start` | POST | `mariadbId` (string) |
| `mariadb-stop` | POST | `mariadbId` (string) |
| `mariadb-update` | POST | `mariadbId` (string), +31 optional |

## mongo

| Tool | Method | Parameters |
|------|--------|------------|
| `mongo-changePassword` | POST | `mongoId` (string), `password` (string) |
| `mongo-changeStatus` | POST | `mongoId` (string), `applicationStatus` ("idle" | "running" | "done" | "error") |
| `mongo-create` | POST | `name` (string), `environmentId` (string), `databaseUser` (string), `databasePassword` (string), +5 optional |
| `mongo-deploy` | POST | `mongoId` (string) |
| `mongo-move` | POST | `mongoId` (string), `targetEnvironmentId` (string) |
| `mongo-one` | GET | `mongoId` (string) |
| `mongo-readLogs` | GET | `mongoId` (string), `tail`?, `since`?, `search`? |
| `mongo-rebuild` | POST | `mongoId` (string) |
| `mongo-reload` | POST | `mongoId` (string), `appName` (string) |
| `mongo-remove` | POST | `mongoId` (string) |
| `mongo-saveEnvironment` | POST | `mongoId` (string), `env` (string | null) |
| `mongo-saveExternalPort` | POST | `mongoId` (string), `externalPort` (number | null) |
| `mongo-search` | GET | +8 optional |
| `mongo-start` | POST | `mongoId` (string) |
| `mongo-stop` | POST | `mongoId` (string) |
| `mongo-update` | POST | `mongoId` (string), +30 optional |

## mounts

| Tool | Method | Parameters |
|------|--------|------------|
| `mounts-allNamedByApplicationId` | GET | `applicationId` (string) |
| `mounts-create` | POST | `type` ("bind" | "volume" | "file"), `mountPath` (string), `serviceId` (string), +5 optional |
| `mounts-listByServiceId` | GET | `serviceType` (string), `serviceId` (string) |
| `mounts-one` | GET | `mountId` (string) |
| `mounts-remove` | POST | `mountId` (string) |
| `mounts-update` | POST | `mountId` (string), +15 optional |

## mysql

| Tool | Method | Parameters |
|------|--------|------------|
| `mysql-changePassword` | POST | `mysqlId` (string), `password` (string), `type`? |
| `mysql-changeStatus` | POST | `mysqlId` (string), `applicationStatus` ("idle" | "running" | "done" | "error") |
| `mysql-create` | POST | `name` (string), `environmentId` (string), `databaseName` (string), `databaseUser` (string), `databasePassword` (string), +5 optional |
| `mysql-deploy` | POST | `mysqlId` (string) |
| `mysql-move` | POST | `mysqlId` (string), `targetEnvironmentId` (string) |
| `mysql-one` | GET | `mysqlId` (string) |
| `mysql-readLogs` | GET | `mysqlId` (string), `tail`?, `since`?, `search`? |
| `mysql-rebuild` | POST | `mysqlId` (string) |
| `mysql-reload` | POST | `mysqlId` (string), `appName` (string) |
| `mysql-remove` | POST | `mysqlId` (string) |
| `mysql-saveEnvironment` | POST | `mysqlId` (string), `env` (string | null) |
| `mysql-saveExternalPort` | POST | `mysqlId` (string), `externalPort` (number | null) |
| `mysql-search` | GET | +8 optional |
| `mysql-start` | POST | `mysqlId` (string) |
| `mysql-stop` | POST | `mysqlId` (string) |
| `mysql-update` | POST | `mysqlId` (string), +31 optional |

## notification

| Tool | Method | Parameters |
|------|--------|------------|
| `notification-all` | GET | None |
| `notification-createCustom` | POST | `name` (string), `endpoint` (string), +9 optional |
| `notification-createDiscord` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `webhookUrl` (string), `decoration` (boolean) |
| `notification-createEmail` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `smtpServer` (string), `smtpPort` (number), `username` (string), `password` (string), `fromAddress` (string), `toAddresses` (string[]) |
| `notification-createGotify` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverUrl` (string), `appToken` (string), `priority` (number), `decoration` (boolean) |
| `notification-createLark` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `webhookUrl` (string) |
| `notification-createMattermost` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `webhookUrl` (string), `channel`?, `username`? |
| `notification-createNtfy` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverUrl` (string), `topic` (string), `accessToken` (string), `priority` (number) |
| `notification-createPushover` | POST | `name` (string), `userKey` (string), `apiToken` (string), +11 optional |
| `notification-createResend` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `apiKey` (string), `fromAddress` (string), `toAddresses` (string[]) |
| `notification-createSlack` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `webhookUrl` (string), `channel` (string) |
| `notification-createTeams` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `webhookUrl` (string) |
| `notification-createTelegram` | POST | `appBuildError` (boolean), `databaseBackup` (boolean), `dokployBackup` (boolean), `volumeBackup` (boolean), `dokployRestart` (boolean), `name` (string), `appDeploy` (boolean), `dockerCleanup` (boolean), `serverThreshold` (boolean), `botToken` (string), `chatId` (string), `messageThreadId` (string) |
| `notification-getEmailProviders` | GET | None |
| `notification-one` | GET | `notificationId` (string) |
| `notification-receiveNotification` | POST | `Type` ("Memory" | "CPU"), `Value` (number), `Threshold` (number), `Message` (string), `Timestamp` (string), `Token` (string), `ServerType`? |
| `notification-remove` | POST | `notificationId` (string) |
| `notification-testCustomConnection` | POST | `endpoint` (string), `headers`? |
| `notification-testDiscordConnection` | POST | `webhookUrl` (string), `decoration`? |
| `notification-testEmailConnection` | POST | `smtpServer` (string), `smtpPort` (number), `username` (string), `password` (string), `toAddresses` (string[]), `fromAddress` (string) |
| `notification-testGotifyConnection` | POST | `serverUrl` (string), `appToken` (string), `priority` (number), `decoration`? |
| `notification-testLarkConnection` | POST | `webhookUrl` (string) |
| `notification-testMattermostConnection` | POST | `webhookUrl` (string), `channel`?, `username`? |
| `notification-testNtfyConnection` | POST | `serverUrl` (string), `topic` (string), `accessToken` (string), `priority` (number) |
| `notification-testPushoverConnection` | POST | `userKey` (string), `apiToken` (string), `priority` (number), `retry`?, `expire`? |
| `notification-testResendConnection` | POST | `apiKey` (string), `fromAddress` (string), `toAddresses` (string[]) |
| `notification-testSlackConnection` | POST | `webhookUrl` (string), `channel` (string) |
| `notification-testTeamsConnection` | POST | `webhookUrl` (string) |
| `notification-testTelegramConnection` | POST | `botToken` (string), `chatId` (string), `messageThreadId` (string) |
| `notification-updateCustom` | POST | `notificationId` (string), `customId` (string), +12 optional |
| `notification-updateDiscord` | POST | `notificationId` (string), `discordId` (string), +12 optional |
| `notification-updateEmail` | POST | `notificationId` (string), `emailId` (string), +16 optional |
| `notification-updateGotify` | POST | `notificationId` (string), `gotifyId` (string), +13 optional |
| `notification-updateLark` | POST | `notificationId` (string), `larkId` (string), +11 optional |
| `notification-updateMattermost` | POST | `notificationId` (string), `mattermostId` (string), +13 optional |
| `notification-updateNtfy` | POST | `notificationId` (string), `ntfyId` (string), +13 optional |
| `notification-updatePushover` | POST | `notificationId` (string), `pushoverId` (string), +15 optional |
| `notification-updateResend` | POST | `notificationId` (string), `resendId` (string), +13 optional |
| `notification-updateSlack` | POST | `notificationId` (string), `slackId` (string), +12 optional |
| `notification-updateTeams` | POST | `notificationId` (string), `teamsId` (string), +11 optional |
| `notification-updateTelegram` | POST | `notificationId` (string), `telegramId` (string), +13 optional |

## organization

| Tool | Method | Parameters |
|------|--------|------------|
| `organization-active` | GET | None |
| `organization-all` | GET | None |
| `organization-allInvitations` | GET | None |
| `organization-create` | POST | `name` (string), `logo`? |
| `organization-delete` | POST | `organizationId` (string) |
| `organization-inviteMember` | POST | `email` (string), `role` (string) |
| `organization-one` | GET | `organizationId` (string) |
| `organization-removeInvitation` | POST | `invitationId` (string) |
| `organization-setDefault` | POST | `organizationId` (string) |
| `organization-update` | POST | `organizationId` (string), `name` (string), `logo`? |
| `organization-updateMemberRole` | POST | `memberId` (string), `role` (string) |

## patch

| Tool | Method | Parameters |
|------|--------|------------|
| `patch-byEntityId` | GET | `id` (string), `type` ("application" | "compose") |
| `patch-cleanPatchRepos` | POST | `serverId`? |
| `patch-create` | POST | `filePath` (string), `content` (string), +4 optional |
| `patch-delete` | POST | `patchId` (string) |
| `patch-ensureRepo` | POST | `id` (string), `type` ("application" | "compose") |
| `patch-markFileForDeletion` | POST | `id` (string), `type` ("application" | "compose"), `filePath` (string) |
| `patch-one` | GET | `patchId` (string) |
| `patch-readRepoDirectories` | GET | `id` (string), `type` ("application" | "compose"), `repoPath` (string) |
| `patch-readRepoFile` | GET | `id` (string), `type` ("application" | "compose"), `filePath` (string) |
| `patch-saveFileAsPatch` | POST | `id` (string), `type` ("application" | "compose"), `filePath` (string), `content` (string), `patchType`? |
| `patch-toggleEnabled` | POST | `patchId` (string), `enabled` (boolean) |
| `patch-update` | POST | `patchId` (string), +6 optional |

## port

| Tool | Method | Parameters |
|------|--------|------------|
| `port-create` | POST | `publishedPort` (number), `publishMode` ("ingress" | "host"), `targetPort` (number), `protocol` ("tcp" | "udp"), `applicationId` (string) |
| `port-delete` | POST | `portId` (string) |
| `port-one` | GET | `portId` (string) |
| `port-update` | POST | `portId` (string), `publishedPort` (number), `publishMode` ("ingress" | "host"), `targetPort` (number), `protocol` ("tcp" | "udp") |

## postgres

| Tool | Method | Parameters |
|------|--------|------------|
| `postgres-changePassword` | POST | `postgresId` (string), `password` (string) |
| `postgres-changeStatus` | POST | `postgresId` (string), `applicationStatus` ("idle" | "running" | "done" | "error") |
| `postgres-create` | POST | `name` (string), `databaseName` (string), `databaseUser` (string), `databasePassword` (string), `environmentId` (string), +4 optional |
| `postgres-deploy` | POST | `postgresId` (string) |
| `postgres-move` | POST | `postgresId` (string), `targetEnvironmentId` (string) |
| `postgres-one` | GET | `postgresId` (string) |
| `postgres-readLogs` | GET | `postgresId` (string), `tail`?, `since`?, `search`? |
| `postgres-rebuild` | POST | `postgresId` (string) |
| `postgres-reload` | POST | `postgresId` (string), `appName` (string) |
| `postgres-remove` | POST | `postgresId` (string) |
| `postgres-saveEnvironment` | POST | `postgresId` (string), `env` (string | null) |
| `postgres-saveExternalPort` | POST | `postgresId` (string), `externalPort` (number | null) |
| `postgres-search` | GET | +8 optional |
| `postgres-start` | POST | `postgresId` (string) |
| `postgres-stop` | POST | `postgresId` (string) |
| `postgres-update` | POST | `postgresId` (string), +30 optional |

## previewDeployment

| Tool | Method | Parameters |
|------|--------|------------|
| `previewDeployment-all` | GET | `applicationId` (string) |
| `previewDeployment-delete` | POST | `previewDeploymentId` (string) |
| `previewDeployment-one` | GET | `previewDeploymentId` (string) |
| `previewDeployment-redeploy` | POST | `previewDeploymentId` (string), `title`?, `description`? |

## project

| Tool | Method | Parameters |
|------|--------|------------|
| `project-all` | GET | None |
| `project-allForPermissions` | GET | None |
| `project-create` | POST | `name` (string), `description`?, `env`? |
| `project-duplicate` | POST | `sourceEnvironmentId` (string), `name` (string), +4 optional |
| `project-homeStats` | GET | None |
| `project-one` | GET | `projectId` (string) |
| `project-remove` | POST | `projectId` (string) |
| `project-search` | GET | +5 optional |
| `project-update` | POST | `projectId` (string), +5 optional |

## redirects

| Tool | Method | Parameters |
|------|--------|------------|
| `redirects-create` | POST | `regex` (string), `replacement` (string), `permanent` (boolean), `applicationId` (string) |
| `redirects-delete` | POST | `redirectId` (string) |
| `redirects-one` | GET | `redirectId` (string) |
| `redirects-update` | POST | `redirectId` (string), `regex` (string), `replacement` (string), `permanent` (boolean) |

## redis

| Tool | Method | Parameters |
|------|--------|------------|
| `redis-changePassword` | POST | `redisId` (string), `password` (string) |
| `redis-changeStatus` | POST | `redisId` (string), `applicationStatus` ("idle" | "running" | "done" | "error") |
| `redis-create` | POST | `name` (string), `databasePassword` (string), `environmentId` (string), +4 optional |
| `redis-deploy` | POST | `redisId` (string) |
| `redis-move` | POST | `redisId` (string), `targetEnvironmentId` (string) |
| `redis-one` | GET | `redisId` (string) |
| `redis-readLogs` | GET | `redisId` (string), `tail`?, `since`?, `search`? |
| `redis-rebuild` | POST | `redisId` (string) |
| `redis-reload` | POST | `redisId` (string), `appName` (string) |
| `redis-remove` | POST | `redisId` (string) |
| `redis-saveEnvironment` | POST | `redisId` (string), `env` (string | null) |
| `redis-saveExternalPort` | POST | `redisId` (string), `externalPort` (number | null) |
| `redis-search` | GET | +8 optional |
| `redis-start` | POST | `redisId` (string) |
| `redis-stop` | POST | `redisId` (string) |
| `redis-update` | POST | `redisId` (string), +28 optional |

## registry

| Tool | Method | Parameters |
|------|--------|------------|
| `registry-all` | GET | None |
| `registry-create` | POST | `registryName` (string), `username` (string), `password` (string), `registryUrl` (string), `registryType` ("cloud"), `imagePrefix` (string | null), `serverId`? |
| `registry-one` | GET | `registryId` (string) |
| `registry-remove` | POST | `registryId` (string) |
| `registry-testRegistry` | POST | `username` (string), `password` (string), `registryUrl` (string), `registryType` ("cloud"), `registryName`?, `imagePrefix`?, `serverId`? |
| `registry-testRegistryById` | POST | `registryId`?, `serverId`? |
| `registry-update` | POST | `registryId` (string), +9 optional |

## rollback

| Tool | Method | Parameters |
|------|--------|------------|
| `rollback-delete` | POST | `rollbackId` (string) |
| `rollback-rollback` | POST | `rollbackId` (string) |

## schedule

| Tool | Method | Parameters |
|------|--------|------------|
| `schedule-create` | POST | `name` (string), `cronExpression` (string), `command` (string), +13 optional |
| `schedule-delete` | POST | `scheduleId` (string) |
| `schedule-list` | GET | `id` (string), `scheduleType` ("application" | "compose" | "server" | "dokploy-server") |
| `schedule-one` | GET | `scheduleId` (string) |
| `schedule-runManually` | POST | `scheduleId` (string) |
| `schedule-update` | POST | `scheduleId` (string), `name` (string), `cronExpression` (string), `command` (string), +12 optional |

## security

| Tool | Method | Parameters |
|------|--------|------------|
| `security-create` | POST | `applicationId` (string), `username` (string), `password` (string) |
| `security-delete` | POST | `securityId` (string) |
| `security-one` | GET | `securityId` (string) |
| `security-update` | POST | `securityId` (string), `username` (string), `password` (string) |

## server

| Tool | Method | Parameters |
|------|--------|------------|
| `server-all` | GET | None |
| `server-allForPermissions` | GET | None |
| `server-buildServers` | GET | None |
| `server-count` | GET | None |
| `server-create` | POST | `name` (string), `description` (string | null), `ipAddress` (string), `port` (number), `username` (string), `sshKeyId` (string | null), `serverType` ("deploy" | "build") |
| `server-getDefaultCommand` | GET | `serverId` (string) |
| `server-getServerMetrics` | GET | `url` (string), `token` (string), `dataPoints` (string) |
| `server-getServerTime` | GET | None |
| `server-one` | GET | `serverId` (string) |
| `server-publicIp` | GET | None |
| `server-remove` | POST | `serverId` (string) |
| `server-security` | GET | `serverId` (string) |
| `server-setup` | POST | `serverId` (string) |
| `server-setupMonitoring` | POST | `serverId` (string), `metricsConfig` (object) |
| `server-update` | POST | `name` (string), `description` (string | null), `serverId` (string), `ipAddress` (string), `port` (number), `username` (string), `sshKeyId` (string | null), `serverType` ("deploy" | "build"), `command`? |
| `server-validate` | GET | `serverId` (string) |
| `server-withSSHKey` | GET | None |

## settings

| Tool | Method | Parameters |
|------|--------|------------|
| `settings-assignDomainServer` | POST | `host` (string), `certificateType` ("letsencrypt" | "none" | "custom"), `letsEncryptEmail`?, `https`? |
| `settings-checkGPUStatus` | GET | `serverId`? |
| `settings-checkInfrastructureHealth` | GET | None |
| `settings-cleanAll` | POST | `serverId`? |
| `settings-cleanAllDeploymentQueue` | POST | None |
| `settings-cleanDockerBuilder` | POST | `serverId`? |
| `settings-cleanDockerPrune` | POST | `serverId`? |
| `settings-cleanMonitoring` | POST | None |
| `settings-cleanRedis` | POST | None |
| `settings-cleanSSHPrivateKey` | POST | None |
| `settings-cleanStoppedContainers` | POST | `serverId`? |
| `settings-cleanUnusedImages` | POST | `serverId`? |
| `settings-cleanUnusedVolumes` | POST | `serverId`? |
| `settings-getDockerDiskUsage` | GET | None |
| `settings-getDokployCloudIps` | GET | None |
| `settings-getDokployVersion` | GET | None |
| `settings-getIp` | GET | None |
| `settings-getLogCleanupStatus` | GET | None |
| `settings-getOpenApiDocument` | GET | None |
| `settings-getReleaseTag` | GET | None |
| `settings-getTraefikPorts` | GET | `serverId`? |
| `settings-getUpdateData` | POST | None |
| `settings-getWebServerSettings` | GET | None |
| `settings-haveActivateRequests` | GET | None |
| `settings-haveTraefikDashboardPortEnabled` | GET | `serverId`? |
| `settings-health` | GET | None |
| `settings-isCloud` | GET | None |
| `settings-isUserSubscribed` | GET | None |
| `settings-readDirectories` | GET | `serverId`? |
| `settings-readMiddlewareTraefikConfig` | GET | None |
| `settings-readTraefikConfig` | GET | None |
| `settings-readTraefikEnv` | GET | `serverId`? |
| `settings-readTraefikFile` | GET | `path` (string), `serverId`? |
| `settings-readWebServerTraefikConfig` | GET | None |
| `settings-reloadRedis` | POST | None |
| `settings-reloadServer` | POST | None |
| `settings-reloadTraefik` | POST | `serverId`? |
| `settings-saveSSHPrivateKey` | POST | `sshPrivateKey` (string) |
| `settings-setupGPU` | POST | `serverId`? |
| `settings-toggleDashboard` | POST | `enableDashboard`?, `serverId`? |
| `settings-toggleRequests` | POST | `enable` (boolean) |
| `settings-updateDockerCleanup` | POST | `enableDockerCleanup` (boolean), `serverId`? |
| `settings-updateLogCleanup` | POST | `cronExpression` (string | null) |
| `settings-updateMiddlewareTraefikConfig` | POST | `traefikConfig` (string) |
| `settings-updateServer` | POST | None |
| `settings-updateServerIp` | POST | `serverIp` (string) |
| `settings-updateTraefikConfig` | POST | `traefikConfig` (string) |
| `settings-updateTraefikFile` | POST | `path` (string), `traefikConfig` (string), `serverId`? |
| `settings-updateTraefikPorts` | POST | `additionalPorts` (object[]), `serverId`? |
| `settings-updateWebServerTraefikConfig` | POST | `traefikConfig` (string) |
| `settings-writeTraefikEnv` | POST | `env` (string), `serverId`? |

## sshKey

| Tool | Method | Parameters |
|------|--------|------------|
| `sshKey-all` | GET | None |
| `sshKey-allForApps` | GET | None |
| `sshKey-create` | POST | `name` (string), `privateKey` (string), `publicKey` (string), `organizationId` (string), `description`? |
| `sshKey-generate` | POST | `type`? |
| `sshKey-one` | GET | `sshKeyId` (string) |
| `sshKey-remove` | POST | `sshKeyId` (string) |
| `sshKey-update` | POST | `sshKeyId` (string), `name`?, `description`?, `lastUsedAt`? |

## sso

| Tool | Method | Parameters |
|------|--------|------------|
| `sso-addTrustedOrigin` | POST | `origin` (string) |
| `sso-deleteProvider` | POST | `providerId` (string) |
| `sso-getTrustedOrigins` | GET | None |
| `sso-listProviders` | GET | None |
| `sso-one` | GET | `providerId` (string) |
| `sso-register` | POST | `providerId` (string), `issuer` (string), `domains` (string[]), +4 optional |
| `sso-removeTrustedOrigin` | POST | `origin` (string) |
| `sso-showSignInWithSSO` | GET | None |
| `sso-update` | POST | `providerId` (string), `issuer` (string), `domains` (string[]), +4 optional |
| `sso-updateTrustedOrigin` | POST | `oldOrigin` (string), `newOrigin` (string) |

## stripe

| Tool | Method | Parameters |
|------|--------|------------|
| `stripe-canCreateMoreServers` | GET | None |
| `stripe-createCheckoutSession` | POST | `tier` ("legacy" | "hobby" | "startup"), `productId` (string), `serverQuantity` (number), `isAnnual` (boolean) |
| `stripe-createCustomerPortalSession` | POST | None |
| `stripe-getCurrentPlan` | GET | None |
| `stripe-getInvoices` | GET | None |
| `stripe-getProducts` | GET | None |
| `stripe-updateInvoiceNotifications` | POST | `enabled` (boolean) |
| `stripe-upgradeSubscription` | POST | `tier` ("hobby" | "startup"), `serverQuantity` (number), `isAnnual` (boolean) |

## swarm

| Tool | Method | Parameters |
|------|--------|------------|
| `swarm-getContainerStats` | GET | `serverId`? |
| `swarm-getNodeApps` | GET | `serverId`? |
| `swarm-getNodeInfo` | GET | `nodeId` (string), `serverId`? |
| `swarm-getNodes` | GET | `serverId`? |

## tag

| Tool | Method | Parameters |
|------|--------|------------|
| `tag-all` | GET | None |
| `tag-assignToProject` | POST | `projectId` (string), `tagId` (string) |
| `tag-bulkAssign` | POST | `projectId` (string), `tagIds` (string[]) |
| `tag-create` | POST | `name` (string), `color`? |
| `tag-one` | GET | `tagId` (string) |
| `tag-remove` | POST | `tagId` (string) |
| `tag-removeFromProject` | POST | `projectId` (string), `tagId` (string) |
| `tag-update` | POST | `tagId` (string), +4 optional |

## user

| Tool | Method | Parameters |
|------|--------|------------|
| `user-all` | GET | None |
| `user-assignPermissions` | POST | `id` (string), `accessedProjects` (string[]), `accessedEnvironments` (string[]), `accessedServices` (string[]), `accessedGitProviders` (string[]), `accessedServers` (string[]), `canCreateProjects` (boolean), `canCreateServices` (boolean), `canDeleteProjects` (boolean), `canDeleteServices` (boolean), `canAccessToDocker` (boolean), `canAccessToTraefikFiles` (boolean), `canAccessToAPI` (boolean), `canAccessToSSHKeys` (boolean), `canAccessToGitProviders` (boolean), `canDeleteEnvironments` (boolean), `canCreateEnvironments` (boolean) |
| `user-checkUserOrganizations` | GET | `userId` (string) |
| `user-createApiKey` | POST | `name` (string), `metadata` (object), +8 optional |
| `user-createUserWithCredentials` | POST | `email` (string), `password` (string), `role` (string) |
| `user-deleteApiKey` | POST | `apiKeyId` (string) |
| `user-generateToken` | POST | None |
| `user-get` | GET | None |
| `user-getBackups` | GET | None |
| `user-getBookmarkedTemplates` | GET | None |
| `user-getContainerMetrics` | GET | `url` (string), `token` (string), `appName` (string), `dataPoints` (string) |
| `user-getInvitations` | GET | None |
| `user-getMetricsToken` | GET | None |
| `user-getPermissions` | GET | None |
| `user-getServerMetrics` | GET | None |
| `user-getUserByToken` | GET | `token` (string) |
| `user-haveRootAccess` | GET | None |
| `user-one` | GET | `userId` (string) |
| `user-remove` | POST | `userId` (string) |
| `user-sendInvitation` | POST | `invitationId` (string), `notificationId` (string) |
| `user-session` | GET | None |
| `user-toggleTemplateBookmark` | POST | `templateId` (string) |
| `user-update` | POST | +25 optional |

## volumeBackups

| Tool | Method | Parameters |
|------|--------|------------|
| `volumeBackups-create` | POST | `name` (string), `volumeName` (string), `prefix` (string), `cronExpression` (string), `destinationId` (string), +15 optional |
| `volumeBackups-delete` | POST | `volumeBackupId` (string) |
| `volumeBackups-list` | GET | `id` (string), `volumeBackupType` ("application" | "postgres" | "mysql" | "mariadb" | "mongo" | "redis" | "compose" | "libsql") |
| `volumeBackups-one` | GET | `volumeBackupId` (string) |
| `volumeBackups-runManually` | POST | `volumeBackupId` (string) |
| `volumeBackups-update` | POST | `name` (string), `volumeName` (string), `prefix` (string), `cronExpression` (string), `destinationId` (string), `volumeBackupId` (string), +15 optional |

## whitelabeling

| Tool | Method | Parameters |
|------|--------|------------|
| `whitelabeling-get` | GET | None |
| `whitelabeling-getPublic` | GET | None |
| `whitelabeling-reset` | POST | None |
| `whitelabeling-update` | POST | `whitelabelingConfig` (object) |

## Notes

- Execute a tool with `./dp --mcp-call <tool-name> --json '{...}'`.
- Describe a tool with `./dp --mcp-describe <tool-name>`.
- Destructive tools are flagged when their operation name contains `delete` or `remove`.
