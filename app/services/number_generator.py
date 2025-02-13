from datetime import datetime
import random
import asyncio
from sqlalchemy.orm import Session
from ..models.number import RandomNumber
from ..database import SessionLocal

class NumberGenerator:
    def __init__(self):
        self.is_running = False
        self.task = None

    def generate(self) -> float:
        return random.uniform(0, 100)

    def save_number(self, db: Session, value: float) -> RandomNumber:
        timestamp = datetime.utcnow().isoformat()
        db_number = RandomNumber(
            timestamp=timestamp,
            value=value
        )
        try:
            db.add(db_number)
            db.commit()
            db.refresh(db_number)
            print(f"Saved number: {db_number.to_dict()}")
            return db_number
        except Exception as e:
            print(f"Error saving number: {str(e)}")
            db.rollback()
            raise

    async def _run(self):
        while self.is_running:
            db = SessionLocal()
            try:
                value = self.generate()
                self.save_number(db, value)
            except Exception as e:
                print(f"Error in number generator: {str(e)}")
            finally:
                db.close()
            await asyncio.sleep(1)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self._run())
            print("Number generator started")

    def get_latest(self, db: Session) -> RandomNumber:
        latest = db.query(RandomNumber).order_by(RandomNumber.timestamp.desc()).first()
        if latest:
            print(f"Latest number: {latest.to_dict()}")
        return latest

number_generator = NumberGenerator()