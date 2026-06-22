# StackDeploy — Self-hosted AI Stack for Hermes Agents

**Version:** v1.1  
**Status:** Active Development  
**Repository:** https://github.com/OneByJorah/StackDeploy

---

## Overview

StackDeploy is a one-command self-hosted stack for Hermes Agents. It brings together **Ollama** for local LLM inference, **SearXNG** for privacy-respecting search, **Honcho memory** for long-term context, **Chrome CDP** for browser automation, **Qdrant** for vector search, and **PostgreSQL + pgvector + Redis** for structured memory — in a single Docker Compose deployment.

Designed for operators who want full control: run the stack on your own hardware, keep data on-prem, and wire it into Hermes via environment configuration. No paid APIs required.

---

## Architecture

```
Client → Hermes Agent → StackDeploy services
  ├── Ollama (local LLM inference)
  ├── SearXNG (web search)
  ├── Honcho API (long-term memory)
  ├── Chrome CDP (browser automation)
  └── Qdrant (vector storage)
```

---

## Technology Stack

| Layer | Stack |
|-------|-------|
| Runtime | Linux (Ubuntu 22.04+) |
| Orchestration | Docker Compose |
| LLM Runtime | Ollama (CPU-only or GPU) |
| Search | SearXNG |
| Memory | Honcho API + Redis + pgvector |
| Vector DB | Qdrant |
| Browser Automation | Chrome CDP |
| Scripts | Bash / curl |
| VCS | Git + GitHub |

---

## Features

- **Local LLM**: Ollama with configurable model, CPU thread tuning, and parallel limits.
- **Privacy search**: self-hosted SearXNG instance.
- **Long-term memory**: Honcho memory API backed by Postgres/pgvector and Redis.
- **Vector search**: Qdrant for semantic retrieval.
- **Browser control**: Chrome CDP integration.
- **Observability**: health-check scripts for every service.
- **One-command bootstrap**: compose + init + bootstrap + healthcheck.
- **CPU-friendly**: tuned for hosts without GPUs. Adjust `OLLAMA_NUM_CPU` to match cores.

---

## Getting Started

```bash
# 1. Clone
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy

# 2. Environment
cp .env.example .env
# Edit .env: set SERVER_IP and HONCHO_DB_PASSWORD

# 3. Bring up the stack
docker compose up -d

# 4. Initialize services
./scripts/init-honcho.sh
./scripts/init-ollama.sh

# 5. Verify
./scripts/healthcheck.sh
```

---

## Environment Variables

Key variables from `.env.example`:

| Variable | Purpose |
|---|---|
| `SERVER_IP` | Mesh-VPN IP of this server (used by healthcheck if no arg passed) |
| `OLLAMA_NUM_CPU` | CPU threads for Ollama (default: 4) |
| `OLLAMA_MAX_LOADED_MODELS` | Max models in memory (default: 1) |
| `OLLAMA_MODEL` | Model to pull on init (default: `qwen2.5:4b`) |
| `HONCHO_DB_PASSWORD` | Postgres password for Honcho |
| `HONCHO_TOKEN` | Auth token for Honcho API |

Keep `.env` out of VCS.

---

## Service Management

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Logs
docker compose logs -f

# Healthcheck
./scripts/healthcheck.sh <your-server-ip>
```

Services expose ports on the host; bind only to trusted interfaces in production.

---

## Project Structure

```
StackDeploy/
├── docker-compose.yml
├── .env.example
├── scripts/
│   ├── bootstrap.sh
│   ├── healthcheck.sh
│   ├── init-honcho.sh
│   └── init-ollama.sh
├── docs/
│   ├── SERVER_SETUP.md
│   └── HERMES_SETUP.md
└── README.md
```

---

## Hermes Configuration

After the stack is up, point Hermes at your local services:

```yaml
model:
  base_url: http://<SERVER_IP>:11434/v1
  default: qwen2.5:4b
  provider: custom
  api_key: hermes-local

web:
  backend: searxng
  searxng_url: http://<SERVER_IP>:8080

browser:
  cdp_url: http://<SERVER_IP>:9222

honcho:
  enabled: true
  base_url: "http://<SERVER_IP>:8081"
  workspace: hermes-main
```

For Obsidian note-taking, set the vault path in Hermes to your local Obsidian directory. No separate service is required — Hermes reads/writes markdown directly.

---

## Notes

- Default model (`qwen2.5:4b`) is sized for CPU-only hosts with ~8 GB RAM. Increase `OLLAMA_NUM_CPU` if you have more cores.
- If you have an NVIDIA GPU, you can switch to the `ollama/ollama:latest` GPU-enabled image and set `OLLAMA_NUM_CPU` lower. GPU passthrough is not included in the default compose.
- SearXNG is fully self-hosted — no external API keys or rate limits.

---

## License

MIT

---

## Author

Built by **Jhonattan L. Jimenez**.
