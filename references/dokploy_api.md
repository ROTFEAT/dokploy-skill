# Dokploy REST API Notes

This reference keeps only the endpoints and gotchas that are useful during real deployment and debugging work.

## Auth

All endpoints use:

```http
x-api-key: <your_key>
```

## Deploy and diagnose

### `POST /api/application.deploy`

Request:

```json
{"applicationId": "..."}
```

Triggers an async deployment. Use `deployment.all` to poll progress.

### `GET /api/deployment.all?applicationId=...`

Returns newest-first deployment records.

Useful fields:

- `deploymentId`
- `status`
- `createdAt`
- `errorMessage`
- `logPath`
- `title`

Observed status values:

- `running`
- `done`
- `error`

### `GET /api/application.readLogs?applicationId=...&tail=N&since=10m`

Returns container stdout as a plain string, not JSON.

Do not use `search=`. Dokploy may turn a grep no-match into HTTP 500. Filter locally instead.

Some self-hosted versions return HTTP 404 even though the application is running. In that case,
use `docker.getContainersByAppLabel`, `docker.getContainersByAppNameMatch`, or
`docker.getServiceContainersByAppName` to discover a target, then read logs from the
`/docker-container-logs` WebSocket with the same `x-api-key`.

### `GET /api/postgres.readLogs?postgresId=...&tail=N`

Returns Postgres container logs as a plain string.

The same 404 compatibility gap can happen here. Fallback is the same: resolve the database
service `appName`, discover a container or swarm target through `docker.*`, then use
`/docker-container-logs`.

### `GET /api/application.one?applicationId=...`

Returns the current application config. Use this first when debugging a bad deploy.

Useful extra fields for log fallback:

- `appName`
- `serverId`

### `GET /api/postgres.one?postgresId=...`

Returns the current Postgres service config.

Useful extra fields for log fallback:

- `appName`
- `serverId`

### `GET /api/docker.getContainersByAppLabel?appName=...&type=standalone`

Returns matching native containers for an app. Good first choice for runtime log fallback.

### `GET /api/docker.getContainersByAppNameMatch?appName=...`

Returns native containers that match the Dokploy `appName`. Useful when label lookup is empty.

### `GET /api/docker.getServiceContainersByAppName?appName=...`

Returns swarm task targets. Use this when no native container target is available.

### `GET /docker-container-logs?...` (WebSocket upgrade)

Query parameters:

- `containerId`
- `tail`
- `since`
- `runType=native|swarm`
- optional `serverId`

Authentication works with the same `x-api-key` header that the REST API uses.

## Creation and update flows

### `POST /api/project.create`

```json
{"name": "my-project", "description": "optional"}
```

Creates a project and its default `production` environment.

### `POST /api/application.create`

```json
{"name": "my-app", "description": "optional", "environmentId": "..."}
```

### `POST /api/application.saveGitProvider`

```json
{
  "applicationId": "...",
  "customGitUrl": "https://<token>@github.com/owner/repo.git",
  "customGitBranch": "main",
  "customGitBuildPath": "/",
  "watchPaths": []
}
```

### `POST /api/application.saveBuildType`

```json
{
  "applicationId": "...",
  "buildType": "dockerfile",
  "dockerfile": "Dockerfile",
  "dockerContextPath": "."
}
```

Common `buildType` values:

- `dockerfile`
- `nixpacks`
- `heroku_buildpacks`
- `paketo_buildpacks`
- `railpack`

### `POST /api/application.saveEnvironment`

```json
{
  "applicationId": "...",
  "env": "KEY1=value1\nKEY2=value2",
  "buildArgs": "",
  "buildSecrets": "",
  "createEnvFile": true
}
```

### `POST /api/application.update`

Partial update. Send `applicationId` plus the fields you want to change.

## Database and exposure

### `POST /api/postgres.create`

```json
{
  "name": "my-db",
  "databaseName": "app",
  "databaseUser": "app",
  "databasePassword": "<generated>",
  "environmentId": "...",
  "dockerImage": "postgres:15"
}
```

### `POST /api/postgres.deploy`

```json
{"postgresId": "..."}
```

### `POST /api/port.create`

```json
{"applicationId": "...", "publishedPort": 1888, "targetPort": 8080, "protocol": "tcp"}
```

Swarm ingress may accept TCP yet still fail HTTP requests. Treat this as a fallback.

### `POST /api/domain.create`

```json
{
  "applicationId": "...",
  "host": "203.0.113.10.sslip.io",
  "port": 8080,
  "path": "/",
  "https": false,
  "certificateType": "none",
  "domainType": "application"
}
```

Prefer this over `port.create` for real traffic. It uses Traefik host routing.

## Fast schema discovery

If you need a Dokploy endpoint that is not documented here, send an intentionally incomplete request and inspect `zodError.fieldErrors`.

Example:

```bash
curl -sS -X POST \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "content-type: application/json" \
  -d '{}' \
  "$DOKPLOY_URL/api/<endpoint>"
```

If the endpoint exists, Dokploy often returns the missing required fields and expected types.
