from pydantic import BaseModel, Field
import os 
import sys
from dotenv import load_dotenv
from agents.financial_metrics_agent.workflow 

load_dotenv()




class GlobalConfig(BaseModel):
    """
    Global configuration for the application.
    """
    api_key: str = Field(..., description="API key for authentication")
    api_url: str = Field(..., description="Base URL for the API")
    timeout: int | None = Field(None, description="Timeout for API requests in seconds") 
    max_retries: int | None = Field(None, description="Maximum number of retries for failed requests")

CONFIG: GlobalConfig = GlobalConfig(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    api_url="https://api.anthropic.com",
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
    # run financial statements agent   
    

    # bring all together

    # return the result