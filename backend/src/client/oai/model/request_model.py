from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum



OPENAI_MODELS = Literal[
    'gpt-4o',
    'o3',
    'gpt-4.1'
]

type FormatType = Literal['text', 'json_schema', 'json_object']

class Reasoning(BaseModel):
    effort: Optional[Literal['low', 'medium', 'high']] = None
    summary: Optional[Literal['auto', 'concise', 'detailed']] = None


# -------------- TOOL CHOICE OBJECTS -------------- 
type ToolChoice = Literal['none', 'auto', 'required']


# ---------------------- TOOLS ----------------------
class FileSearchTool(BaseModel):
    type: Literal["file_search"] = Field(default="file_search")
    vector_store_ids: List[str]
    filters: Optional[Dict[str, Any]] = None
    max_num_results: Optional[int] = Field(default=None, ge=1, le=50)
    ranking_options: Optional[Dict[str, Any]] = None


class WebSearchType(str, Enum):
    legacy = "web_search_preview"
    current = "web_search_preview_2025_03_11"


class WebSearchPreviewTool(BaseModel):
    type: WebSearchType
    search_context_size: Optional[Literal["low", "medium", "high"]] = "medium"
    user_location: Optional[Dict[str, Any]] = None


class CodeInterpreterTool(BaseModel):
    type: Literal["code_interpreter"] = Field(default="code_interpreter")
    # container can be a string ID or an object with file-ids, etc.
    container: Union[str, Dict[str, Any]]

Tool = Union[
    FileSearchTool,
    WebSearchPreviewTool,
    CodeInterpreterTool,
]

ALLOWED_ROLES = Literal["user", "assistant", "system"]

class ChatInput(BaseModel):
    role: ALLOWED_ROLES
    content: str

class OpenAIRequest(BaseModel):
    input: list[ChatInput] | str
    model: OPENAI_MODELS
    background: Optional[bool | None] = None
    temperature: Optional[float] = None
    parallel_tool_calls: Optional[bool] = True
    reasoning: Optional[Reasoning] = None
    stream: Optional[bool] = False
    text: Optional[FormatType] = None
    tool_choice: Optional[ToolChoice] = None
    tools: Optional[List[Tool]] = None





