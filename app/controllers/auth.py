# app/controllers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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
    request: Request,
    db: Session = Depends(get_db),
    user_login: UserLogin | None = None  # This will generate a JSON body in docs
):
    if user_login is not None:
        # Use the parsed JSON from the body (docs and JSON requests will use this)
        username = user_login.username
        password = user_login.password
    else:
        # Fallback for non-JSON (e.g. form-data)
        content_type = request.headers.get("Content-Type", "")
        if "application/json" in content_type:
            data = await request.json()
            username = data.get("username")
            password = data.get("password")
        elif "application/x-www-form-urlencoded" in content_type:
            data = await request.form()
            username = data.get("username")
            password = data.get("password")
        else:
            raise HTTPException(status_code=400, detail="Unsupported content type")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    user = AuthService.authenticate_user(db, username=username, password=password)
    if not user:
        # Register the user if not found
        user_data = UserCreate(username=username, password=password)
        user = AuthService.create_user(db, user_data)
        # Authenticate again after registration
        user = AuthService.authenticate_user(db, username=username, password=password)
    
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