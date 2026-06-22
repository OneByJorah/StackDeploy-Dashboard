# Server Setup

## Prerequisites

- Docker + Docker Compose v2+
- Mesh-VPN installed

## Install

```bash
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy
cp .env.example .env
# Edit .env: set SERVER_IP, HONCHO_DB_PASSWORD, HONCHO_TOKEN
docker compose up -d
./scripts/init-honcho.sh
./scripts/healthcheck.sh <server-ip>
```

All services should return `200`.

## Services

| Service | Port | Notes |
|---|---|---|
| SearXNG | `8080` | Self-hosted web search |
| Honcho API | `8081` | Long-term memory |
| Chrome CDP | `9222` | Browser automation |
| Qdrant | `6333` | Vector storage |

## Notes

- LLM inference is NOT included in this stack by design. Use Hermes pluggable providers for free cloud models, or enable the local LLM add-on blocks in `docker-compose.yml` if you want self-hosted inference later.
- Enabling Ollama requires adding its variables to `.env` and uncommenting the block in `docker-compose.yml`. Enabling llama.cpp requires an NVIDIA GPU and a mounted GGUF model.
