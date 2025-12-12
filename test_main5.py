from fastapi.testclient import TestClient
from main5 import app   # <-- make sure this matches your backend filename

client = TestClient(app)

def test_create_plan():
    payload = {"name": "Test Trip", "type": "solo", "destination": "Delhi", "notes": "Testing"}
    response = client.post("/plans", json=payload)
    assert response.status_code == 200
    assert "created" in response.json()["message"]

def test_read_plans():
    response = client.get("/plans")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_plan():
    payload = {"name": "Update Trip", "type": "group", "destination": "Agra", "notes": "Before update"}
    create = client.post("/plans", json=payload)
    assert create.status_code == 200

    plans = client.get("/plans").json()
    plan_id = plans[-1][0]

    update_payload = {"notes": "After update"}
    update = client.put(f"/plans/{plan_id}", json=update_payload)
    assert update.status_code == 200
    assert "updated" in update.json()["message"]

def test_delete_plan():
    payload = {"name": "Delete Trip", "type": "solo", "destination": "Mumbai", "notes": "To be deleted"}
    create = client.post("/plans", json=payload)
    assert create.status_code == 200

    plans = client.get("/plans").json()
    plan_id = plans[-1][0]

    delete = client.delete(f"/plans/{plan_id}")
    assert delete.status_code == 204
