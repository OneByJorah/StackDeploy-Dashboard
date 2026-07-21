<div align="center">

# ForgeDash

**Self-hosted control plane and onboarding gateway for AI service stacks.**

[![CI](https://github.com/OneByJorah/ForgeDash/actions/workflows/ci.yml/badge.svg)](https://github.com/OneByJorah/ForgeDash/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-FFB300?style=flat-square)
![Version](https://img.shields.io/badge/version-2.0.0-FFB300?style=flat-square)

</div>

ForgeDash deploys SearXNG, Qdrant, Honcho, Ollama, Camofox, and Obsidian behind a single gateway with auto-discoverable APIs and an onboarding dashboard. Choose between local LLM inference (Ollama) or a cloud API (OpenRouter) for Honcho's AI features.

---

## Quick Start

### Zero-config auto-deploy (recommended)

```bash
git clone https://github.com/OneByJorah/ForgeDash.git
cd ForgeDash
sudo ./bootstrap.sh --auto
```

This single command generates secure passwords, deploys the full stack (gateway, SearXNG, Qdrant, Honcho, Obsidian, Camofox, Ollama), pulls a default 1B LLM model (`llama3.2:1b`), and auto-configures Honcho to use it — zero prompts, zero manual editing.

### Interactive setup

```bash
./setup.sh              # Interactive credential prompts
sudo ./bootstrap.sh     # Deploy the stack
```

Open **http://localhost:9090** for the onboarding dashboard or **http://localhost:9090/api/v1/discover** for the agent auto-discovery API.

---

## Features

- **Onboarding API** — Agents hit `/api/v1/discover` to auto-configure to all local services
- **One-command auto-deploy** — `sudo ./bootstrap.sh --auto` generates everything: secure passwords, Ollama config, model pull, Honcho setup
- **Interactive Setup** — `./setup.sh` prompts for passwords, generates `.env`, no manual editing
- **Local LLM (Ollama)** — Run Honcho entirely offline with local model inference (opt-in)
- **Cloud or Local** — Choose between local Ollama or cloud OpenRouter during setup
- **Cloudflare Tunnel** — Optional public HTTPS access (no open firewall ports)
- **Auto-Discovery** — Gateway aggregates health and connection info for all backend services

---

## Setup

### First-time install

```bash
./setup.sh
```

This interactive script will prompt for:
1. **Admin credentials** — username/password for the gateway dashboard
2. **Tailscale auth key** — optional, for mesh networking
3. **Cloudflare Tunnel token** — optional, for public HTTPS access
4. **LLM provider** — choose between:
   - **(L)ocal Ollama** — runs entirely on-device, no API key needed
   - **(C)loud API (OpenRouter)** — uses OpenRouter or any OpenAI-compatible API
5. **Service passwords** — Honcho DB, Camofox API keys

All credentials are auto-generated if left blank. The `.env.honcho` file is generated automatically based on your LLM provider choice — no manual editing needed.

### Auto-deploy (zero config)

```bash
# One-command deploy — generates .env, deploys stack, pulls Ollama model
sudo ./bootstrap.sh --auto

# With a different model
sudo ./bootstrap.sh --auto --model llama3.2:1b

# With custom model + Tailscale + Cloudflare
sudo ./bootstrap.sh --auto --with-tailscale --with-public
```

### Manual deploy

```bash
# Basic deploy (cloud API)
sudo ./bootstrap.sh

# With local LLM (Ollama) — auto-pulls model
sudo ./bootstrap.sh --with-local-llm

# With a specific Ollama model
sudo ./bootstrap.sh --with-local-llm --model qwen2.5:0.5b

# With Tailscale mesh
sudo ./bootstrap.sh --with-tailscale

# With Tailscale + Cloudflare Tunnel (public HTTPS)
sudo ./bootstrap.sh --with-tailscale --with-public

# Skip setup prompt (use existing .env)
sudo ./bootstrap.sh --skip-setup
```

---

## Local LLM (Ollama) Quick Start

When using `--with-local-llm` or `--auto`, Honcho is automatically configured to route all AI requests (memory summarization, reasoning, embeddings) to the local Ollama instance. The default 1B model is pulled automatically. To manage models:

```bash
# Pull additional models
docker exec ollama ollama pull llama3.2

# List available models
docker exec ollama ollama list

# Remove a model
docker exec ollama ollama rm qwen2.5:0.5b
```

The Ollama API is discoverable via the gateway at `http://ollama:11434` for other services to use. The Honcho config applies the same model across all features via per-feature env var overrides.

---

## Agent Onboarding

Agents can auto-configure to the API stack by hitting the discover endpoint:

```bash
# Get all available services with connection details
curl -u admin:your-password http://localhost:9090/api/v1/discover
```

Response includes each service's internal URL, health status, and description. The onboarding page at **http://localhost:9090/onboard** shows a human-friendly dashboard.

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` or `/onboard` | Human-friendly onboarding dashboard |
| `/api/v1/discover` | Agent auto-discovery JSON (auth required) |
| `/api/v1/health` | Aggregated health status of all services |

---

## Services

| Service | Internal URL | Description |
|---------|-------------|-------------|
| SearXNG | `http://searxng:8080` | Private meta-search engine |
| Qdrant | `http://qdrant:6333` | Vector database for semantic memory |
| Honcho | `http://honcho:8000` | AI memory & session management |
| Ollama | `http://ollama:11434` | Local LLM inference (opt-in) |
| Camofox | `http://camofox-browser:9377` | Browser automation |
| Obsidian | `http://obsidian:8080` | Notes & knowledge management |
| CloakBrowser | `http://cloak-browser:9222` | Protected browser |

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Purpose | Default |
|----------|---------|---------|
| `SERVER_IP` | Host/mesh IP for service URLs | `127.0.0.1` |
| `OBSIDIAN_VAULT_PATH` | Host path for Obsidian vault | `/opt/forgedash/ObsidianVault` |
| `HONCHO_TOKEN` | Honcho API auth token | required |
| `HONCHO_DB_PASSWORD` | Honcho PostgreSQL password | required |
| `POSTGRES_PASSWORD` | PostgreSQL superuser password | required |
| `CAMOFOX_API_KEY` | Camofox auth key | optional |
| `CAMOFOX_ADMIN_KEY` | Camofox admin key | optional |

---

## CI/CD

- `ci.yml` — Python lint (ruff) and unit tests for the gateway
- `webpack.yml` — Node build matrix for the browser components
- `ci-cd.yml` — Lint, build, test, and optional SSH deploy

---

## Contributing

1. Fork the repo
2. Create a branch: `fix/your-fix` or `feature/your-feature`
3. Open a PR against `main`

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## License

MIT © Jhonattan L. Jimenez

---

## Security

Report vulnerabilities to **info@jorahone.com**. Do not open public issues for security matters.
