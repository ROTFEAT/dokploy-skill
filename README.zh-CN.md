# dokploy-skill

[English](README.md) | [简体中文](README.zh-CN.md)

适用于 Claude Code 和 Codex 的 Dokploy 技能包。通过 Dokploy REST API 提供统一入口，覆盖**部署 -> 轮询状态 -> 查看运行时或数据库日志 -> 故障诊断**，并附带与 Dokploy 官方 MCP 工具集一致的生成式工具目录。支持本地或远程 Dokploy 实例。

## 安装

```bash
git clone https://github.com/ROTFEAT/dokploy-skill.git
cd dokploy-skill
./install.sh
```

默认安装会更新 Claude 和 Codex 的链接。也可以使用以下选项：

```bash
./install.sh --claude-only
./install.sh --codex-only
```

安装脚本会创建以下符号链接和文件：

- `~/.claude/skills/dokploy-ops -> <repo>`
- `~/.claude/skills/dokploy-deploy -> <repo>`（旧版别名）
- `~/.claude/commands/dp.md`、`~/.claude/commands/dp-update.md`
- `~/.codex/skills/dokploy-ops -> <repo>`
- 将技能路径缓存到 `~/.claude/.dokploy-skill-path`
- 安装 Git pre-commit hook，每次提交时自动递增 `VERSION` 的补丁版本号

## 使用

在 Claude Code 中：

- `/dp` — 完整流程（部署、轮询状态并查看日志）
- `/dp-update` — 拉取最新版本并重新安装
- 也可以用自然语言触发技能，例如“部署到 dokploy”“dokploy 部署”“deploy to dokploy”“看 dokploy 日志”

在 Codex 中：

- 提及 `dokploy-ops`，或要求在 Dokploy 上部署、检查日志
- 安装程序会将仓库根目录链接到 `~/.codex/skills/dokploy-ops`

配置应用源时默认使用 GitHub provider（通过 `github-githubProviders` 查找已配置的 GitHub App，并使用 `application-saveGithubProvider` 保存）。如果 GitHub 不可用，技能会询问一次，然后可以改用通用 Git（`application-saveGitProvider`）或预构建 Docker 镜像（`application-saveDockerProvider`）。详见 [references/dokploy_api.md](references/dokploy_api.md)。

直接使用 CLI：

```bash
./dp                            # 触发部署、轮询状态并查看应用日志
python3 scripts/dokploy_api.py  # 不使用封装脚本，执行相同逻辑
./dp --only-status              # 查看最近一次部署状态
./dp --only-logs --log-tail=200 # 查看运行时日志（应用容器）
./dp --only-logs --search=ERROR # 客户端筛选日志，不会触发服务端 500 问题
./dp --db-logs --postgres=<id>  # 查看 PostgreSQL 容器日志
./dp --inspect                  # 查看当前应用配置
./dp --list                     # 列出最近 5 次部署
./dp --mcp-tools                # 查看 MCP 工具分类摘要
./dp --mcp-tools --mcp-tag application
./dp --mcp-search deploy
./dp --mcp-describe application-one
./dp --mcp-call project-all
./dp --mcp-call application-one --json '{"applicationId":"app_x"}'
./dp --mcp-call application-delete --json '{"applicationId":"app_x"}' --yes
./dp --api-call /project.all --api-method GET
./dp --version                  # 查看本地技能版本
./dp --check-update             # 与 GitHub HEAD 中的 VERSION 比较
```

MCP 工具目录由 Dokploy 官方 MCP OpenAPI 输入生成，目前包含 48 个分类、524 个工具。简明列表见 `references/dokploy_mcp_tools.md`；精确参数结构和注解见 `references/dokploy_mcp_tools.json`。

## 配置

按以下顺序使用第一个匹配到的配置：

