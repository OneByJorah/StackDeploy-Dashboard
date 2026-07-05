# StackDeploy Dashboard

Self-hosted all-in-one API platform — deploy SearXNG, Qdrant, Honcho, Ollama, Camofox, and Obsidian behind a single gateway with auto-discoverable APIs, Tailscale mesh, and optional Cloudflare Tunnel for public HTTPS. Choose between local LLM inference (Ollama) or cloud API (OpenRouter) for Honcho's AI features.

[![CI](https://github.com/OneByJorah/StackDeploy-Dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/OneByJorah/StackDeploy-Dashboard/actions/workflows/ci.yml)
![Version](https://img.shields.io/badge/version-2.0.0-FFB300?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-FFB300?style=flat-square)
![Build](https://img.shields.io/badge/build-passing-FFB300?style=flat-square)

## Quick Start

### Zero-config auto-deploy (recommended)

```bash
git clone https://github.com/OneByJorah/StackDeploy-Dashboard.git
cd StackDeploy-Dashboard
sudo ./bootstrap.sh --auto
```

This single command generates secure passwords, deploys the full stack (gateway, SearXNG, Qdrant, Honcho, Obsidian, Camofox, Ollama), pulls a 1B LLM model (`llama3.2:1b`), and auto-configures Honcho to use it — zero prompts, zero manual editing.

### Interactive setup

```bash
./setup.sh              # Interactive credential prompts
sudo ./bootstrap.sh     # Deploy the stack
```

Open **http://localhost:9090** for the onboarding dashboard or **http://localhost:9090/api/v1/discover** for the agent auto-discovery API.

## Features

- **Onboarding API** — Agents hit `/api/v1/discover` to auto-configure to all local services
- **One-command auto-deploy** — `sudo ./bootstrap.sh --auto` generates everything: secure passwords, Ollama config, model pull, Honcho setup. Zero interaction needed
- **Interactive Setup** — `./setup.sh` prompts for passwords, generates `.env`, no manual editing
- **Local LLM (Ollama)** — Run Honcho entirely offline with local model inference (opt-in via `--with-local-llm` or `--auto`)
- **Cloud or Local** — Choose between local Ollama or cloud OpenRouter during setup; `.env.honcho` configured automatically
- **Tailscale Mesh** — Each service gets its own Tailscale identity for secure mesh networking
- **Cloudflare Tunnel** — Optional public HTTPS access via Cloudflare Tunnel (no open firewall ports)
- **Auto-Discovery** — Gateway aggregates health and connection info for all backend services

## Architecture

```mermaid
graph TB
    subgraph Public
        A[Cloudflare Tunnel]
    end
    subgraph Tailscale_Mesh
        B[Gateway :9090]
        C[SearXNG :8080]
        D[Qdrant :6333]
        E[Honcho :8000]
    end
    subgraph Local_LLM
        I[Ollama :11434]
    end
    subgraph Local_Network
        F[Camofox :9377]
        G[Obsidian :8083]
        H[CloakBrowser :9222]
    end

    A -->|HTTPS| B
    B -->|Discover API| C
    B -->|Discover API| D
    B -->|Discover API| E
    B -->|Discover API| F
    B -->|Discover API| G
    B -->|Discover API| H
    E ---->|LLM inference| I

    style B fill:#1a1a2e,stroke:#FFB300,color:#fff
    style C fill:#1a1a2e,stroke:#FFB300,color:#fff
    style D fill:#1a1a2e,stroke:#FFB300,color:#fff
    style E fill:#1a1a2e,stroke:#FFB300,color:#fff
    style I fill:#1a1a2e,stroke:#10b981,color:#fff
```

StackDeploy Dashboard is the control-plane island in the JorahOne archipelago — the single ingress through which agents discover and connect to every service.

## Setup

### First-time install

```bash
./setup.sh
```

This interactive script will prompt for:
1. **Admin credentials** — username/password for the gateway dashboard
2. **Tailscale auth key** — optional, for mesh networking (get one from https://login.tailscale.com/admin/settings/keys)
3. **Cloudflare Tunnel token** — optional, for public HTTPS access (create a tunnel at https://one.dash.cloudflare.com/)
4. **LLM Provider** — choose between:
   - **(L)ocal Ollama** — runs entirely on-device, no API key needed. You pick a default model (default: `llama3.2`)
   - **(C)loud API (OpenRouter)** — uses OpenRouter or any OpenAI-compatible API. You provide an API key
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

`--auto` does everything: generates a secure `.env` with random passwords, generates `.env.honcho` pointing to local Ollama, deploys all services, pulls the default model (`llama3.2:1b`), and restarts Honcho to activate it. The admin password is printed at the end.

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

# With everything
sudo ./bootstrap.sh --with-tailscale --with-public --with-local-llm

# Skip setup prompt (use existing .env)
sudo ./bootstrap.sh --skip-setup
```

### Local LLM (Ollama) Quick Start

When using `--with-local-llm` or `--auto`, Honcho is automatically configured to route all AI requests (memory summarization, reasoning, embeddings) to the local Ollama instance. The default 1B model is pulled automatically. To manage models:

```bash
# Pull additional models
docker exec ollama ollama pull llama3.2

# List available models
docker exec ollama ollama list

# Remove a model
docker exec ollama ollama rm qwen2.5:0.5b
```

The Ollama API is also discoverable via the gateway at `http://ollama:11434` for other services to use. The Honcho config applies the same model across all features (deriver, summarization, dialectic, dream, embeddings) via per-feature env var overrides.

## Agent Onboarding

Agents (Hermes, Claude Code, custom scripts) can auto-configure to the API stack by hitting the discover endpoint:

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

## Contributing

1. Fork the repo
2. Create a branch: `fix/your-fix` or `feature/your-feature`
3. Open a PR against `main`
4. Response time: I read PRs within 48 hours

## License

MIT — JorahOne LLC
