from typing import Optional, List
from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime

class PriceData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    open: float
    close: float
    high: float
    low: float
    volume: float
    time: str
    time_milliseconds: int

class CompanyCandlesResponse(BaseModel):
    prices: List[PriceData]
