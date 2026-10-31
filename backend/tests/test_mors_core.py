import pytest
from fastapi.testclient import TestClient
from app.core.database import SessionLocal
from app.models.models import Member, User
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_login_success():
    res = client.post("/api/v1/auth/login", json={
        "username": "clerk.lp",
        "password": "Password123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["unit"] == "CLERK_LP"
    assert data["user"]["role"] == "SUPER_USER"

def test_portal_search():
    res = client.get("/api/v1/portal/search?q=Kariuki")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "full_name" in data[0]
        assert "category" in data[0]

def test_portal_prefill():
    res = client.get("/api/v1/portal/member/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert "full_name" in data
    assert "party" in data

def test_dashboard_summary():
    # Login as clerk office to view dashboard
    login_res = client.post("/api/v1/auth/login", json={
        "username": "clerk.office",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    res = client.get("/api/v1/dashboards/summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "funnel" in data
    assert data["funnel"]["total_gazetted"] == 349
    assert len(data["unit_progress"]) == 5

def test_demographic_insights():
    login_res = client.post("/api/v1/auth/login", json={
        "username": "clerk.office",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    res = client.get("/api/v1/dashboards/insights", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "avg_age" in data
    assert "female_share_pct" in data
    assert "party_breakdown" in data

def test_clearance_unit_restrictions():
    # Media relations user should not be able to tick ICT biometrics
    login_res = client.post("/api/v1/auth/login", json={
        "username": "media.lead",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    res = client.post("/api/v1/clearance/ict/biometrics", json={
        "member_id": 1,
        "collected": True
    }, headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 403  # Forbidden for non-ICT
