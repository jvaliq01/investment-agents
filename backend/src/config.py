from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

class GlobalConfig(BaseModel):
    """
    Global configuration for the application.
    """
    anthropic_api_key: str = Field(..., description="Anthropic API key for authentication")
    anthropic_api_url: str = Field(..., description="Base URL for the API")
    financial_datasets_api_key: str = Field(..., description="Financial Datasets Api Key")
    financial_datasets_api_url: str = Field(..., description="Financial Datasets Api URL")
    timeout: int | None = Field(None, description="Timeout for API requests in seconds") 
    max_retries: int | None = Field(None, description="Maximum number of retries for failed requests")

# Create a global config instance
CONFIG = GlobalConfig(
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    anthropic_api_url=os.getenv("ANTHROPIC_API_URL"),
    financial_datasets_api_key=os.getenv("FINANCIAL_DATASETS_API_KEY"),
    financial_datasets_api_url=os.getenv("FINANCIAL_DATASETS_API_URL"),
    timeout=int(os.getenv("API_TIMEOUT", "30")),
    max_retries=int(os.getenv("API_MAX_RETRIES", "3"))
) 