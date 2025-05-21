import os
import json
from typing import List, Optional, AsyncGenerator, Dict
import httpx
from pydantic import BaseModel, Field, field_validator
import asyncio

# Base URL for Claude endpoints
ANTHROPIC_API_URL = "https://api.anthropic.com"
DEFAULT_TIMEOUT = 120.0  # Increased from 30.0 to 120.0 seconds
ANTHROPIC_API_VERSION = "2023-06-01"  # Updated to a recent version
MAX_RETRIES = 3  # Maximum number of retry attempts

# --------------------
# Pydantic Models
# --------------------

class BaseRequest(BaseModel):
    model: str = Field(..., description="Model name, e.g. 'claude-3-opus-20240229'")

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
    content: List[Dict[str, str]] = Field(...)  # Changed to List[Dict] to match Anthropic's response format
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
            "anthropic-version": ANTHROPIC_API_VERSION,
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
        
        Note: This API (/v1/complete) is deprecated. Consider using chat API instead.
        """
        payload = request.model_dump(exclude_none=True)
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
        
        Note: This API (/v1/complete) is deprecated. Consider using chat API instead.
        """
        request_copy = request.model_copy()
        request_copy.stream = True
        payload = request_copy.model_dump(exclude_none=True)
        
        async with self._client.stream(
            "POST", "/v1/complete", json=payload, headers=self.headers
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line and line.strip():
                    data = json.loads(line)
                    yield CompleteResponse(**data)

    async def chat_complete(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Perform a chat completion call using the messages API with retry logic.
        """
        payload = request.model_dump(exclude_none=True)
        # Format messages to match Anthropic's expected format
        payload["messages"] = [msg.model_dump() for msg in request.messages]
        
        last_exception = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = await self._client.post(
                    "/v1/messages", 
                    json=payload,
                    headers=self.headers
                )
                resp.raise_for_status()
                data = resp.json()
                return ChatCompletionResponse(**data)
            except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff: 2^attempt seconds
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise last_exception
            except Exception as e:
                raise e

    async def stream_chat_complete(
        self, request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionResponse, None]:
        """
        Stream chat completion in chunks using the messages API.
        """
        request_copy = request.model_copy()
        request_copy.stream = True
        payload = request_copy.model_dump(exclude_none=True)
        
        # Format messages to match Anthropic's expected format
        payload["messages"] = [msg.model_dump() for msg in request.messages]
        
        async with self._client.stream(
            "POST", "/v1/messages", json=payload, headers=self.headers
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line and line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("type") == "content_block_delta":
                            # Handle streaming response format which is different
                            # This is a simplification - you may need to accumulate deltas
                            yield ChatCompletionResponse(
                                id=data.get("message_id", ""),
                                type=data.get("type", ""),
                                role="assistant",
                                content=data.get("delta", {}).get("text", ""),
                                model=request.model,
                                stop_reason=None
                            )
                        elif data.get("type") == "message_stop":
                            # Final message with stop reason
                            yield ChatCompletionResponse(
                                id=data.get("message_id", ""),
                                type="message_stop",
                                role="assistant",
                                content="",
                                model=request.model,
                                stop_reason=data.get("stop_reason")
                            )
                    except json.JSONDecodeError:
                        continue

    async def close(self):
        """
        Close the underlying HTTP client.
        """
        await self._client.aclose()