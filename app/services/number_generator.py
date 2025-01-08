import random
from sqlalchemy.orm import Session
from ..models.number import RandomNumber

class NumberGenerator:
    @staticmethod
    def generate() -> float:
        return random.uniform(0, 100)

    @staticmethod
    def save_number(db: Session, value: float) -> RandomNumber:
        db_number = RandomNumber(value=value)
        db.add(db_number)
        db.commit()
        db.refresh(db_number)
        return db_number

    @staticmethod
    def get_latest(db: Session) -> RandomNumber:
        return db.query(RandomNumber).order_by(RandomNumber.timestamp.desc()).first()
