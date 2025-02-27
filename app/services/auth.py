from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status
from ..models.user import User, UserSession
from ..core.security import get_password_hash, verify_password, create_token
from ..schemas.user import UserCreate, UserLogin

class AuthService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        """Authenticate user and return user object, or None if authentication fails"""
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None  # Instead of raising an exception, return None

        if not user.is_active:
            return None  # Handle inactive users silently as well
        
        return user


    @staticmethod
    def create_session(db: Session, user: User) -> dict:
        """Create new session for user"""
        # Deactivate all existing sessions
        db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).update({"is_active": False})
        
        # Create new tokens
        access_token, access_exp = create_token(user.username, "access")
        refresh_token, refresh_exp = create_token(user.username, "refresh")
        
        session = UserSession(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires=access_exp,
            refresh_token_expires=refresh_exp
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    
    @staticmethod
    def refresh_session(db: Session, refresh_token: str) -> dict:
        """Create new access token using refresh token"""
        session = (
            db.query(UserSession)
            .filter(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            )
            .join(User)  # Join with User table
            .first()
        )
        
        if not session or session.refresh_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get username from the joined user relationship
        username = db.query(User).filter(User.id == session.user_id).first().username
        access_token, access_exp = create_token(username, "access")
        
        session.access_token = access_token
        session.access_token_expires = access_exp
        
        db.commit()
        db.refresh(session)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def get_session(db: Session, token: str) -> UserSession:
        """Get active session by token"""
        session = db.query(UserSession).filter(
            UserSession.access_token == token,
            UserSession.is_active == True
        ).first()
        
        if not session or session.access_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token"
            )
            
        return session

    @staticmethod
    def logout(db: Session, token: str) -> bool:
        """Deactivate user session"""
        session = db.query(UserSession).filter(
            UserSession.access_token == token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
            
        return False