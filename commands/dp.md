---
description: Dokploy 部署工作流（触发 → 轮询 → 看日志）
---

请调用 `dokploy-ops` skill 处理本次部署请求。严格按照 skill 里定义的工作流执行：

1. 从用户消息、env、`.env` 解析 `DOKPLOY_URL` / `DOKPLOY_API_KEY` / `DOKPLOY_APP_ID`
2. 缺什么就一次问齐，不要逐项追问
3. 优先执行 `~/.claude/skills/dokploy-ops/dp`（默认完整流程：触发 + 轮询 + 日志）
4. 解读 `status` / `errorMessage` / 运行时日志，只返回高信号内容

用户的额外参数: $ARGUMENTS
