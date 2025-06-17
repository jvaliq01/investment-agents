# Investment Agents

Welcome, Investment Agents!  
We're exploring how well LLMs can make trading decisions using fundamental financial analysis and daily news.

---

## Getting Started

In your terminal:

```bash
# 1. Establish the path of your environment for relative imports 
export PYTHONPATH=$PWD

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Install the requirements
pip install -r requirements.txt --no-cache

# 5. Run the backend
python backend/src/agents/orchestration.py
```

## .env Notes
- Set up you .env file under the backend folder, just like the .env.example file 
- You must obtain both and Anthropic and OpenAI API key to run 
- The financial datasets api key is provided. However, we can only collect data on AAPL currently

## Front-End Agent Panel Description 
- Top Left - Financial Metrics Analysis 
- Top Right - Financial Statements Analysis
- Bottom Left - Web Search Analysis 
- Bottom Right - Investment Recommendation 


A lot to come in the future. Excited to see where this goes!!

