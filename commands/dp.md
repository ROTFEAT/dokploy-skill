---
description: Dokploy 部署工作流（触发 → 轮询 → 看日志）
---

请调用 `dokploy-ops` skill 处理本次 Dokploy 请求。严格按照 skill 里定义的工作流执行：

1. 从用户消息、env、`.env` 解析 `DOKPLOY_URL` / `DOKPLOY_API_KEY` / `DOKPLOY_APP_ID`
2. 缺什么就一次问齐，不要逐项追问
3. 优先执行 `~/.claude/skills/dokploy-ops/dp`（默认完整流程：触发 + 轮询 + 日志）
4. 如果请求不是部署/日志高频路径，使用 `--mcp-tools` / `--mcp-search` / `--mcp-describe` / `--mcp-call` 调用生成的 Dokploy MCP 工具目录
5. 对 delete/remove 等 destructive 工具，先展示工具名和 JSON body 并获得用户明确确认，再传 `--yes`
6. 解读 `status` / `errorMessage` / API 响应，只返回高信号内容

用户的额外参数: $ARGUMENTS
