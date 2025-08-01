from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, Dict, Optional, Literal, Union
from enum import Enum
from datetime import datetime, timezone
import uuid
from backend.src.client.oai.model.request_model import OPENAI_MODELS
from backend.src.client.oai.utils import generate_id

       

class ResponseError(BaseModel): 
    code: str
    message: str



class BaseOutput(BaseModel):
    type: str
    id: str
    status: Literal["completed", "in_progress", "errored"] 


class WebSearchCall(BaseOutput):
    type: Literal["web_search_call"] = "web_search_call"  
    id: str = Field(default_factory=lambda: generate_id("ws"))
    status: Literal["completed", "in_progress", "errored"]

class WebSearchCitations(BaseModel):
    type: Literal["url_citation"] = "url_citation"
    start_index: int
    end_index: int
    url: str
    title: str 

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("URL must start with 'http://' or 'https://'")
        return v


class MessageContent(BaseModel):
    type: Literal["output_text"] 
    text: str
    annotations: Optional[list[WebSearchCitations]]


class MessageOutput(BaseOutput):
    type: Literal["message"] = "message"
    id: str = Field(default_factory=lambda: generate_id("msg"))
    role: Literal["assistant"] = "assistant"
    content: list[MessageContent | WebSearchCall]


OutputVariant = Union[MessageOutput, WebSearchCall]



class OpenAIResponse(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("resp"))
    object: Literal["response"] = "response"
    created_at: float
    status: Literal["completed", "in_progress", "errored"]
    error: ResponseError | None = None
    model: OPENAI_MODELS
    output: list[OutputVariant] | None

    @field_validator("model", mode="before")
    def _strip_suffix(v: str) -> str:
        for base in OPENAI_MODELS.__args__:
            if v == base or v.startswith(base + "-"):
                return base
        raise ValueError(f"Unknown model '{v}'. Must start with one of {OPENAI_MODELS.__args__}")