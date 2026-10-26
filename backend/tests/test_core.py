import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client):
    res = await client.post("/api/v1/auth/login", json={
        "email": "treasury@kaizen.dev",
        "password": "Demo1234!"
    })
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_health_endpoints(client):
    res = await client.get("/health/live")
    assert res.status_code == 200
    assert res.json()["status"] == "alive"

    res = await client.get("/health/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_auth_me(client, auth_token):
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "treasury@kaizen.dev"
    assert res.json()["role"] == "treasury_manager"


@pytest.mark.asyncio
async def test_dashboard_summary(client, auth_token):
    res = await client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = res.json()
    assert float(data["total_available_usd_equivalent"]) > 0
    assert data["open_incidents"] >= 0


@pytest.mark.asyncio
async def test_payments_list(client, auth_token):
    res = await client.get("/api/v1/payments?page=1&page_size=10", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) > 0
    assert data["total"] > 0


@pytest.mark.asyncio
async def test_incidents_and_investigation(client, auth_token):
    res = await client.get("/api/v1/incidents", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    incidents = res.json()["items"]
    assert len(incidents) > 0

    first_id = incidents[0]["id"]
    inv_res = await client.post(f"/api/v1/incidents/{first_id}/investigate", headers={"Authorization": f"Bearer {auth_token}"})
    assert inv_res.status_code == 200
    assert "report" in inv_res.json()


@pytest.mark.asyncio
async def test_treasury_positions(client, auth_token):
    res = await client.get("/api/v1/treasury/positions", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    positions = res.json()
    assert len(positions) > 0
    currencies = [p["currency"] for p in positions]
    assert "USD" in currencies


@pytest.mark.asyncio
async def test_risk_duplicate_check(client, auth_token):
    res = await client.post("/api/v1/risk/check-duplicate", headers={"Authorization": f"Bearer {auth_token}"}, json={
        "amount": "125000.00",
        "beneficiary_id": "test-ben"
    })
    assert res.status_code == 200
    assert "is_duplicate_risk" in res.json()


@pytest.mark.asyncio
async def test_audit_logs_and_export(client, auth_token):
    res = await client.get("/api/v1/audit-logs", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert res.json()["total"] > 0

    csv_res = await client.get("/api/v1/audit-logs/export?format=csv", headers={"Authorization": f"Bearer {auth_token}"})
    assert csv_res.status_code == 200
    assert "Timestamp" in csv_res.text


@pytest.mark.asyncio
async def test_integrations_probe(client, auth_token):
    res = await client.get("/api/v1/integrations", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    integrations = res.json()
    assert len(integrations) > 0

    first_id = integrations[0]["id"]
    test_res = await client.post(f"/api/v1/integrations/{first_id}/test", headers={"Authorization": f"Bearer {auth_token}"})
    assert test_res.status_code == 200
    assert test_res.json()["status"] == "healthy"
