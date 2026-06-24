# dokploy-skill

Dokploy skill bundle for both Claude Code and Codex. One entry point for
**deploy -> poll -> tail runtime or DB logs -> diagnose** via the Dokploy REST
API, plus a generated catalog that mirrors the official Dokploy MCP tool
surface. Works against local or remote Dokploy.

## Install

```bash
git clone https://github.com/ROTFEAT/dokploy-skill.git
cd dokploy-skill
./install.sh
```

Default install refreshes both Claude and Codex links. Optional flags:

```bash
./install.sh --claude-only
./install.sh --codex-only
```

Creates symlinks:
- `~/.claude/skills/dokploy-ops -> <repo>`
- `~/.claude/skills/dokploy-deploy -> <repo>` (legacy alias)
- `~/.claude/commands/dp.md`, `~/.claude/commands/dp-update.md`
- `~/.codex/skills/dokploy-ops -> <repo>`
- Caches skill path at `~/.claude/.dokploy-skill-path`
- Installs git pre-commit hook that auto-bumps `VERSION`'s patch number

## Usage

Inside Claude Code:
- `/dp` — full flow (deploy + poll + logs)
- `/dp-update` — pull latest, reinstall
- Natural language also triggers the skill: "部署到 dokploy", "dokploy 部署",
  "deploy to dokploy", "看 dokploy 日志"

Inside Codex:
- mention `dokploy-ops` by name, or ask to deploy/check logs on Dokploy
- the installer exposes the repo root as `~/.codex/skills/dokploy-ops`

Direct CLI:

```bash
./dp                            # trigger deploy + poll + tail app logs
python3 scripts/dokploy_api.py  # same logic without the wrapper
./dp --only-status              # latest deployment status
./dp --only-logs --log-tail=200 # runtime logs (app container)
./dp --only-logs --search=ERROR # client-side grep, no 500 bug
./dp --db-logs --postgres=<id>  # postgres container logs
./dp --inspect                  # current application config
./dp --list                     # last 5 deployments
./dp --mcp-tools                # MCP category summary
./dp --mcp-tools --mcp-tag application
./dp --mcp-search deploy
./dp --mcp-describe application-one
./dp --mcp-call project-all
./dp --mcp-call application-one --json '{"applicationId":"app_x"}'
./dp --mcp-call application-delete --json '{"applicationId":"app_x"}' --yes
./dp --api-call /project.all --api-method GET
./dp --version                  # local skill version
./dp --check-update             # compare to GitHub HEAD VERSION
```

The MCP catalog is generated from Dokploy's official MCP OpenAPI input and
currently includes 524 tools across 48 categories. Use
`references/dokploy_mcp_tools.md` for the compact list, or
`references/dokploy_mcp_tools.json` for exact schemas and annotations.

## Config

First match wins:
1. CLI args (`--url --key --app [--postgres]`)
2. Env vars: `DOKPLOY_URL`, `DOKPLOY_API_KEY`, `DOKPLOY_APP_ID`, `DOKPLOY_POSTGRES_ID`
3. `.env` in CWD with the same keys

The generic MCP/API path also honors the official MCP-style environment
variables:

- `DOKPLOY_CUSTOM_HEADERS` — JSON object of extra upstream headers
- `DOKPLOY_ENABLED_TAGS` — comma-separated category filter
- `DOKPLOY_TIMEOUT` — request timeout in milliseconds
- `DOKPLOY_RETRY_ATTEMPTS`, `DOKPLOY_RETRY_DELAY`
- `DOKPLOY_REDACT_ENV`, `DOKPLOY_REDACT_FIELDS`

If you launch the helper from outside the target workspace, pass:

```bash
python3 scripts/dokploy_api.py --env-file /absolute/path/to/.env
```

## Exit codes

| code | meaning |
|------|---------|
| 0    | done / ok |
| 1    | deploy error or HTTP error |
| 2    | missing config |
| 3    | poll timeout |

## Known gotchas

- `application.readLogs?search=...` returns **HTTP 500 on no match** (the
  server-side `docker logs | grep` exits non-zero). `dp --search=` therefore
  greps client-side.
- Some self-hosted Dokploy versions expose runtime containers but return
  **HTTP 404** for `application.readLogs` / `postgres.readLogs`. The bundled
  helper falls back to `docker.*` discovery plus `/docker-container-logs`
  WebSocket with the same `x-api-key`.
- Swarm **ingress port publishing** (`port.create`) often accepts TCP but times
  out on HTTP. Prefer Traefik host routing via `domain.create` with a wildcard
  DNS (`<ip>.sslip.io`, `<ip>.nip.io`, `<dash-ip>.traefik.me`).
- A `python foo.py` CMD without `-u` swallows `print()` output; `logging.*`
  (stderr) is still visible. Startup looks "stuck" in `readLogs` but isn't.
- sslip.io / nip.io / traefik.me hostnames are hijacked by Tailscale MagicDNS
  on some machines — return `198.19.x.x`. Test with `curl -H "Host: ..."` or
  `--resolve host:80:<ip>`.

## Version & auto-update

- Pre-commit hook bumps `VERSION` patch number on every commit (installed by
  `./install.sh`).
- `/dp-update` or `python skills/update_check.py --update` pulls latest from
  GitHub if remote `VERSION` is newer.
- Refresh the MCP catalog from upstream with:
  `python3 scripts/sync_mcp_tools.py`

## Dokploy endpoints used

See [references/dokploy_api.md](references/dokploy_api.md) for schemas of all
endpoints invoked by this skill, including the 404 log fallback path and common
creation flows (project / application / postgres / git source / build type /
env / port / domain).

See [references/dokploy_mcp_tools.md](references/dokploy_mcp_tools.md) for the
generated MCP tool catalog, matching Dokploy's official MCP server.
