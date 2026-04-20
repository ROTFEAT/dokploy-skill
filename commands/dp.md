---
description: Dokploy 部署工作流（触发 → 轮询 → 看日志）
---

请调用 `dokploy-deploy` skill 处理本次部署请求。严格按照 skill 里定义的四步工作流执行：

1. 从 env / `.env` / MEMORY 解析 `DOKPLOY_URL` / `DOKPLOY_API_KEY` / `DOKPLOY_APP_ID`
2. 缺什么就用 AskUserQuestion 一次问齐
3. 执行 `~/.claude/skills/dokploy-deploy/dp`（默认完整流程：触发 + 轮询 + 日志）
4. 解读 status / errorMessage / 运行时日志

用户的额外参数: $ARGUMENTS
