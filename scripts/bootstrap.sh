#!/usr/bin/env bash
set -euo pipefail

echo "=== StackDeploy Bootstrap ==="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose v2 not found. Please install Docker Compose v2."
    exit 1
fi

# Check .env
if [[ ! -f .env ]]; then
    if [[ -f .env.example ]]; then
        cp .env.example .env
        echo "📋 Created .env from .env.example"
        echo "⚠️  Please edit .env with your passwords before continuing!"
        echo "   Required: HONCHO_DB_PASSWORD"
        echo "   Optional: CAMOFOX_API_KEY, CAMOFOX_ADMIN_KEY, OBSIDIAN_VAULT_PATH"
        exit 1
    else
        echo "❌ .env.example not found"
        exit 1
    fi
fi

echo "🔧 Pulling images..."
docker compose pull

echo "🚀 Starting services..."
docker compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🏥 Running health check..."
./scripts/healthcheck.sh localhost

echo ""
echo "✅ StackDeploy is ready!"
echo ""
echo "Access points:"
echo "  Portainer (Admin):  http://localhost:9000"
echo "  SearXNG:            http://localhost:8080"
echo "  Camofox:            http://localhost:9377"
echo "  CloakBrowser:       http://localhost:9222"
echo "  Obsidian:           http://localhost:8083"
echo "  Qdrant:             http://localhost:6333"
echo "  Honcho API:         http://localhost:8081"