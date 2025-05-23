from backend.src.client.anthropic_client import ChatCompletionRequest, ChatMessage, ChatCompletionResponse, AnthropicClient
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.config import CONFIG
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional
from backend.src.agents.financial_metrics_agent.model import FinancialMetrics, FinancialMetricsResponse, FinancialMetricsRequest
import asyncio
from anthropic import Anthropic


class FinancialMetricsAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    financial_client: FinancialDatasetsClient
    anthropic_client: AnthropicClient

    async def _get_financial_metrics(self, fin_metrics_request: FinancialMetricsRequest) -> FinancialMetricsResponse | None:
        # Implementation here
        try:
            metrics = self.financial_client.fetch_financial_metrics(
                ticker=fin_metrics_request.ticker,
                period=fin_metrics_request.period,
                limit=fin_metrics_request.limit
            )
        except Exception as e:
            print(f"Error fetching financial metrics: {e}")
            return None
        if not metrics:
            print("No financial metrics found.")
            return None

        return metrics

    async def analyze_metrics_with_llm(self,
                                        fin_metrics_request: FinancialMetricsRequest 
                                        ) -> ChatCompletionResponse:
        """
        Analyze trends using the LLM.
        """
        metrics = await self._get_financial_metrics(fin_metrics_request)
        # Implementation here

        analyze_metrics_request = ChatCompletionRequest(
            model="claude-3-7-sonnet-20250219",
            messages=[
                ChatMessage(role="user", content=f"Analyze the following financial metrics: {metrics}")],
            temperature=0.7,
            max_tokens=64000,
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

    anthropic_client = AnthropicClient(
        anthropic_api_key=CONFIG.anthropic_api_key,
        anthropic_api_url=CONFIG.anthropic_api_url,
        )

    # instantiate the agent with keyword args
    agent = FinancialMetricsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
    )

    # financial metrics request
    fin_metrics_request = FinancialMetricsRequest(
        ticker="AAPL",
        period="quarterly",
        limit=4,
    )

    analysis = asyncio.run(agent.analyze_metrics_with_llm(fin_metrics_request))
    print(analysis)


    