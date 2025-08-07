from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum



OPENAI_MODELS = Literal[
    'gpt-4o',
    'o3',
    'gpt-4.1'
]

INCLUDE_OPTIONS = Literal[
    'file_search_call.results',
    'message.input_image.image_url',
    'computer_call_output.output.image_url',
    'reasoning.encrypted_content',
    'code_interpreter_call.outputs'
]

SERVICE_TIERS = Literal[
    'auto',
    'default',
    'flex'
]

TRUNCATION_OPTIONS = Literal[
    'auto',
    'Disabled'
]


class FormatType(str, Enum):
    text = "text"           # default
    json_schema = "json_schema"
    json_object = "json_object"         


class _TextFormat(BaseModel):
    type: FormatType = Field(default=FormatType.text, Literal=True)


class _JsonObjFormat(BaseModel):
    type: FormatType = Field(default=FormatType.json_object, Literal=True)


class _JsonSchFormat(BaseModel):
    type: FormatType = Field(default=FormatType.json_schema, Literal=True)
    schema: Dict[str, Any]    


Format = Union[_TextFormat, _JsonObjFormat, _JsonSchFormat]

class Reasoning(BaseModel):
    effort: Optional[Literal['low', 'medium', 'high']] = None
    summary: Optional[Literal['auto', 'concise', 'detailed']] = None

class TextOptions(BaseModel):
    format: Format = Field(default=_TextFormat())



# ____________ TOOL CHOICE OBJECTS ____________
class ToolChoiceMode(str, Enum):
    none = "none"        # model will never call a tool
    auto = "auto"        # model decides (default in OpenAI API)
    required = "required"  # model must call ≥1 tool


class HostedToolChoice(BaseModel):
    """
    Force the model to call a *built-in* tool
      { "type": "file_search" }   etc.
    """
    type: Literal[
        "file_search",
        "web_search_preview",
        "computer_use_preview",
        "code_interpreter",
        "mcp",
        "image_generation",
    ]


class FunctionToolChoice(BaseModel):
    """
    Force the model to call a *specific function*
      { "type": "function", "name": "my_fn" }
    """
    type: Literal["function"] = Field(default="function", Literal=True)
    name: str


ToolChoice = Union[ToolChoiceMode, HostedToolChoice, FunctionToolChoice]




# ---------------------- TOOLS ----------------------
class FunctionTool(BaseModel):
    type: Literal["function"] = Field(default="function", Literal=True)
    name: str
    parameters: Dict[str, Any]            # JSON schema
    strict: bool = True                   # spec “default true”
    description: Optional[str] = None



class FileSearchTool(BaseModel):
    type: Literal["file_search"] = Field(default="file_search", Literal=True)
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


class ComputerUsePreviewTool(BaseModel):
    type: Literal["computer_use_preview"] = Field(default="computer_use_preview", Literal=True)
    display_height: int
    display_width: int
    environment: str


class MCPRequireApproval(str, Enum):
    always = "always"
    never = "never"


class MCPTool(BaseModel):
    type: Literal["mcp"] = Field(default="mcp", Literal=True)
    server_label: str
    server_url: str
    allowed_tools: Optional[Union[List[str], Dict[str, Any]]] = None
    headers: Optional[Dict[str, str]] = None
    require_approval: Optional[Union[MCPRequireApproval, Dict[str, Any]]] = MCPRequireApproval.always


class CodeInterpreterTool(BaseModel):
    type: Literal["code_interpreter"] = Field(default="code_interpreter", Literal=True)
    # container can be a string ID or an object with file-ids, etc.
    container: Union[str, Dict[str, Any]]


class ImageBackground(str, Enum):
    transparent = "transparent"
    opaque = "opaque"
    auto = "auto"


class ImageOutputFormat(str, Enum):
    png = "png"
    webp = "webp"
    jpeg = "jpeg"


class ImageQuality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    auto = "auto"


class ImageSize(str, Enum):
    s1 = "1024x1024"
    s2 = "1024x1536"
    s3 = "1536x1024"
    auto = "auto"


class ImageGenerationTool(BaseModel):
    type: Literal["image_generation"] = Field(default="image_generation", Literal=True)
    background: ImageBackground = ImageBackground.auto
    input_image_mask: Optional[Dict[str, Any]] = None
    model: str = "gpt-image-1"
    moderation: str = "auto"
    output_compression: int = 100
    output_format: ImageOutputFormat = ImageOutputFormat.png
    partial_images: int = Field(default=0, ge=0, le=3)
    quality: ImageQuality = ImageQuality.auto
    size: ImageSize = ImageSize.auto


class LocalShellTool(BaseModel):
    type: Literal["local_shell"] = Field(default="local_shell", Literal=True)


Tool = Union[
    FunctionTool,
    FileSearchTool,
    WebSearchPreviewTool,
    ComputerUsePreviewTool,
    MCPTool,
    CodeInterpreterTool,
    ImageGenerationTool,
    LocalShellTool,
]


ALLOWED_ROLES = Literal["user", "assistant", "system"]

class ChatInput(BaseModel):
    role: ALLOWED_ROLES
    content: str

class OpenAIRequest(BaseModel):
    input: list[ChatInput] | str
    model: OPENAI_MODELS
    background: Optional[bool | None] = None
    include: Optional[list[INCLUDE_OPTIONS]] = None
    instructions: Optional[str] = None
    max_output_tokens: Optional[int] = None
    temperature: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    parallel_tool_calls: Optional[bool] = True
    previous_response_id: Optional[str] = None
    reasoning: Optional[Reasoning] = None
    service_tier: Optional[SERVICE_TIERS] = 'auto'
    store: Optional[bool] = True
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.5
    text: Optional[TextOptions] = None
    tool_choice: Optional[List[ToolChoice]] = None
    tools: Optional[List[Tool]] = None
    top_p: Optional[float] = 1
    truncation: Optional[TRUNCATION_OPTIONS] = 'auto'
    user: Optional[str] = None





