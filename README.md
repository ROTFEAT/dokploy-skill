# dokploy-skill

Claude Code skill + `/dp` / `/dp-update` slash commands for Dokploy. One entry
point for **deploy → poll → tail runtime/DB logs → diagnose** via the Dokploy
REST API. Works against local or remote Dokploy.

## Install

```bash
git clone https://github.com/ROTFEAT/dokploy-skill.git
cd dokploy-skill
./install.sh
```

Creates symlinks:
- `~/.claude/skills/dokploy-deploy → <repo>`
- `~/.claude/commands/dp.md`, `~/.claude/commands/dp-update.md`
- Caches skill path at `~/.claude/.dokploy-skill-path`
- Installs git pre-commit hook that auto-bumps `VERSION`'s patch number

## Usage

Inside Claude Code:
- `/dp` — full flow (deploy + poll + logs)
- `/dp-update` — pull latest, reinstall
- Natural language also triggers the skill: "部署到 dokploy", "dokploy 部署",
  "deploy to dokploy", "看 dokploy 日志"

Direct CLI:

```bash
./dp                            # trigger deploy + poll + tail app logs
./dp --only-status              # latest deployment status
./dp --only-logs --log-tail=200 # runtime logs (app container)
./dp --only-logs --search=ERROR # client-side grep, no 500 bug
./dp --db-logs --postgres=<id>  # postgres container logs
./dp --inspect                  # current application config
./dp --list                     # last 5 deployments
./dp --version                  # local skill version
./dp --check-update             # compare to GitHub HEAD VERSION
```

## Config

First match wins:
1. CLI args (`--url --key --app [--postgres]`)
2. Env vars: `DOKPLOY_URL`, `DOKPLOY_API_KEY`, `DOKPLOY_APP_ID`, `DOKPLOY_POSTGRES_ID`
3. `.env` in CWD with the same keys

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

## Dokploy endpoints used

See [REFERENCE.md](REFERENCE.md) for schemas of all endpoints invoked by this
skill — including creation flows (project / application / postgres / git
source / build type / env / port / domain).