1. CLI 参数（`--url --key --app [--postgres]`）
2. 环境变量：`DOKPLOY_URL`、`DOKPLOY_API_KEY`、`DOKPLOY_APP_ID`、`DOKPLOY_POSTGRES_ID`
3. 当前工作目录中的环境文件（使用找到的第一个文件）：
   - 设置 `DOKPLOY_ENV=<env>` 时使用 `.dokploy.<env>.env`，每个部署环境使用单独文件（例如 `.dokploy.dev.env`、`.dokploy.production.env`）
   - 单环境项目可使用 `.env`，键名相同

每次部署成功后，技能会将完整部署上下文（`DOKPLOY_URL`、`DOKPLOY_APP_ID`、`DOKPLOY_APP_NAME`、`DOKPLOY_APP_PATH`，可选的 `DOKPLOY_SERVER_ID` / `DOKPLOY_SERVER_IP`、`DOKPLOY_POSTGRES_ID`）保存到当前环境对应的环境文件；文件不存在时会创建。之后部署只需运行 `DOKPLOY_ENV=<env> ./dp`。只有在用户明确批准后才会写入 API key。

通用 MCP/API 调用路径也支持官方 MCP 风格的环境变量：

- `DOKPLOY_CUSTOM_HEADERS` — 额外上游请求头的 JSON 对象
- `DOKPLOY_ENABLED_TAGS` — 以逗号分隔的分类筛选项
- `DOKPLOY_TIMEOUT` — 请求超时时间（毫秒）
- `DOKPLOY_RETRY_ATTEMPTS`、`DOKPLOY_RETRY_DELAY`
- `DOKPLOY_REDACT_ENV`、`DOKPLOY_REDACT_FIELDS`

如果从目标工作区之外启动辅助脚本，请传入：

```bash
python3 scripts/dokploy_api.py --env-file /absolute/path/to/.env
```

## 退出码

| 代码 | 含义 |
|------|------|
| 0    | 完成 / 成功 |
| 1    | 部署错误或 HTTP 错误 |
| 2    | 缺少配置 |
| 3    | 轮询超时 |

## 已知问题与注意事项

- `application.readLogs?search=...` 在没有匹配项时会返回 **HTTP 500**（服务端执行 `docker logs | grep` 后退出码非零）。因此 `dp --search=` 会在客户端筛选日志。
- 某些自托管 Dokploy 版本可以找到运行时容器，但调用 `application.readLogs` / `postgres.readLogs` 会返回 **HTTP 404**。内置辅助脚本会回退到 `docker.*` 容器发现接口和 `/docker-container-logs` WebSocket，并使用相同的 `x-api-key`。
- Swarm 的**入口模式端口发布**（`port.create`）通常可以接受 TCP 请求，但 HTTP 请求会超时。建议通过 `domain.create` 配合通配符 DNS（`<ip>.sslip.io`、`<ip>.nip.io`、`<dash-ip>.traefik.me`）使用 Traefik 主机路由。
- `python foo.py` 命令未带 `-u` 时，`print()` 输出可能会被缓冲；`logging.*`（stderr）仍可见。因此 `readLogs` 中看似卡住的启动过程不一定真的卡住。
- 在某些机器上，Tailscale MagicDNS 会劫持 sslip.io / nip.io / traefik.me 主机名并返回 `198.19.x.x`。可以使用 `curl -H "Host: ..."` 或 `--resolve host:80:<ip>` 进行测试。

## 版本与自动更新

- `./install.sh` 安装的 pre-commit hook 会在每次提交时递增 `VERSION` 的补丁版本号。
- `/dp-update` 或 `python skills/update_check.py --update` 会在 GitHub 远端 `VERSION` 更新时拉取最新版本。
- 使用 `python3 scripts/sync_mcp_tools.py` 从上游刷新 MCP 工具目录。

## 使用的 Dokploy 接口

所有由此技能调用的接口结构（包括日志 404 回退方案，以及 project / application / postgres / git source / build type / env / port / domain 等常见创建流程），请参阅 [references/dokploy_api.md](references/dokploy_api.md)。

[references/dokploy_mcp_tools.md](references/dokploy_mcp_tools.md) 提供与 Dokploy 官方 MCP 服务相匹配的生成式工具目录。
