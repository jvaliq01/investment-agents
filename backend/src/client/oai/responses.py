from backend.src.client.oai import model as oai
from backend.src.config import CONFIG
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
import asyncio
from typing import Literal
from typing import Optional
import json




class OpenAIClient(BaseModel):
    api_key: str | None = CONFIG.openai_api_key
    base_url: str | None= CONFIG.openai_api_url
    timeout: Optional[float] = CONFIG.timeout
    max_retries: int = CONFIG.max_retries

    async def create_responses_completion(self, request: oai.OpenAIRequest) -> oai.OpenAIResponse:
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
        except Exception as e:
            raise Exception(f"Error creating responses completion: {e}")

        # validate the response
        validated_response = oai.OpenAIResponse.model_validate(response.model_dump(exclude_none=True))

        return validated_response
    

    async def run_oai_responses_request(
        self,
        request: oai.OpenAIRequest,
    ) -> oai.OpenAIResponse:
        try:
            response: oai.OpenAIResponse = await self.create_responses_completion(request)
            validated_response = oai.OpenAIResponse.model_validate(response.model_dump(exclude_none=True))
        except Exception as e:
            raise Exception(f"Error running OpenAI responses request: {e}")
        
        if not validated_response.output:
            raise Exception("No output found in the response.")

        if validated_response.output[0].type == "message":
            output_text: str = validated_response.output[0].content[0].text

        elif validated_response.output[0].type == "web_search_call":
            output_text: str = validated_response.output[1].content[0].text

        if not output_text:
            print("No output text found in the response.")
            return None

        return output_text.strip()
    


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

