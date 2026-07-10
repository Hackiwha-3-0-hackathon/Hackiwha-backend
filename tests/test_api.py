import pytest
import httpx
import uuid

# Update if your backend URL changes
BASE_URL = "http://localhost:8000/api/v1"

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL)

@pytest.fixture
def auth_headers(client):
    # Generates a fresh user for every test run
    uid = str(uuid.uuid4())[:8]
    email = f"user_{uid}@example.com"
    pwd = "password123"
    
    client.post("/auth/register", json={
        "name": "Test User", "email": email, "avatar": "x", "password": pwd
    })
    
    resp = client.post("/auth/login", data={"username": email, "password": pwd})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- 1. PROFILE FLOW ---
def test_profile_flow(client, auth_headers):
    resp = client.post("/profiles/me", headers=auth_headers, json={
        "bio": "I am a tester", "social_links": {}
    })
    assert resp.status_code == 201
    assert client.get("/profiles/me", headers=auth_headers).status_code == 200

# --- 2. BRAND FLOW ---
def test_brand_workflow(client, auth_headers):
    # 'company_name' is required per your validation error
    payload = {"name": "Brand X", "description": "Desc", "company_name": "CorpX"}
    res = client.post("/brands/", headers=auth_headers, json=payload)
    assert res.status_code == 201
    brand_id = res.json()["id"]
    
    assert client.get(f"/brands/{brand_id}").status_code == 200
    assert client.put(f"/brands/{brand_id}", headers=auth_headers, json={"name": "New Name"}).status_code == 200

# --- 3. CAMPAIGN FLOW ---
def test_campaign_workflow(client, auth_headers):
    # Create brand first
    b = client.post("/brands/", headers=auth_headers, json={
        "name": "B2", "description": "D2", "company_name": "CorpB"
    }).json()
    
    # Create Campaign with numeric reward
    c = client.post(f"/campaigns/brand/{b['id']}", headers=auth_headers, json={
        "title": "Campaign 1",
        "description": "Desc",
        "budget": 100,
        "is_active": True,
        "reward": 100.0,       # Numeric, not string
        "target_views": 1000
    })
    assert c.status_code == 201, f"Campaign creation failed: {c.json()}"
    campaign_id = c.json()["id"]
    
    assert client.get(f"/campaigns/{campaign_id}").status_code == 200
    assert client.get("/campaigns/").status_code == 200

# --- 4. APPLICATION FLOW ---
def test_application_flow(client, auth_headers):
    # Create brand and campaign for the application
    b = client.post("/brands/", headers=auth_headers, json={"name": "B3", "description": "D3", "company_name": "CorpC"}).json()
    c = client.post(f"/campaigns/brand/{b['id']}", headers=auth_headers, json={
        "title": "Camp3", "description": "Desc", "budget": 10, "is_active": True, "reward": 5.0, "target_views": 10
    }).json()
    
    # Apply
    app = client.post("/applications/", headers=auth_headers, json={"campaign_id": c['id']})
    assert app.status_code == 201
    
    # Verify my apps list
    assert client.get("/applications/me", headers=auth_headers).status_code == 200