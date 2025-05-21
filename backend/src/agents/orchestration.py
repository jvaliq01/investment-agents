import os 
import sys
from dotenv import load_dotenv
from backend.src.agents.financial_statements_agent.workflow import FinancialStatementsAgent
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.client.anthropic_client import AnthropicClient
from backend.src.config import CONFIG
import asyncio

print("\nCONFIG", CONFIG)

load_dotenv()

async def master_orchestrator(ticker: str, start_date: str, end_date: str):
    """Orchestrates the execution of financial analysis agents."""
    financial_client = FinancialDatasetsClient(CONFIG.financial_datasets_api_key, CONFIG.financial_datasets_api_url)
    anthropic_client = AnthropicClient(CONFIG.anthropic_api_key)
    
    agent = FinancialStatementsAgent(financial_client, anthropic_client)

    analsysis = await agent.analyze(ticker=ticker, report_period_gte=start_date, report_period_lte=end_date)
    print("ANALYSIS", analsysis)


    return analsysis

if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    result = asyncio.run(master_orchestrator(ticker, start_date, end_date))
    print("RESULT", result)

