# app/controllers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..services.auth import AuthService
from ..schemas.user import UserCreate, UserLogin, Token
from ..config import get_settings

settings = get_settings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")
router = APIRouter()

@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user = AuthService.create_user(db, user_data)
    return {"message": "User created successfully"}

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # This is important for Swagger UI
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = AuthService.authenticate_user(
        db,
        username=form_data.username,
        password=form_data.password
    )
    return AuthService.create_session(db, user)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    return AuthService.refresh_session(db, refresh_token)

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if AuthService.logout(db, token):
        return {"message": "Logged out successfully"}
    raise HTTPException(status_code=400, detail="Logout failed")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return AuthService.get_session(db, token)