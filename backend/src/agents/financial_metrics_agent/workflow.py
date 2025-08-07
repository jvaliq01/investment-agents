"""
Financial Metrics Agent Workflow
This module contains the FinancialMetricsAgent class, which is responsible for analyzing financial metrics 
using a language model (LLM) and fetching data from a financial datasets API.
"""

from backend.src.client.anthropic_client import ChatCompletionRequest, ChatMessage, ChatCompletionResponse, AnthropicClient
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.config import CONFIG
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional
from backend.src.agents.financial_metrics_agent.model import FinancialMetrics, FinancialMetricsResponse, FinancialMetricsRequest
import asyncio
from anthropic import Anthropic
from textwrap import dedent


class FinancialMetricsAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    financial_client: FinancialDatasetsClient   
    anthropic_client: AnthropicClient
    fin_metrics_request: FinancialMetricsRequest


    async def _get_financial_metrics(self) -> FinancialMetricsResponse:
        # Implementation here
        try:
            metrics = await self.financial_client.fetch_financial_metrics(
                self.fin_metrics_request
            )
        except Exception as e:
            raise Exception(f"Error fetching financial metrics: {e}")

        if not metrics:
            raise Exception("No financial metrics found.")

        return metrics

    async def _prompt_for_financial_metrics(self) -> str:
        """
        Create a prompt for the LLM to analyze financial metrics.
        """
        metrics = await self._get_financial_metrics()
        if not metrics:
            return "No financial metrics available."

        prompt = dedent(f"""You are an expert financial analyst with a Chartered Financial Analyst (CFA) designation.
You are tasked with analyzing the financial metrics of a company.
You are given the following financial metrics:
- Ticker: {self.fin_metrics_request.ticker}
- Period: {self.fin_metrics_request.period}
- Limit: {self.fin_metrics_request.limit}'

You are to analyze the following financial metrics:
{metrics}:



**DO NOT**:
- Give a recommendation on whether to buy, sell, or hold the stock. This will be done by another agent in the workflow.
**DO**:
- Provide an analysis of the financial metrics, including trends, patterns, and any significant changes over the specified period.
- Focus more on trends and patterns seen in more current time periods, rather than historical data.
                    \n""")
        # Add more metrics as needed

        return prompt

    async def analyze_metrics_with_llm(self) -> ChatCompletionResponse:
        """
        Analyze trends using the LLM.
        """
        # Implementation here
        prompt = await self._prompt_for_financial_metrics()  

        analyze_metrics_request = ChatCompletionRequest(
            model="claude-sonnet-4-20250514",
            messages=[
                ChatMessage(role="user", content=f"{prompt}")],
            temperature=0.7,
            max_tokens=32000
        )

        try: 
            chat_response = await self.anthropic_client.chat_complete(analyze_metrics_request)
        except Exception as e: 
            raise Exception(f"Error during LLM analysis: {e}")

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

    fin_metrics_request = FinancialMetricsRequest(
        ticker="AAPL",
        period="quarterly",
        limit=4,
    )

    # instantiate the agent with keyword args
    agent = FinancialMetricsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        fin_metrics_request=fin_metrics_request,
    )




    analysis = asyncio.run(agent.analyze_metrics_with_llm(fin_metrics_request))
    print(analysis)


    