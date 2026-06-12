import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


BASE_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    expected_activity_names = set(BASE_ACTIVITIES.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == expected_activity_names
    assert payload["Chess Club"]["description"] == BASE_ACTIVITIES["Chess Club"]["description"]


def test_signup_for_activity_adds_student_to_participants(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    initial_participants = len(BASE_ACTIVITIES[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_participants + 1


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}