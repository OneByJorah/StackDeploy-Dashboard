# Server Setup

## Prerequisites

- Docker + Docker Compose v2+
- Mesh-VPN installed

## Install

```bash
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy
cp .env.example .env
# Edit .env: set SERVER_IP, HONCHO_DB_PASSWORD
docker compose up -d
./scripts/init-honcho.sh
./scripts/init-obsidian.sh
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
| Obsidian Web *(optional)* | `8083` | Note-taking vault browser |

## Notes

- LLM inference is NOT included in this stack by default. Use Hermes pluggable providers for free cloud models, or enable the local LLM add-on blocks in `docker-compose.yml` if you want self-hosted inference later.
- The Obsidian vault is stored at the host path configured in `OBSIDIAN_VAULT_PATH`. The Obsidian desktop app can open this folder directly. If you uncomment the `obsidian:` service, it will expose the vault through a web browser on port `8083`.
