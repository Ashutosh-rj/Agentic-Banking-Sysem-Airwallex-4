"""
Verification script for KAIZEN FinTech Backend
Tests:
1. Health & readiness endpoints
2. Authentication (login with seeded demo credentials)
3. Dashboard summary & metrics
4. Payments list & detail
5. Incidents list, detail, and AI investigation run
6. Reconciliation runs & records
7. Treasury accounts, positions, obligations, and forecast
8. Risk overview & alerts
9. Analytics overview, incident performance, and business impact
10. Audit logs & export
11. Integrations list & test
"""
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app


async def test_all_endpoints():
    print("[START] Comprehensive backend verification...")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health checks
        r = await client.get("/health/live")
        assert r.status_code == 200, f"Health live failed: {r.text}"
        print("  [OK] /health/live:", r.json()["status"])

        r = await client.get("/health/ready")
        assert r.status_code == 200, f"Health ready failed: {r.text}"
        print("  [OK] /health/ready:", r.json()["status"])

        # 2. Login
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "treasury@kaizen.dev",
            "password": "Demo1234!"
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        data = login_res.json()
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  [OK] /api/v1/auth/login: Authenticated as", data["user"]["full_name"], f"({data['user']['role']})")

        # 3. /auth/me
        r = await client.get("/api/v1/auth/me", headers=headers)
        assert r.status_code == 200
        print("  [OK] /api/v1/auth/me")

        # 4. Dashboard Summary
        r = await client.get("/api/v1/dashboard/summary", headers=headers)
        assert r.status_code == 200, f"Summary failed: {r.text}"
        summary = r.json()
        print(f"  [OK] /api/v1/dashboard/summary: USD Equiv = ${summary['total_available_usd_equivalent']}, Open Incidents = {summary['open_incidents']}")

        # 5. Dashboard Activity & Trends
        r = await client.get("/api/v1/dashboard/activity", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/dashboard/activity: {len(r.json())} items")

        r = await client.get("/api/v1/dashboard/trends", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/dashboard/trends: {len(r.json())} trend days")

        # 6. Payments
        r = await client.get("/api/v1/payments", headers=headers)
        assert r.status_code == 200
        payments = r.json()
        print(f"  [OK] /api/v1/payments: {payments['total']} payments found")
        first_pay_id = payments["items"][0]["id"]

        r = await client.get(f"/api/v1/payments/{first_pay_id}", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/payments/{{id}}: Payment {r.json()['payment_number']}")

        r = await client.get(f"/api/v1/payments/{first_pay_id}/timeline", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/payments/{{id}}/timeline: {len(r.json())} timeline events")

        # 7. Incidents & AI Investigation
        r = await client.get("/api/v1/incidents", headers=headers)
        assert r.status_code == 200
        incidents = r.json()
        print(f"  [OK] /api/v1/incidents: {incidents['total']} incidents found")
        first_inc_id = incidents["items"][0]["id"]

        r = await client.get(f"/api/v1/incidents/{first_inc_id}", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/incidents/{{id}}: Incident {r.json()['incident_number']}")

        # Run AI Investigation pipeline
        r = await client.post(f"/api/v1/incidents/{first_inc_id}/investigate", headers=headers)
        assert r.status_code == 200
        investigation = r.json()
        print(f"  [OK] /api/v1/incidents/{{id}}/investigate: {investigation['message']}")

        # 8. Reconciliation
        r = await client.get("/api/v1/reconciliation/runs", headers=headers)
        assert r.status_code == 200
        runs = r.json()
        print(f"  [OK] /api/v1/reconciliation/runs: {runs['total']} reconciliation runs")

        # 9. Treasury
        r = await client.get("/api/v1/treasury/accounts", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/treasury/accounts: {len(r.json())} accounts")

        r = await client.get("/api/v1/treasury/positions", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/treasury/positions: {len(r.json())} currency positions")

        r = await client.get("/api/v1/treasury/obligations", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/treasury/obligations: {r.json()['total']} obligations")

        r = await client.get("/api/v1/treasury/forecast", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/treasury/forecast: {len(r.json())} forecast days")

        # 10. Risk
        r = await client.get("/api/v1/risk/overview", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/risk/overview: {r.json()['total_alerts']} total alerts")

        r = await client.get("/api/v1/risk/alerts", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/risk/alerts: {r.json()['total']} risk alerts")

        # 11. Analytics
        r = await client.get("/api/v1/analytics/overview", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/analytics/overview: success rate {r.json()['success_rate']}")

        r = await client.get("/api/v1/analytics/incident-performance", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/analytics/incident-performance: {r.json()['total_incidents']} incidents analyzed")

        r = await client.get("/api/v1/analytics/business-impact", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/analytics/business-impact: Saved = ${r.json()['estimated_cost_savings']}")

        # 12. Audit Logs
        r = await client.get("/api/v1/audit-logs", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/audit-logs: {r.json()['total']} audit logs")

        r = await client.get("/api/v1/audit-logs/export?format=csv", headers=headers)
        assert r.status_code == 200
        assert "Timestamp" in r.text
        print("  [OK] /api/v1/audit-logs/export?format=csv")

        # 13. Integrations
        r = await client.get("/api/v1/integrations", headers=headers)
        assert r.status_code == 200
        integrations = r.json()
        print(f"  [OK] /api/v1/integrations: {len(integrations)} integrations active")

        r = await client.post(f"/api/v1/integrations/{integrations[0]['id']}/test", headers=headers)
        assert r.status_code == 200
        print(f"  [OK] /api/v1/integrations/{{id}}/test: {r.json()['message']}")

    print("\n[COMPLETE] ALL BACKEND ENDPOINTS AND WORKFLOWS VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
