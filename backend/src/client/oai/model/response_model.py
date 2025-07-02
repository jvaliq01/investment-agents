from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum
from datetime import datetime, timezone
import uuid
from backend.src.client.oai.model.request_model import OPENAI_MODELS

class GenerateID(BaseModel):
     id: str

     @classmethod()
     def _make_id(cls, id):
          return 
     


class ResponseError(BaseModel): 
    code: str
    message: str


class OpenAiResponses(BaseModel):
    id: str 
    created_at: str
    status: Literal["completed", "in_progress", "errored"]
    models: OPENAI_MODELS
    error: ResponseError | None = None
    