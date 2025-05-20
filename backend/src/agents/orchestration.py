from pydantic import BaseModel, Field
import os 
import sys
from dotenv import load_dotenv
from financial_metrics_agent.workflow import run_financial_metrics_agent

load_dotenv()


class GlobalConfig(BaseModel):
    """
    Global configuration for the application.
    """
    api_key: str = Field(..., description="API key for authentication")
    api_url: str = Field(..., description="Base URL for the API")

CONFIG: GlobalConfig = GlobalConfig(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    api_url=os.environ.get("ANTHROPIC_API_URL")
)

async def master_orhcestrator(
    stock_ticker: str,
    start_date: str,
    end_date: str,
) -> BaseModel:
    
    config = GlobalConfig(api_key=os.environ.get("ANTHROPIC_API_KEY"), api_url="https://api.anthropic.com")


    # run company news agent
    run_company_news_agent()
    # run financial metrics agent
    run_financial_metrics_agent()
    # run financial statements agent

    

    # bring all together

    # return the result