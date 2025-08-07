from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, Dict, Optional, Literal, Union
from enum import Enum
from datetime import datetime, timezone
import uuid
from backend.src.client.oai.model.request_model import OPENAI_MODELS
from utils import generate_id

       

class ResponseError(BaseModel): 
    code: str
    message: str


class MessageContent(BaseModel):
    type: Literal["output_text"]  # add other content types as needed
    text: str

class MessageOutput(BaseModel):
    type: Literal["message"]
    id: str = Field(default_factory=lambda: generate_id("msg"))
    status: Literal["completed", "in_progress", "errored"]
    role: Literal["assistant"]
    content: list[MessageContent]

# Discriminated union – Pydantic chooses the right model based on "type"
OutputVariant = Union[MessageOutput]


class OpenAIResponse(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("resp"))
    object: Literal["response"] = "response"
    created_at: float
    status: Literal["completed", "in_progress", "errored"]
    error: ResponseError | None = None
    model: OPENAI_MODELS
    output: list[MessageOutput] | None

    @field_validator("model", mode="before")
    def _strip_suffix(v: str) -> str:
        for base in OPENAI_MODELS.__args__:
            if v == base or v.startswith(base + "-"):
                return base
        raise ValueError(f"Unknown model '{v}'. Must start with one of {OPENAI_MODELS.__args__}")