"""
This module implements an agent for analyzing financial statements and making trading decisions.
The agent uses various tools to analyze financial data and make informed decisions.
"""
from typing import Optional, Dict, Any, List, Tuple
from abc import ABC, abstractmethod
from src.client.fin_datasetsai import FinancialDatasetsClient
from src.client.anthropic_client import AnthropicClient, ChatCompletionRequest, ChatMessage
from .model import (
    CompanyFinancialStatementsResponse,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement
)

class FinancialTool(ABC):
    """Abstract base class defining the interface for financial analysis tools."""
    
    @abstractmethod
    def execute(self, data: Any) -> Dict[str, Any]:
        """
        Execute the tool's analysis on the provided data.
        
        Args:
            data: The financial data to analyze. Type depends on the specific tool.
            
        Returns:
            Dict containing the analysis results.
        """
        pass

class ProfitabilityAnalyzer(FinancialTool):
    def execute(self, income: IncomeStatement) -> Dict[str, float]:
        """Analyze profitability metrics."""
        if not income.revenue or not income.net_income:
            return {}
        
        return {
            "gross_margin": (income.gross_profit / income.revenue * 100) if income.gross_profit else 0,
            "operating_margin": (income.operating_income / income.revenue * 100) if income.operating_income else 0,
            "net_margin": (income.net_income / income.revenue * 100) if income.net_income else 0,
        }

class LiquidityAnalyzer(FinancialTool):
    def execute(self, balance: BalanceSheet) -> Dict[str, float]:
        """Analyze liquidity metrics."""
        if not balance.current_assets or not balance.current_liabilities:
            return {}
        
        return {
            "current_ratio": balance.current_assets / balance.current_liabilities,
            "quick_ratio": (balance.current_assets - balance.inventory) / balance.current_liabilities if balance.inventory else 0,
        }

class LeverageAnalyzer(FinancialTool):
    def execute(self, balance: BalanceSheet) -> Dict[str, float]:
        """Analyze leverage metrics."""
        if not balance.total_assets or not balance.total_liabilities:
            return {}
        
        return {
            "debt_to_equity": balance.total_liabilities / balance.shareholders_equity if balance.shareholders_equity else 0,
            "debt_to_assets": balance.total_liabilities / balance.total_assets,
        }

class EfficiencyAnalyzer(FinancialTool):
    def execute(self, data: Tuple[IncomeStatement, BalanceSheet]) -> Dict[str, float]:
        """Analyze efficiency metrics."""
        income, balance = data
        if not income.revenue or not balance.total_assets:
            return {}
        
        return {
            "asset_turnover": income.revenue / balance.total_assets,
            "return_on_assets": (income.net_income / balance.total_assets * 100) if income.net_income else 0,
            "return_on_equity": (income.net_income / balance.shareholders_equity * 100) 
                if income.net_income and balance.shareholders_equity else 0,
        }

class CashFlowAnalyzer(FinancialTool):
    def execute(self, cash_flow: CashFlowStatement) -> Dict[str, float]:
        """Analyze cash flow metrics."""
        if not cash_flow.net_income:
            return {}
        
        return {
            "operating_cash_flow_ratio": (cash_flow.net_cash_flow_from_operations / cash_flow.net_income * 100) 
                if cash_flow.net_cash_flow_from_operations else 0,
            "free_cash_flow_yield": (cash_flow.free_cash_flow / cash_flow.net_income * 100) 
                if cash_flow.free_cash_flow else 0,
        }

class GrowthAnalyzer(FinancialTool):
    def execute(self, statements: List[IncomeStatement]) -> Dict[str, float]:
        """Analyze growth metrics."""
        if len(statements) < 2:
            return {}
        
        current = statements[0]
        previous = statements[1]
        
        def calculate_growth(current: float, previous: float) -> float:
            if previous == 0:
                return 0
            return ((current - previous) / abs(previous)) * 100
        
        return {
            "revenue_growth": calculate_growth(current.revenue or 0, previous.revenue or 0),
            "net_income_growth": calculate_growth(current.net_income or 0, previous.net_income or 0),
        }

