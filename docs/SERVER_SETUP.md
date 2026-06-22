# Server Setup

## Prerequisites

- Docker + Docker Compose v2+
- Mesh-VPN installed
- (Optional) NVIDIA GPU + NVIDIA Container Toolkit if you want GPU-accelerated Ollama

## Install

```bash
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy
cp .env.example .env
# Edit .env: set SERVER_IP, HONCHO_DB_PASSWORD, HONCHO_TOKEN
docker compose up -d
./scripts/init-honcho.sh
./scripts/init-ollama.sh
./scripts/healthcheck.sh <server-ip>
```

All services should return `200`.

## Services

| Service | Port | Notes |
|---|---|---|
| Ollama | `11434` | Local LLM inference |
| SearXNG | `8080` | Self-hosted web search |
| Honcho API | `8081` | Long-term memory |
| Chrome CDP | `9222` | Browser automation |
| Qdrant | `6333` | Vector storage |

## Notes

- Default model is `qwen2.5:4b`, sized for CPU-only hosts with ~8 GB RAM. Edit `OLLAMA_MODEL` and `OLLAMA_NUM_CPU` in `.env` to match your hardware.
- If you have an NVIDIA GPU, add GPU device reservations to the `ollama` service and set `OLLAMA_NUM_CPU` low.
