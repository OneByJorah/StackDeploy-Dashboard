#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cat > "$REPO_ROOT/.env" <<EOF
SERVER_IP=REPLACE_WITH_YOUR_MESH_VPN_IP

# Local LLM options (only used if enabled in docker-compose.yml)
# OLLAMA_MODEL=qwen2.5:4b
# OLLAMA_NUM_CPU=4
# OLLAMA_MAX_LOADED_MODELS=1
# OLLAMA_NUM_PARALLEL=2
# MODEL_PATH=/models/Qwen3.5-9B-Coder-Q4_K_M.gguf
# CTX_SIZE=65536

# Services
HONCHO_TOKEN=<REPLACE_WITH_YOUR_HONCHO_TOKEN>
HONCHO_DB_PASSWORD=REPLACE_WITH_SECURE_PASSWORD
EOF
echo "init-honcho: wrote $REPO_ROOT/.env"
