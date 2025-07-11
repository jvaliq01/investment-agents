from responses import OpenAIClient, OpenAIRequest, OpenAIResponse
from typing import Literal, Union, Dict, Any, Optional
import asyncio
import json



def input_prompt():
    """
    Function to prompt the user for input.
    This is a placeholder function that can be replaced with actual input handling logic.
    """
    return [
        {
            "role": "user",
            "content": """
            Can you give me some current news on Nvidia and create a trading strategy based on the 
            latest news and the current market conditions?""".strip()
        }
    ]

async def main():
    openai_client = OpenAIClient()

    request = OpenAIRequest(
        input=input_prompt(),
        model="gpt-4o",
    )

    response: str = await openai_client.run_oai_responses_request(request)

    print(f"Response From OpenAI Test:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
    