class FinancialStatementsAgent:
    def __init__(self):
        self.financial_client = FinancialDatasetsClient()
        self.anthropic_client = AnthropicClient()
        self.tools = {
            "profitability": ProfitabilityAnalyzer(),
            "liquidity": LiquidityAnalyzer(),
            "leverage": LeverageAnalyzer(),
            "efficiency": EfficiencyAnalyzer(),
            "cash_flow": CashFlowAnalyzer(),
            "growth": GrowthAnalyzer(),
        }

    async def analyze(
        self,
        ticker: str,
        period: str = "Q1",
        limit: int = 4,
        report_period_gte: Optional[str] = None,
        report_period_lte: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a company's financial statements using available tools and provide trading recommendations.
        """
        # Fetch financial statements
        statements = self.financial_client.fetch_financial_statements(
            ticker=ticker,
            period=period,
            limit=limit,
            report_period_gte=report_period_gte,
            report_period_lte=report_period_lte,
        )

        # Use tools to analyze the data
        metrics = self._use_tools(statements)
        
        # Generate analysis prompt with calculated metrics
        prompt = self._generate_analysis_prompt(ticker, statements, metrics)
        
        # Get AI analysis
        analysis = await self._get_ai_analysis(prompt)
        
        return {
            "analysis": analysis,
            "metrics": metrics,
            "raw_data": statements.model_dump()
        }

    def _use_tools(self, statements: CompanyFinancialStatementsResponse) -> Dict[str, Any]:
        """Use available tools to analyze the financial statements."""
        if not statements.financials.income_statements or not statements.financials.balance_sheets:
            return {}

        latest_income = statements.financials.income_statements[0]
        latest_balance = statements.financials.balance_sheets[0]
        latest_cash_flow = statements.financials.cash_flow_statements[0] if statements.financials.cash_flow_statements else None

        # Use each tool to analyze relevant data
        metrics = {
            "profitability": self.tools["profitability"].execute(latest_income),
            "liquidity": self.tools["liquidity"].execute(latest_balance),
            "leverage": self.tools["leverage"].execute(latest_balance),
            "efficiency": self.tools["efficiency"].execute((latest_income, latest_balance)),
        }

        if latest_cash_flow:
            metrics["cash_flow"] = self.tools["cash_flow"].execute(latest_cash_flow)

        metrics["growth"] = self.tools["growth"].execute(statements.financials.income_statements)

        return metrics

    def _generate_analysis_prompt(
        self,
        ticker: str,
        statements: CompanyFinancialStatementsResponse,
        metrics: Dict[str, Any]
    ) -> str:
        """Generate a detailed prompt for financial analysis."""
        return f"""You are a professional financial analyst. Analyze the following financial data for {ticker} and provide a detailed trading recommendation.

Financial Metrics:
{metrics}

Raw Financial Data:
{statements.model_dump()}

Please provide your analysis in the following format:
1. Key Financial Metrics Analysis
   - Profitability Metrics
   - Liquidity Metrics
   - Leverage Metrics
   - Efficiency Metrics
   - Cash Flow Metrics
   - Growth Rates

2. Growth Trends
   - Revenue Growth
   - Profit Growth
   - Cash Flow Growth

3. Financial Health Assessment
   - Overall Financial Position
   - Key Strengths
   - Key Weaknesses

4. Risk Factors
   - Financial Risks
   - Operational Risks
   - Market Risks

5. Trading Recommendation
   - Buy/Hold/Sell with confidence level
   - Price Target
   - Time Horizon
   - Key Catalysts

6. Supporting Evidence
   - Key Metrics Supporting the Recommendation
   - Peer Comparison (if available)
   - Industry Context

Focus on:
- Revenue growth and profitability trends
- Debt levels and financial leverage
- Cash flow generation and management
- Working capital efficiency
- Return on equity and assets
- Market position and competitive advantages

Provide specific numbers and metrics to support your analysis."""

    async def _get_ai_analysis(self, prompt: str) -> Dict[str, Any]:
        """Get AI analysis using Claude."""
        request = ChatCompletionRequest(
            model="claude-3-5-sonnet-20240620",
            messages=[
                ChatMessage(role="user", content=prompt)
            ],
            max_tokens_to_sample=4000,
            temperature=0.7
        )
        
        response = await self.anthropic_client.chat_complete(request)
        return {
            "analysis": response.completion,
            "model": response.model,
            "stop_reason": response.stop_reason
        }

async def analyze_company(ticker: str) -> Dict[str, Any]:
    """
    Analyze a company's financial statements and get trading recommendations.
    
    Args:
        ticker: Company stock ticker
        
    Returns:
        Dict containing analysis results and trading recommendation
    """
    agent = FinancialStatementsAgent()
    return await agent.analyze(ticker=ticker)
