# Server Setup

## Prerequisites

- Docker + Docker Compose v2+
- Mesh-VPN installed

## Install

```bash
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy
cp .env.example .env
# Edit .env: set SERVER_IP, APPLICATION_TOKEN, DB_ACCOUNT_PASSWORD, POSTGRES_PASSWORD
docker compose up -d
./scripts/init-honcho.sh
./scripts/init-obsidian.sh
./scripts/healthcheck.sh <server-ip>
```

All services should return `200`.

## Services

| Service | Port |
|---|---|
| SearXNG | `8080` |
| Honcho API | `8081` |
| Chrome CDP | `9222` |
| Qdrant | `6333` |
| Obsidian Web | `8083` |

## Notes

- LLM inference is NOT included by default. Use Hermes pluggable providers for free cloud models.
- To enable a local LLM later, uncomment the matching block in `docker-compose.yml` and add vars to `.env`.
- Obsidian vault data persists in the `obsidian-vault` Docker volume. Back it up regularly.
