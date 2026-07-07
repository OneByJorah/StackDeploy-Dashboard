# INTENT.md — ForgeDash

> **Phase -1 (ORACLE) — Engineering Intent Reconstruction**
> Repository: `OneByJorah/ForgeDash`
> Analysis Date: 2026-07-05
> Analyst: J1-PIPELINE ORACLE (read-only)
> Status: Intent Reconstructed (verified against code)

---

## What This System Does

**ForgeDash is a self-hosted, all-in-one API platform** that bundles seven backend services behind a single FastAPI gateway with agent auto-discovery. It is the infrastructure control plane for the JorahOne ecosystem — the single ingress through which AI agents (primarily Hermes Agent) discover, connect to, and health-check every local service.

### Core Gateway (FastAPI, port 9090)

| Endpoint | Purpose |
|---|---|
| `GET /` or `/onboard` | Human-friendly onboarding dashboard (dark-themed HTML with live service status, auto-refresh every 30s) |
| `GET /api/v1/discover` | Agent auto-discovery JSON — returns all services with internal URLs, health status, descriptions, Tailscale hostname, and Cloudflare domain |
| `GET /api/v1/health` | Aggregated health status of all backend services (OPERATIONAL / DEGRADED) |
| `GET /health` | Self-health check for the gateway itself |

### Managed Services (defined in docker-compose.yml)

| Service | Internal Host:Port | Host Port | Role |
|---|---|---|---|
| **SearXNG** | `searxng:8080` | 8080 | Private meta-search engine (JSON API, no public instance) |
| **Qdrant** | `qdrant:6333` | 6333 | Vector database for semantic memory |
| **Honcho** | `honcho:8081` | 8081 | AI memory & session management (PostgreSQL + pgvector + Redis) |
| **Camofox** | `camofox-browser:9377` | 9377 | Browser automation service (headless Chromium) |
| **Obsidian** | `obsidian:8080` | 8083 | Notes & knowledge management (remote Obsidian) |
| **CloakBrowser** | `cloak-browser:9222` | 9222 | Protected browser for authenticated sites (CDP) |

**Note:** Ollama is referenced in the gateway's `SERVICE_REGISTRY` and documented as an opt-in service, but no Ollama service is defined in any `docker-compose*.yml` file. It must be deployed separately or added manually.

### Optional Add-on Stacks

- **Honcho upstream build** (`docker-compose.honcho.yml`) — builds Honcho from `vendor/honcho` submodule with configurable LLM providers (OpenRouter, Venice, etc.) and multi-tier model routing. Exposes on port 8000 (vs. the pre-built image on 8081 in the base compose).
- **Headroom / Aphrodite proxy** (`docker-compose.headroom.yml`) — memory proxy stack with Qdrant + Neo4j backends for vector + graph memory.

### Deployment Model

- **Docker Compose** — all services defined in `docker-compose.yml` with health checks, restart policies, and persistent volumes
- **Bootstrap** — `bootstrap.sh` runs init scripts and `docker compose up -d` (note: the README describes `--auto`, `--with-local-llm`, `--with-tailscale`, `--with-public` flags, but the actual `bootstrap.sh` is a simple 17-line script with no argument parsing — the README describes a more sophisticated bootstrap than what currently exists)
- **Interactive setup** — the README references `./setup.sh` for credential prompts, but no `setup.sh` exists at the repo root (only `browser-search/scripts/setup.sh`)
- **Tailscale mesh** — each service can get its own Tailscale identity for secure mesh networking
- **Cloudflare Tunnel** — optional public HTTPS access without opening firewall ports

### Testing & CI

- **Unit tests** (`gateway/tests/test_gateway.py`) — 30+ tests using FastAPI TestClient with httpx mocking, covering all endpoints, auth edge cases, and service registry integrity
- **Integration tests** (`gateway/tests/test_integration.py`) — 20+ tests hitting the live deployed stack, verifying cross-endpoint consistency
- **Smoke tests** (`tests/smoke.sh`) — end-to-end service verification
- **CI pipeline** (`.github/workflows/ci.yml`) — ruff lint + pytest on push/PR
- **CI/CD pipeline** (`.github/workflows/ci-cd.yml`) — hadolint + shellcheck + yamllint + docker build + healthcheck + SSH deploy
- **CodeQL** (`.github/workflows/codeql.yml`) — security analysis (Python, JavaScript, TypeScript)
- **Dependabot** (`.github/dependabot.yml`) — weekly pip, Docker, and Actions updates

