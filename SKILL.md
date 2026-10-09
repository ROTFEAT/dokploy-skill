---
name: dokploy-ops
description: |
  Operate Dokploy through its REST API: trigger application deployments, poll deployment
  status, inspect app configuration, read runtime or Postgres logs, call any endpoint from
  the official Dokploy MCP tool catalog, and diagnose common Dokploy build or routing
  failures. Use when the user asks to deploy to Dokploy, inspect Dokploy status/logs,
  create/update/delete Dokploy resources, manage projects, apps, compose services,
  databases, domains, backups, notifications, servers, settings, users, SSO, Docker,
  Git providers, or run /dp.
---

# dokploy-ops

Use this skill as the single entry point for Dokploy deployment, status checks, logs, and API-level troubleshooting.
It includes high-level deploy/log commands plus a generated catalog matching the official Dokploy MCP server tools.

## Workflow

### 1. Resolve config before asking

Check in this order:

1. Values already provided in the user request
2. Environment variables: `DOKPLOY_URL`, `DOKPLOY_API_KEY`, `DOKPLOY_APP_ID`, optional `DOKPLOY_POSTGRES_ID`
3. `.env` in the current working directory

Do not ask for secrets if the values are already available.

### 2. Ask once if anything is missing

Ask for every missing item in one concise message.

- App actions need `DOKPLOY_URL`, `DOKPLOY_API_KEY`, `DOKPLOY_APP_ID`
- Postgres log actions need `DOKPLOY_URL`, `DOKPLOY_API_KEY`, `DOKPLOY_POSTGRES_ID`

Do not echo the API key back to the user. Do not write secrets into `.env` unless the user explicitly asks.

### 2b. Default to the GitHub provider when configuring an app's source

When creating an application or wiring up its deployment source, default to the
GitHub provider and do not ask which provider to use:

1. List configured GitHub apps with `./dp --mcp-call github-githubProviders` (no body).
2. If none exist, tell the user to install the Dokploy GitHub App first
   (Dokploy UI → Git providers) and stop. If one exists, pick it — ask only
   when several are configured.
3. Resolve the repo the user wants to deploy: prefer the current workspace
   `git remote get-url origin`; otherwise ask once. Parse `owner`/`repository`
   from the URL and set `branch` to the current branch (fallback `main`).
4. Save the source with `application-saveGithubProvider` (all schema-required
   fields, nullable values may be `null`):

```bash
./dp --mcp-call application-saveGithubProvider --json \
  '{"applicationId":"<app>","githubId":"<id>","owner":"<owner>","repository":"<repo>","branch":"main","buildPath":"/","triggerType":"push"}'
```

If the GitHub provider is unavailable — no GitHub App configured, the repo is
not on GitHub, or the user prefers otherwise — ask once which alternative to
use, then proceed without further questions:

- Generic git (any host, or a token-authenticated HTTPS URL):

```bash
./dp --mcp-call application-saveGitProvider --json \
  '{"applicationId":"<app>","customGitUrl":"https://<token>@host/owner/repo.git","customGitBranch":"main","customGitBuildPath":"/","watchPaths":[]}'
```

- Docker image (prebuilt, public or private registry):

```bash
./dp --mcp-call application-saveDockerProvider --json \
  '{"applicationId":"<app>","dockerImage":"registry.example.com/app:tag","username":null,"password":null,"registryUrl":null}'
```

Do not echo registry passwords or git tokens back to the user.

### 3. Run the bundled CLI

Prefer the bundled script over ad-hoc `curl` for flows it already covers. From the repo root or installed skill bundle:

```bash
python3 scripts/dokploy_api.py
python3 scripts/dokploy_api.py --only-status
python3 scripts/dokploy_api.py --only-logs --log-tail=200
python3 scripts/dokploy_api.py --only-logs --search=ERROR
python3 scripts/dokploy_api.py --db-logs --postgres=<id>
python3 scripts/dokploy_api.py --inspect
python3 scripts/dokploy_api.py --list
```

