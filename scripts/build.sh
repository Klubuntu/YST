#!/usr/bin/env bash
# Build the single-file executable for the current platform.
#
#   ./scripts/build.sh          -> dist/YST.exe on Windows, dist/yst elsewhere
#
# PyInstaller only produces a binary for the platform it runs on, so use
# scripts/build-linux.sh or scripts/build-macos.sh to cross-build.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

python -m pip install -r requirements.txt pyinstaller

if [ "$(uname -s)" = "Darwin" ]; then
    name=yst
else
    name=YST
fi

# A .spec build is already onefile, and PyInstaller rejects --onefile and
# --name there; the name comes from YST_BINARY_NAME instead.
YST_BINARY_NAME="$name" python -m PyInstaller build/YST.spec \
    --distpath dist \
    --workpath build/yst

ls -l "dist/$name"
sha256sum "dist/$name" | tee "dist/$name.sha256"
echo "Built dist/$name for $(uname -s -m)"