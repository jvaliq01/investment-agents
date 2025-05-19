import os 
import sys
from dotenv import load_dotenv
from backend.src.agents.financial_statements_agent.workflow import FinancialStatementsAgent
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.client.anthropic_client import AnthropicClient
from backend.src.config import CONFIG

load_dotenv()

async def master_orchestrator(ticker: str, start_date: str, end_date: str):
    """Orchestrates the execution of financial analysis agents."""
    financial_client = FinancialDatasetsClient(CONFIG.financial_datasets_api_key, CONFIG.financial_datasets_api_url)
    anthropic_client = AnthropicClient(CONFIG.anthropic_api_key)
    
    agent = FinancialStatementsAgent(financial_client, anthropic_client)
    return await agent.analyze(ticker=ticker, report_period_gte=start_date, report_period_lte=end_date)

