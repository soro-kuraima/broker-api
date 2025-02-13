from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class RandomNumberBase(BaseModel):
    id: int
    timestamp_value: Dict[str, float]

    class Config:
        from_attributes = True

    @classmethod
    def from_db_model(cls, number):
        return cls(
            id=number.id,
            timestamp_value={number.timestamp: number.value}
        )
