from backend.src.client.anthropic_client import ChatCompletionRequest, ChatMessage, ChatCompletionResponse, AnthropicClient
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.config import CONFIG
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional
import asyncio
from anthropic import Anthropic
from textwrap import dedent
from backend.src.agents.financial_statements_agent.model import FinancialStatements, FinancialStatementsResponse, FinancialStatementsRequest



class FinancialStatementsAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    financial_client: FinancialDatasetsClient   
    anthropic_client: AnthropicClient
    fin_statements_request: FinancialStatementsRequest


    async def _get_financial_statements(self) -> FinancialStatementsResponse | None:
        print("\nFINANCIAL STATEMENTS REQUEST: ", self.fin_statements_request)
        # Implementation here
        try:
            statements = self.financial_client.fetch_financial_statements(
                self.fin_statements_request
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
        Create a prompt for the LLM to analyze financial statements.
        """
        statements = await self._get_financial_statements()
        if not statements:
            return "No financial statements available."

        prompt = dedent(f"""You are an expert financial analyst with a Chartered Financial Analyst (CFA) designation.
        You are tasked with analyzing the financial statements of a company.
        You are given the following financial statements:
        - Ticker: {self.fin_statements_request.ticker}
        - Period: {self.fin_statements_request.period}
        - Limit: {self.fin_statements_request.limit}'

        You are to analyze the following financial statements:
        {statements}:
                    \n""")
        # Add more statements as needed

        return prompt

    async def analyze_statements_with_llm(self) -> ChatCompletionResponse:
        """
        Analyze trends using the LLM.
        """
        # Implementation here
        prompt = await self._prompt_for_financial_statements()  

        analyze_statements_request = ChatCompletionRequest(
            model="claude-3-7-sonnet-20250219",
            messages=[
                ChatMessage(role="user", content=f"{prompt}")],
            temperature=0.7,
            max_tokens=32000
        )


        chat_response = await self.anthropic_client.chat_complete(analyze_statements_request)

        print(f"TYPE: {type(chat_response)}")

        return chat_response


# if __name__ == "__main__":
#     # Example usage
#     print("CONFIG: ", CONFIG)
#     financial_client = FinancialDatasetsClient(api_key=CONFIG.financial_datasets_api_key,
#                                                base_url=CONFIG.financial_datasets_api_url)

#     anthropic_client = AnthropicClient(anthropic_api_key=CONFIG.anthropic_api_key,
#                                         anthropic_api_url=CONFIG.anthropic_api_url) 
#     fin_statements_request = FinancialStatementsRequest(
#         ticker="AAPL",
#         period="quarterly",
#         limit=4,
#         report_period_gte="2023-01-01",
#         report_period_lte="2023-12-31"
#     )
#     fin_statements_agent = FinancialStatementsAgent(
#         financial_client=financial_client,
#         anthropic_client=anthropic_client,
#         fin_statements_request=fin_statements_request
#     )
#     asyncio.run(fin_statements_agent.analyze_statements_with_llm())

    