---

## Why This Was Built

### The Real Problem

AI agents — especially Hermes Agent, but also Claude Code and custom scripts — need a local, self-hosted stack of infrastructure services to operate autonomously:

1. **Search** — agents need web search without depending on public APIs (SearXNG)
2. **Memory** — agents need persistent, long-term memory with vector search (Honcho + Qdrant)
3. **Browser automation** — agents need to interact with web pages (Camofox)
4. **Knowledge management** — agents need to read/write notes (Obsidian)
5. **Local LLM inference** — agents need offline-capable LLM inference (Ollama, opt-in)
6. **Protected browsing** — agents need to access authenticated sites (CloakBrowser)

Configuring each of these services individually is complex, error-prone, and unreproducible. Each has its own setup procedure, configuration format, authentication model, and API surface. There is no standard way for an agent to discover what services are available on a given host.

### Why Existing Tools Were Insufficient

- **No single turnkey solution** existed that bundled search, vector DB, memory, browser automation, notes, and LLM inference behind a unified API
- **No agent auto-discovery standard** — agents had no way to programmatically discover what infrastructure was available on a host
- **Docker Compose stacks** for individual services existed, but no composable, opinionated bundle with health checks, secrets management, and reproducible deployment
- **Cloud-dependent** — most AI agent infrastructure assumed cloud APIs (OpenAI, etc.), with no path to local/offline operation
- **No Hermes-native integration** — Hermes Agent had no plug-and-play skill for configuring itself to a local service stack

### What Triggered Development

The repository evolved from an earlier project called **"Free Auto Project"** (initial commit: `e7cb899`, 2026-06-16, "chore: bootstrap Free Auto Project repo"). It was privacy-sanitized for public release in the same session, then renamed through several iterations: Free Auto → J1-Stack-Deploy → StackDeploy → StackDeploy-Dashboard → ForgeDash.

The git history shows a clear evolution visible in the 52 commits:

1. **Initial creation** — generic "Free Auto Project" repo for deploying AI infrastructure
2. **Privacy sanitization** (`0a81f1d`, `f08dcc8`) — real IPs/passwords replaced with placeholders before public release
3. **Repo renames** (`b8d3b31` through `2ab4dac`) — migrated from Free Auto → J1-Stack-Deploy → StackDeploy
4. **Obsidian integration** — added knowledge management
5. **Honcho integration** (`22915b3`) — added AI memory/session management with PostgreSQL + Redis
6. **Production upgrade** (`89ee98f`) — health checks, restart policies, production-grade config
7. **Headroom integration** (`1688f87`) — optional memory proxy stack with Neo4j
8. **Gateway v2** — FastAPI gateway with agent auto-discovery, onboarding dashboard, aggregated health
9. **CI/CD pipeline** (`28f8556`, `8f8d11e`) — lint, test, CodeQL, Dependabot
10. **Hermes skill** (`78a997a`) — plug-and-play Hermes Agent integration skill
11. **Security audit** (`2655f5d`, `7ccf645`) — sanitized email and path references, redacted exposed Tailscale IPs

The driving force was the need for a **reproducible, one-command-deployable local infrastructure stack** that Hermes Agent could discover and use autonomously.

### JorahOne Ecosystem Fit

ForgeDash is the **control-plane island** in the JorahOne archipelago. It provides:

- **Infrastructure layer** — the physical/virtual services that Hermes Agent depends on
- **Discovery layer** — agents auto-configure by hitting `/api/v1/discover`
- **Health layer** — aggregated health monitoring across all services
- **Onboarding layer** — human-friendly dashboard for operators
- **Network layer** — Tailscale mesh + Cloudflare Tunnel for secure access

Without ForgeDash, Hermes Agent would need to be manually configured with the URL, port, auth, and health-check path of every service. With it, a single `curl http://localhost:9090/api/v1/discover` gives the agent everything it needs.

---

## Operational Classification

**Classification: PRODUCTION**

This is a deployed, tested, CI/CD-gated infrastructure stack. Evidence:

