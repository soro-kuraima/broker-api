from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from ..database import Base

class RandomNumber(Base):
    __tablename__ = "random_numbers"
    
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
