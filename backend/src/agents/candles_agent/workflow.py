from pydantic import BaseModel, ConfigDict, Field

from backend.src.agents.candles_agent.model import CompanyCandlesResponse
from backend.src.client.anthropic_client import ChatCompletionRequest
from backend.src.client import anthropic_client
from backend.src.client.fin_datasetsai import FinancialDatasetsClient

class CandleAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    financial_client: FinancialDatasetsClient
    anthropic_client: anthropic_client.AnthropicClient

    async def _get_company_candles(self, ticker: str) -> CompanyCandlesResponse | None:
        """
        Fetch company candles data.
        """
        try:
            candles_response = await self.financial_client.fetch_price_data (
                ticker=ticker
            )
        except Exception as e:
            print(f"Error fetching company candles: {e}")
            return None
        
        if not candles_response:
            print("No company candles found.")
            return None

        return candles_response
    
    async def _prompt_for_company_candles(self, ticker: str) -> str:
        """
        Create a prompt for the LLM to analyze company candles.
        """
        candles = await self._get_company_candles(ticker)
        if not candles:
            return "No company candles data available."

        prompt = f"""
        You are an expert financial analyst with a Chartered Financial Analyst (CFA) designation.
        You are tasked with analyzing the price data of a company.
        Here is the price data for {ticker}:
        {candles}
        """
        
        return prompt
    
    async def analyze_candles_with_llm(self, ticker: str) -> :
        """
        Analyze company candles using the LLM.
        """
        prompt = await self._prompt_for_company_candles(ticker)

        request = anthropic_client.ChatCompletionRequest(
            messages=[
                self.anthropic_client.ChatMessage(role="user", content=prompt)
            ]
        )

        response = await self.anthropic_client.chat_complete(request)
        if not response:
            return self.anthropic_client.ChatCompletionResponse(text="Error in LLM response.")

        return response

