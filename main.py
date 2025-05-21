from backend.src.agents.orchestration import master_orchestrator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Connect to your local Ollama instance
async def main():
    result = await master_orchestrator("AAPL", "20240101", "20250101")
    
    console = Console()
    
    # Print the AI analysis in a panel
    analysis_text = result["analysis"]["analysis"] if isinstance(result["analysis"], dict) else result["analysis"]
    console.print(Panel(analysis_text, title="AI Analysis", border_style="blue"))
    
    # Print metrics in a table
    metrics_table = Table(title="Financial Metrics")
    metrics_table.add_column("Category", style="cyan")
    metrics_table.add_column("Metric", style="green")
    metrics_table.add_column("Value", style="yellow")
    
    for category, metrics in result["metrics"].items():
        for metric, value in metrics.items():
            metrics_table.add_row(
                category.capitalize(),
                metric.replace("_", " ").title(),
                f"{value:.2f}" if isinstance(value, float) else str(value)
            )
    
    console.print(metrics_table)
    
    # Print raw data summary
    raw_data = result["raw_data"]
    console.print("\n[bold]Raw Data Summary:[/bold]")
    console.print(f"Number of Income Statements: {len(raw_data['financials']['income_statements'])}")
    console.print(f"Number of Balance Sheets: {len(raw_data['financials']['balance_sheets'])}")
    console.print(f"Number of Cash Flow Statements: {len(raw_data['financials']['cash_flow_statements'])}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())