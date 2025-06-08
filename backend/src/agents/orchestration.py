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
from backend.src.client.anthropic_client import ChatCompletionRequest, ChatMessage, ChatCompletionResponse, AnthropicClient
from backend.src.agents.financial_statements_agent.model import CompanyFinancialStatementsRequest

# Web server imports
import webbrowser
from threading import Thread
from flask import Flask, render_template_string
import markdown
import socket

from backend.src.agents.financial_statements_agent.model import FinancialStatementsRequest, FinancialStatementsResponse
from backend.src.agents.financial_statements_agent.workflow_new import FinancialStatementsAgent

load_dotenv()

# HTML template for the dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Analysis Dashboard - {{ ticker }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(45deg, #2c3e50, #34495e);
            color: white;
            padding: 2.5rem 2rem;
            text-align: center;
        }

        .header h1 {
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }

        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            min-height: 70vh;
        }

        .analysis-section {
            padding: 2.5rem;
            border-right: 1px solid #e8ecef;
            overflow-y: auto;
            max-height: 80vh;
        }

        .analysis-section:last-child {
            border-right: none;
        }

        .section-title {
            color: #2c3e50;
            font-size: 1.6rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.8rem;
            border-bottom: 3px solid #3498db;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .markdown-content {
            font-size: 0.95rem;
            line-height: 1.7;
        }

        .markdown-content h1 {
            color: #2c3e50;
            font-size: 1.8rem;
            margin: 2rem 0 1rem;
            font-weight: 600;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 0.5rem;
        }

        .markdown-content h2 {
            color: #34495e;
            font-size: 1.4rem;
            margin: 1.5rem 0 0.8rem;
            font-weight: 600;
        }

        .markdown-content h3 {
            color: #7f8c8d;
            font-size: 1.2rem;
            margin: 1.2rem 0 0.6rem;
            font-weight: 600;
        }

        .markdown-content p {
            margin-bottom: 1.2rem;
            color: #555;
            text-align: justify;
        }

        .markdown-content ul, .markdown-content ol {
            margin-left: 1.8rem;
            margin-bottom: 1.2rem;
        }

        .markdown-content li {
            margin-bottom: 0.6rem;
            color: #555;
        }

        .markdown-content strong {
            color: #2c3e50;
            font-weight: 600;
        }

        .markdown-content code {
            background: #f8f9fa;
            padding: 0.3rem 0.5rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 0.85rem;
            color: #e74c3c;
        }

        .markdown-content pre {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            border-left: 4px solid #3498db;
        }

        .markdown-content blockquote {
            border-left: 4px solid #3498db;
            padding-left: 1.5rem;
            margin: 1.5rem 0;
            color: #7f8c8d;
            font-style: italic;
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-radius: 0 8px 8px 0;
        }

        .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }

        .markdown-content th, .markdown-content td {
            border: 1px solid #e8ecef;
            padding: 0.8rem;
            text-align: left;
        }

        .markdown-content th {
            background: #34495e;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }

        .markdown-content td {
            background: white;
        }

        .markdown-content tr:nth-child(even) td {
            background: #f8f9fa;
        }

        @media (max-width: 1024px) {
            .content {
                grid-template-columns: 1fr;
            }
            
            .analysis-section {
                border-right: none;
                border-bottom: 1px solid #e8ecef;
                max-height: none;
            }
            
            .analysis-section:last-child {
                border-bottom: none;
            }
            
            .header h1 {
                font-size: 2.2rem;
            }
            
            .container {
                margin: 10px;
                border-radius: 10px;
            }
        }

        .loading {
            text-align: center;
            padding: 3rem;
            color: #7f8c8d;
            font-size: 1.1rem;
        }

        .error {
            background: #e74c3c;
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            font-weight: 500;
        }

        /* Scrollbar styling */
        .analysis-section::-webkit-scrollbar {
            width: 6px;
        }

        .analysis-section::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        .analysis-section::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }

        .analysis-section::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Financial Analysis Dashboard</h1>
            <div class="subtitle">{{ ticker }} | {{ start_date }} to {{ end_date }}</div>
        </div>
        
        <div class="content">
            <div class="analysis-section">
                <div class="section-title">📊 Financial Statements Analysis</div>
                <div class="markdown-content">
                    {{ fin_statements_html | safe }}
                </div>
            </div>
            
            <div class="analysis-section">
                <div class="section-title">📈 Financial Metrics Analysis</div>
                <div class="markdown-content">
                    {{ fin_metrics_html | safe }}
                </div>
            </div>

            <div class="analysis-section">
                <div class="section-title">🎯 Investment Recommendation</div>
                <div class="markdown-content">
                    {{ investment_recommendation_html | safe }}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def find_free_port():
    """Find a free port to run the Flask server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def extract_markdown_content(analysis_text):
    """Extract markdown content from the analysis text."""
    if isinstance(analysis_text, str):
        return analysis_text
    
    # Handle different response object structures
    if hasattr(analysis_text, 'content') and analysis_text.content:
        if isinstance(analysis_text.content, list) and len(analysis_text.content) > 0:
            # Handle list of content items
            content_item = analysis_text.content[0]
            if isinstance(content_item, dict):
                return content_item.get('text', str(analysis_text))
            else:
                return str(content_item)
        elif isinstance(analysis_text.content, str):
            return analysis_text.content
    
    # Handle message-like objects
    if hasattr(analysis_text, 'text'):
        return analysis_text.text
    
    # Fallback to string conversion
    return str(analysis_text)

def create_flask_app(ticker, start_date, end_date, fin_statements_analysis, fin_metrics_analysis, investment_recommendation):
    """Create and configure Flask app with the analysis data."""
    app = Flask(__name__)
    
    @app.route('/')
    def dashboard():
        try:
            # Extract markdown content from analysis responses
            statements_markdown = extract_markdown_content(fin_statements_analysis)
            metrics_markdown = extract_markdown_content(fin_metrics_analysis)
            recommendation_markdown = extract_markdown_content(investment_recommendation)
            
            # Convert markdown to HTML
            fin_statements_html = markdown.markdown(
                statements_markdown, 
                extensions=['tables', 'fenced_code', 'codehilite']
            )
            fin_metrics_html = markdown.markdown(
                metrics_markdown, 
                extensions=['tables', 'fenced_code', 'codehilite']
            )
            investment_recommendation_html = markdown.markdown(
                recommendation_markdown,
                extensions=['tables', 'fenced_code', 'codehilite']
            )
            
            return render_template_string(
                HTML_TEMPLATE,
                ticker=ticker.upper(),
                start_date=start_date,
                end_date=end_date,
                fin_statements_html=fin_statements_html,
                fin_metrics_html=fin_metrics_html,
                investment_recommendation_html=investment_recommendation_html
            )
        except Exception as e:
            error_html = f'<div class="error">Error rendering dashboard: {str(e)}</div>'
            return render_template_string(
                HTML_TEMPLATE.replace('{{ fin_statements_html | safe }}', error_html)
                            .replace('{{ fin_metrics_html | safe }}', error_html)
                            .replace('{{ investment_recommendation_html | safe }}', error_html),
                ticker=ticker.upper(),
                start_date=start_date,
                end_date=end_date
            )
    
    return app

def run_server(app, port):
    """Run the Flask server in a separate thread."""
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

## TODO ## 
# 1. Make data model that holds the state of the orchestration
# 2. Make the orchestration agent
# 3. Add error handling across all agents
# 4. Add logging across all agents

async def master_orchestrator(
    ticker: str, 
    start_date: str,
    end_date: str,
    serve_web: bool = True) -> str:
    """Orchestrates the execution of financial analysis agents."""

    print(f"🚀 Starting financial analysis for {ticker.upper()}")
    print(f"📅 Period: {start_date} to {end_date}")
    
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
    
    fin_statements_agent = FinancialStatementsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        fin_statements_request=fin_statements_request,
    )

    company_news_agent = CompanyNewsAgent(
        financial_client=financial_client,
        anthropic_client=anthropic_client,
        company_news_request=company_news_request,
    )


    print(f"📊 FINANCIAL STATEMENTS REQUEST: {fin_statements_request}")

    # Run analyses
    fin_statements_analysis, fin_metrics_analysis  = await asyncio.gather(
        fin_statements_agent.analyze_statements_with_llm(),
        fin_metrics_agent.analyze_metrics_with_llm(),
    )
    # fin_news_analysis = await company_news_agent.analyze_metrics_with_llm()
    
    print(f"✅ FINANCIAL STATEMENTS ANALYSIS: {fin_statements_analysis}")
    print(f"✅ FINANCIAL METRICS ANALYSIS: {fin_metrics_analysis}")
    # print(f"✅ COMPANY NEWS ANALYSIS: {fin_news_analysis}")
    
    # Create a final investment recommendation that combines all analyses
    investment_recommendation_prompt = f"""You are an expert financial analyst with a Chartered Financial Analyst (CFA) designation.
    Based on the following comprehensive analyses, provide a clear investment recommendation (BUY, SELL, or HOLD) for {ticker.upper()}.
    
    FINANCIAL STATEMENTS ANALYSIS:
    {fin_statements_analysis}
    
    FINANCIAL METRICS ANALYSIS:
    {fin_metrics_analysis}
    
    
    Please provide:
    1. A clear BUY, SELL, or HOLD recommendation at the top
    2. Target price range if applicable
    3. Key reasons for the recommendation
    4. Main risks to consider
    5. Confidence level in the recommendation (High, Medium, Low)
    
    Format your response in markdown with clear sections."""


    investment_recommendation_request = ChatCompletionRequest(
        model="claude-sonnet-4-20250514",
        messages=[ChatMessage(role="user", content=investment_recommendation_prompt)],
        temperature=0.7,
        max_tokens=32000
    )

    investment_recommendation = await anthropic_client.chat_complete(investment_recommendation_request)
    print(f"✅ INVESTMENT RECOMMENDATION: {investment_recommendation}")


    if serve_web:
        # Create Flask app with the analysis results
        app = create_flask_app(ticker, start_date, end_date, fin_statements_analysis, fin_metrics_analysis, investment_recommendation)
        
        # Find a free port and start the server
        port = find_free_port()
        url = f"http://127.0.0.1:{port}"
        
        print(f"\n🌐 Starting web server...")
        print(f"📊 Financial Analysis Dashboard available at: {url}")
        print(f"🔍 Analysis for {ticker.upper()} from {start_date} to {end_date}")
        print(f"💡 Press Ctrl+C to stop the server\n")
        
        # Start the server in a separate thread
        server_thread = Thread(target=run_server, args=(app, port), daemon=True)
        server_thread.start()
        
        # Open browser automatically
        try:
            webbrowser.open(url)
            print(f"🌍 Opened dashboard in your default browser")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"🔗 Please manually open: {url}")
        
        # Keep the main thread alive
        try:
            print("🎯 Dashboard is running. Press Ctrl+C to stop...")
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down server...")
            return f"Analysis complete. Dashboard was available at {url}"
    else:
        return "Analysis complete - web serving disabled"

if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    start_date = "2020-01-01"
    end_date = "2023-01-01"
    
    # Run with web dashboard (default)
    result = asyncio.run(master_orchestrator(ticker, start_date, end_date, serve_web=True))
    print(result)