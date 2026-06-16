# Free Auto Project

One-command self-hosted stack for Hermes agents.

## What this gives you

- **llama.cpp** as your local LLM backend
- **SearXNG** as an unlimited web search backend
- **Honcho** for cross-session memory
- **Chrome CDP** for real browser automation
- **Qdrant + pgvector** for embeddings / vector memory
- **Edge-TTS** for offline speech synthesis
- **Open-WebUI** for a web chat UI
- **Prometheus + Grafana** for observability

Default server address is `REPLACE_WITH_YOUR_TAILSCALE_IP` (Tailscale). Change `.env` before first run if needed.

## Requirements

- Docker + Docker Compose (v2+)
- NVIDIA GPU + NVIDIA Container Toolkit
- Hermes agent installed

## 1-Click Setup (server)

```bash
git clone https://github.com/<your-org>/free-auto-project.git
cd free-auto-project
cp .env.example .env
docker compose up -d
./scripts/init-honcho.sh
./scripts/bootstrap.sh           # optional: show the client command
```

That's it. All services start automatically.

## Connect a Hermes client

From any machine that has Hermes installed:

```bash
bash <(curl -s http://REPLACE_WITH_YOUR_TAILSCALE_IP:8501/bootstrap.sh)
```

Restart Hermes and you're connected to the whole stack.

## What the bootstrap command does

- Updates `~/.hermes/config.yaml`:
  - LLM → `http://<server>:8082/v1`
  - Search → `http://<server>:8080`
  - Browser → `http://<server>:9222`
  - Honcho → `http://<server>:8081`
- Adds the server's Honcho token to `~/.honcho/config.json`
- Backs up the original Hermes config to `~/.hermes/config.yaml.bak`

## Services

| Service | Port | Purpose |
|---|---|---|
| llama.cpp | `8082` | Local LLM API |
| SearXNG | `8080` | Web search backend |
| Honcho API | `8081` | Agent memory |
| Chrome CDP | `9222` | Browser automation |
| Qdrant | `6333` | Vector DB |
| pgvector | `5432` | Postgres + vectors |
| Redis | `6380` | Cache / Honcho broker |
| Edge-TTS | internal | TTS worker |
| Open-WebUI | `3000` | Chat UI |
| Prometheus | `9090` | Metrics |
| Grafana | `3001` | Dashboards |
| OWL Dashboard | `8501` | Savings tracker |

## Docs

- Server setup: [docs/SERVER_SETUP.md](docs/SERVER_SETUP.md)
- Hermes integration: [docs/HERMES_SETUP.md](docs/HERMES_SETUP.md)
- Maintenance: [docs/MAINTENANCE.md](docs/MAINTENANCE.md)
