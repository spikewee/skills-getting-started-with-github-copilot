import copy
from fastapi.testclient import TestClient
from src.app import app, activities


def _client():
    return TestClient(app)


def test_get_activities():
    client = _client()
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # Keep activities state isolated by snapshotting and restoring
    original = copy.deepcopy(activities)
    try:
        client = _client()
        activity = "Chess Club"
        email = "pytest_tester@example.com"

        # Ensure clean start
        if email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(email)

        # Signup should succeed
        r = client.post(f"/activities/{activity}/signup?email={email}")
        assert r.status_code == 200
        assert email in activities[activity]["participants"]

        # Duplicate signup should fail
        r2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert r2.status_code == 400

        # Unregister should succeed
        r3 = client.post(f"/activities/{activity}/unregister?email={email}")
        assert r3.status_code == 200
        assert email not in activities[activity]["participants"]
    finally:
        activities.clear()
        activities.update(original)
