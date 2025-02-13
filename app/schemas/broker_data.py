from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class BrokerDataBase(BaseModel):
    user: str = Field(..., pattern=r"^user_\d+$")
    broker: str = Field(..., pattern=r"^Broker[A-C]$")
    api_key: str = Field(..., pattern=r"^APIKEY_\d+$")
    api_secret: str = Field(..., pattern=r"^APISECRET_\d+$")
    pnl: float
    margin: float
    max_risk: float

    @validator('user')
    def validate_user(cls, v):
        if not re.match(r"^user_\d+$", v):
            raise ValueError('Invalid user format')
        return v

    @validator('broker')
    def validate_broker(cls, v):
        if v not in ["BrokerA", "BrokerB", "BrokerC"]:
            raise ValueError('Invalid broker')
        return v

    @validator('api_key')
    def validate_api_key(cls, v):
        if not re.match(r"^APIKEY_\d+$", v):
            raise ValueError('Invalid API key format')
        return v

    @validator('api_secret')
    def validate_api_secret(cls, v):
        if not re.match(r"^APISECRET_\d+$", v):
            raise ValueError('Invalid API secret format')
        return v

    @validator('max_risk')
    def validate_max_risk(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Max risk must be between 0 and 100')
        return v

class BrokerDataCreate(BrokerDataBase):
    pass

class BrokerDataUpdate(BrokerDataBase):
    user: Optional[str] = None
    broker: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    pnl: Optional[float] = None
    margin: Optional[float] = None
    max_risk: Optional[float] = None

class BrokerDataResponse(BrokerDataBase):
    id: int

    class Config:
        from_attributes = True