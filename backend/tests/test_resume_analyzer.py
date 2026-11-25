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

import app.routers.resume_analyzer as resume_router
from app.utils.skill_matcher import find_skills, calculate_skill_match


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


# TEST CLIENT AND USER
@pytest.fixture
def client_with_user(db_session):
    user = User(
        full_name="Test User",
        email="test@example.com",
        hashed_password="test-password"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

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
            "Origin": "http://localhost:5173",
            "X-CSRF-Token": csrf_token
        })

        yield test_client, user

    app.dependency_overrides.clear()


# HELPER: UPLOAD A PDF
def upload_pdf(
    client,
    contents=None,
    filename="resume.pdf",
    content_type="application/pdf",
    job_description="Python SQL FastAPI Developer"
):

    if contents is None:
        contents = b"%PDF-1.4\nTest PDF content"

    return client.post(
        "/resume/analyze",
        files={
            "resume": (filename, contents, content_type)
        },
        data={
            "job_description": job_description
        }
    )


# 1. SUCCESSFUL RESUME ANALYSIS
def test_successful_resume_analysis(
    client_with_user,
    monkeypatch
):
    client, user = client_with_user

    # Mock PDF extraction to return predictable resume text
    monkeypatch.setattr(
        resume_router,
        "extract_text_from_pdf",
        lambda file_path: "Python developer with SQL experience."
    )

    response = upload_pdf(client)

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Resume analyzed successfully!"
    assert data["user_id"] == user.id
    assert data["resume_text"] == "Python developer with SQL experience."

    analysis = data["analysis"]

    assert analysis["total_required_skills"] == 3
    assert analysis["matched_skills"] == ["Python", "SQL"]
    assert analysis["missing_skills"] == ["FastAPI"]
    assert analysis["match_percentage"] == 66.67


# 2. REJECT NON-PDF CONTENT TYPE
def test_reject_non_pdf_content_type(client_with_user):
    client, _ = client_with_user

    response = upload_pdf(
        client,
        filename="resume.txt",
        content_type="text/plain"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."


# 3. REJECT INVALID FILE EXTENSION
def test_reject_invalid_file_extension(client_with_user):
    client, _ = client_with_user

    response = upload_pdf(
        client,
        filename="resume.docx",
        content_type="application/pdf"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload a valid PDF file."


# 4. REJECT EMPTY JOB DESCRIPTION
def test_reject_empty_job_description(client_with_user):
    client, _ = client_with_user

    response = upload_pdf(
        client,
        job_description="   "
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Job description cannot be empty."


# 5. REJECT INVALID PDF CONTENT
def test_reject_invalid_pdf_content(client_with_user):
    client, _ = client_with_user

    response = upload_pdf(
        client,
        contents=b"This is not a PDF file"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is not a valid PDF."


# 6. REJECT PDF LARGER THAN 5 MB
def test_reject_large_pdf(client_with_user):
    client, _ = client_with_user

    large_pdf = b"%PDF-" + (b"A" * (5 * 1024 * 1024))

    response = upload_pdf(
        client,
        contents=large_pdf
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "PDF size must be less than 5 MB."


# 7. REJECT PDF WITHOUT READABLE TEXT
def test_reject_pdf_without_readable_text(
    client_with_user,
    monkeypatch
):
    client, _ = client_with_user

    monkeypatch.setattr(
        resume_router,
        "extract_text_from_pdf",
        lambda file_path: ""
    )

    response = upload_pdf(client)

    assert response.status_code == 400
    assert response.json()["detail"] == "No readable text found in the PDF."


# 8. HANDLE PDF PARSING ERRORS
def test_handle_pdf_parsing_error(
    client_with_user,
    monkeypatch
):
    client, _ = client_with_user

    def raise_parser_error(file_path):
        raise ValueError("Test parser error")

    monkeypatch.setattr(
        resume_router,
        "extract_text_from_pdf",
        raise_parser_error
    )

    response = upload_pdf(client)

    assert response.status_code == 400
    assert response.json()["detail"] == "Test parser error"


# 9. REJECT UNAUTHENTICATED ACCESS
def test_resume_analysis_without_login(client_with_user):
    client, _ = client_with_user

    app.dependency_overrides.pop(get_current_user)

    response = upload_pdf(client)

    assert response.status_code == 401


# 10. TEST SKILL DETECTION
def test_find_skills():
    text = "I know Python, SQL and FastAPI. I am learning Django."

    skills = find_skills(text)

    assert "Python" in skills
    assert "SQL" in skills
    assert "FastAPI" in skills
    assert "Django" in skills


# 11. TEST SKILL MATCH CALCULATION
def test_calculate_skill_match():
    resume_text = "Python developer with SQL experience."

    job_description = (
        "Looking for Python, SQL and FastAPI skills."
    )

    result = calculate_skill_match(
        resume_text,
        job_description
    )

    assert result["total_required_skills"] == 3
    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == ["FastAPI"]
    assert result["match_percentage"] == 66.67
    assert len(result["suggestions"]) == 1