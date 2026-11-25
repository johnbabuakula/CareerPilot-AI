
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


# HELPER: CREATE AN INTERVIEW
def create_test_interview(client, total_questions=2):
    payload = {
        "job_role": "Python Developer",
        "topic": "Python",
        "total_questions": total_questions
    }

    return client.post("/interviews/", json=payload)


# 1. CREATE AN INTERVIEW SESSION
def test_create_interview(client_with_users):
    client, user, _ = client_with_users

    response = create_test_interview(client, 3)

    assert response.status_code == 200

    data = response.json()

    assert data["job_role"] == "Python Developer"
    assert data["topic"] == "Python"
    assert data["total_questions"] == 3
    assert data["score"] == 0
    assert len(data["questions"]) == 3

    for question in data["questions"]:
        assert question["question"]
        assert question["user_answer"] is None


# 2. REJECT AN UNSUPPORTED TOPIC
def test_create_interview_unsupported_topic(client_with_users):
    client, _, _ = client_with_users

    payload = {
        "job_role": "Python Developer",
        "topic": "UnsupportedTopicXYZ",
        "total_questions": 2
    }

    response = client.post("/interviews/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported interview topic."


# 3. GET ALL INTERVIEW SESSIONS
def test_get_interviews(client_with_users):
    client, _, _ = client_with_users

    create_test_interview(client, 2)
    create_test_interview(client, 3)

    response = client.get("/interviews/")

    assert response.status_code == 200
    assert len(response.json()) == 2


# 4. SUBMIT AN ANSWER
def test_submit_interview_answer(client_with_users):
    client, _, _ = client_with_users

    create_response = create_test_interview(client, 2)

    session_data = create_response.json()
    session_id = session_data["id"]
    question_id = session_data["questions"][0]["id"]

    payload = {
        "answer": (
            "Python is a high-level interpreted programming "
            "language used for general purpose software development."
        )
    }

    response = client.post(
        f"/interviews/{session_id}/questions/{question_id}/answer",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Answer evaluated successfully!"
    assert data["question_id"] == question_id
    assert isinstance(data["score"], int)
    assert isinstance(data["feedback"], str)
    assert isinstance(data["session_score"], int)


# 5. PREVENT DUPLICATE ANSWER SUBMISSION
def test_duplicate_answer_submission(client_with_users):
    client, _, _ = client_with_users

    create_response = create_test_interview(client, 2)

    session_data = create_response.json()
    session_id = session_data["id"]
    question_id = session_data["questions"][0]["id"]

    payload = {
        "answer": "Python is a programming language."
    }

    first_response = client.post(
        f"/interviews/{session_id}/questions/{question_id}/answer",
        json=payload
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/interviews/{session_id}/questions/{question_id}/answer",
        json=payload
    )

    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "You have already submitted an answer for this question."
    )


# 6. GET SUMMARY BEFORE ANSWERING
def test_interview_summary_not_started(client_with_users):
    client, _, _ = client_with_users

    create_response = create_test_interview(client, 2)
    session_id = create_response.json()["id"]

    response = client.get(
        f"/interviews/{session_id}/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_questions"] == 2
    assert data["answered_questions"] == 0
    assert data["pending_questions"] == 2
    assert data["average_score"] == 0
    assert data["percentage"] == 0
    assert data["performance"] == "Not Started"
    assert data["completed"] is False


# 7. GET SUMMARY AFTER COMPLETING INTERVIEW
def test_completed_interview_summary(client_with_users):
    client, _, _ = client_with_users

    create_response = create_test_interview(client, 1)

    session_data = create_response.json()
    session_id = session_data["id"]
    question_id = session_data["questions"][0]["id"]

    answer_response = client.post(
        f"/interviews/{session_id}/questions/{question_id}/answer",
        json={
            "answer": (
                "Python is a high-level interpreted programming "
                "language used for software development."
            )
        }
    )

    assert answer_response.status_code == 200

    response = client.get(
        f"/interviews/{session_id}/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_questions"] == 1
    assert data["answered_questions"] == 1
    assert data["pending_questions"] == 0
    assert data["completed"] is True
    assert data["average_score"] >= 0
    assert data["percentage"] >= 0
    assert data["performance"] != "Not Started"


# 8. REJECT A MISSING INTERVIEW SESSION
def test_missing_interview_session(client_with_users):
    client, _, _ = client_with_users

    response = client.get("/interviews/9999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview session not found."


# 9. REJECT A MISSING QUESTION
def test_missing_interview_question(client_with_users):
    client, _, _ = client_with_users

    create_response = create_test_interview(client, 2)
    session_id = create_response.json()["id"]

    response = client.post(
        f"/interviews/{session_id}/questions/9999/answer",
        json={"answer": "This is a test answer."}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found."


# 10. PREVENT UNAUTHENTICATED ACCESS
def test_interviews_without_login(client_with_users):
    client, _, _ = client_with_users

    app.dependency_overrides.pop(get_current_user)

    response = client.get("/interviews/")

    assert response.status_code == 401


# 11. VERIFY USER DATA ISOLATION
def test_user_cannot_access_another_users_interview(
    client_with_users
):
    client, user, other_user = client_with_users

    create_response = create_test_interview(client, 2)

    session_data = create_response.json()
    session_id = session_data["id"]
    question_id = session_data["questions"][0]["id"]

    # Switch authentication to the second user
    app.dependency_overrides[get_current_user] = (
        lambda: other_user
    )

    # Second user should not see the first user's sessions
    get_response = client.get("/interviews/")

    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

    # Second user should not access the first user's summary
    summary_response = client.get(
        f"/interviews/{session_id}/summary"
    )

    assert summary_response.status_code == 404

    # Second user should not submit an answer to the first user's question
    answer_response = client.post(
        f"/interviews/{session_id}/questions/{question_id}/answer",
        json={"answer": "Unauthorized answer."}
    )

    assert answer_response.status_code == 404

    # Switch back to the first user
    app.dependency_overrides[get_current_user] = lambda: user

    final_response = client.get("/interviews/")

    assert len(final_response.json()) == 1
    assert final_response.json()[0]["id"] == session_id
