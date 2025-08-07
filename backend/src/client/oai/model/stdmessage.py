from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum
from datetime import datetime, timezone
import uuid
from backend.src.client.oai.model.request_model import OPENAI_MODELS


type MessageStatus = Literal['in_progress', 'completed', 'incomplete']
type MessageRole = Literal['user, system, developer']




## ------------- INPUTS ------------- ##
class InputText(BaseModel):
   type: Literal['input_text'] = 'input_text'
   text: str | None

class InputImage(BaseModel):
   detail: Literal['high', 'low', 'auto'] = 'auto'
   type: Literal['input_image'] = 'input_image'
   file_id: str
   image_url: str | None = None

class InputFile(BaseModel): 
   type: Literal['input_file'] = 'input_file'
   file_data: str
   file_id: str
   filename: str


class InputData(BaseModel): 
   content: InputText | InputImage | InputFile
   id: str
   type: Literal['message'] = 'message'
   status: MessageStatus
   role: MessageRole

class Input(BaseModel):
   object: Literal['list'] = 'list'
   first_id: str 
   last_id: str
   type: str
   data: InputData
