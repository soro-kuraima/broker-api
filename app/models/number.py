# app/models/number.py
from sqlalchemy import Column, Integer, Float, String
from datetime import datetime
from ..database import Base

class RandomNumber(Base):
   __tablename__ = "random_numbers"
   
   id = Column(Integer, primary_key=True, index=True)
   timestamp = Column(String)  # Store timestamp as string
   value = Column(Float)

   def to_dict(self):
       """Convert to dictionary with timestamp as key"""
       return {
           "id": self.id,
           self.timestamp: self.value
       }