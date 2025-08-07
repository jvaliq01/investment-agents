"""
This module defines the data models for the Company News Agent API.
"""

from typing import Optional, List
from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime

#### COMPANY NEWS ####
## Request Model ##
class CompanyNewsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticker: str
    limit: int | None = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

## Response Model ##
class CompanyNewsReponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticker: str
    title: str
    author: str
    source: str
    date: datetime
    url: str
    image_url: HttpUrl | None
    sentiment: str | None


class CompanyNewsResponse(BaseModel):
    news: List[CompanyNewsReponse]