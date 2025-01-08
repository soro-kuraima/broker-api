from sqlalchemy import Column, Integer, String, Float
from ..database import Base

class BrokerData(Base):
    __tablename__ = "broker_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, unique=True, index=True)
    broker = Column(String)
    api_key = Column(String, unique=True)
    api_secret = Column(String, unique=True)
    pnl = Column(Float)
    margin = Column(Float)
    max_risk = Column(Float)