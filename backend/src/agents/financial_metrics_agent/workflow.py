# from client.anthropic_client import AnthropicClient 
import os 
import sys 
## This is a workaround to add the parent directory to the path
print(sys.path)
from src.client.fin_datasetsai import FinancialDatasetsClient
from src.agents.orchestration import CONFIG


async def get_financial_metrics(
        ticker: str,
        period: str,
        limit: int,
    ) -> str | None:
    """
    Fetch financial metrics for a given stock ticker.
    """
    client = FinancialDatasetsClient()
    response = client.fetch_financial_metrics(ticker, period, limit)

    if not response:
        return None
    
    return response.metrics


async def run_financial_metrics_agent(
        ticker: str,
        period: str,
        limit: int,
    ) -> str | None:
    """
    Run the financial metrics agent workflow.
    """
    metrics = await get_financial_metrics(ticker, period, limit)


if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    period = "Q1"
    limit = 4

    result = get_financial_metrics(ticker, period, limit)
    print(result)
    

    






    