#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd -P)"

INSTALL_CLAUDE=1
INSTALL_CODEX=1

for arg in "$@"; do
    case "$arg" in
        --claude-only)
            INSTALL_CODEX=0
            ;;
        --codex-only)
            INSTALL_CLAUDE=0
            ;;
        *)
            echo "unknown flag: $arg" >&2
            echo "usage: ./install.sh [--claude-only|--codex-only]" >&2
            exit 2
            ;;
    esac
done

if [ "$INSTALL_CLAUDE" -eq 1 ] && [ "$INSTALL_CODEX" -eq 1 ]; then
    MODE_LABEL="claude+codex"
elif [ "$INSTALL_CLAUDE" -eq 1 ]; then
    MODE_LABEL="claude"
else
    MODE_LABEL="codex"
fi

ensure_dir_link() {
    local link_path="$1"
    local target_path="$2"

    if [ -e "$link_path" ] && [ ! -L "$link_path" ]; then
        local resolved_existing
        resolved_existing="$(cd "$link_path" && pwd -P 2>/dev/null || true)"
        if [ "$resolved_existing" != "$target_path" ]; then
            echo "refusing to replace non-symlink path: $link_path" >&2
            exit 1
        fi
    fi

    rm -rf "$link_path"
    ln -s "$target_path" "$link_path"
}

if [ "$INSTALL_CLAUDE" -eq 1 ]; then
    mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands"
    ensure_dir_link "$HOME/.claude/skills/dokploy-ops" "$REPO"
    ensure_dir_link "$HOME/.claude/skills/dokploy-deploy" "$REPO"
    ln -sfn "$REPO/commands/dp.md" "$HOME/.claude/commands/dp.md"
    ln -sfn "$REPO/commands/dp-update.md" "$HOME/.claude/commands/dp-update.md"
    echo "$REPO" > "$HOME/.claude/.dokploy-skill-path"
fi

if [ "$INSTALL_CODEX" -eq 1 ]; then
    mkdir -p "$HOME/.codex/skills"
    ensure_dir_link "$HOME/.codex/skills/dokploy-ops" "$REPO"
fi

chmod +x "$REPO/dp" "$REPO/hooks/pre-commit" "$REPO/scripts/dokploy_api.py" "$REPO/scripts/sync_mcp_tools.py" 2>/dev/null || true

# install git pre-commit hook (auto-bump VERSION patch)
if [ -d "$REPO/.git" ]; then
    cp "$REPO/hooks/pre-commit" "$REPO/.git/hooks/pre-commit"
    chmod +x "$REPO/.git/hooks/pre-commit"
    HOOK_STATUS="✓ pre-commit hook installed"
else
    HOOK_STATUS="- skipped (not a git checkout)"
fi

VERSION=$(cat "$REPO/VERSION" 2>/dev/null || echo unknown)

echo "installed dokploy-skill v$VERSION ($MODE_LABEL)"
if [ "$INSTALL_CLAUDE" -eq 1 ]; then
    echo "  claude skill  → $HOME/.claude/skills/dokploy-ops -> $REPO"
    echo "  claude alias  → $HOME/.claude/skills/dokploy-deploy -> $REPO"
    echo "  /dp           → $HOME/.claude/commands/dp.md"
    echo "  /dp-update    → $HOME/.claude/commands/dp-update.md"
    echo "  path cache    → $HOME/.claude/.dokploy-skill-path"
fi
if [ "$INSTALL_CODEX" -eq 1 ]; then
    echo "  codex skill   → $HOME/.codex/skills/dokploy-ops -> $REPO"
fi
echo "  git hook      $HOOK_STATUS"
echo
echo "usage:"
if [ "$INSTALL_CLAUDE" -eq 1 ]; then
    echo "  /dp                              # slash command"
    echo "  /dp-update                       # pull latest + reinstall"
fi
echo "  '部署到 dokploy' / 'deploy to dokploy'  # natural-language trigger"
echo "  $REPO/dp --help                  # direct CLI wrapper"
echo "  python3 $REPO/scripts/dokploy_api.py --help"
