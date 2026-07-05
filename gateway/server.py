"""
StackDeploy Dashboard — Gateway API

Single ingress point for all backend services. Provides:
  - /onboard    → HTML onboarding page for human operators
  - /api/v1/discover → JSON endpoint for agents to auto-configure
  - /api/v1/health   → Aggregated health status of all services
  - /api/v1/config   → Update configuration (requires admin auth)
"""

import os
from typing import Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(
    title="StackDeploy Dashboard API",
    version="2.0.0",
    description="Self-hosted all-in-one API platform — auto-discover services, check health, and configure agents.",
)

# Security: auto_error=False allows unauthenticated read-only access
security = HTTPBasic(auto_error=False)

# ── Config (from env) ─────────────────────────────────────────────────────────
GATEWAY_USERNAME = os.getenv("GATEWAY_USERNAME", "admin")
GATEWAY_PASSWORD = os.getenv("GATEWAY_PASSWORD", "changeme")

# Service registry — maps service names to their internal Docker host:port
# In Docker Compose, services are reachable by their container name.
SERVICE_REGISTRY = {
    "searxng": {
        "host": "searxng",
        "port": 8080,
        "description": "Private meta-search engine",
        "health_endpoint": "/search?q=healthcheck&format=json",
    },
    "qdrant": {
        "host": "qdrant",
        "port": 6333,
        "description": "Vector database for semantic memory",
        "health_endpoint": "/healthz",
    },
    "honcho": {
        "host": "honcho",
        "port": 8000,
        "description": "AI memory & session management",
        "health_endpoint": "/health",
    },
    "camofox": {
        "host": "camofox-browser",
        "port": 9377,
        "description": "Browser automation service",
        "health_endpoint": "/health",
    },
    "obsidian": {
        "host": "obsidian",
        "port": 8080,
        "description": "Notes & knowledge management",
        "health_endpoint": "/",
    },
    "ollama": {
        "host": "ollama",
        "port": 11434,
        "description": "Local LLM inference (Ollama) — pull models with: docker exec ollama ollama pull <model>",
        "health_endpoint": "/api/tags",
    },
    "cloakbrowser": {
        "host": "cloak-browser",
        "port": 9222,
        "description": "Protected browser for authenticated sites",
        "health_endpoint": "/json/version",
    },
    "gateway": {
        "host": "gateway",
        "port": 9090,
        "description": "StackDeploy Gateway API (this service)",
        "health_endpoint": "/health",
    },
}


