#!/bin/sh
set -eu
REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PORT=${1:-8000}
HUGO_BIN=${HUGO_BIN:-hugo}
printf 'Website preview: http://127.0.0.1:%s/\nSave Markdown changes to refresh automatically. Press Control-C to stop.\n' "$PORT"
exec "$HUGO_BIN" server --source "$REPO_DIR/site" --destination "$REPO_DIR/build/preview-$PORT" --bind 127.0.0.1 --port "$PORT" --baseURL "http://127.0.0.1:$PORT/" --disableFastRender