- Production-grade Docker Compose with health checks, restart policies, and persistent volumes
- 50+ unit and integration tests with CI enforcement (two CI workflows)
- CodeQL security scanning (Python, JavaScript, TypeScript)
- Dependabot for dependency updates (pip, Docker, GitHub Actions)
- Ruff linting with standardized config
- Versioned gateway API (v2.0.0)
- Tailscale + Cloudflare Tunnel for production networking
- Comprehensive documentation (6 docs files: server setup, maintenance, Hermes setup, Honcho setup, Headroom setup, Hermes integration)
- Security audit commits in git history (4 commits with audit/sanitize/security messages)
- Community governance files: CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, MIT LICENSE
- GitHub issue/PR templates (bug report, feature request, PR template)
- SSH-based deploy workflow in CI/CD

---

## Key Architectural Decisions

1. **Single gateway ingress** — all external traffic goes through port 9090; internal services communicate via Docker DNS
2. **Read-only discover by default** — `/api/v1/discover` works without auth; write operations require HTTP Basic auth
3. **Docker Compose as the unit of deployment** — no Kubernetes, no Nomad; single-host simplicity
4. **Composable override files** — `docker-compose.honcho.yml` and `docker-compose.headroom.yml` are opt-in overlays
5. **Inline HTML** — the onboarding dashboard is embedded in `server.py` as a Python string, no separate templates directory
6. **Env-var-driven config** — all secrets and service-specific settings come from `.env`; no hardcoded credentials
7. **Hermes skill as integration contract** — the `skills/devops/stackdeploy/SKILL.md` defines the canonical way Hermes connects to the stack
8. **Dual Honcho deployment paths** — base compose uses a pre-built image on port 8081; the overlay compose builds from source on port 8000
9. **Pre-built images for most services** — only CloakBrowser is built locally; SearXNG, Qdrant, Camofox, Obsidian are pulled from registries

---

## Repository Structure

```
ForgeDash/
├── .env.example                  # Required env vars template
├── .env.headroom.example         # Headroom-specific env vars
├── .gitignore
├── .gitmodules                   # Submodules: vendor/honcho, vendor/headroom
├── .dockerignore
├── bootstrap.sh                  # One-shot deploy script (simple, no arg parsing)
├── docker-compose.yml            # Core stack (7 services)
├── docker-compose.honcho.yml     # Optional: Honcho upstream build overlay
├── docker-compose.headroom.yml   # Optional: Headroom memory proxy overlay
├── INTENT.md                     # This file
├── README.md                     # Main documentation
├── LICENSE                       # MIT
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
├── test_results.txt              # Historical test output (Honcho build log)
│
├── gateway/                      # FastAPI gateway
│   ├── server.py                 # Main app (350 lines, all endpoints + inline HTML)
│   ├── Dockerfile                # python:3.11-slim, uvicorn
│   ├── requirements.txt          # fastapi, uvicorn, httpx, python-multipart, pydantic
│   ├── ruff.toml                 # Linter config
│   └── tests/
│       ├── test_gateway.py       # 30+ unit tests
│       └── test_integration.py   # 20+ integration tests
│
├── scripts/
│   ├── bootstrap.sh              # (same as root bootstrap.sh)
│   ├── install.sh                # Python venv setup
│   ├── healthcheck.sh            # Service health verification
│   ├── init-honcho.sh            # Honcho env initialization
│   ├── init-obsidian.sh          # Obsidian vault initialization
│   ├── init-headroom.sh          # Headroom env initialization
│   └── install-browser-search.sh # Browser-search npm install
│
├── tests/
│   └── smoke.sh                  # End-to-end smoke tests
│
├── docs/
│   ├── SERVER_SETUP.md           # Server installation guide
│   ├── MAINTENANCE.md            # Maintenance procedures
│   ├── HERMES_SETUP.md           # Hermes Agent configuration
│   ├── HONCHO_SETUP.md           # Honcho setup guide
│   ├── HEADROOM_SETUP.md         # Headroom setup guide
│   └── hermes.md                 # Hermes integration reference
│
├── searxng/
│   └── settings.yml              # SearXNG config (JSON format, public_instance: false)
│
├── honcho/
│   ├── config.toml               # Honcho LLM provider config (OpenRouter, Venice)
│   ├── honcho-config.json        # Hermes Honcho integration config
│   └── .env.honcho.example       # Honcho env template
│
├── headroom/
│   └── headroom-config.example   # Headroom config template
│
├── browser-search/               # Camofox/CloakBrowser source (subtree, not submodule)
│   ├── docker/                   # Dockerfiles
│   ├── scripts/                  # CLI tools (cloak-fetch.mjs, setup.sh)
│   └── SKILL.md                  # Hermes skill for browser-search
│
├── obsidian-skills/
│   └── defuddle/SKILL.md         # Hermes skill for Defuddle web extraction
│
├── skills/
│   └── devops/stackdeploy/
│       ├── SKILL.md              # Hermes StackDeploy integration skill
│       └── references/
│           └── stackdeploy-install-notes.md
│
├── vendor/                       # Submodule stubs (empty — not checked out)
│   ├── honcho/                   # → https://github.com/plastic-labs/honcho.git
│   └── headroom/                 # → https://github.com/OneByJorah/headroom-j1.git
│
└── .github/
    ├── workflows/
    │   ├── ci.yml                # Python lint + test
    │   ├── ci-cd.yml             # Docker lint + build + test + deploy
    │   ├── codeql.yml            # Security analysis
    │   └── webpack.yml           # Stale: Node.js webpack build (template vestige)
    ├── dependabot.yml            # Weekly dependency updates
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md
```

