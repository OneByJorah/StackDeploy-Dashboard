<div align="center">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Portainer-13BEF9?style=for-the-badge&logo=portainer&logoColor=white">
  <img src="https://img.shields.io/badge/SearXNG-000?style=for-the-badge&logo=googlesearch&logoColor=white">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
</div>

<br>

<div align="center">
  <h1>📊 StackDeploy Dashboard</h1>
  <p><strong>Unified Dashboard for Self-Hosted Docker Services</strong></p>
  <p>Centralized management, monitoring, and control for your self-hosted infrastructure stack</p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-services">Services</a> •
    <a href="#-architecture">Architecture</a>
  </p>
</div>

---

## ✨ Features

- **Centralized Management** — Single admin panel for all services
- **Portainer Integration** — Visual container lifecycle management
- **Privacy-Focused** — Self-hosted search with SearXNG
- **Vector Storage** — Qdrant for long-term memory and embeddings
- **Browser Automation** — CloakBrowser for automated web tasks
- **Obsidian Integration** — Note-taking and knowledge management
- **Mesh-VPN Ready** — Secure networking out of the box
- **Health Monitoring** — NOC dashboard with service health checks

## 🚀 Quick Start

### Prerequisites
- Docker 24+ & Docker Compose v2
- 8GB+ RAM, 50GB+ disk

### Installation

```bash
git clone https://github.com/OneByJorah/StackDeploy-Dashboard.git
cd StackDeploy-Dashboard
cp .env.example .env
# Edit .env with your configuration
sudo ./bootstrap.sh
```

## 🏗️ Services

| Service | Port | Description |
|---------|------|-------------|
| **SearXNG** | 8080 | Private meta-search engine |
| **Camofox** | 9377 | Privacy-focused browser rendering |
| **CloakBrowser** | 9222 | Stealth browser automation |
| **Qdrant** | 6333 | Vector database for embeddings |
| **PostgreSQL + pgvector** | 5432 | Relational + vector storage |
| **Redis** | 6379 | Caching and pub/sub |
| **Obsidian** | 8083 | Remote vault web UI |
| **Portainer** | 9000/9443 | Container management |
| **NOC Dashboard** | 9500 | Service health monitoring |

## 🐳 Optional Overlays

```bash
# With Portainer + Headroom monitoring
docker compose \
  -f docker-compose.yml \
  -f docker-compose.portainer.yml \
  -f docker-compose.headroom.yml \
  up -d --build
```

## 📄 License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>📊 One dashboard to manage them all</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
