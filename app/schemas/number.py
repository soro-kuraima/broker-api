from pydantic import BaseModel
from datetime import datetime

class RandomNumberBase(BaseModel):
    value: float
    timestamp: datetime

class RandomNumberCreate(RandomNumberBase):
    pass

class RandomNumber(RandomNumberBase):
    id: int

    class Config:
        from_attributes = True