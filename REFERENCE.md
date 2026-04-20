# Dokploy REST API — 实测端点参考

本文件收录本 skill 实际调用过、验证过的端点。字段名基于 Dokploy 服务端返回的 `zodError`。

## 认证

所有端点带 `x-api-key: <your_key>`。密钥在 Dokploy UI → Settings → API Keys 生成；也可直接从 Dokploy 内部数据库的 `apikey` 表取出（仅限宿主机管理员）。

## 项目与环境

### `POST /api/project.create`
```json
{"name": "smartmoney", "description": "Polymarket whale tracker"}
```
返回 `{project:{projectId,...}, environment:{environmentId, name:"production", isDefault:true, ...}}`。每个项目自动带一个 `production` 环境。

### `GET /api/project.all`
返回所有项目（含嵌套 `environments[0].applications / postgres / mysql / compose`），用来盘点已有资源。

## 应用

### `POST /api/application.create`
```json
{"name": "...", "description": "...", "environmentId": "..."}
```
返回 `{applicationId, appName, sourceType:"github", buildType:"nixpacks", ...}`。默认 `sourceType=github` 但 `githubId=null`——需要下一步 `saveGitProvider` 指定通用 Git URL。

### `POST /api/application.saveGitProvider` — 通用 Git 源
```json
{
  "applicationId": "...",
  "customGitUrl": "https://<PAT>@github.com/owner/repo.git",
  "customGitBranch": "main",
  "customGitBuildPath": "/",
  "watchPaths": []
}
```
**私仓**：把 PAT 塞到 URL 的 userinfo 部分（`https://ghp_xxx@github.com/...`），Dokploy 会用它 git clone。
**SSH**：用 `customGitSSHKeyId` 指向 Dokploy 里导入的私钥（需先 `sshKey.create`）。

### `POST /api/application.saveBuildType`
```json
{
  "applicationId": "...",
  "buildType": "dockerfile",
  "dockerfile": "Dockerfile",
  "dockerContextPath": ".",
  "dockerBuildStage": "",
  "herokuVersion": "24",
  "railpackVersion": "0.15.4"
}
```
`buildType` 可选：`dockerfile` / `nixpacks`（默认）/ `heroku_buildpacks` / `paketo_buildpacks` / `railpack`。

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
`env` 是 KEY=VAL 换行串。`createEnvFile=true` 时 Dokploy 会在容器里生成 `.env`（方便 dotenv 类库读取）。

### `POST /api/application.deploy`
```json
{"applicationId": "..."}
```
立即返回（异步），部署进度通过 `deployment.all` 轮询。

### `GET /api/application.one?applicationId=…`
完整应用配置。排查配置错误时先看这个。

### `GET /api/application.readLogs?applicationId=…&tail=N&since=10m`
返回容器 stdout 字符串（**不是 JSON**）。
**⚠️ 不要加 `search=`**：底层是 `docker logs | grep`，无匹配时 grep 退出码 1 被当作 500 抛出。客户端本地 grep 更稳。

### `POST /api/application.update`
局部字段更新，只需传 `applicationId` 和要改的字段。

## Postgres

### `POST /api/postgres.create`
```json
{
  "name": "smartmoney-db",
  "databaseName": "smartmoney",
  "databaseUser": "smartmoney",
  "databasePassword": "<generated>",
  "environmentId": "...",
  "dockerImage": "postgres:15"
}
```
返回含 `appName: "postgres-<slug>-<rand>"`——**这是容器内 DNS 主机名**，同项目其他应用连它时用 `postgresql://user:pw@<appName>:5432/db`。

### `POST /api/postgres.deploy`
```json
{"postgresId": "..."}
```
异步，等几秒 Postgres 容器就绪。

### `GET /api/postgres.readLogs?postgresId=…&tail=N`
Postgres 容器日志。同样**不要加 `search=`**。

## 端口与域名（两种暴露方式）

### 方案 A：`POST /api/port.create` — Swarm ingress 端口发布
```json
{"applicationId":"…","publishedPort":1888,"targetPort":8080,"protocol":"tcp"}
```
**注意**：实测 Swarm ingress routing mesh 常常不通（TCP 建连成功但 HTTP 超时），具体机器/Docker 版本相关。生产首选方案 B。

### 方案 B：`POST /api/domain.create` — Traefik Host 路由（推荐）
```json
{
  "applicationId": "...",
  "host": "152.53.53.84.sslip.io",
  "port": 8080,
  "path": "/",
  "https": false,
  "certificateType": "none",
  "domainType": "application"
}
```
- `host` 可填真实域名，或用公共通配 DNS：
  - `<ip>.sslip.io` / `<ip>.nip.io`
  - `<dash-ip>.traefik.me` 或 `<ip>.traefik.me`
- Traefik 监听 80/443，按 `Host` header 匹配路由到容器 `port`。
- 开 HTTPS：`"certificateType":"letsencrypt"`（域名必须真实解析到 Dokploy 主机）。

### `POST /api/domain.delete`
```json
{"domainId": "..."}
```

## 部署历史

### `GET /api/deployment.all?applicationId=…`
最新在前的数组。每项含 `deploymentId / status / createdAt / errorMessage / logPath / title`。
- `status` 取值：`running` / `done` / `error`
- `logPath` 是 Dokploy 宿主机本地路径（REST 读不到，要 SSH 或 UI）

## Schema 探测技巧

所有 tRPC endpoint 在收到缺字段的请求时返回 HTTP 400 + `zodError.fieldErrors`，列出全部必填字段和期望类型。探新端点的速战速决：

```bash
curl -sS -X POST -H "x-api-key: $KEY" -H "content-type: application/json" \
  -d '{}' "$URL/api/<endpoint>"
```

看 `fieldErrors` 就能拼出最小 body。`zodError: null` + HTTP 404 表示端点不存在。

## 已验证端点清单（v1.1.0）

部署/日志：`application.deploy`、`application.readLogs`、`application.one`、`deployment.all`、`postgres.readLogs`、`postgres.deploy`

资源：`project.create`、`project.all`、`application.create`、`application.saveGitProvider`、`application.saveBuildType`、`application.saveEnvironment`、`application.update`、`postgres.create`、`port.create`、`domain.create`、`domain.delete`
