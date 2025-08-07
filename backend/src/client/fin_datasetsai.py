from datetime import date
from tracemalloc import start
import requests
from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from backend.exceptions import APIError, ValidationFailure
import asyncio
from backend.src.agents.company_news_agent.model import CompanyNewsResponse
from backend.src.agents.candles_agent.model import CompanyCandlesResponse
from backend.src.agents.financial_metrics_agent.model import FinancialMetricsRequest, FinancialMetricsResponse
from backend.src.agents.financial_statements_agent.model import FinancialStatementsRequest, FinancialStatementsResponse
from backend.src.config import CONFIG

class FinancialDatasetsClient:
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        self.headers = {}
        self.headers["X-API-KEY"] = api_key

    async def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        resp = requests.get(url, headers=self.headers, params=params)
        if resp.status_code != 200:
            raise APIError(f"{resp.status_code} {resp.text}")
        return resp.json()

    async def fetch_financial_metrics(
        self, 
        fin_metrics_request: FinancialMetricsRequest
    ) -> FinancialMetricsResponse:
        ticker = fin_metrics_request.ticker
        period = fin_metrics_request.period
        limit = fin_metrics_request.limit
        report_period_gte = fin_metrics_request.report_period_gte
        report_period_lte = fin_metrics_request.report_period_lte

        data = await self._get(
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

    async def fetch_financial_statements(
        self,
        request: FinancialStatementsRequest,
    ) -> FinancialStatementsResponse:
        params = {
            "ticker": request.ticker,
            "period": request.period,
            "limit": request.limit,
            "period": request.period,
            "report_period_gte": request.report_period_gte,
            "report_period_lte": request.report_period_lte,
        }
        # if report_period_gte:
        #     params["report_period_gte"] = report_period_gte
        # if report_period_lte:
        #     params["report_period_lte"] = report_period_lte
        

        data = await self._get("financials", params)
        return FinancialStatementsResponse.model_validate(data)

    async def fetch_company_news(
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
    
    async def fetch_price_data(
        self,
        ticker: str,
    ):
        params = {
            "ticker": ticker,
            "interval": "daily",
            "interval_multiplier": 1,
            "start_date": date.today().isoformat()
        }
        data = await self._get("prices", params)
        if not data:
            raise APIError("No price data found")
        return CompanyCandlesResponse.model_validate(data)

async def run_fetch_all_data():
    client = FinancialDatasetsClient(
        api_key=CONFIG.financial_datasets_api_key,
        base_url=CONFIG.financial_datasets_api_url,
    )

    financial_statements_request = FinancialStatementsRequest(
        ticker="AAPL",
        period="quarterly",
        limit=5,
        report_period_gte="2022-01-01",
        report_period_lte="2023-01-01"
    )
    try:
        financial_statements_response = await client.fetch_financial_statements(financial_statements_request)
        return financial_statements_response


    except APIError as e:
        print(f"API Error: {e}")
    except ValidationFailure as e:
        print(f"Validation Error: {e}")

    
if __name__ == "__main__":
    asyncio.run(run_fetch_all_data())
