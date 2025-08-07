import os
import json
from typing import List, Optional, AsyncGenerator, Dict
import httpx
from pydantic import BaseModel, Field, field_validator
import asyncio
from anthropic import Anthropic, AsyncAnthropic
from backend.src.config import CONFIG

# Base URL for Claude endpoints
ANTHROPIC_API_URL = "https://api.anthropic.com"
DEFAULT_TIMEOUT = 120.0  # Increased from 30.0 to 120.0 seconds
ANTHROPIC_API_VERSION = "2023-06-01"  # Updated to a recent version
MAX_RETRIES = 3  # Maximum number of retry attempts

ALLOWABLE_ROLES = ["user", "assistant"]
# Custom validator to check role
def validate_role(role: str):
    if role not in ALLOWABLE_ROLES:
        raise ValueError(f"Role must be one of {ALLOWABLE_ROLES}")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message: 'user' or 'assistant'")
    content: str = Field(..., description="Message content text")

class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., description="Messages for the chat session")
    max_tokens: int = Field(1024, ge=1)
    model: str = Field(..., description="Model name")
    temperature: float = Field(1.0, ge=0.0, le=1.0)

    top_k: int | None = Field(default=None, ge=0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    stop_sequences: list[str] | None = None
    stream: bool = Field(default=False, description="Whether to stream response chunks")
    system: str | None = None       

class ChatCompletionResponse(BaseModel):
    id: str = Field(...)
    type: str = Field(...)
    role: str = Field(...)
    content: List[Dict[str, str]] = Field(...)  
    model: str = Field(...)
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: Optional[dict] = Field(None, description="Token usage information")

    @property
    def text(self) -> str:
        """Get the text content from the response."""
        # Extract text from the first content block
        if self.content and len(self.content) > 0:
            return self.content[0].get("text", "")
        return ""

# --------------------
# API Client
# --------------------
class AnthropicClient(BaseModel):
    """
    Client for interacting with the Anthropic API.
    """
    anthropic_api_key: str  | None
    anthropic_api_url: str | None
    timeout: int | None = CONFIG.timeout
    max_retries: int = CONFIG.max_retries

    async def chat_complete( 
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Perform a chat completion call using the messages API.
        """
        client = AsyncAnthropic(
            api_key=self.anthropic_api_key,
            base_url=self.anthropic_api_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )

        payload = request.model_dump(exclude_none=True)
        payload["messages"] = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        print(f"Payload for chat_complete: {json.dumps(payload, indent=2)}")

        try:
            result = await client.messages.create(**payload)
        except Exception as e:
            raise Exception(f"Error during chat completion: {e}")

        if not result:
            raise Exception("No response received from the chat completion API.")

        raw_response = result.model_dump(exclude_none=True)
        validated_response = ChatCompletionResponse.model_validate(raw_response)
        print(f"Type of validated_response: {type(validated_response)}")

        return validated_response





"Put everything between backticks just like the ```markdown ```"