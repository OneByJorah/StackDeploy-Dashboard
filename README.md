# StackDeploy — Self-hosted Services for Hermes Agents

**Version:** v1.2  
**Status:** Active Development  
**Repository:** https://github.com/OneByJorah/StackDeploy

---

## Overview

StackDeploy is a one-command self-hosted stack of **Hermes-compatible services**. Use it to run local web search, long-term memory, browser automation, and vector storage for your Hermes Agent. **LLM inference is intentionally left out** so you can plug in a free cloud API directly, or optionally enable the local inference add-on later if you change your mind.

Designed for operators who want full control: run the services you need on your own hardware, keep data on-prem, and wire them into Hermes via environment configuration.

---

## Services Included

| Service | Purpose | Hermes Integration |
|---------|---------|--------------------|
| **SearXNG** | Self-hosted web search | `web.searxng_url` |
| **Honcho** | Long-term memory API | `honcho.base_url` |
| **Chrome CDP** | Browser automation | `browser.cdp_url` |
| **Qdrant** | Vector search | optional semantic retrieval |
| **PostgreSQL + pgvector + Redis** | Memory/context backend | used by Honcho |

---

## LLM Strategy: Free Cloud First

StackDeploy does not ship a local LLM runtime. Configure Hermes to use a free cloud LLM directly — for example OpenRouter free models, Nous Portal, HuggingFace Inference, or any OpenAI-compatible API.

**Where to configure this:**
- Hermes config: `~/.hermes/config.yaml` or `~/.hermes/.env`
- Set `model.base_url`, `model.default`, and provider credentials there.

See `docs/HERMES_SETUP.md` for concrete examples.

---

## Optional: Local LLM Add-Ons

If you later want a local fallback/always-on model, you can add one of the pre-written blocks in `docker-compose.yml`:

- **Option A — Ollama:** CPU-friendly local inference. Good for 8 GB RAM hosts.
- **Option B — llama.cpp:** GPU-accelerated local inference. Requires NVIDIA GPU.

To enable: edit `docker-compose.yml`, uncomment the desired block, add the matching vars to `.env`, then re-run `docker compose up -d`.

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

# 4. Initialize Honcho
./scripts/init-honcho.sh

# 5. Verify
./scripts/healthcheck.sh <server-ip>
```

---

## Environment Variables

Key variables from `.env.example`:

| Variable | Purpose |
|---|---|
| `SERVER_IP` | Mesh-VPN or local IP used in docs/examples |
| `HONCHO_DB_PASSWORD` | Postgres password for Honcho |
| `HONCHO_TOKEN` | Auth token for Honcho API |
| `OLLAMA_MODEL` | *(optional)* Model tag if you enable Ollama |
| `MODEL_PATH` | *(optional)* GGUF path if you enable llama.cpp |
| `CTX_SIZE` | *(optional)* Context window size for llama.cpp |

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
./scripts/healthcheck.sh <server-ip>
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
│   └── init-honcho.sh
├── docs/
│   ├── SERVER_SETUP.md
│   └── HERMES_SETUP.md
└── README.md
```

---

## Hermes Configuration

After the stack is up, point Hermes at your services and your preferred LLM provider:

```yaml
model:
  # Use your free cloud provider here — Hermes will pick this up automatically
  base_url: https://openrouter.ai/api/v1
  default: <provider-model-id>
  provider: openrouter
  api_key: <OPENROUTER_API_KEY>

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

For Obsidian note-taking, set the vault path in Hermes to your local vault folder. No extra service is needed — Hermes reads/writes markdown directly.

---

## License

MIT

---

## Author

Built by **Jhonattan L. Jimenez**.
