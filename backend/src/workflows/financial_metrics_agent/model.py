"""
Define the data model for the financial metrics agent.
"""

from typing import Optional, List
from pydantic import BaseModel


##### FINANCIAL METRICS #####
class FinancialMetrics(BaseModel):
    # Required core metadata and valuation ratios
    ticker: str
    report_period: str
    fiscal_period: str
    period: str
    currency: str 

    # Optional but still very valuable
    market_cap: float | None
    enterprise_value: float | None
    price_to_earnings_ratio: float | None
    price_to_book_ratio: float | None
    price_to_sales_ratio: float | None
    enterprise_value_to_ebitda_ratio: float | None
    enterprise_value_to_revenue_ratio: float | None
    gross_margin: float | None
    operating_margin: float | None
    net_margin: float | None
    return_on_equity: float | None
    return_on_assets: float | None
    current_ratio: float | None
    quick_ratio: float | None
    earnings_per_share: float | None
    debt_to_equity: float| None

    # Optional deeper analysis metrics
    free_cash_flow_yield: Optional[float] = None
    peg_ratio: Optional[float] = None
    return_on_invested_capital: Optional[float] = None
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    days_sales_outstanding: Optional[float] = None
    operating_cycle: Optional[float] = None
    working_capital_turnover: Optional[float] = None
    cash_ratio: Optional[float] = None
    operating_cash_flow_ratio: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage: Optional[float] = None

    # Growth metrics (optional but valuable)
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    book_value_growth: Optional[float] = None
    earnings_per_share_growth: Optional[float] = None
    free_cash_flow_growth: Optional[float] = None
    operating_income_growth: Optional[float] = None
    ebitda_growth: Optional[float] = None

    # Per-share and payout ratios (optional)
    payout_ratio: Optional[float] = None
    book_value_per_share: Optional[float] = None
    free_cash_flow_per_share: Optional[float] = None


class FinancialMetricsResponse(BaseModel):
    metrics: List[FinancialMetrics]

