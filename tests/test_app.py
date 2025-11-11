from fastapi.testclient import TestClient
from src.app import app
import urllib.parse

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic shape checks
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"].get("participants"), list)


def test_signup_and_remove_flow():
    activity = "Chess Club"
    email = "testuser+pytest@example.com"

    # Ensure email not present (cleanup if needed)
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{activity}/participants?email={urllib.parse.quote(email, safe='')}")

    # Sign up the test user
    resp = client.post(f"/activities/{activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant was added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Duplicate signup should return 400
    resp = client.post(f"/activities/{activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 400

    # Remove participant
    resp = client.delete(f"/activities/{activity}/participants?email={urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify removal
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
