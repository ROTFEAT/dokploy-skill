---
description: 更新 dokploy-skill 到最新版本
---

更新 dokploy-skill 并重新安装命令/钩子。

## 步骤

1. 定位 skill 目录（优先缓存路径，其次默认路径）：
   ```bash
   DP_DIR=$(cat ~/.claude/.dokploy-skill-path 2>/dev/null || echo "$HOME/.claude/skills/dokploy-ops")
   ```

2. 记录旧版本：
   ```bash
   OLD=$(cat "$DP_DIR/VERSION" 2>/dev/null || echo unknown)
   echo "current: v$OLD"
   ```

3. 拉取更新：
   ```bash
   cd "$DP_DIR" && git pull --ff-only origin main
   ```
   若因本地改动失败，提示：
   ```bash
   cd "$DP_DIR" && git stash && git pull --ff-only origin main && git stash pop
   ```

4. 重新运行安装（刷新 Claude/Codex 软链接与钩子）：
   ```bash
   cd "$DP_DIR" && ./install.sh 2>&1 | tail -6
   ```

5. 对比版本并汇报：
   ```bash
   NEW=$(cat "$DP_DIR/VERSION")
   echo "updated: v$OLD → v$NEW"
   ```

6. 如果版本没变，报告"已是最新"。
