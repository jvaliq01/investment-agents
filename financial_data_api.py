import os 
import requests
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.models import FinancialMetrics, FinancialMetricsResponse

def fetch_financial_data(
    ticker: str,
    period: str,
    limit: int):
    """
    Fetch financial data from the financial datasets API
    Parameters:
    - ticker: str: The stock ticker symbol
    - period: str: The period of the data to fetch (annual, quarterly, or ttm (trailing twelve months))
    - limit: int: The number of data points to fetch
    """
    # If not in cache or insufficient data, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    # create the URL
    url = (
        f'https://api.financialdatasets.ai/financial-metrics'
        f'?ticker={ticker}'
        f'&period={period}'
        f'&limit={limit}'
    )
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    # Parse response with Pydantic model
    metrics_response = FinancialMetricsResponse(**response.json())
    print("Metrics Response", metrics_response)

    financial_metrics = metrics_response.financial_metrics
    return financial_metrics



if __name__ == "__main__":
    fetch_financial_data(ticker="AAPL", period="ttm", limit=10)