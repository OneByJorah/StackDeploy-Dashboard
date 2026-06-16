#!/usr/bin/env bash
set -euo pipefail
docker compose up -d
./scripts/init-honcho.sh