# ── Auth ──────────────────────────────────────────────────────────────────────
def verify_admin(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    if (
        credentials.username != GATEWAY_USERNAME
        or credentials.password != GATEWAY_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def verify_admin_optional(
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
):
    """Returns username if authenticated, None if no auth provided."""
    if credentials is None:
        return None
    if (
        credentials.username == GATEWAY_USERNAME
        and credentials.password == GATEWAY_PASSWORD
    ):
        return credentials.username
    return None


# ── Health checks ─────────────────────────────────────────────────────────────
async def check_service_health(name: str, svc: dict) -> dict:
    """Ping a service's health endpoint and return status."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"http://{svc['host']}:{svc['port']}{svc['health_endpoint']}"
            resp = await client.get(url)
            healthy = resp.status_code < 500
    except (httpx.ConnectError, httpx.TimeoutException):
        healthy = False
    return {
        "name": name,
        "healthy": healthy,
        "description": svc["description"],
        "internal_url": f"http://{svc['host']}:{svc['port']}",
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    """Basic health check for the gateway itself."""
    return {
        "status": "OPERATIONAL",
        "service": "StackDeploy Dashboard Gateway",
        "version": "2.0.0",
    }


@app.get("/api/v1/health")
async def aggregated_health():
    """Aggregated health status of all backend services."""
    results = []
    for name, svc in SERVICE_REGISTRY.items():
        result = await check_service_health(name, svc)
        results.append(result)
    all_healthy = all(r["healthy"] for r in results)
    return {
        "status": "OPERATIONAL" if all_healthy else "DEGRADED",
        "services": results,
        "healthy_count": sum(1 for r in results if r["healthy"]),
        "total_count": len(results),
    }


@app.get("/api/v1/discover")
async def discover(credentials: Optional[str] = Depends(verify_admin_optional)):
    """
    Agent onboarding endpoint.
    Returns all available services with their connection details.
    Agents hit this to auto-configure themselves to the local API stack.

    Read-only access is available without authentication for the onboarding dashboard.
    Authentication is required for agent configuration and write operations.
    """
    results = []
    for name, svc in SERVICE_REGISTRY.items():
        result = await check_service_health(name, svc)
        results.append(result)

    # Tailnet info (if available)
    tailscale_hostname = os.getenv("TS_CERT_DOMAIN", "")

    return {
        "platform": "StackDeploy Dashboard",
        "version": "2.0.0",
        "tailnet_hostname": tailscale_hostname,
        "cloudflare_domain": os.getenv("CLOUDFLARE_TUNNEL_DOMAIN", ""),
        "services": results,
        "healthy_count": sum(1 for r in results if r["healthy"]),
        "total_count": len(results),
    }


# ── Onboarding HTML page ──────────────────────────────────────────────────────

ONBOARDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StackDeploy Dashboard — Onboarding</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'JetBrains Mono', 'Courier New', monospace; background: #0a0e1a; color: #e2e8f0; min-height: 100vh; }
.container { max-width: 960px; margin: 0 auto; padding: 2rem; }
.header { text-align: center; margin-bottom: 2.5rem; }
.header h1 { color: #FFB300; font-size: 1.8rem; letter-spacing: -0.02em; margin-bottom: 0.5rem; }
.header p { color: #64748b; font-size: 0.85rem; }
.header .badge { display: inline-block; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1rem; }
.badge-ok { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.badge-warn { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-err { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.service-grid { display: grid; gap: 0.75rem; margin-bottom: 2rem; }
.service-card { background: #0d1526; border: 1px solid rgba(255,179,0,0.12); border-radius: 10px; padding: 1rem 1.25rem; display: flex; align-items: center; justify-content: space-between; transition: border-color 0.2s; }
.service-card:hover { border-color: rgba(255,179,0,0.25); }
.service-info .name { font-weight: 600; font-size: 0.9rem; }
.service-info .desc { color: #64748b; font-size: 0.78rem; margin-top: 2px; }
.service-status { font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
.status-up { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.status-down { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.status-unknown { background: rgba(100,116,139,0.15); color: #64748b; border: 1px solid rgba(100,116,139,0.2); }
.service-url { font-size: 0.75rem; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }
.actions { display: flex; gap: 0.75rem; justify-content: center; margin: 2rem 0; }
.btn { padding: 0.6rem 1.5rem; border-radius: 8px; border: 1px solid rgba(255,179,0,0.3); background: transparent; color: #FFB300; font-family: inherit; font-size: 0.85rem; font-weight: 500; cursor: pointer; transition: all 0.15s; text-decoration: none; }
.btn:hover { background: rgba(255,179,0,0.1); border-color: #FFB300; }
.btn-primary { background: #FFB300; color: #0a0e1a; border-color: #FFB300; font-weight: 700; }
.btn-primary:hover { background: #ffc233; }
.discover-json { background: #070b14; border: 1px solid rgba(255,179,0,0.1); border-radius: 8px; padding: 1.25rem; font-size: 0.78rem; color: #a6e3a1; max-height: 300px; overflow-y: auto; white-space: pre-wrap; margin-top: 1rem; }
.footer { text-align: center; color: #475569; font-size: 0.75rem; margin-top: 3rem; }
.title-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
.title-row h2 { font-size: 1.1rem; color: #FFB300; }
.copy-btn { background: transparent; border: 1px solid rgba(255,179,0,0.2); color: #FFB300; padding: 0.3rem 0.8rem; border-radius: 6px; cursor: pointer; font-size: 0.75rem; font-family: inherit; }
.copy-btn:hover { background: rgba(255,179,0,0.1); }
.loading { text-align: center; color: #64748b; padding: 2rem; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>⛭ StackDeploy Dashboard</h1>
    <p>Self-hosted API platform — auto-discover all services</p>
    <div id="status-badge" class="badge badge-ok">● Checking...</div>
  </div>

  <div class="title-row">
    <h2>🔌 Service Islands</h2>
    <button class="copy-btn" onclick="copyDiscoverURL()">📋 Copy API URL</button>
  </div>

  <div id="service-grid" class="service-grid">
    <div class="loading">⟳ Loading service status...</div>
  </div>

  <div class="actions">
    <a class="btn btn-primary" href="/api/v1/discover" target="_blank">🚀 Agent Onboarding API</a>
    <a class="btn" href="/api/v1/health" target="_blank">📊 Health Dashboard</a>
    <button class="btn" onclick="refreshStatus()">↻ Refresh</button>
  </div>

  <div class="title-row">
    <h2>📋 Discover JSON</h2>
    <button class="copy-btn" onclick="copyDiscoverJSON()">📋 Copy</button>
  </div>
  <div id="discover-json" class="discover-json">Loading...</div>

  <div class="footer">
    JorahOne LLC · StackDeploy Dashboard v2.0
  </div>
</div>

<script>
async function refreshStatus() {
  document.getElementById('service-grid').innerHTML = '<div class="loading">⟳ Refreshing...</div>';
  try {
    const resp = await fetch('/api/v1/discover');
    const data = await resp.json();

    // Update badge
    const badge = document.getElementById('status-badge');
    if (data.healthy_count === data.total_count) {
      badge.textContent = '● All Systems Operational';
      badge.className = 'badge badge-ok';
    } else if (data.healthy_count > 0) {
      badge.textContent = `● ${data.healthy_count}/${data.total_count} Online`;
      badge.className = 'badge badge-warn';
    } else {
      badge.textContent = '● All Services Down';
      badge.className = 'badge badge-err';
    }

    // Render services
    let html = '';
    data.services.forEach(s => {
      const statusClass = s.healthy ? 'status-up' : 'status-down';
      const statusText = s.healthy ? '● Online' : '○ Offline';
      html += `
        <div class="service-card">
          <div class="service-info">
            <div class="name">${s.name}</div>
            <div class="desc">${s.description}</div>
            <div class="service-url">${s.internal_url}</div>
          </div>
          <div>
            <span class="service-status ${statusClass}">${statusText}</span>
          </div>
        </div>
      `;
    });
    document.getElementById('service-grid').innerHTML = html;

    // Show discover JSON
    document.getElementById('discover-json').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById('service-grid').innerHTML = '<div style="color:#ef4444;text-align:center;padding:2rem;">✖ Failed to connect to gateway</div>';
    document.getElementById('discover-json').textContent = 'Error: ' + e.message;
  }
}

function copyDiscoverURL() {
  navigator.clipboard.writeText(window.location.origin + '/api/v1/discover');
}

function copyDiscoverJSON() {
  const text = document.getElementById('discover-json').textContent;
  navigator.clipboard.writeText(text);
}

// Auto-refresh on load
refreshStatus();
// Auto-refresh every 30 seconds
setInterval(refreshStatus, 30000);
</script>
</body>
</html>
"""


@app.get("/onboard", response_class=HTMLResponse)
async def onboarding_page():
    """Human-friendly onboarding page showing all service status."""
    return ONBOARDING_HTML


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root redirects to onboarding."""
    return ONBOARDING_HTML
