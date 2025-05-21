import requests
from typing import Any, Dict
from pydantic import ValidationError

from backend.exceptions import APIError, ValidationFailure
import asyncio
from backend.src.agents.company_news_agent.model import CompanyNewsResponse
from backend.src.agents.financial_metrics_agent.model import FinancialMetricsResponse
from backend.src.agents.financial_statements_agent.model import CompanyFinancialStatementsResponse
import os 
from dotenv import load_dotenv
load_dotenv()

class FinancialDatasetsClient:
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        self.headers = {}
        self.headers["X-API-KEY"] = api_key

    def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper method to make GET requests to the API.
        Args:
            endpoint (str): The API endpoint to call.
            params (Dict[str, Any]): The query parameters to include in the request.
        Returns:
            Dict[str, Any]: The JSON response from the API.
        """

        url = (f"{self.base_url}{endpoint}"    
               f"{'?' if params else ''}{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        )
        print("\nURL: ", url)
        resp = requests.get(url, headers=self.headers, params=params)
        if resp.status_code != 200:
            raise APIError(f"{resp.status_code} {resp.text}")
        return resp.json()

    def fetch_financial_metrics(
        self, ticker: str, period: str, limit: int
    ) -> FinancialMetricsResponse:
        data = self._get(
            "financial-metrics",
            {"ticker": ticker, "period": period, "limit": limit},
        )
        metrics = data.get("financial_metrics", [])
        if not metrics:
            raise APIError("No financial metrics in response")

        valid = []
        for i, m in enumerate(metrics):
            try:
                valid.append(FinancialMetricsResponse.model_validate({"metrics": [m]}).metrics[0])
            except ValidationError as e:
                # log.warning(...)
                continue

        if not valid:
            raise ValidationFailure("All metrics failed validation")

        return FinancialMetricsResponse(metrics=valid)

    def fetch_financial_statements(
        self,
        ticker: str,
        period: str,
        limit: int,
        report_period_gte: str = None,
        report_period_lte: str = None,
    ) -> CompanyFinancialStatementsResponse:
        params = {
            "ticker": ticker,
            "period": period,
            "limit": limit,
        }
        if report_period_gte:
            params["report_period_gte"] = report_period_gte
        if report_period_lte:
            params["report_period_lte"] = report_period_lte

        data = self._get("financials", params)
        return CompanyFinancialStatementsResponse.model_validate(data)

    def fetch_company_news(
        self, ticker: str, limit: int, start_date: str = None, end_date: str = None
    ) -> CompanyNewsResponse:

        params = {"ticker": ticker, "limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date


        data = self._get("news", params)
        if not data:
            raise APIError("No news found")
        return CompanyNewsResponse.model_validate(data)

async def run_fetch_all_data():
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    base_url = os.getenv("FINANCIAL_DATASETS_API_URL")
    
    client = FinancialDatasetsClient(
        api_key= api_key,
        base_url= base_url
    )
    try:
        company_news_response = client.fetch_company_news("AAPL", 5)
        print("\nCOMPANY NEWS: ", company_news_response)
        financial_statements_response = client.fetch_financial_statements("AAPL", "Q1", 5)
        print("\nFINANCIAL STATEMENTS: ", financial_statements_response)
        financial_metrics_response = client.fetch_financial_metrics("AAPL", "quarterly", 5)
        print("\nFINANCIAL METRICS: ", financial_metrics_response)

    except APIError as e:
        print(f"API Error: {e}")
    except ValidationFailure as e:
        print(f"Validation Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_fetch_all_data())