---

## Notes

### Discrepancies Found

1. **Honcho port mismatch**: INTENT.md previously stated Honcho at `honcho:8000`. The base `docker-compose.yml` exposes Honcho on port **8081** (internal and host). The overlay `docker-compose.honcho.yml` uses port 8000 for the upstream build. Both are valid depending on which compose file is used.

2. **Ollama not in compose**: The gateway's `SERVICE_REGISTRY` references `ollama:11434` and the README documents it as an opt-in service, but no Ollama service is defined in any `docker-compose*.yml` file. It must be deployed separately.

3. **Missing `setup.sh`**: The README references `./setup.sh` for interactive credential prompts, but no `setup.sh` exists at the repo root. Only `bootstrap.sh` exists. The `browser-search/scripts/setup.sh` is unrelated.

4. **Bootstrap script simpler than documented**: The README describes `--auto`, `--with-local-llm`, `--with-tailscale`, `--with-public` flags, but the actual `bootstrap.sh` is a 17-line script with no argument parsing. The documented flags do not exist in the code.

5. **Portainer reference**: `scripts/healthcheck.sh` checks Portainer at port 9000, but no Portainer service is defined in any compose file.

6. **`llama-server` reference**: `docs/MAINTENANCE.md` references `docker compose up -d llama-server`, but no such service exists in any compose file.

7. **Stale webpack workflow**: `.github/workflows/webpack.yml` is a Node.js webpack build workflow targeting the `master` branch (not `main`). This appears to be a template vestige — the repo has no `package.json` or webpack config at the root level.

8. **Submodules not checked out**: `vendor/honcho` and `vendor/headroom` are empty directories. The submodules are defined in `.gitmodules` but not initialized. This affects the Honcho upstream build and Headroom overlay.

9. **Repo naming history**: The initial commit was "bootstrap Free Auto Project repo" (2026-06-16). The repo went through renames: Free Auto → J1-Stack-Deploy → StackDeploy → StackDeploy-Dashboard → ForgeDash. Some docs still reference the old `StackDeploy` name (e.g., `docs/SERVER_SETUP.md` references `https://github.com/OneByJorah/StackDeploy.git`).

10. **SearXNG healthcheck**: The SearXNG healthcheck (`curl -sf 'http://localhost:8080/search?q=healthcheck&format=json'`) may fail intermittently — the `test_results.txt` shows SearXNG as `(unhealthy)` even when the service is functional. This is a known issue noted in the Hermes skill.

### Security Audit History

4 commits with security-related messages:
- `0a81f1d` — sanitize: replace real IPs/passwords with placeholders before publish
- `f08dcc8` — feat: final docs/scripts, privacy-sanitized for public release
- `7ccf645` — security: redact exposed tailscale IPs and demo emails
- `2655f5d` — audit(ForgeDash): sanitize email and path references

This is a positive maturity signal — the repo was intentionally sanitized before public release.

### Empty Directories

- `vendor/honcho/` — submodule not checked out
- `vendor/headroom/` — submodule not checked out
