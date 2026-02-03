import sys
import os
from rich.prompt import Prompt, Confirm

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.database import init_db
from app.interfaces.cli import display_welcome, display_menu, display_idea_framing, display_evaluation, console
from app.workflows.ideation import frame_idea, conduct_research, save_structured_idea
from app.workflows.evaluation import evaluate_idea
from app.interfaces.voice import transcribe_audio

def main():
    init_db()
    display_welcome()
    
    while True:
        display_menu()
        choice = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")
        
        if choice == "3":
            console.print("[bold]Goodbye![/bold]")
            break
            
        raw_input = ""
        source = "text"
        
        if choice == "1":
            raw_input = Prompt.ask("\n[bold]Enter your idea[/bold]")
                
        elif choice == "2":
            # Voice Sub-Menu
            console.print("\n[bold]Voice Input Options:[/bold]")
            console.print("1. [green]Provide Audio File[/green]")
            console.print("2. [dim]Record Current Voice (Not available in WSL/Headless)[/dim]") 
            # Note: keeping disabled/dim for now to ensure stability
            
            v_choice = Prompt.ask("Choose", choices=["1", "2"], default="1")
            
            if v_choice == "2":
                console.print("[yellow]Live recording requires local audio setup. Please provide a file instead.[/yellow]")
                
            file_path = Prompt.ask("\n[bold]Path to audio file (wav/mp3)[/bold]")
            file_path = file_path.strip('"').strip("'")
            
            if not os.path.exists(file_path):
                console.print(f"[red]File not found: {file_path}[/red]")
                continue
                
            try:
                console.print("[dim]Transcribing...[/dim]")
                raw_input = transcribe_audio(file_path)
                console.print(f"[dim]Transcribed: {raw_input}[/dim]")
                source = "voice"
            except Exception as e:
                console.print(f"[red]Transcription failed: {e}[/red]")
                continue

        if not raw_input.strip():
            console.print("[red]Empty input![/red]")
            continue

        # --- Deep Researcher Flow ---
        try:
            # Step 1: Framing & Confirmation Loop
            current_context = raw_input
            framed_data = None
            
            while True:
                with console.status("[bold cyan]Deep Researcher: Framing your idea...[/bold cyan]"):
                    framed_data = frame_idea(current_context)
                
                console.print("\n[bold cyan]--- Interpretation ---[/bold cyan]")
                console.print(f"[italic]{framed_data.get('restatement')}[/italic]")
                console.print(f"\n[bold yellow]Agent asks:[/bold yellow] {framed_data.get('confirmation_question')}")
                
                # Custom loop for Yes/No/Exit
                console.print("\n[bold]Is this what you meant?[/bold]")
                console.print("1. [green]Yes, proceed[/green]")
                console.print("2. [yellow]No, let me refine it[/yellow]")
                console.print("3. [red]Trash idea and exit[/red]")
                
                conf_choice = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")
                
                if conf_choice == "1":
                    break # Proceed to research
                elif conf_choice == "3":
                    console.print("[dim]Idea trashed.[/dim]")
                    framed_data = None # Signal to skip rest
                    break 
                elif conf_choice == "2":
                    refinement = Prompt.ask("\n[bold]What details would you like to add or clarify?[/bold]")
                    if refinement.lower() == 'exit':
                        console.print("[dim]Idea trashed.[/dim]")
                        framed_data = None
                        break
                    # Append refinement to context to keep history
                    current_context += f"\nUser Clarification: {refinement}"
                    continue # Loop back to framing

            if not framed_data:
                continue # Go back to main menu if trashed

            # Step 2: Research
            console.print("\n[bold blue]Checking History & Web...[/bold blue]")
            with console.status("[bold blue]Deep Researcher: Scanning for duplicates...[/bold blue]"):
                research_report = conduct_research(framed_data.get('restatement', current_context))
            
            console.print(Panel(Markdown(research_report), title="Research Verification", border_style="blue"))
            
            # Step 3: Decision
            console.print("\n[bold]How do you want to proceed?[/bold]")
            console.print("1. [green]Pursue & structure this idea[/green]")
            console.print("2. [yellow]Edit/Refine based on research[/yellow]")
            console.print("3. [red]Drop idea[/red]")
            
            decision = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")
            
            if decision == "3":
                console.print("[dim]Idea dropped.[/dim]")
                continue
            elif decision == "2":
                console.print("[yellow]Please re-enter your refined idea:[/yellow]")
                # In a fancier version we'd maintain context, but keeping it simple for CLI loop
                continue

            # Step 4: Structuring & Saving
            with console.status("[bold green]Structuring & Saving...[/bold green]"):
                idea_obj = save_structured_idea(raw_input, source)
            
            display_idea_framing(idea_obj)
            
            # Workflow B: Evaluation
            if Confirm.ask("\nEvaluate this idea?"):
                with console.status("[bold magenta]Evaluating feasibility & market fit...[/bold magenta]"):
                    eval_obj = evaluate_idea(idea_obj)
                
                display_evaluation(eval_obj)
                
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            # In debug mode check traceback
            # import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
