"""
Integration tests for the StackDeploy Dashboard Gateway.

These tests hit the live, deployed stack (gateway on localhost:9090).
They verify that the actual running services report correct health,
that the discover API returns the expected service registry, and that
the onboarding page renders correctly.

Prerequisites:
  - The full stack must be deployed: sudo ./bootstrap.sh
  - Gateway must be accessible at http://localhost:9090

Run with:  pytest gateway/tests/test_integration.py -v
"""

import os
import time
from urllib.parse import urlparse

import httpx
import pytest

# ── Configuration ────────────────────────────────────────────────────────────

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:9090")
GATEWAY_USERNAME = os.getenv("GATEWAY_USERNAME", "admin")
GATEWAY_PASSWORD = os.getenv("GATEWAY_PASSWORD", "testpass123")
HEALTHCHECK_TIMEOUT = 5.0  # seconds per service health check

# Services that are expected to always be online (cloakbrowser requires private ghcr.io)
ALWAYS_ONLINE = {
    "gateway": {"host": "gateway", "port": 9090, "description": "StackDeploy Gateway API"},
    "searxng": {"host": "searxng", "port": 8080, "description": "Private meta-search engine"},
    "qdrant": {"host": "qdrant", "port": 6333, "description": "Vector database"},
    "honcho": {"host": "honcho", "port": 8000, "description": "AI memory & session management"},
    "camofox": {"host": "camofox-browser", "port": 9377, "description": "Browser automation"},
    "obsidian": {"host": "obsidian", "port": 8080, "description": "Notes & knowledge management"},
    "ollama": {"host": "ollama", "port": 11434, "description": "Local LLM inference"},
}

