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
from backend.src.agents.financial_statements_agent.model import CompanyFinancialStatements, CompanyFinancialStatementsResponse, CompanyFinancialStatementsRequest
import asyncio
from anthropic import Anthropic
from textwrap import dedent

class FinancialStatementsAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    financial_client: FinancialDatasetsClient   
    anthropic_client: AnthropicClient
    fin_statements_request: CompanyFinancialStatementsRequest


    async def _get_financial_statements(self) -> CompanyFinancialStatementsResponse | None:
        # Implementation here
        try:
            statements = self.financial_client.fetch_financial_statements(
                self.fin_statements_request.ticker,
                self.fin_statements_request.period,
                self.fin_statements_request.limit,
            )
        except Exception as e:
            print(f"Error fetching financial statements: {e}")
            return None
        if not statements:
            print("No financial statements found.")
            return None

        return statements

    async def _prompt_for_financial_statements(self) -> str:
        """
        Create a prompt for the LLM to analyze financial metrics.
        """

        statements = await self._get_financial_statements()
        if not statements:
            return "No financial metrics available."

        prompt = dedent(f"""You are an expert financial analyst with a Chartered Financial Analyst (CFA) designation.
        You are tasked with analyzing the financial statements of a company.
        You are given the following financial statements:
        - Ticker: {self.fin_statements_request.ticker}
        - Period: {self.fin_statements_request.period}
        - Limit: {self.fin_statements_request.limit}'

        You are to analyze the following financial statements:
        {statements}:
                    \n""")
        # Add more metrics as needed

        return prompt

    async def analyze_statements_with_llm(self) -> ChatCompletionResponse:
        """
        Analyze trends using the LLM.
        """
        # Implementation here
        prompt = await self._prompt_for_financial_statements()  

        analyze_statements_request = ChatCompletionRequest(
            model="claude-sonnet-4-20250514",
            messages=[
                ChatMessage(role="user", content=f"{prompt}")],
            temperature=0.7,
            max_tokens=32000
        )


        chat_response = await self.anthropic_client.chat_complete(analyze_statements_request)

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

    fin_statements_request = CompanyFinancialStatementsRequest(
        ticker="AAPL",
        period="quarterly",
        limit=4,
    )

    # instantiate the agent with keyword args
    agent = FinancialStatementsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        fin_statements_request=fin_statements_request,
    )




    analysis = asyncio.run(agent.analyze_statements_with_llm(fin_statements_request))
    print(analysis)


    