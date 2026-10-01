#!/usr/bin/env bash
# Build the Linux executable from any host, using Docker.
#
#   ./scripts/build-linux.sh            -> dist/yst.linux
#
# PyInstaller cannot cross-compile, so the build runs inside a Linux container.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image="${PYTHON_IMAGE:-python:3.12-slim}"

docker run --rm \
    -v "$root:/src" \
    -w /src \
    -e PYTHONDONTWRITEBYTECODE=1 \
    -e YST_BINARY_NAME=yst \
    "$image" \
    bash -c '
        set -euo pipefail
        apt-get update -qq && apt-get install -y -qq --no-install-recommends binutils >/dev/null
        pip install --quiet -r requirements.txt pyinstaller
        python -m PyInstaller build/YST.spec \
            --distpath dist --workpath build/yst-linux
        mv dist/yst dist/yst.linux
        sha256sum dist/yst.linux > dist/yst.linux.sha256
    '

ls -l dist/yst.linux
cat dist/yst.linux.sha256
echo "Built dist/yst.linux — it needs a recent glibc and does not run on macOS"