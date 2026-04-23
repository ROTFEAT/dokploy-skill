---
name: dokploy-ops
description: |
  Operate Dokploy through its REST API: trigger application deployments, poll deployment
  status, inspect app configuration, read runtime or Postgres logs, and diagnose common
  Dokploy build or routing failures. Use when the user asks to deploy to Dokploy, inspect
  Dokploy status/logs, troubleshoot a Dokploy application or database, or run /dp.
---

# dokploy-ops

Use this skill as the single entry point for Dokploy deployment, status checks, logs, and API-level troubleshooting.

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
