from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

class GlobalConfig(BaseModel):
    """
    Global configuration for the application.
    """
    anthropic_api_key: str | None
    anthropic_api_url: str | None

    financial_datasets_api_key: str | None
    financial_datasets_api_url: str | None

    openai_api_key: str | None
    openai_api_url: str | None 

    timeout: int | None 
    max_retries: int = 3

# Create a global config instance
CONFIG = GlobalConfig(
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    anthropic_api_url=os.getenv("ANTHROPIC_API_URL"),

    financial_datasets_api_key=os.getenv("FINANCIAL_DATASETS_API_KEY"),
    financial_datasets_api_url=os.getenv("FINANCIAL_DATASETS_API_URL"),

    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_url=os.getenv("OPENAI_API_URL"),

    timeout=30,
    max_retries=3
) 