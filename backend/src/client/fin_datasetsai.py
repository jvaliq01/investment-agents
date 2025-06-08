import requests
from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from backend.exceptions import APIError, ValidationFailure
import asyncio
from backend.src.agents.company_news_agent.model import CompanyNewsResponse
from backend.src.agents.financial_metrics_agent.model import FinancialMetricsRequest, FinancialMetricsResponse
from backend.src.agents.financial_statements_agent.model import FinancialStatementsResponse
from backend.src.config import CONFIG

class FinancialDatasetsClient:
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        self.headers = {}
        self.headers["X-API-KEY"] = api_key

    def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        print("\nPARAMS: ", params)
        url = f"{self.base_url}/{endpoint}"
        print("\nURL: ", url)
        resp = requests.get(url, headers=self.headers, params=params)
        print("\nRESPONSE: ", resp.json())
        if resp.status_code != 200:
            raise APIError(f"{resp.status_code} {resp.text}")
        return resp.json()

    def fetch_financial_metrics(
        self, 
        fin_metrics_request: FinancialMetricsRequest
    ) -> FinancialMetricsResponse:
        ticker = fin_metrics_request.ticker
        period = fin_metrics_request.period
        limit = fin_metrics_request.limit
        report_period_gte = fin_metrics_request.report_period_gte
        report_period_lte = fin_metrics_request.report_period_lte

        data = self._get(
            "financial-metrics",
            {"ticker": ticker, "period": period, "limit": limit, "report_period_gte": report_period_gte, "report_period_lte": report_period_lte},
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
    ) -> FinancialStatementsResponse:
        params = {
            "ticker": ticker,
            "period": period,
            "limit": limit,
            "period": "ttm",
        }
        # if report_period_gte:
        #     params["report_period_gte"] = report_period_gte
        # if report_period_lte:
        #     params["report_period_lte"] = report_period_lte
        
        print("I GER HERE")

        data = self._get("financials", params)
        return CompanyFinancialStatementsResponse.model_validate(data)

    def fetch_company_news(
        self, ticker: str, 
        limit: Optional[int] = None, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
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
    client = FinancialDatasetsClient(
        api_key=CONFIG.financial_datasets_api_key,
        base_url=CONFIG.financial_datasets_api_url,
    )
    try:
        # company_news_response = client.fetch_company_news("AAPL", limit=5)  
        # print("\nCOMPANY NEWS: ", company_news_response)
        financial_statements_response = client.fetch_financial_statements("AAPL", "Q1", 5)
        print("\nFINANCIAL STATEMENTS: ", financial_statements_response)
        # financial_metrics_response = client.fetch_financial_metrics("AAPL", "quarterly",a 5)
        # print("\nFINANCIAL METRICS: ", financial_metrics_response)

    except APIError as e:
        print(f"API Error: {e}")
    except ValidationFailure as e:
        print(f"Validation Error: {e}")

    
if __name__ == "__main__":
    asyncio.run(run_fetch_all_data())
