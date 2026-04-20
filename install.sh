#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd -P)"

mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands"

# skill dir — only (re)create link if it doesn't already resolve to $REPO,
# otherwise `ln -sfn` on a symlink-to-dir produces a self-referencing loop.
SKILL_LINK="$HOME/.claude/skills/dokploy-deploy"
if [ "$(readlink -f "$SKILL_LINK" 2>/dev/null)" != "$REPO" ]; then
    rm -rf "$SKILL_LINK"
    ln -s "$REPO" "$SKILL_LINK"
fi
ln -sfn "$REPO/commands/dp.md"        "$HOME/.claude/commands/dp.md"
ln -sfn "$REPO/commands/dp-update.md" "$HOME/.claude/commands/dp-update.md"

# cache install path so /dp-update can find the repo
echo "$REPO" > "$HOME/.claude/.dokploy-skill-path"

chmod +x "$REPO/dp" "$REPO/hooks/pre-commit" 2>/dev/null || true

# install git pre-commit hook (auto-bump VERSION patch)
if [ -d "$REPO/.git" ]; then
    cp "$REPO/hooks/pre-commit" "$REPO/.git/hooks/pre-commit"
    chmod +x "$REPO/.git/hooks/pre-commit"
    HOOK_STATUS="✓ pre-commit hook installed"
else
    HOOK_STATUS="- skipped (not a git checkout)"
fi

VERSION=$(cat "$REPO/VERSION" 2>/dev/null || echo unknown)

echo "installed dokploy-skill v$VERSION"
echo "  skill         → $HOME/.claude/skills/dokploy-deploy -> $REPO"
echo "  /dp           → $HOME/.claude/commands/dp.md"
echo "  /dp-update    → $HOME/.claude/commands/dp-update.md"
echo "  path cache    → $HOME/.claude/.dokploy-skill-path"
echo "  git hook      $HOOK_STATUS"
echo
echo "usage:"
echo "  /dp                              # slash command"
echo "  /dp-update                       # pull latest + reinstall"
echo "  '部署到 dokploy' / 'deploy to dokploy'  # natural-language trigger"
echo "  $REPO/dp --help                  # direct CLI"
