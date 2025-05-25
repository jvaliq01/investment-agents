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
import asyncio
from anthropic import Anthropic
from textwrap import dedent
from backend.src.agents.company_news_agent.model import CompanyNewsRequest, CompanyNewsResponse


class CompanyNewsAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    financial_client: FinancialDatasetsClient
    anthropic_client: AnthropicClient
    company_news_request: CompanyNewsRequest

    async def _get_company_news(self, news_request: CompanyNewsRequest) -> CompanyNewsResponse | None:
        # Implementation here
        try:
            company_news = self.financial_client.fetch_company_news(
                ticker=news_request.ticker,
                limit=news_request.limit,
                start_date=news_request.start_date,
                end_date=news_request.end_date
            )
            

            print(f"NEWS: {company_news}")
        except Exception as e:
            print(f"Error fetching company news: {e}")
            return None
        if not company_news:
            print("No company news found.")
            return None

        return company_news

    async def _prompt_for_company_metrics(self) -> str:
        """
        Create a prompt for the LLM to analyze financial metrics.
        """
        company_news_response = await self._get_company_news(self.company_news_request)
        if not company_news_response:
            return "No financial metrics available."

        prompt = dedent(f"""You are an expert financial analyst with a Chartered Financial Analyst (CFA) designation.
        You are tasked with analyzing the recent news of a company and its impact on the financial metrics.
        You are given the following financial metrics:
        - Ticker: {company_news_request.ticker}
        - Start Date: {company_news_request.start_date}
        - End Date: {company_news_request.end_date}
        - Limit: {company_news_request.limit}'


        Here is the recent news:
        {company_news_response}:
                    \n""")

        

            # Add more metrics as needed

        return prompt

    async def analyze_metrics_with_llm(self) -> ChatCompletionResponse:
        """
        Analyze trends using the LLM.
        """
        # Fetch prompt
        prompt = await self._prompt_for_company_metrics()
        if not prompt:
            return "No financial metrics available."

        # Implementation here
        analyze_news_request = ChatCompletionRequest(
            model="claude-3-7-sonnet-20250219",
            messages=[
                ChatMessage(role="user", content=f"{prompt}")],
            temperature=0.7,
            max_tokens=32000,
        )

        chat_response = await self.anthropic_client.chat_complete(analyze_news_request)
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

    # financial metrics request
    company_news_request = CompanyNewsRequest(
        ticker="AAPL",
        limit=4,
    )

    # instantiate the agent with keyword args
    agent = CompanyNewsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        company_news_request=company_news_request
    )

    analysis = asyncio.run(agent.analyze_metrics_with_llm())
    print(analysis)


    