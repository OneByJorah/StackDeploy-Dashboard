# StackDeploy — Self-hosted Services for Hermes Agents

![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)

**Repository:** https://github.com/OneByJorah/StackDeploy

---

## What is this?

StackDeploy is a one command, self-hosted stack of **Hermes-compatible services** for your AI agent. Run SearXNG search, Honcho memory, Chrome browser automation, Qdrant vector search, and Obsidian note-taking on your own hardware. No local GPU is required.

LLM inference is intentionally left out. Use a free cloud API (OpenRouter, Nous Portal, HuggingFace Inference, etc.) so you don't pay for models you already have access to.

---

## Services included

| Service | Port | Self-hosted | Purpose |
|---|---|---|---|
| SearXNG | `8080` | Yes | Privacy-respecting web search |
| Honcho API | `8081` | Yes | Long-term memory |
| Chrome CDP | `9222` | Yes | Browser automation |
| Qdrant | `6333` | Yes | Vector storage |
| Obsidian | `8083` | Yes | Markdown note vault |
| PostgreSQL + pgvector + Redis | internal | Yes | Memory backend |

---

## Getting started

One command after config:
```bash
bash scripts/bootstrap.sh
```

Manual:
```bash
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy
cp .env.example .env
docker compose up -d
./scripts/init-honcho.sh
./scripts/init-obsidian.sh
./scripts/healthcheck.sh <SERVER_IP>
```

---

## Hermes auto-wiring

After bootstrap, add this to `~/.hermes/config.yaml`:

```yaml
model:
  base_url: https://openrouter.ai/api/v1
  default: <free-model-id>
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

obsidian:
  enabled: true
  vault_path: /home/<user>/ObsidianVault
```

Run `hermes restart` to apply.

---

## Environment variables

| Variable | Example | Notes |
|---|---|---|
| `SERVER_IP` | `100.x.y.z` | Mesh-VPN or LAN IP |
| `APPLICATION_TOKEN` | `abc123` | Honcho access token |
| `DB_ACCOUNT_PASSWORD` | `s3cure!` | Postgres password |
| `POSTGRES_PASSWORD` | `s3cure!` | Postgres password (repeat) |
| `OBSIDIAN_VAULT_PATH` | `/home/<user>/ObsidianVault` | Host path for Obsidian |

Keep `.env` out of version control.

---

## Optional: local LLM add-ons

Uncomment ONE block below in `docker-compose.yml` and add vars to `.env` if you want self-hosted inference later:

- **Ollama** — CPU-friendly
- **llama.cpp** — GPU-accelerated

---

## Project structure

```
StackDeploy/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── scripts/
│   ├── bootstrap.sh
│   ├── healthcheck.sh
│   ├── init-honcho.sh
│   └── init-obsidian.sh
├── docs/
│   ├── SERVER_SETUP.md
│   └── HERMES_SETUP.md
└── README.md
```

---

## Service management

```bash
docker compose up -d
docker compose down
docker compose logs -f
./scripts/healthcheck.sh <SERVER_IP>
```

---

## License

MIT

---

## Author

Built by **Jhonattan L. Jimenez**.
