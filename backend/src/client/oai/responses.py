from backend.src.client.oai.model.request_model import OpenAIRequest
from backend.src.config import CONFIG
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
import asyncio
from typing import Literal
from typing import Optional





class OpenAIClient(BaseModel):
    api_key: str = CONFIG.openai_api_key
    base_url: str = CONFIG.openai_api_url
    timeout: Optional[float] = CONFIG.timeout
    max_retries: Optional[int] = CONFIG.max_retries

    async def create_responses_completion(self, request: OpenAIRequest) -> any:
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )

        payload = request.model_dump(exclude_none=True)
        print(f"Payload for create_responses_completion: {payload}")

        try:
            response = await client.responses.create(**payload)
        except Exception as e:
            print(f"Error in create_responses_completion: {e}")
            return None

        return response
    


# Needs more work !!!!!!!!!!!

class TextInputResponse(BaseModel):
    id: str
    object: str = "response"
    created_at: int
    background: bool | None = None

     



# if __name__ == "__main__":
#     # Example usage
#     openai_client = OpenAIClient()

#     request = OpenAIRequest(
#         input=[{"role": "user", "content": """
#         Can you give me some current news on Nvidia and create a trading strategy based on the 
#         lastet news and the current market conditions?""".strip()}],
#         model="gpt-4o",
#         tools=[{"type": "web_search_preview"}],
#     )

#     response = asyncio.run(openai_client.create_responses_completion(request))
#     print(response)

