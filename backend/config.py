import os

BASE_URL = "https://api.financialdatasets.ai"

def get_financial_data_ai_api_key() -> str | None:
    return os.environ.get("FINANCIAL_DATASETS_API_KEY")


