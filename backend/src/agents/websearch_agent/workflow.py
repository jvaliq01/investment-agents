from openai import OpenAI
import os
from backend.src.config import CONFIG
from backend.src.client.oai.model import OpenAIRequest
from backend.src.client.oai.responses import OpenAIClient
import asyncio
from pydantic import BaseModel, Field



class WebSearchAgent(BaseModel):
    openai_client: OpenAIClient
    ticker: str



    async def _system_prompt(self) -> str:
        return """
You are a Chartered Financial Analyst (CFA) and a professional trader.
You are tasked with analyzing macroeconomic trends regarding a specific stock, the industry
it operates in, and the overall market conditions.

You will be provided with a stock ticker and you will need to perform a web search to gather
the latest news and information about the stock, its industry, and the overall market conditions.

You will then analyze the information and provide a comprehensive analysis of the stock, including
its current market position, potential risks, and opportunities for investment.

DO NOT:
Dive too deep into technical details or financial metrics. These will be provided by other
agents in the workflow.

DO:
Provide a high-level analysis of the stock, its industry, and the overall market conditions.
""".strip()

    async def _user_prompt(self) -> str:
        return f"""
Here is the stock that I want you to analyze: {self.ticker}
""".strip()


    async def analyze_web_with_llm(self) -> any:
        """
        Run the web search workflow using OpenAI's API.
        """
        user_prompt = await self._user_prompt()
        system_prompt = await self._system_prompt()


        request = OpenAIRequest(
            input=[
                {"role": "user", "content": user_prompt},
                {"role": "system", "content": system_prompt}
            ],
            model="gpt-4.1",
            tools=[{"type": "web_search_preview"}],
        )

        try: 
            response = await self.openai_client.create_responses_completion(request)
        except Exception as e:
            print(f"Error during OpenAI request: {e}")
            return None
        if not response:
            print("No response received from OpenAI.")
            return None

        return response.output[1].content[0].text

    
if __name__ == "__main__":
    # Example usage

    openai_client = OpenAIClient(
        api_key=CONFIG.openai_api_key,
        base_url=CONFIG.openai_api_url,
        timeout=CONFIG.timeout,
        max_retries=CONFIG.max_retries
    )
    agent = WebSearchAgent(openai_client=openai_client, ticker="AAPL")


    response = asyncio.run(agent.analyze_web_with_llm())
    print(response)

        

        
