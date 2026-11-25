
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base
from app.database.dependencies import get_db


# Separate in-memory SQLite database
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


FRONTEND_ORIGIN = "http://localhost:5173"


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:

        # Initialize CSRF protection
        csrf_response = test_client.get("/auth/csrf")

        assert csrf_response.status_code == 200

        csrf_token = csrf_response.json()["csrf_token"]

        test_client.headers.update({
            "Origin": FRONTEND_ORIGIN,
            "X-CSRF-Token": csrf_token
        })

        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def refresh_csrf_token(client):
    """Get a fresh CSRF token and update the request header."""
    response = client.get("/auth/csrf")

    assert response.status_code == 200

    csrf_token = response.json()["csrf_token"]

    client.headers.update({
        "X-CSRF-Token": csrf_token
    })

    return csrf_token


def register_user(client, email):
    # Ensure a valid CSRF token is available
    refresh_csrf_token(client)

    return client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "TestPassword123"
        }
    )


def login_user(client, email):
    # Ensure a valid CSRF token is available
    refresh_csrf_token(client)

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123"
        }
    )

    # Login rotates the CSRF token
    if response.status_code == 200:
        new_csrf_token = response.json().get("csrf_token")

        if new_csrf_token:
            client.headers.update({
                "X-CSRF-Token": new_csrf_token
            })

    return response


def create_test_application(client):
    return client.post(
        "/applications/",
        json={
            "company_name": "Google",
            "job_role": "Python Developer",
            "status": "Applied",
            "application_date": "2026-11-24",
            "job_description": "Python and FastAPI developer"
        }
    )


# TEST 1: Create application
def test_create_application(client):
    register_user(client, "user1@example.com")
    login_user(client, "user1@example.com")

    response = create_test_application(client)

    assert response.status_code == 201
    assert response.json()["company_name"] == "Google"
    assert response.json()["job_role"] == "Python Developer"
    assert response.json()["status"] == "Applied"


# TEST 2: Get all applications
def test_get_applications(client):
    register_user(client, "user2@example.com")
    login_user(client, "user2@example.com")

    create_test_application(client)

    response = client.get("/applications/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["company_name"] == "Google"


# TEST 3: Update application
def test_update_application(client):
    register_user(client, "user3@example.com")
    login_user(client, "user3@example.com")

    create_response = create_test_application(client)
    application_id = create_response.json()["id"]

    response = client.put(
        f"/applications/{application_id}",
        json={
            "company_name": "Microsoft",
            "job_role": "Software Developer",
            "status": "Interview",
            "application_date": "2026-11-25",
            "job_description": "Software development role"
        }
    )

    assert response.status_code == 200
    assert response.json()["company_name"] == "Microsoft"
    assert response.json()["status"] == "Interview"


# TEST 4: Delete application
def test_delete_application(client):
    register_user(client, "user4@example.com")
    login_user(client, "user4@example.com")

    create_response = create_test_application(client)
    application_id = create_response.json()["id"]

    response = client.delete(
        f"/applications/{application_id}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Application deleted successfully"

    list_response = client.get("/applications/")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 0


# TEST 5: Update non-existing application
def test_update_missing_application(client):
    register_user(client, "user5@example.com")
    login_user(client, "user5@example.com")

    response = client.put(
        "/applications/999",
        json={
            "company_name": "Microsoft",
            "job_role": "Developer",
            "status": "Applied",
            "application_date": "2026-11-25",
            "job_description": "Test description"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


# TEST 6: Delete non-existing application
def test_delete_missing_application(client):
    register_user(client, "user6@example.com")
    login_user(client, "user6@example.com")

    response = client.delete("/applications/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


# TEST 7: Prevent unauthenticated access
def test_applications_without_login(client):
    response = client.get("/applications/")

    assert response.status_code == 401


# TEST 8: Prevent another user from accessing applications
def test_user_data_isolation(client):
    # First user creates an application
    register_user(client, "first@example.com")
    login_user(client, "first@example.com")

    create_response = create_test_application(client)
    application_id = create_response.json()["id"]

    # Log out first user
    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 200

    # Second user registers and logs in
    register_user(client, "second@example.com")
    login_user(client, "second@example.com")

    # Second user should not see first user's application
    list_response = client.get("/applications/")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 0

    # Second user should not update first user's application
    update_response = client.put(
        f"/applications/{application_id}",
        json={
            "company_name": "Amazon",
            "job_role": "Developer",
            "status": "Interview",
            "application_date": "2026-11-25",
            "job_description": "Test description"
        }
    )

    assert update_response.status_code == 404

    # Second user should not delete first user's application
    delete_response = client.delete(
        f"/applications/{application_id}"
    )

    assert delete_response.status_code == 404


# TEST 9: Career analytics
def test_application_analytics(client):
    register_user(client, "analytics@example.com")
    login_user(client, "analytics@example.com")

    create_test_application(client)

    client.post(
        "/applications/",
        json={
            "company_name": "Microsoft",
            "job_role": "Software Developer",
            "status": "Interview",
            "application_date": "2026-11-24",
            "job_description": "Software development"
        }
    )

    response = client.get("/applications/analytics")

    assert response.status_code == 200

    data = response.json()

    assert data["total_applications"] == 2
    assert data["interviews"] == 1
    assert data["status_breakdown"]["Applied"] == 1
    assert data["status_breakdown"]["Interview"] == 1
    assert data["interview_conversion_rate"] == 50.0
