
import os

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.utils.security import hash_password, verify_password
from app.core.jwt import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.dependencies import get_current_user
from app.core.csrf import generate_csrf_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# COOKIE CONFIGURATION
COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "false").lower() == "true"
)

COOKIE_SETTINGS = {
    "httponly": True,
    "secure": COOKIE_SECURE,
    "samesite": "lax",
    "path": "/"
}

CSRF_COOKIE_SETTINGS = {
    "httponly": True,
    "secure": COOKIE_SECURE,
    "samesite": "lax",
    "path": "/"
}


# GENERATE CSRF TOKEN
@router.get("/csrf")
def get_csrf_token(response: Response):
    csrf_token = generate_csrf_token()

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=60 * 60 * 24,
        **CSRF_COOKIE_SETTINGS
    )

    return {
        "csrf_token": csrf_token
    }


# USER REGISTRATION
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return new_user


# USER LOGIN
@router.post("/login")
def login_user(
    user_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if (
        not user
        or not user.is_active
        or not verify_password(
            user_data.password,
            user.hashed_password
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    # Rotate the CSRF token after successful login
    csrf_token = generate_csrf_token()

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **COOKIE_SETTINGS
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=60 * 60 * 24,
        **CSRF_COOKIE_SETTINGS
    )

    return {
        "message": "Login successful",
        "csrf_token": csrf_token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email
        }
    }


# USER LOGOUT
@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(
        key="access_token",
        **COOKIE_SETTINGS
    )

    response.delete_cookie(
        key="csrf_token",
        **CSRF_COOKIE_SETTINGS
    )

    return {
        "message": "Logout successful"
    }


# GET LOGGED-IN USER PROFILE
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
