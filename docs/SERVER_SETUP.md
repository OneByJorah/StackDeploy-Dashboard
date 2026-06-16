# Server Setup

## Prerequisites

- Docker + Docker Compose v2+
- NVIDIA GPU + NVIDIA Container Toolkit
- Mesh-VPN installed

## Install

```bash
git clone https://github.com/<your-org>/free-auto-project.git
cd free-auto-project
cp .env.example .env
# Edit .env: set SERVER_IP, MODEL_PATH, HONCHO_DB_PASSWORD, HONCHO_TOKEN
docker compose up -d
./scripts/init-honcho.sh
./scripts/healthcheck.sh
```

All services should show `OK`.

## Services

| Service | Port |
|---|---|
| llama.cpp | `8082` |
| SearXNG | `8080` |
| Honcho API | `8081` |
| Chrome CDP | `9222` |
| Qdrant | `6333` |
| Dashboard | `8501` |
