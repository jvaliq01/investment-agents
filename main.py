from backend.src.agents.orchestration import master_orchestrator

# Connect to your local Ollama instance
async def main():
    await master_orchestrator("AAPL", "20240101", "20250101")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())