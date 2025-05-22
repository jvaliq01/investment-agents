from backend.src.client.anthropic_client import ChatCompletionRequest, ChatMessage, ChatCompletionResponse, AnthropicClient
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.config import CONFIG
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional
from backend.src.agents.financial_metrics_agent.model import FinancialMetrics, FinancialMetricsResponse
import asyncio
from anthropic import Anthropic


class FinancialMetricsAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    financial_client: FinancialDatasetsClient

    async def _get_financial_metrics(self, ticker: str, period: str, limit: int) -> FinancialMetricsResponse | None:
        # Implementation here
        try:
            metrics = self.financial_client.fetch_financial_metrics(
                ticker=ticker,
                period=period,
                limit=limit
            )
        except Exception as e:
            print(f"Error fetching financial metrics: {e}")
            return None
        if not metrics:
            print("No financial metrics found.")
            return None

        return metrics

    async def analyze_metrics_with_llm(self) -> ChatCompletionResponse:
        """
        Analyze trends using the LLM.
        """
        metrics = await self._get_financial_metrics(ticker="AAPL", period="quarterly", limit=4)
        # Implementation here

        analyze_metrics_request = ChatCompletionRequest(
            model="claude-3-7-sonnet-20250219",
            messages=[
                ChatMessage(role="user", content=f"Analyze the following financial metrics: {metrics}")],
            temperature=0.7,
            max_tokens=64000,
        )

        anthropic_client = AnthropicClient(
            anthropic_api_key=CONFIG.anthropic_api_key,
            anthropic_api_url=CONFIG.anthropic_api_url,
        )

        chat_response = await anthropic_client.chat_complete(analyze_metrics_request)

        print(f"TYPE: {type(chat_response)}")

        return chat_response

    

if __name__ == "__main__":
    # Example usage
    # build our clients first
    financial_client = FinancialDatasetsClient(
        CONFIG.financial_datasets_api_key,
        CONFIG.financial_datasets_api_url,
    )

    # instantiate the agent with keyword args
    agent = FinancialMetricsAgent(
        financial_client=financial_client,
    )

    analysis = asyncio.run(agent.analyze_metrics_with_llm())
    print(analysis)


    