Run it from the target workspace so the workspace `.env` is visible. If you must invoke it
from another directory, pass `--env-file=/absolute/path/to/.env`.

Use CLI flags when the user already supplied values directly:

```bash
python3 scripts/dokploy_api.py \
  --url=http://host:3000 --key=<api-key> --app=<application-id>
```

For legacy Claude installs, `./dp` remains a wrapper around the same script and still supports
`--version` and `--check-update`.

### 3b. Use the MCP catalog for full API coverage

For Dokploy operations not covered by the high-level deploy/log flags, use the generated MCP catalog instead of hand-rolling `curl`.

Discover tools:

```bash
./dp --mcp-tools
./dp --mcp-tools --mcp-tag application
./dp --mcp-search domain
./dp --mcp-describe application-one
```

Call tools by name:

```bash
./dp --mcp-call project-all
./dp --mcp-call application-one --json '{"applicationId":"app_x"}'
./dp --mcp-call postgres-deploy --json '{"postgresId":"pg_x"}'
./dp --mcp-call domain-create --json-file /absolute/path/domain.json
./dp --mcp-call application-update --param applicationId=app_x --param replicas=2
```

The catalog lives in `references/dokploy_mcp_tools.json` and the compact human-readable list lives in
`references/dokploy_mcp_tools.md`. Read those references when you need exact parameter names, required fields,
or available categories.

Safety rules:

- Before calling a tool with `destructiveHint` or a name containing delete/remove, show the exact tool name and JSON body to the user and get explicit confirmation. Then pass `--yes`.
- Do not use `--yes` for destructive calls unless the user has confirmed that exact action.
- Do not print API keys. Use `DOKPLOY_REDACT_ENV=true` or `--redact` when responses may include env vars, compose files, tokens, passwords, or SSH keys.
- Honor `DOKPLOY_ENABLED_TAGS` when present; it intentionally narrows the visible tool surface.

For an endpoint that exists in Dokploy but is not in the catalog, use raw API mode only after checking the references:

```bash
./dp --api-call /project.all --api-method GET
./dp --api-call /some.path --api-method POST --json '{"key":"value"}'
```

### 4. Interpret the result

If the final status is `done`, report success and show only the relevant warnings or errors from logs.

If the final status is `error`:

1. 打印 `errorMessage`
2. Classify the failure if obvious: build error, image pull failure, port/routing issue, disk full, bad env, and so on
3. If `logPath` exists, mention that the full build log lives on the Dokploy host and is not exposed by the REST API
4. Suggest the next debugging step

If the script exits with a timeout, say the deployment is still running and suggest `--only-status`.

## Known gotchas

- Do not pass `search=` to `application.readLogs`; Dokploy may return HTTP 500 on no match. Use `--search`, which filters client-side.
- Some self-hosted Dokploy versions expose `docker.*` container discovery routes but do not expose `application.readLogs` / `postgres.readLogs`. The bundled script auto-falls back to `/docker-container-logs` WebSocket with the same `x-api-key`.
- Swarm `port.create` often accepts TCP but still fails HTTP traffic. Prefer `domain.create` with Traefik host routing.
- `python app.py` without `-u` may buffer stdout, so `print()` can look missing in logs while `logging` output still appears.
- `zodError.fieldErrors` is the fastest way to discover the required body for an unknown endpoint.
- Some failures can only be diagnosed from the host-side `logPath`; the REST API does not expose that file.

## References

Read `references/dokploy_api.md` when you need endpoint schemas or creation/update flows beyond deploy, status, and logs.

## Boundaries

- Do not dump full raw logs unless the user asks for them.
- Do not hand-roll new API calls before checking whether the bundled script already supports the flow.
- If a needed Dokploy endpoint is not covered by the script, read `references/dokploy_api.md` first and then call the API directly.
