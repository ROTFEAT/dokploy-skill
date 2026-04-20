#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands"
ln -sfn "$REPO" "$HOME/.claude/skills/dokploy-deploy"
ln -sfn "$REPO/commands/dp.md" "$HOME/.claude/commands/dp.md"
chmod +x "$REPO/dp"
echo "installed:"
echo "  skill     → $HOME/.claude/skills/dokploy-deploy -> $REPO"
echo "  /dp       → $HOME/.claude/commands/dp.md"
echo "  binary    → $REPO/dp (chmod +x)"
echo
echo "usage:"
echo "  /dp                               # slash command in Claude Code"
echo "  'deploy to dokploy' / '部署到 dokploy'  # natural language triggers the skill"
echo "  $REPO/dp --help                   # direct CLI"
