
import os
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.csrf import validate_csrf_token
from app.routers.resume_analyzer import router as resume_router
from app.routers.auth import router as auth_router
from app.routers.job_applications import router as applications_router
from app.routers.interview import router as interview_router
from app.routers.reminders import router as reminders_router


app = FastAPI(
    title="CareerPilot AI API",
    description="AI-Powered Job Search & Career Management Platform",
    version="1.0.0"
)


# FRONTEND ORIGIN CONFIGURATION
allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]


# CSRF PROTECTION
@app.middleware("http")
async def csrf_protection(request: Request, call_next):

    # Safe methods do not need CSRF validation
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return await call_next(request)

    # Validate the request origin
    origin = request.headers.get("origin")

    if not origin:
        referer = request.headers.get("referer")

        if referer:
            parsed_referer = urlsplit(referer)
            origin = f"{parsed_referer.scheme}://{parsed_referer.netloc}"

    if not origin or origin.rstrip("/") not in allowed_origins:
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Invalid or missing request origin"
            }
        )

    # Validate CSRF cookie and request header
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")

    if not validate_csrf_token(
        csrf_cookie,
        csrf_header
    ):
        return JSONResponse(
            status_code=403,
            content={
                "detail": "CSRF validation failed"
            }
        )

    return await call_next(request)


# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-CSRF-Token"
    ],
)


# REGISTER API ROUTERS
app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(reminders_router)


# ROOT ENDPOINT
@app.get("/")
def root():
    return {
        "message": "Welcome to CareerPilot AI API!"
    }


# HEALTH CHECK
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
