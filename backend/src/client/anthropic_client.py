import os
import json
from typing import List, Optional, AsyncGenerator
import httpx
from pydantic import BaseModel, Field, field_validator

# Base URL for Claude endpoints
ANTHROPIC_API_URL = "https://api.anthropic.com"
DEFAULT_TIMEOUT = 30.0

# --------------------
# Pydantic Models
# --------------------

class BaseRequest(BaseModel):
    model: str = Field(..., description="Model name, e.g. 'claude-2.1' or 'claude-instant-v1'")

class CompleteRequest(BaseRequest):
    prompt: str = Field(..., description="The prompt string to be completed")
    max_tokens_to_sample: int = Field(256, ge=1, description="Max tokens to generate")
    temperature: float = Field(1.0, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop_sequences: Optional[List[str]] = Field(None, description="List of stop sequences")
    stream: bool = Field(False, description="Whether to stream response chunks")

    @field_validator("stop_sequences")
    @classmethod
    def _validate_stop_sequences(cls, v):
        if v is not None and not isinstance(v, list):
            raise ValueError("stop_sequences must be a list of strings")
        return v

class CompleteResponse(BaseModel):
    completion: str = Field(..., description="Generated text completion")
    stop_reason: Optional[str] = Field(None, description="Why the generation stopped")
    model: str = Field(..., description="Model that produced this response")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message: 'user' or 'assistant'")
    content: str = Field(..., description="Message content text")

class ChatCompletionRequest(BaseRequest):
    messages: List[ChatMessage] = Field(..., description="List of chat history messages")
    max_tokens: int = Field(1024, ge=1)
    temperature: float = Field(1.0, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop_sequences: Optional[List[str]] = None
    stream: bool = Field(False)
    system: Optional[str] = Field(None, description="System message to set the behavior of the assistant")

class ChatCompletionResponse(BaseModel):
    id: str = Field(...)
    type: str = Field(...)
    role: str = Field(...)
    content: List[dict] = Field(...)
    model: str = Field(...)
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: Optional[dict] = Field(None, description="Token usage information")

    @property
    def text(self) -> str:
        """Get the text content from the response."""
        if not self.content:
            return ""
        return self.content[0].get("text", "")

# --------------------
# API Client
# --------------------

class AnthropicClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key must be provided via parameter or ANTHROPIC_API_KEY"
            )
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        self._client = httpx.AsyncClient(
            base_url=ANTHROPIC_API_URL,
            timeout=timeout,
        )

    async def complete(
        self, request: CompleteRequest
    ) -> CompleteResponse:
        """
        Perform a one-shot completion call.
        """
        payload = request.model_dump_json(exclude_none=True)
        resp = await self._client.post(
            "/v1/complete", json=payload, headers=self.headers
        )
        resp.raise_for_status()
        return CompleteResponse(**resp.json())

    async def stream_complete(
        self, request: CompleteRequest
    ) -> AsyncGenerator[CompleteResponse, None]:
        """
        Stream completion in chunks.
        """
        payload = request.model_dump_json(exclude_none=True)
        payload['stream'] = True
        async with self._client.stream(
            "POST", "/v1/complete", json=payload, headers=self.headers
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield CompleteResponse(**data)

    async def chat_complete(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Perform a chat completion call.
        """
        payload = request.model_dump(exclude_none=True)
        # Ensure messages are properly formatted
        payload["messages"] = [msg.model_dump() for msg in request.messages]
        
        resp = await self._client.post(
            "/v1/messages", 
            json=payload, 
            headers={
                **self.headers,
                "anthropic-version": "2023-01-01"
            }
        )
        resp.raise_for_status()
        data = resp.json()
        return ChatCompletionResponse(**data)

    async def stream_chat_complete(
        self, request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionResponse, None]:
        """
        Stream chat completion in chunks.
        """
        payload = request.model_dump_json(exclude_none=True)
        payload['stream'] = True
        async with self._client.stream(
            "POST", "/v1/chat/completions", json=payload, headers=self.headers
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield ChatCompletionResponse(**data)

    async def close(self):
        """
        Close the underlying HTTP client.
        """
        await self._client.aclose()