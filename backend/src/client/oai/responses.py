from backend.src.client.oai.model.request_model import OpenAIRequest
from backend.src.client.oai.model.response_model import OpenAIResponse, OpenAIResponseError
from backend.src.config import CONFIG
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
import asyncio
from typing import Literal
from typing import Optional
import json
from openai import (
    APIError,
    APIConnectionError,
    RateLimitError,
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    UnprocessableEntityError,
    InternalServerError,
)


REQUEST_ERRORS = (
    APIError,
    APIConnectionError,
    RateLimitError,
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    UnprocessableEntityError,
    InternalServerError,
)




class AsyncOpenAIClient(BaseModel):
    api_key: Optional[str] = CONFIG.openai_api_key
    base_url: Optional[str] = CONFIG.openai_api_url
    timeout: Optional[float] = CONFIG.timeout
    max_retries: int = CONFIG.max_retries

    async def create_responses_completion(self, request: OpenAIRequest) -> OpenAIResponse:
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )

        pretty = json.dumps(request.model_dump(exclude_none=True), indent=2, sort_keys=True)
        print(f"Payload for create_responses_completion:\n{pretty}")

        payload = request.model_dump(exclude_none=True)

        try:
            response = await client.responses.create(**payload)
        except REQUEST_ERRORS as e:
            raise OpenAIResponseError(
                f"Failed to create response completion: {type(e).__name__}: {e}"
            ) from e
                
        # validate the response
        validated_response = OpenAIResponse.model_validate(response.model_dump(exclude_none=True))

        return validated_response
    

    async def run_oai_responses_request(
        self,
        request: OpenAIRequest,
    ) -> str | None:
        try:
            response: OpenAIResponse = await self.create_responses_completion(request)
            validated_response = OpenAIResponse.model_validate(response.model_dump(exclude_none=True))
        except Exception as e:
            print(f"Error during OpenAI request: {e}")
            return None
        
        assert validated_response.output, "Why is the output empty? This should not happen."
        if validated_response.output[0].type == "message":
            output_text: str = validated_response.output[0].content[0].text

        elif validated_response.output[0].type == "web_search_call":
            output_text: str = validated_response.output[1].content[0].text

        if not output_text:
            print("No output text found in the response.")
            return None

        return output_text.strip()
     

