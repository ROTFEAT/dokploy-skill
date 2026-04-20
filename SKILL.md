---
name: dokploy-deploy
description: |
  触发 Dokploy 应用部署、轮询部署状态、查看运行时和数据库日志、排查部署问题。
  Deploy a Dokploy application via API, poll deployment status, tail runtime/DB logs, diagnose port routing.
  触发词：部署到 dokploy / dokploy 部署 / deploy to dokploy / 推到 dokploy / 看 dokploy 日志 / /dp
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - AskUserQuestion
---

# dokploy-deploy

Dokploy 工作流通用入口：**部署 / 查日志 / 看状态 / 排障**。全部走 REST API，本地或远程 Dokploy 都能用。

## 工作流程

### 第 1 步：定位配置

**不要一上来就问用户要密钥。** 按以下顺序查找：

1. 环境变量：`DOKPLOY_URL` / `DOKPLOY_API_KEY` / `DOKPLOY_APP_ID`（可选 `DOKPLOY_POSTGRES_ID`）
2. 当前工作目录的 `.env`
3. 用户记忆（MEMORY.md）中同项目的历史记录

### 第 2 步：补齐缺失项

如果三项齐全 → 直接第 3 步。否则用 `AskUserQuestion` 一次问齐（不要一项一项追问）：
- 缺 `DOKPLOY_URL` → "Dokploy 地址（如 http://host:3000）"
- 缺 `DOKPLOY_API_KEY` → "x-api-key 值"
- 缺 `DOKPLOY_APP_ID` → "applicationId"

拿到后再问：**是否保存到当前目录的 `.env`？**（默认不保存，避免误写）。用户确认后 append，不覆盖已有键。

### 第 3 步：调用 `dp`

```bash
~/.claude/skills/dokploy-deploy/dp
```

完整流程：`POST /api/application.deploy` → 每 3 秒轮询 `deployment.all` → 终态时打印 `readLogs` 最后 80 行。

**子命令**（按需选用，不要自己拼 curl）：

| 子命令 | 作用 |
|---|---|
| `dp` | 触发部署 + 轮询 + 打印运行时日志 |
| `dp --only-status` | 打印最新一次部署状态 |
| `dp --only-logs --log-tail=200` | 拉应用容器运行时日志；可加 `--search=ERROR`（客户端 grep，绕开服务端 500） |
| `dp --db-logs --postgres=<id>` | 拉 Postgres 容器日志 |
| `dp --inspect` | 打印应用当前配置（git 源、build type、env、状态） |
| `dp --list` | 最近 5 次部署 |
| `dp --version` / `dp --check-update` | 本地版本 / 对比远端 VERSION |

**退出码：** 0=成功，1=部署失败/HTTP 错误，2=缺配置，3=轮询超时。

### 第 4 步：结果解读

**status=done** → 告诉用户部署成功，只挑日志里真正的 error/warn 展示，不要粘全量日志。

**status=error** →
1. 打印 `errorMessage`
2. 判断错误类型：构建错误 / 拉镜像失败 / 端口冲突 / 磁盘满 …
3. `errorMessage` 若被截断，提示完整构建日志在 Dokploy 宿主机 `<logPath>`（REST 拿不到，需 SSH 或 UI）
4. 给出下一步建议

**TIMEOUT (exit 3)** → 部署仍在跑，提示 `dp --only-status` 可随时查。

## 已知坑位

- **`readLogs?search=...` 无匹配时返回 HTTP 500**（底层 `docker logs | grep` 非零退出）。`dp --search=` 已改为客户端 grep 避开此坑，不要直接在 URL 里塞 `search=`。
- **Swarm ingress 端口映射常常不通**：`port.create` 创建了 `publishedPort:targetPort` 但外部 TCP 建连后 HTTP 超时。优先用 `domain.create` 挂 Traefik Host 路由（可用 `<ip>.sslip.io` / `<ip>.nip.io` / `<ip>-dashed.traefik.me` 三选一的公共通配 DNS，无需自建解析）。
- **`python entrypoint.py` 不带 `-u`**：`print()` 走 stdout 缓冲区不会出现在 `readLogs`；`logging.*` 走 stderr 立即可见。排查"启动卡住"先看是不是 buffering 假象。
- **sslip.io / traefik.me 域名在 Tailscale MagicDNS 下会被劫持**返回 `198.19.x.x`。本机测试用 `curl --resolve host:80:<ip>` 或 `curl -H "Host: <host>" http://<ip>/`。
- **400 响应里的 `zodError`** 会列出全部必填字段（探 schema 最快的路径）。
- **500 响应的 `message` 字段有时会泄漏 docker 容器 ID** — 出问题可拿来追容器。

## 端点参考

部署与日志：
- `POST /api/application.deploy` `{applicationId}`
- `GET  /api/deployment.all?applicationId=…` → 数组，首条最新
- `GET  /api/application.readLogs?applicationId=…&tail=&since=` → 容器 stdout 字符串（不要加 `search=`）
- `GET  /api/application.one?applicationId=…` → 完整应用配置
- `GET  /api/postgres.readLogs?postgresId=…&tail=` → Postgres 容器日志

资源管理（`REFERENCE.md` 有完整 schema）：
- `POST /api/project.create` `{name}`
- `POST /api/application.create` `{name, environmentId}`
- `POST /api/postgres.create` `{name, databaseName, databaseUser, databasePassword, environmentId}`
- `POST /api/postgres.deploy` `{postgresId}`
- `POST /api/application.saveGitProvider` `{applicationId, customGitUrl, customGitBranch, customGitBuildPath, watchPaths}`
- `POST /api/application.saveBuildType` `{applicationId, buildType:"dockerfile", dockerfile, dockerContextPath, ...}`
- `POST /api/application.saveEnvironment` `{applicationId, env, buildArgs, buildSecrets, createEnvFile}`
- `POST /api/port.create` `{applicationId, publishedPort, targetPort, protocol}`
- `POST /api/domain.create` `{applicationId, host, port, path, https, certificateType, domainType:"application"}`

认证：`x-api-key: <key>`。

## 不要做的事

- 不要在配置齐全时追问用户。
- 不要把 API key 回显到输出（用 `<set>` 或 `***` 代替）。
- 不要在没拿到用户确认前往 `.env` 写敏感值。
- 不要自己拼 curl/python — 先看 `dp` 是否已经有对应子命令。

## 版本与更新

- 本地版本：`dp --version`
- 对比远端：`dp --check-update`
- 拉取更新：`/dp-update` 或 `python ~/.claude/skills/dokploy-deploy/skills/update_check.py --update`
