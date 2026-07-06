<!-- j1-brand:v2 -->
<div align="center">

# StackDeploy Dashboard

A self-hosted all-in-one API platform gateway — deploy and manage SearXNG, Qdrant, Honcho, Ollama, Camofox, and Obsidian behind a single dashboard with Tailscale mesh networking.

[![GitHub](https://img.shields.io/badge/github-OneByJorah%2FStackDeploy--Dashboard-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah/StackDeploy-Dashboard)
[![License](https://img.shields.io/badge/license-MIT-FFB300?style=for-the-badge&labelColor=0d0d0c)](LICENSE)
[![Language](https://img.shields.io/badge/JavaScript-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://javascript.com)
[![Built by](https://img.shields.io/badge/built%20by-JorahOne%20LLC-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah)

</div>

---

## Why This Exists

StackDeploy got your infrastructure running — now you need a dashboard to manage it. StackDeploy Dashboard provides a unified gateway with auto-discoverable APIs, Tailscale mesh networking, and optional Cloudflare Tunneling for HTTPS. A zero-config bootstrap option automates password generation, stack deployment, and Ollama configuration.

## Key Features

| Feature | Why It Matters |
|---|---|
| Unified service gateway | One dashboard to manage all StackDeploy services |
| Auto-discoverable APIs | Agents auto-configure via `/api/v1/discover` |
| Zero-config bootstrap | `sudo ./bootstrap.sh --auto` handles everything |
| Flexible LLM routing | Local Ollama or cloud APIs (OpenRouter) |
| Tailscale mesh networking | Secure service-to-service communication |
| Cloudflare Tunneling | HTTPS without opening firewall ports |

## Quick Start

```bash
git clone https://github.com/OneByJorah/StackDeploy-Dashboard.git
cd StackDeploy-Dashboard

# Zero-config (recommended)
sudo ./bootstrap.sh --auto

# Interactive setup
./setup.sh
```

## Documentation

| Doc | Description |
|---|---|
| [Getting Started](docs/start.md) | Prerequisites and deployment |
| [Service Configuration](docs/services.md) | Managing the stack services |
| [Networking](docs/networking.md) | Tailscale and Cloudflare Tunnel setup |

---

## License

MIT © JorahOne, LLC — see [LICENSE](LICENSE)

<sub>Part of the JorahOne infrastructure ecosystem.</sub>
