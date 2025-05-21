"""
This module implements an agent for analyzing financial statements and making trading decisions.
The agent uses various tools to analyze financial data and make informed decisions.
"""
from typing import Optional, Dict, Any, List, Tuple
from abc import ABC, abstractmethod
from backend.src.client.fin_datasetsai import FinancialDatasetsClient
from backend.src.client.anthropic_client import AnthropicClient, ChatCompletionRequest, ChatMessage
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

class LiquidityAnalyzer(FinancialTool):
    def execute(self, balance: BalanceSheet) -> Dict[str, float]:
        """Analyze liquidity metrics."""
        if not balance.current_assets or not balance.current_liabilities:
            return {}
        
        return {
            "current_ratio": balance.current_assets / balance.current_liabilities,
            "quick_ratio": (balance.current_assets - balance.inventory) / balance.current_liabilities if balance.inventory else 0,
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
    def __init__(self, financial_datasets_client, anthropic_client):
        self.financial_client = financial_datasets_client
        self.anthropic_client = anthropic_client
        self.tools = {
            "liquidity": LiquidityAnalyzer(),
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
            "liquidity": self.tools["liquidity"].execute(latest_balance),
            "growth": self.tools["growth"].execute(statements.financials.income_statements),
        }

        # if latest_cash_flow:
        #     metrics["cash_flow"] = self.tools["cash_flow"].execute(latest_cash_flow)

        # metrics["growth"] = self.tools["growth"].execute(statements.financials.income_statements)

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
            model="claude-3-sonnet-20240229",
            messages=[
                ChatMessage(role="user", content=prompt)
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        print(f"Sending request to Anthropic")
        response = await self.anthropic_client.chat_complete(request)
        print(f"Received response from Anthropic")
        return {
            "analysis": response.content[0]["text"],
            "model": response.model,
            "stop_reason": response.stop_reason
        }