# Services that may be offline (private images, not deployed)
OPTIONALLY_OFFLINE = {
    "cloakbrowser": {"host": "cloak-browser", "port": 9222, "description": "Protected browser"},
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_json(path: str, auth: tuple = None) -> dict:
    """GET a path on the gateway and return parsed JSON."""
    url = f"{GATEWAY_URL}{path}"
    resp = httpx.get(url, auth=auth, timeout=HEALTHCHECK_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_text(path: str) -> str:
    """GET a path and return raw text (for HTML)."""
    url = f"{GATEWAY_URL}{path}"
    resp = httpx.get(url, timeout=HEALTHCHECK_TIMEOUT)
    resp.raise_for_status()
    return resp.text


# ── Pre-checks ───────────────────────────────────────────────────────────────

def test_gateway_is_reachable():
    """The gateway must be running before any integration tests run."""
    try:
        resp = httpx.get(f"{GATEWAY_URL}/health", timeout=3.0)
        assert resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutError) as e:
        pytest.fail(
            f"Gateway unreachable at {GATEWAY_URL}/health.\n"
            f"Deploy the stack first: sudo ./bootstrap.sh\n"
            f"Error: {e}"
        )


# ── /health endpoint ─────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self):
        data = get_json("/health")
        assert data["status"] == "OPERATIONAL"
        assert data["service"] == "StackDeploy Dashboard Gateway"
        assert data["version"] == "2.0.0"

    def test_health_no_auth_required(self):
        resp = httpx.get(f"{GATEWAY_URL}/health", timeout=HEALTHCHECK_TIMEOUT)
        assert resp.status_code == 200

    def test_health_ignores_bad_auth(self):
        resp = httpx.get(
            f"{GATEWAY_URL}/health",
            auth=("admin", "wrong"),
            timeout=HEALTHCHECK_TIMEOUT,
        )
        assert resp.status_code == 200


# ── /api/v1/discover endpoint ────────────────────────────────────────────────

class TestDiscoverEndpoint:
    def test_discover_returns_200(self):
        data = get_json("/api/v1/discover")
        assert data["platform"] == "StackDeploy Dashboard"
        assert data["version"] == "2.0.0"

    def test_discover_lists_all_services(self):
        data = get_json("/api/v1/discover")
        service_names = {s["name"] for s in data["services"]}

        # All always-online services must be present
        for name in ALWAYS_ONLINE:
            assert name in service_names, f"Missing service: {name}"

        # cloakbrowser may or may not be present (requires private ghcr.io image)

    def test_discover_counts_are_reasonable(self):
        """At minimum the gateway itself must be healthy."""
        data = get_json("/api/v1/discover")
        assert data["total_count"] >= len(ALWAYS_ONLINE)
        assert data["healthy_count"] >= 1  # Gateway is always healthy
        assert data["healthy_count"] <= data["total_count"]

    def test_discover_each_service_has_required_fields(self):
        data = get_json("/api/v1/discover")
        for svc in data["services"]:
            assert "name" in svc, f"Service missing 'name'"
            assert "healthy" in svc, f"{svc.get('name', '?')} missing 'healthy'"
            assert "description" in svc, f"{svc['name']} missing 'description'"
            assert "internal_url" in svc, f"{svc['name']} missing 'internal_url'"
            assert isinstance(svc["healthy"], bool), f"{svc['name']} 'healthy' must be bool"
            assert isinstance(svc["description"], str), f"{svc['name']} 'description' must be str"
            # internal_url must be a valid URL
            parsed = urlparse(svc["internal_url"])
            assert parsed.scheme in ("http", "https"), f"{svc['name']} bad URL scheme: {svc['internal_url']}"
            assert parsed.hostname, f"{svc['name']} bad URL: {svc['internal_url']}"

    def test_discover_gateway_is_healthy(self):
        """The gateway service should always report healthy (it pings itself)."""
        data = get_json("/api/v1/discover")
        gw = next(s for s in data["services"] if s["name"] == "gateway")
        assert gw["healthy"] is True
        assert gw["internal_url"] == "http://gateway:9090"

    def test_discover_works_without_auth(self):
        """Read-only discover should work without authentication."""
        data = get_json("/api/v1/discover")
        assert "services" in data

    def test_discover_works_with_valid_auth(self):
        data = get_json("/api/v1/discover", auth=(GATEWAY_USERNAME, GATEWAY_PASSWORD))
        assert "services" in data

    def test_discover_works_with_wrong_auth(self):
        """Wrong auth should still return data (read-only, auto_error=False)."""
        data = get_json("/api/v1/discover", auth=("admin", "wrong"))
        assert "services" in data
        assert data["platform"] == "StackDeploy Dashboard"

    def test_discover_includes_healthy_count(self):
        data = get_json("/api/v1/discover")
        assert isinstance(data["healthy_count"], int)
        assert isinstance(data["total_count"], int)
        assert data["healthy_count"] >= 1  # At least gateway
        assert data["total_count"] >= len(ALWAYS_ONLINE)

    def test_discover_internal_urls_are_docker_hostnames(self):
        """Internal URLs should use Docker service names, not localhost."""
        data = get_json("/api/v1/discover")
        for svc in data["services"]:
            url = svc["internal_url"]
            parsed = urlparse(url)
            # The hostname should be a Docker service name, not localhost or IP
            assert parsed.hostname != "localhost", f"{svc['name']} uses localhost, not Docker hostname"
            assert parsed.hostname != "127.0.0.1", f"{svc['name']} uses 127.0.0.1, not Docker hostname"

    def test_discover_gateway_url_matches(self):
        """Gateway's internal URL should point to itself."""
        data = get_json("/api/v1/discover")
        gw = next(s for s in data["services"] if s["name"] == "gateway")
        assert gw["internal_url"] == f"http://gateway:{ALWAYS_ONLINE['gateway']['port']}"

    def test_discover_searxng_port(self):
        data = get_json("/api/v1/discover")
        sx = next(s for s in data["services"] if s["name"] == "searxng")
        assert "8080" in sx["internal_url"]

    def test_discover_honcho_port(self):
        data = get_json("/api/v1/discover")
        hn = next(s for s in data["services"] if s["name"] == "honcho")
        assert "8000" in hn["internal_url"]

    def test_discover_ollama_port(self):
        data = get_json("/api/v1/discover")
        ol = next(s for s in data["services"] if s["name"] == "ollama")
        assert "11434" in ol["internal_url"]

    def test_discover_ollama_is_healthy(self):
        """Ollama should be healthy when deployed with --with-local-llm."""
        data = get_json("/api/v1/discover")
        ol = next(s for s in data["services"] if s["name"] == "ollama")
        assert ol["healthy"] is True, "Ollama should be healthy when stack is deployed with --with-local-llm"


# ── /api/v1/health endpoint ─────────────────────────────────────────────────

class TestAggregatedHealthEndpoint:
    def test_health_returns_200(self):
        data = get_json("/api/v1/health")
        assert data["status"] in ("OPERATIONAL", "DEGRADED")

    def test_health_has_services_list(self):
        data = get_json("/api/v1/health")
        assert "services" in data
        assert len(data["services"]) >= len(ALWAYS_ONLINE)

    def test_health_counts_match_services(self):
        data = get_json("/api/v1/health")
        assert len(data["services"]) == data["total_count"]
        actual_healthy = sum(1 for s in data["services"] if s["healthy"])
        assert data["healthy_count"] == actual_healthy

    def test_health_gateway_is_healthy(self):
        data = get_json("/api/v1/health")
        gw = next(s for s in data["services"] if s["name"] == "gateway")
        assert gw["healthy"] is True

    def test_health_no_auth_required(self):
        resp = httpx.get(f"{GATEWAY_URL}/api/v1/health", timeout=HEALTHCHECK_TIMEOUT)
        assert resp.status_code == 200


# ── /onboard and / endpoints ────────────────────────────────────────────────

class TestOnboardingEndpoints:
    def test_onboard_returns_html(self):
        html = get_text("/onboard")
        assert "StackDeploy Dashboard" in html
        assert "Service Islands" in html
        assert "Agent Onboarding API" in html
        assert "/api/v1/discover" in html

    def test_onboard_contains_service_grid(self):
        html = get_text("/onboard")
        assert 'id="service-grid"' in html
        assert 'id="status-badge"' in html
        assert 'id="discover-json"' in html

    def test_onboard_has_refresh_button(self):
        html = get_text("/onboard")
        assert "Refresh" in html

    def test_root_returns_onboarding_html(self):
        html = get_text("/")
        assert "StackDeploy Dashboard" in html
        assert "Service Islands" in html

    def test_onboard_has_health_link(self):
        html = get_text("/onboard")
        assert "/api/v1/health" in html

    def test_onboard_javascript_fetch_target(self):
        """The onboarding page should reference the correct API path."""
        html = get_text("/onboard")
        assert "'/api/v1/discover'" in html or '"/api/v1/discover"' in html


# ── Cross-endpoint consistency ──────────────────────────────────────────────

class TestCrossEndpointConsistency:
    def test_discover_and_health_return_same_services(self):
        """Both /api/v1/discover and /api/v1/health should list the same services."""
        discover = get_json("/api/v1/discover")
        health = get_json("/api/v1/health")

        d_names = {s["name"] for s in discover["services"]}
        h_names = {s["name"] for s in health["services"]}
        assert d_names == h_names, f"Service names differ between endpoints"

    def test_discover_and_health_same_counts(self):
        discover = get_json("/api/v1/discover")
        health = get_json("/api/v1/health")
        assert discover["total_count"] == health["total_count"]
        assert discover["healthy_count"] == health["healthy_count"]

    def test_service_descriptions_match(self):
        """A service should have the same description in discover and health."""
        discover = get_json("/api/v1/discover")
        health = get_json("/api/v1/health")

        d_map = {s["name"]: s["description"] for s in discover["services"]}
        h_map = {s["name"]: s["description"] for s in health["services"]}
        for name in d_map:
            assert d_map[name] == h_map[name], f"Description mismatch for {name}"


# ── Gateway health check endpoint ───────────────────────────────────────────
