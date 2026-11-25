
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base
from app.database.dependencies import get_db
from app.core.dependencies import get_current_user
from app.models.user import User


FRONTEND_ORIGIN = "http://localhost:5173"


# TEST DATABASE
@pytest.fixture
def db_session():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


# TEST CLIENT AND USERS
@pytest.fixture
def client_with_users(db_session):
    user = User(
        full_name="Test User",
        email="test@example.com",
        hashed_password="test-password"
    )

    other_user = User(
        full_name="Other User",
        email="other@example.com",
        hashed_password="other-password"
    )

    db_session.add_all([user, other_user])
    db_session.commit()

    db_session.refresh(user)
    db_session.refresh(other_user)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as test_client:

        # Initialize CSRF protection
        csrf_response = test_client.get("/auth/csrf")

        assert csrf_response.status_code == 200

        csrf_token = csrf_response.json()["csrf_token"]

        test_client.headers.update({
            "Origin": FRONTEND_ORIGIN,
            "X-CSRF-Token": csrf_token
        })

        yield test_client, user, other_user

    app.dependency_overrides.clear()


# CREATE A REMINDER
def test_create_reminder(client_with_users):
    client, user, _ = client_with_users

    payload = {
        "title": "Python Interview",
        "description": "Prepare Python questions",
        "reminder_type": "Interview",
        "reminder_date": (
            datetime.now() + timedelta(days=2)
        ).isoformat()
    }

    response = client.post("/reminders/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Python Interview"
    assert data["description"] == "Prepare Python questions"
    assert data["reminder_type"] == "Interview"
    assert data["user_id"] == user.id
    assert data["is_completed"] is False


# GET ALL REMINDERS
def test_get_reminders(client_with_users):
    client, _, _ = client_with_users

    for i in range(2):
        payload = {
            "title": f"Reminder {i + 1}",
            "description": "Test reminder",
            "reminder_type": "Deadline",
            "reminder_date": (
                datetime.now() + timedelta(days=i + 1)
            ).isoformat()
        }

        client.post("/reminders/", json=payload)

    response = client.get("/reminders/")

    assert response.status_code == 200
    assert len(response.json()) == 2


# UPDATE A REMINDER
def test_update_reminder(client_with_users):
    client, _, _ = client_with_users

    payload = {
        "title": "Original Reminder",
        "description": "Original description",
        "reminder_type": "Interview",
        "reminder_date": (
            datetime.now() + timedelta(days=3)
        ).isoformat()
    }

    create_response = client.post("/reminders/", json=payload)
    reminder_id = create_response.json()["id"]

    update_payload = {
        "title": "Updated Reminder",
        "is_completed": True
    }

    response = client.put(
        f"/reminders/{reminder_id}",
        json=update_payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated Reminder"
    assert data["is_completed"] is True
    assert data["description"] == "Original description"


# DELETE A REMINDER
def test_delete_reminder(client_with_users):
    client, _, _ = client_with_users

    payload = {
        "title": "Delete Me",
        "description": "Temporary reminder",
        "reminder_type": "Follow-up",
        "reminder_date": (
            datetime.now() + timedelta(days=1)
        ).isoformat()
    }

    create_response = client.post("/reminders/", json=payload)
    reminder_id = create_response.json()["id"]

    response = client.delete(f"/reminders/{reminder_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Reminder deleted successfully!"

    get_response = client.get("/reminders/")

    assert len(get_response.json()) == 0


# UPDATE A NON-EXISTING REMINDER
def test_update_missing_reminder(client_with_users):
    client, _, _ = client_with_users

    response = client.put(
        "/reminders/9999",
        json={"title": "Updated Title"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Reminder not found"


# DELETE A NON-EXISTING REMINDER
def test_delete_missing_reminder(client_with_users):
    client, _, _ = client_with_users

    response = client.delete("/reminders/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Reminder not found"


# UNAUTHENTICATED ACCESS
def test_reminders_without_login(client_with_users):
    client, _, _ = client_with_users

    app.dependency_overrides.pop(get_current_user)

    response = client.get("/reminders/")

    assert response.status_code == 401


# USER DATA ISOLATION
def test_user_cannot_access_another_users_reminder(
    client_with_users
):
    client, user, other_user = client_with_users

    payload = {
        "title": "Private Reminder",
        "description": "Only for first user",
        "reminder_type": "Interview",
        "reminder_date": (
            datetime.now() + timedelta(days=2)
        ).isoformat()
    }

    create_response = client.post("/reminders/", json=payload)

    reminder_id = create_response.json()["id"]

    # Switch authentication to the second user
    app.dependency_overrides[get_current_user] = (
        lambda: other_user
    )

    # Second user should not see the first user's reminder
    get_response = client.get("/reminders/")

    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

    # Second user should not update the first user's reminder
    update_response = client.put(
        f"/reminders/{reminder_id}",
        json={"title": "Unauthorized Update"}
    )

    assert update_response.status_code == 404

    # Second user should not delete the first user's reminder
    delete_response = client.delete(
        f"/reminders/{reminder_id}"
    )

    assert delete_response.status_code == 404

    # Switch back to the first user and verify reminder still exists
    app.dependency_overrides[get_current_user] = lambda: user

    final_response = client.get("/reminders/")

    assert len(final_response.json()) == 1
    assert final_response.json()[0]["title"] == "Private Reminder"
