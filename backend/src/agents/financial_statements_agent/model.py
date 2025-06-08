"""
This module defines the data models for financial statements using Pydantic.
"""

from typing import Optional, List
from pydantic import BaseModel



# periods can be 'annual', 'quarterly', or 'monthly'
from typing import Literal
PeriodTypes = Literal["annual", "quarterly", "monthly"]

class FinancialStatementsRequest(BaseModel):
    ticker: str
    period: PeriodTypes
    limit: Optional[int] = None
    cik: Optional[str] = None
    report_period_gte: Optional[str] = None
    report_period_lte: Optional[str] = None

##### FINANCIAL STATEMENTS #####
class IncomeStatement(BaseModel):
    ticker: str
    report_period: str
    fiscal_period: str
    period: str
    currency: str
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_expense: Optional[float] = None
    selling_general_and_administrative_expenses: Optional[float] = None
    research_and_development: Optional[float] = None
    operating_income: Optional[float] = None
    interest_expense: Optional[float] = None
    ebit: Optional[float] = None
    income_tax_expense: Optional[float] = None
    net_income_discontinued_operations: Optional[float] = None
    net_income_non_controlling_interests: Optional[float] = None
    net_income: Optional[float] = None
    net_income_common_stock: Optional[float] = None
    preferred_dividends_impact: Optional[float] = None
    consolidated_income: Optional[float] = None
    earnings_per_share: Optional[float] = None
    earnings_per_share_diluted: Optional[float] = None
    dividends_per_common_share: Optional[float] = None
    weighted_average_shares: Optional[float] = None
    weighted_average_shares_diluted: Optional[float] = None

    class Config:
        extra = "ignore"
        validate_by_name = True 


class BalanceSheet(BaseModel):
    ticker: str
    report_period: str
    fiscal_period: str
    period: str
    currency: str
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    inventory: Optional[float] = None
    current_investments: Optional[float] = None
    trade_and_non_trade_receivables: Optional[float] = None
    non_current_assets: Optional[float] = None
    property_plant_and_equipment: Optional[float] = None
    goodwill_and_intangible_assets: Optional[float] = None
    investments: Optional[float] = None
    non_current_investments: Optional[float] = None
    outstanding_shares: Optional[float] = None
    tax_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    current_liabilities: Optional[float] = None
    current_debt: Optional[float] = None
    trade_and_non_trade_payables: Optional[float] = None
    deferred_revenue: Optional[float] = None
    deposit_liabilities: Optional[float] = None
    non_current_liabilities: Optional[float] = None
    non_current_debt: Optional[float] = None
    tax_liabilities: Optional[float] = None
    shareholders_equity: Optional[float] = None
    retained_earnings: Optional[float] = None
    accumulated_other_comprehensive_income: Optional[float] = None
    total_debt: Optional[float] = None

    class Config:
        extra = "ignore"
        validate_by_name = True


class CashFlowStatement(BaseModel):
    ticker: str
    report_period: str
    fiscal_period: str
    period: str
    currency: str
    net_income: Optional[float] = None
    depreciation_and_amortization: Optional[float] = None
    share_based_compensation: Optional[float] = None
    net_cash_flow_from_operations: Optional[float] = None
    capital_expenditure: Optional[float] = None
    business_acquisitions_and_disposals: Optional[float] = None
    investment_acquisitions_and_disposals: Optional[float] = None
    net_cash_flow_from_investing: Optional[float] = None
    issuance_or_repayment_of_debt_securities: Optional[float] = None
    issuance_or_purchase_of_equity_shares: Optional[float] = None
    dividends_and_other_cash_distributions: Optional[float] = None
    net_cash_flow_from_financing: Optional[float] = None
    change_in_cash_and_equivalents: Optional[float] = None
    effect_of_exchange_rate_changes: Optional[float] = None
    ending_cash_balance: Optional[float] = None
    free_cash_flow: Optional[float] = None

    class Config:
        extra = "ignore"
        validate_by_name = True


class FinancialStatements(BaseModel):
    income_statements: List[IncomeStatement]
    balance_sheets: List[BalanceSheet]
    cash_flow_statements: List[CashFlowStatement]

    class Config:
        extra = "ignore"
        validate_by_name = True


class FinancialStatementsResponse(BaseModel):
    financials: FinancialStatements
 
    class Config:
        extra = "ignore"
        validate_by_name = True
    
class FinancialStatementsRequest(BaseModel):
    ticker: str
    period: str
    limit: int
    report_period_gte: str
    report_period_lte: str

