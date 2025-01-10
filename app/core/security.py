# app/core/security.py
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext
from ..config import get_settings

settings = get_settings()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_token(subject: Union[str, Any], token_type: str = "access") -> tuple[str, datetime]:
    """Create a JWT token"""
    if token_type == "access":
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:  # refresh token
        expires_delta = timedelta(days=7)  # 7 days for refresh token
        
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "token_type": token_type
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt, expire

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)