"""
Unit tests for the StackDeploy Dashboard Gateway API.

Uses FastAPI TestClient with httpx mocking to avoid external network calls.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment before importing the app
os.environ["GATEWAY_USERNAME"] = "admin"
os.environ["GATEWAY_PASSWORD"] = "testpass"

from server import SERVICE_REGISTRY, app

client = TestClient(app)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_env():
    """Ensure test env vars are always set before each test."""
    os.environ["GATEWAY_USERNAME"] = "admin"
    os.environ["GATEWAY_PASSWORD"] = "testpass"
    os.environ.pop("TS_CERT_DOMAIN", None)
    os.environ.pop("CLOUDFLARE_TUNNEL_DOMAIN", None)
    yield


def mock_health_response(healthy=True):
    """Create a mock async context manager for httpx.AsyncClient."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 200 if healthy else 503
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=None)

    mock_client = AsyncMock(spec=AsyncClient)
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


# ── /health endpoint ─────────────────────────────────────────────────────────


class TestHealthEndpoint:
    def test_health_returns_200(self):
        """GET /health should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_schema(self):
        """GET /health should return the correct JSON schema."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "OPERATIONAL"
        assert data["service"] == "StackDeploy Dashboard Gateway"
        assert data["version"] == "2.0.0"

    def test_health_does_not_require_auth(self):
        """GET /health should work without authentication."""
        response = client.get("/health")
        assert response.status_code == 200


# ── /api/v1/discover endpoint ────────────────────────────────────────────────


class TestDiscoverEndpoint:
    def test_discover_returns_200_without_auth(self):
        """GET /api/v1/discover should return 200 even without auth (read-only)."""
        response = client.get("/api/v1/discover")
        assert response.status_code == 200

    def test_discover_returns_200_with_valid_auth(self):
        """GET /api/v1/discover with valid auth should return 200."""
        response = client.get(
            "/api/v1/discover",
            auth=("admin", "testpass"),
        )
        assert response.status_code == 200

    def test_discover_returns_200_with_wrong_auth(self):
        """GET /api/v1/discover with wrong credentials returns 200 (read-only, no auth required)."""
        response = client.get(
            "/api/v1/discover",
            auth=("admin", "wrongpassword"),
        )
        # Discover is read-only; verify_admin_optional auto_error=False means
        # wrong credentials just return None — no 401.
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert data["platform"] == "StackDeploy Dashboard"

    @patch("server.httpx.AsyncClient")
    def test_discover_schema_all_healthy(self, mock_async_client):
        """GET /api/v1/discover should return correct schema with all services."""
        mock_async_client.return_value = mock_health_response(healthy=True)

        response = client.get("/api/v1/discover")
        data = response.json()

        assert data["platform"] == "StackDeploy Dashboard"
        assert data["version"] == "2.0.0"
        assert "services" in data
        assert "healthy_count" in data
        assert "total_count" in data
        assert data["healthy_count"] == data["total_count"]
        assert data["total_count"] == len(SERVICE_REGISTRY)

    @patch("server.httpx.AsyncClient")
    def test_discover_schema_some_down(self, mock_async_client):
        """GET /api/v1/discover should report DEGRADED when some services are down."""
        with patch("server.httpx.AsyncClient") as mock:
            mock.return_value = mock_health_response(healthy=False)

            response = client.get("/api/v1/discover")
            data = response.json()

            assert data["healthy_count"] == 0
            assert data["total_count"] == len(SERVICE_REGISTRY)

    @patch("server.httpx.AsyncClient")
    def test_discover_includes_all_services(self, mock_async_client):
        """GET /api/v1/discover should list all services from the registry."""
        mock_async_client.return_value = mock_health_response(healthy=True)

        response = client.get("/api/v1/discover")
        data = response.json()

        service_names = {s["name"] for s in data["services"]}
        expected_names = set(SERVICE_REGISTRY.keys())
        assert service_names == expected_names

    @patch("server.httpx.AsyncClient")
    def test_discover_service_details(self, mock_async_client):
        """Each service in discover should have name, healthy, description, internal_url."""
        mock_async_client.return_value = mock_health_response(healthy=True)

        response = client.get("/api/v1/discover")
        data = response.json()

        for svc in data["services"]:
            assert "name" in svc
            assert "healthy" in svc
            assert "description" in svc
            assert "internal_url" in svc
            assert isinstance(svc["healthy"], bool)
            assert svc["description"] == SERVICE_REGISTRY[svc["name"]]["description"]

    @patch("server.httpx.AsyncClient")
    def test_discover_includes_tailnet_hostname(self, mock_async_client):
        """TS_CERT_DOMAIN env var should appear in discover response."""
        os.environ["TS_CERT_DOMAIN"] = "test.tailnet.com"
        mock_async_client.return_value = mock_health_response(healthy=True)

        # Re-import app to pick up env var — but lazy approach: just check directly
        from server import app as app2

        c2 = TestClient(app2)
        response = c2.get("/api/v1/discover")
        data = response.json()
        assert data["tailnet_hostname"] == "test.tailnet.com"

    @patch("server.httpx.AsyncClient")
    def test_discover_includes_cloudflare_domain(self, mock_async_client):
        """CLOUDFLARE_TUNNEL_DOMAIN env var should appear in discover response."""
        os.environ["CLOUDFLARE_TUNNEL_DOMAIN"] = "api.example.com"
        mock_async_client.return_value = mock_health_response(healthy=True)

        from server import app as app3

        c3 = TestClient(app3)
        response = c3.get("/api/v1/discover")
        data = response.json()
        assert data["cloudflare_domain"] == "api.example.com"

    @patch("server.httpx.AsyncClient")
    def test_each_service_has_correct_internal_url(self, mock_async_client):
        """Each service should expose its internal_url matching the registry."""
        mock_async_client.return_value = mock_health_response(healthy=True)

        response = client.get("/api/v1/discover")
        data = response.json()

        for svc in data["services"]:
            registered = SERVICE_REGISTRY[svc["name"]]
            expected_url = f"http://{registered['host']}:{registered['port']}"
            assert svc["internal_url"] == expected_url


