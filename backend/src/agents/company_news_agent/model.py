"""
This module defines the data models for the Company News Agent API.
"""

from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from datetime import datetime

#### COMPANY NEWS ####
class NewsArticle(BaseModel):
    ticker: str
    title: str
    author: str
    source: str
    date: datetime
    url: HttpUrl
    image_url: HttpUrl
    sentiment: Optional[str] = None

class CompanyNewsResponse(BaseModel):
    news: List[NewsArticle]