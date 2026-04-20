---
name: dokploy-deploy
description: |
  触发 Dokploy 应用部署、轮询部署状态、查看运行时日志。
  Deploy a Dokploy application via API, poll deployment status, then tail runtime logs.
  触发词：部署到 dokploy / dokploy 部署 / deploy to dokploy / 推到 dokploy / /dp
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - AskUserQuestion
---

# dokploy-deploy

一个统一的 Dokploy 部署工作流：**触发部署 → 轮询状态 → 拉取日志**。
全部通过 Dokploy REST API 完成，本地或远程 Dokploy 都能用。

## 工作流程（每次被调用时严格按顺序执行）

### 第 1 步：定位配置

**不要一上来就问用户要密钥。** 按以下顺序查找 `DOKPLOY_URL` / `DOKPLOY_API_KEY` / `DOKPLOY_APP_ID`：

1. **环境变量**（已经在 shell 里）：`echo "${DOKPLOY_URL:-}" "${DOKPLOY_API_KEY:+SET}" "${DOKPLOY_APP_ID:-}"`
2. **当前工作目录的 `.env`**：
   ```bash
   grep -E '^(DOKPLOY_URL|DOKPLOY_API_KEY|DOKPLOY_APP_ID)=' .env 2>/dev/null | sed -E 's/(API_KEY=).*/\1<set>/'
   ```
3. **用户记忆（MEMORY.md）**：如果有同项目的历史部署记录（app ID、URL），可以参考建议。

### 第 2 步：补齐缺失项

如果上一步拿到全部三项 → 跳过此步，直接进入第 3 步。

否则 **用 AskUserQuestion 一次问清楚缺失的值**（不要一项一项追问）：
- 缺 `DOKPLOY_URL` 就问 "Dokploy 地址（如 http://host:3000）"
- 缺 `DOKPLOY_API_KEY` 就问 "x-api-key 值"
- 缺 `DOKPLOY_APP_ID` 就问 "applicationId"

拿到后，再问一次：**是否保存到当前目录的 `.env`？**（默认不保存，避免误写）。
用户确认保存才 append 到 `.env`，且不覆盖已有同名键。

### 第 3 步：触发部署 + 轮询 + 日志（一条命令搞定）

```bash
~/.claude/skills/dokploy-deploy/dp
```

脚本会自动：
- 从 CLI 参数 / env / `.env` 解析配置（优先级降序）
- `POST /api/application.deploy`
- 每 3 秒 `GET /api/deployment.all` 轮询首条部署的 `status`
- 终态（`done` / `error`）时打印最近 80 行 `application.readLogs`
- `error` 时打印 `errorMessage` 与服务器端 `logPath`

**退出码：** 0=成功，1=部署失败，2=缺配置，3=轮询超时。

如果用户只想单独查状态或日志，用子命令：
- `dp --only-status` — 打印最新一次部署状态
- `dp --only-logs --tail=200` — 拉最近 N 行运行时日志（可加 `--search=xxx` / `--since=10m`）
- `dp --list` — 列出最近 5 次部署

### 第 4 步：结果解读

**status=done** → 告诉用户部署成功，并展示运行时日志尾部最值得注意的部分（错误/警告优先）。

**status=error** →
1. 打印 `errorMessage`
2. 判断错误类型（构建错误 / 拉镜像失败 / 端口冲突 / 磁盘满…）
3. 如果 `errorMessage` 被截断，提示 "完整构建日志在 Dokploy 宿主机 `<logPath>`；REST 无法读取，需 SSH 或 Dokploy UI"
4. 给出下一步建议（改 Dockerfile / 检查 secrets / 重试等）

**TIMEOUT (exit 3)** → 部署还在跑。告诉用户 `dp --only-status` 可以随时查。

## 不要做的事

- 不要在"直接能部署"的情况下还去问用户问题
- 不要把 API key 回显到输出里（用 `<set>` 之类代替）
- 不要在没拿到用户明确同意前往 `.env` 写敏感值
- 不要自己拼 curl — 直接调 `~/.claude/skills/dokploy-deploy/dp`

## 端点参考（已实测）

- `POST /api/application.deploy`  body: `{"applicationId": "..."}`
- `GET  /api/deployment.all?applicationId=...`  → 数组，首条 = 最新，字段 `deploymentId/status/createdAt/errorMessage/logPath/title`
- `GET  /api/application.readLogs?applicationId=...&tail=N&since=&search=`  → 容器 stdout 字符串
- 认证：header `x-api-key: <key>`
