#!/bin/bash
# sync.sh — Update all upstream shallow clones and rebuild framework
# Usage: ./sync.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_DIR="$SCRIPT_DIR/upstream"

echo "=== Updating upstream repositories ==="

cd "$UPSTREAM_DIR"

# Array of repo directories
repos=(
    "agcp-spec"
    "ai-governance-framework"
    "eu-ai-act-crosswalk"
    "awesome-agent-governance"
    "awesome-eu-ai-act"
    "awesome-ai-security"
)

for repo in "${repos[@]}"; do
    if [[ -d "$repo/.git" ]]; then
        echo "Updating $repo..."
        cd "$repo"
        git fetch --depth 1 origin
        git reset --hard origin/HEAD
        cd ..
    else
        echo "WARNING: $repo not found, skipping"
    fi
done

echo ""
echo "=== Rebuilding framework from upstream ==="
cd "$SCRIPT_DIR"
./rebuild-framework.sh

echo ""
echo "=== Sync complete ==="