# ── /api/v1/health endpoint ─────────────────────────────────────────────────


class TestAggregatedHealthEndpoint:
    def test_aggregated_health_returns_200(self):
        """GET /api/v1/health should return 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    @patch("server.httpx.AsyncClient")
    def test_aggregated_health_all_healthy(self, mock_async_client):
        """GET /api/v1/health should return OPERATIONAL when all services are up."""
        mock_async_client.return_value = mock_health_response(healthy=True)

        response = client.get("/api/v1/health")
        data = response.json()

        assert data["status"] == "OPERATIONAL"
        assert data["healthy_count"] == data["total_count"]
        assert data["total_count"] == len(SERVICE_REGISTRY)

    @patch("server.httpx.AsyncClient")
    def test_aggregated_health_degraded(self, mock_async_client):
        """GET /api/v1/health should return DEGRADED when some services are down."""
        mock_async_client.return_value = mock_health_response(healthy=False)

        response = client.get("/api/v1/health")
        data = response.json()

        assert data["status"] == "DEGRADED"
        assert data["healthy_count"] == 0

    @patch("server.httpx.AsyncClient")
    def test_aggregated_health_services_list(self, mock_async_client):
        """GET /api/v1/health services should have all fields."""
        mock_async_client.return_value = mock_health_response(healthy=True)

        response = client.get("/api/v1/health")
        data = response.json()

        for svc in data["services"]:
            assert "name" in svc
            assert "healthy" in svc
            assert "description" in svc
            assert "internal_url" in svc


# ── /onboard and / endpoints ─────────────────────────────────────────────────


class TestOnboardingEndpoints:
    def test_onboard_returns_html(self):
        """GET /onboard should return HTML."""
        response = client.get("/onboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_onboard_contains_title(self):
        """GET /onboard should contain the dashboard title."""
        response = client.get("/onboard")
        assert "StackDeploy Dashboard" in response.text
        assert "Service Islands" in response.text
        assert "Agent Onboarding API" in response.text

    def test_onboard_contains_discover_endpoint_link(self):
        """GET /onboard should link to /api/v1/discover."""
        response = client.get("/onboard")
        assert "/api/v1/discover" in response.text

    def test_root_redirects_to_onboard(self):
        """GET / should return the onboarding HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "StackDeploy Dashboard" in response.text


# ── Auth edge cases ─────────────────────────────────────────────────────────


class TestAuthEdgeCases:
    def test_discover_no_auth_still_returns_services(self):
        """Without auth, /api/v1/discover should still return services."""
        response = client.get("/api/v1/discover")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data

    def test_discover_with_auth_returns_same_structure(self):
        """With valid auth, /api/v1/discover should have same structure."""
        unauth = client.get("/api/v1/discover").json()
        auth = client.get("/api/v1/discover", auth=("admin", "testpass")).json()

        assert unauth["platform"] == auth["platform"]
        assert unauth["total_count"] == auth["total_count"]
        assert set(s["name"] for s in unauth["services"]) == set(
            s["name"] for s in auth["services"]
        )

    def test_health_ignores_auth(self):
        """/health should work identically with or without auth."""
        unauth = client.get("/health")
        auth = client.get("/health", auth=("admin", "testpass"))
        assert unauth.status_code == auth.status_code == 200
        assert unauth.json() == auth.json()


# ── Service registry integrity ──────────────────────────────────────────────


class TestServiceRegistry:
    def test_all_services_have_required_fields(self):
        """Every service in the registry must have host, port, description, health_endpoint."""
        for name, svc in SERVICE_REGISTRY.items():
            assert "host" in svc, f"{name} missing host"
            assert "port" in svc, f"{name} missing port"
            assert "description" in svc, f"{name} missing description"
            assert "health_endpoint" in svc, f"{name} missing health_endpoint"
            assert isinstance(svc["port"], int), f"{name} port must be int"
            assert svc["description"], f"{name} description is empty"

    def test_host_port_mapping_unique(self):
        """Each service should have a unique host:port combination."""
        host_ports = [(svc["host"], svc["port"]) for svc in SERVICE_REGISTRY.values()]
        assert len(host_ports) == len(set(host_ports)), (
            "Duplicate host:port found in SERVICE_REGISTRY"
        )
        # Note: Docker allows different containers to use the same internal port.
        # searxng and obsidian both use port 8080 internally but have different hostnames.

    def test_unique_host_names(self):
        """No two services should share the same hostname."""
        hosts = [svc["host"] for svc in SERVICE_REGISTRY.values()]
        assert len(hosts) == len(set(hosts)), "Duplicate hostnames in SERVICE_REGISTRY"
