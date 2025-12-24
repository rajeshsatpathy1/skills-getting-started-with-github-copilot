import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

import src.app as appmod

client = TestClient(appmod.app)


def setup_function():
    # Keep a deep copy of activities to restore after each test
    appmod._activities_backup = copy.deepcopy(appmod.activities)


def teardown_function():
    # Restore original activities
    appmod.activities = appmod._activities_backup
    del appmod._activities_backup


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Science Club"
    email = "testuser@example.com"

    # Sign up
    r = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]

    # Verify participant is present
    r2 = client.get("/activities")
    assert email in r2.json()[activity]["participants"]

    # Delete participant
    r3 = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")
    assert r3.status_code == 200
    assert "Removed" in r3.json()["message"]

    # Verify participant removed
    r4 = client.get("/activities")
    assert email not in r4.json()[activity]["participants"]


def test_delete_nonexistent_participant():
    activity = "Chess Club"
    email = "doesnotexist@example.com"
    r = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")
    assert r.status_code == 404
