from sqlalchemy.orm import Session
from ..models.user import UserSession
from ..core.security import create_access_token
from typing import Optional

class AuthService:
    @staticmethod
    def create_session(db: Session, username: str) -> str:
        token = create_access_token(username)
        db_session = UserSession(username=username, token=token)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return token

    @staticmethod
    def get_session(db: Session, token: str) -> Optional[UserSession]:
        return db.query(UserSession).filter(UserSession.token == token).first()
