#!/usr/bin/env bash
# Build the macOS executable from any host, using Docker.
#
#   ./scripts/build-macos.sh            -> dist/yst.macos
#
# PyInstaller cannot cross-compile, so the build runs inside a macOS container.
# A Linux Docker daemon cannot run the macOS image: build this one on a Mac, or
# let .github/workflows/release.yml build it on macos-latest.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$(uname -s)" != "Darwin" ]; then
    echo "The macOS image needs a macOS Docker host; on Linux use CI or a Mac." >&2
    exit 1
fi

docker run --rm \
    -v "$root:/src" \
    -w /src \
    -e PYTHONDONTWRITEBYTECODE=1 \
    ghcr.io/macpaw/macos-ci:latest \
    bash -c '
        set -euo pipefail
        pip install --quiet -r requirements.txt pyinstaller
        python -m PyInstaller build/YST.spec \
            --distpath dist --workpath build/yst-macos --onefile --name yst
        mv dist/yst dist/yst.macos
        sha256sum dist/yst.macos > dist/yst.macos.sha256
    '

ls -l dist/yst.macos
cat dist/yst.macos.sha256
echo "Built dist/yst.macos — the binary is unsigned, so Gatekeeper asks on first run"