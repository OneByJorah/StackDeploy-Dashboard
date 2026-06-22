# StackDeploy (StackDeploy)

**Version:** v1.3  
**Status:** Production Ready  
**Repository:** https://github.com/OneByJorah/StackDeploy

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Service Management](#service-management)
- [CI/CD & Deployment](#cicd--deployment)
- [Security](#security)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

StackDeploy is a Docker Compose-based self-hosted stack for Hermes Agents. It consolidates local web search, long-term memory, browser automation, vector storage, and Obsidian note-taking into a reproducible, one-command deployment. The stack is designed to run on CPU-only hosts with no local GPU, while keeping the LLM layer intentionally external so you can plug in free cloud providers.

Secrets and environment configuration are managed via `docker-compose.yml` and `.env`, never committed to version control.

---

## Architecture

Client → Hermes Agent → Local services (SearXNG, Honcho, Chrome, Qdrant, Obsidian, PostgreSQL + Redis) → optional upstream LLM provider via Hermes config.

---

## Technology Stack

| Layer | Stack |
|---|---|
| Runtime | Linux (Ubuntu 22.04+) |
| Primary Stack | Docker Compose / Bash |
| VCS | Git + GitHub (`github.com/OneByJorah/StackDeploy`) |
| Memory / Context | Honcho |
| Notifications | Telegram (J1-bot) |
| Release path | `git push origin main` (documentation/build on branch) |

---

## Features

- **SearXNG**: privacy-respecting self-hosted web search.
- **Honcho API**: long-term memory and workspace context for Hermes.
- **Chrome CDP**: browser automation via remote DevTools.
- **Qdrant**: vector storage for semantic retrieval.
- **Obsidian vault**: markdown-backed note-taking exposed via web UI.
- **PostgreSQL + pgvector + Redis**: durable memory backend with vector support.
- **One-command bootstrap**: clone, env, stack, init, healthcheck.
- **Extensible service-based design**: add modules via Compose blocks.
- **CPU-first design**: no local GPU required for base stack.

---

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/OneByJorah/StackDeploy.git
cd StackDeploy

# 2. Environment
cp .env.example .env
# Edit .env: set SERVER_IP, HONCHO_TOKEN, HONCHO_DB_PASSWORD

# 3. Start the stack
docker compose up -d
./scripts/init-honcho.sh
./scripts/init-obsidian.sh
```

---

## Environment Variables

| Variable | Purpose | Notes |
|---|---|---|
| `SERVER_IP` | Mesh-VPN or local IP used in docs/examples | Required |
| `HONCHO_TOKEN` | Auth token for Honcho API | Optional |
| `HONCHO_DB_PASSWORD` | Postgres password for Honcho backend | Required |
| `OBSIDIAN_VAULT_PATH` | Host path for the Obsidian vault | Optional |

Keep `.env` out of VCS. Prefer `.env.example` placeholders in docs.

---

## Service Management

```bash
# Start the stack
docker compose up -d

# Stop
docker compose down

# Tail logs
docker compose logs -f

# Healthcheck
./scripts/healthcheck.sh <server-ip>
```

---

## CI/CD & Deployment

- Branch model: `main` for stable, feature branches for work-in-progress.
- Use `git push origin <branch>` to publish changes and trigger downstream automation.
- Keep Cheatsheet/docs in sync before merging: docs, README, and any changed service ports/endpoints.

---

## Security

- Secrets are handled through `.env` files with restrictive permissions; never store raw API tokens in README or source.
- Frontend artifacts and dashboard access paths are not credential-based in this repository.
- Services expose ports on localhost / trusted interfaces by default; bind only to trusted networks in production.

---

## Project Structure

```text
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

## Screenshots

All screenshots are live captures from the local dev instance.

_(Screenshots will be added after build/run capture.)_

---

## Contributing

1. Create a feature branch off `main`.
2. Follow the existing code style and README section order.
3. Submit a PR with description and screenshots for UI changes.
4. Do not commit real secrets or `.env` files.

---

## License

MIT

---

## Author

Built by **Jhonattan L. Jimenez**.
