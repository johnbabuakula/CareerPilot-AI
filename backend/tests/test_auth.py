
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base
from app.database.dependencies import get_db


# Create a separate in-memory SQLite database for testing
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
    # Create fresh database tables for each test
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:

        # Initialize CSRF protection for the test client
        csrf_response = test_client.get("/auth/csrf")

        assert csrf_response.status_code == 200

        csrf_token = csrf_response.json()["csrf_token"]

        test_client.headers.update({
            "Origin": FRONTEND_ORIGIN,
            "X-CSRF-Token": csrf_token
        })

        yield test_client

    # Clean up after each test
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# Helper function to register a test user
def register_test_user(client):
    return client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123"
        }
    )


# Helper function to log in and update the CSRF token
def login_test_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "TestPassword123"
        }
    )

    if response.status_code == 200:
        new_csrf_token = response.json().get("csrf_token")

        if new_csrf_token:
            client.headers.update({
                "X-CSRF-Token": new_csrf_token
            })

    return response


# TEST 1: Root endpoint
def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to CareerPilot AI API!"


# TEST 2: Health check
def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# TEST 3: Successful registration
def test_user_registration(client):
    response = register_test_user(client)

    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"
    assert response.json()["full_name"] == "Test User"
    assert "hashed_password" not in response.json()


# TEST 4: Duplicate email registration
def test_duplicate_registration(client):
    register_test_user(client)

    response = register_test_user(client)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


# TEST 5: Successful login
def test_user_login(client):
    register_test_user(client)

    response = login_test_user(client)

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert "csrf_token" in response.json()
    assert "access_token" in response.headers.get("set-cookie", "")


# TEST 6: Invalid login
def test_invalid_login(client):
    register_test_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


# TEST 7: Get logged-in user profile
def test_get_current_user(client):
    register_test_user(client)

    login_test_user(client)

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


# TEST 8: Profile access without login
def test_profile_without_login(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


# TEST 9: Successful logout
def test_user_logout(client):
    register_test_user(client)

    login_test_user(client)

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"

    profile_response = client.get("/auth/me")

    assert profile_response.status_code == 401


# TEST 10: Reject request without CSRF token
def test_request_without_csrf_token(client):
    client.headers.pop("X-CSRF-Token", None)

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "missingcsrf@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 403


# TEST 11: Reject request with invalid CSRF token
def test_request_with_invalid_csrf_token(client):
    client.headers.update({
        "X-CSRF-Token": "invalid-csrf-token"
    })

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "invalidcsrf@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 403


# TEST 12: Reject request from an unauthorized origin
def test_request_from_invalid_origin(client):
    client.headers.update({
        "Origin": "https://evil.example"
    })

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "invalidorigin@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 403
