import openai
# Connect to your local Ollama instance
client = openai.Client(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
response = client.chat.completions.create(
    model="deepseek-r1:7b", # change the "XX" by the distilled model you choose
    messages=[{"role": "user", "content": "Explain blockchain security"}],
    temperature=0.7  # Controls creativity vs precision
)

print(response)