# dokploy-skill

Claude Code skill + `/dp` slash command for Dokploy deploys. One entry point for
**trigger → poll status → tail logs** via the Dokploy REST API — works against
local or remote Dokploy.

## Install

```bash
git clone <this-repo> dokploy-skill
cd dokploy-skill
./install.sh
```

Creates symlinks:
- `~/.claude/skills/dokploy-deploy → <repo>`
- `~/.claude/commands/dp.md`

## Usage

Inside Claude Code:

- `/dp` — invokes the full workflow
- Any natural-language variant also triggers the skill: "部署到 dokploy",
  "dokploy 部署", "deploy to dokploy", "推到 dokploy"

The skill:
1. Resolves `DOKPLOY_URL` / `DOKPLOY_API_KEY` / `DOKPLOY_APP_ID` from env or `.env`
2. If anything is missing, asks you once (not per-field)
3. Runs `dp` — triggers deploy, polls `deployment.all`, prints runtime logs

Direct CLI is also fine:

```bash
./dp                          # full flow
./dp --only-status            # latest deployment only
./dp --only-logs --tail=200   # runtime logs only
./dp --list                   # last 5 deployments
./dp --url=... --key=... --app=...
```

## Config

First match wins:

1. CLI args (`--url --key --app`)
2. Env vars: `DOKPLOY_URL`, `DOKPLOY_API_KEY`, `DOKPLOY_APP_ID`
3. `.env` in CWD with the same keys

## Exit codes

| code | meaning |
|------|---------|
| 0    | deploy done |
| 1    | deploy error (Dokploy status=error or HTTP error) |
| 2    | missing config |
| 3    | poll timeout |

## Dokploy endpoints used

| method | path | purpose |
|--------|------|---------|
| POST | `/api/application.deploy` | trigger deploy |
| GET  | `/api/deployment.all?applicationId=…` | list deployments (newest first) |
| GET  | `/api/application.readLogs?applicationId=…&tail=&since=&search=` | container stdout |

Authentication: header `x-api-key: <key>`.

## Known limits

- Full **build logs** are not exposed via REST — Dokploy UI streams them over
  WebSocket. The skill gives you `errorMessage` + server-side `logPath`; for
  the full build trace, SSH to the Dokploy host or open Dokploy UI.
- `application.readLogs` returns empty when the container isn't running yet.
