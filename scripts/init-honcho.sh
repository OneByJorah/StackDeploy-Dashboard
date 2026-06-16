#!/usr/bin/env bash
set -euo pipefail
mkdir -p /home/<user>/docker/free-auto
cat > /home/<user>/docker/free-auto/.env <<EOF
SERVER_IP=REPLACE_WITH_YOUR_MESH_VPN_IP
HONCHO_TOKEN=<REPLACE_WITH_YOUR_HONCHO_TOKEN>
HONCHO_DB_PASSWORD=REPLACE_WITH_SECURE_PASSWORD
EOF
echo "init-honcho: wrote /home/<user>/docker/free-auto/.env"
