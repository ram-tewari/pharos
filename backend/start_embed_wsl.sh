#!/usr/bin/env bash
# Start the standalone Pharos embed server in WSL.
# Run from Windows: wsl -e bash start_embed_wsl.sh
# Or from inside WSL: bash /mnt/c/Users/rooma/PycharmProjects/pharos/backend/start_embed_wsl.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV="$SCRIPT_DIR/.wsl-venv"
if [ ! -f "$VENV/bin/activate" ]; then
    echo "ERROR: WSL venv not found at $VENV"
    echo "Run: python3 -m venv .wsl-venv && source .wsl-venv/bin/activate && pip install -r requirements-embed.txt"
    exit 1
fi

source "$VENV/bin/activate"

# Reuse Windows HuggingFace model cache (avoids 500MB re-download)
export HF_HOME="/mnt/c/Users/rooma/.cache/huggingface"
export TRANSFORMERS_CACHE="$HF_HOME"

echo "Starting Pharos Embed Server (WSL) on port ${EDGE_EMBED_PORT:-8001}..."
exec python embed_server.py
