from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from app.storage.database import Idea, Evaluation

console = Console()

def display_welcome():
    console.print(Panel.fit("[bold blue]ExecMind[/bold blue]\n[italic]CEO Ideation & Evaluation System[/italic]", border_style="blue"))

def display_menu():
    console.print("\n[bold]Select an option:[/bold]")
    console.print("1. [green]New Idea (Text)[/green]")
    console.print("2. [yellow]New Idea (Voice)[/yellow]")
    console.print("3. [red]Exit[/red]")

def display_idea_framing(idea: Idea):
    console.print("\n[bold cyan]--- Framed Idea ---[/bold cyan]")
    
    grid = Table.grid(expand=True)
    grid.add_column(style="bold yellow")
    grid.add_column()
    
    grid.add_row("Problem:", idea.problem_statement)
    grid.add_row("Solution:", idea.proposed_solution)
    grid.add_row("Users:", idea.target_users)
    grid.add_row("Assumptions:", idea.assumptions)
    
    console.print(Panel(grid, title=f"Idea #{idea.id}", border_style="cyan"))

def display_evaluation(evaluation: Evaluation):
    console.print("\n[bold magenta]--- Evaluation Results ---[/bold magenta]")
    
    # Scores Table
    table = Table(title="Scorecard")
    table.add_column("Metric", style="cyan")
    table.add_column("Score (1-10)", justify="right", style="green")
    
    table.add_row("Feasibility", str(evaluation.feasibility))
    table.add_row("Market Value", str(evaluation.market_value))
    table.add_row("Complexity", str(evaluation.complexity))
    table.add_row("Risk", str(evaluation.risk))
    table.add_row("Innovation", str(evaluation.innovation))
    
    console.print(table)
    
    # Verdict Panel
    verdict_color = "green" if evaluation.verdict == "pursue" else "yellow" if evaluation.verdict == "refine" else "red"
    
    summary_md = f"**Verdict:** [{verdict_color}]{evaluation.verdict.upper()}[/{verdict_color}]\n\n**Final Score:** {evaluation.final_score}/10\n\n**Summary:** {evaluation.summary}"
    
    console.print(Panel(Markdown(summary_md), title="Conclusion", border_style=verdict_color))
