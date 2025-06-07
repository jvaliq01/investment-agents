import os 
import sys
from dotenv import load_dotenv
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.client.anthropic_client import AnthropicClient
from backend.src.config import CONFIG
import asyncio
from backend.src.agents.financial_metrics_agent.workflow import FinancialMetricsAgent
from backend.src.agents.financial_metrics_agent.model import FinancialMetricsRequest, FinancialMetricsResponse

from backend.src.agents.company_news_agent.workflow import CompanyNewsAgent
from backend.src.agents.company_news_agent.model import CompanyNewsRequest, CompanyNewsResponse

from backend.src.agents.financial_statements_agent.model import FinancialStatementsRequest, FinancialStatementsResponse
from backend.src.agents.financial_statements_agent.workflow_new import FinancialStatementsAgent

load_dotenv()


## TODO ## 
# 1. Make data model that holds the state of the orchestration
# 2. Make the orchestration agent
# 3. Add error handling across all agents
# 4. Add logging across all agents


async def master_orchestrator(
    ticker: str, 
    start_date: str,
    end_date: str) -> str:
    """Orchestrates the execution of financial analysis agents."""

    # Initialize clients
    financial_client = FinancialDatasetsClient(
        api_key=CONFIG.financial_datasets_api_key,
        base_url=CONFIG.financial_datasets_api_url,
    )
    anthropic_client = AnthropicClient(
        anthropic_api_key=CONFIG.anthropic_api_key,
        anthropic_api_url=CONFIG.anthropic_api_url,
    )



    # Create the request objects
    fin_metrics_request = FinancialMetricsRequest(
        ticker=ticker,
        period="quarterly",
        limit=4,
        report_period_gte=start_date,
        report_period_lte=end_date
    )
    financial_statements_request = FinancialStatementsRequest(
        ticker=ticker,
        period="quarterly",
        limit=4,
        report_period_gte=start_date,
        report_period_lte=end_date
    )
    company_news_request = CompanyNewsRequest(
        ticker=ticker,
        limit=10,
        # start_date=start_date,
        # end_date=end_date
    )

    ## REQUEST OBJECTS ##
    fin_metrics_agent = FinancialMetricsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        fin_metrics_request=fin_metrics_request,
    )
    company_news_agent = CompanyNewsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        company_news_request=company_news_request,
    )
    financial_statements_agent = FinancialStatementsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        fin_statements_request=financial_statements_request,
    )



    ## AGENT EXECUTION ##
    fin_metrics_analysis = await fin_metrics_agent.analyze_metrics_with_llm()
    company_news_analysis = await company_news_agent.analyze_metrics_with_llm()
    financial_statements_analysis = await financial_statements_agent.analyze_statements_with_llm() 

    print(f"FINANCIAL METRICS ANALYSIS: {fin_metrics_analysis}")
    print(f"COMPANY NEWS ANALYSIS: {company_news_analysis}")
    print(f"FINANCIAL STATEMENTS ANALYSIS: {financial_statements_analysis}")

    return "Done"

if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    start_date = "2020-01-01"
    end_date = "2023-01-01"
    
    result = asyncio.run(master_orchestrator(ticker, start_date, end_date))
    print(result)