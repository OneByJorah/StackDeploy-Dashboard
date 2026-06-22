#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source env
set -a
source "$REPO_ROOT/.env"
set +a

MODEL="${OLLAMA_MODEL:-qwen2.5:4b}"
HOST="${SERVER_IP:-localhost}"

echo "Pulling Ollama model: $MODEL"
curl -sf "http://$HOST:11434/api/pull" -d "{\"name\":\"$MODEL\"}" || {
  echo "WARN: Ollama may not be reachable yet. Run this again after 'docker compose up -d'."
  exit 1
}

echo "Verifying model list:"
curl -s "http://$HOST:11434/api/tags" | head -c 800
echo
echo "init-ollama: done"
