"""
SecReviewAgent CLI.

Command-line interface for analyzing IaC directories and PRs.
"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from secreviewagent.agents.review_agent import SecReviewAgent

app = typer.Typer(
    name="secreview",
    help="Educational IaC Security Review Agent",
    add_completion=False,
)
console = Console()


@app.command()
def analyze(
    directory: Path = typer.Argument(..., help="Directory containing IaC files"),
    iac_type: str = typer.Option(
        "terraform",
        "--type", "-t",
        help="Type of IaC (terraform or kubernetes)",
    ),
    output: str = typer.Option(
        "markdown",
        "--output", "-o",
        help="Output format (markdown or json)",
    ),
    model: str = typer.Option(
        "claude-sonnet-4-20250514",
        "--model", "-m",
        help="LLM model to use",
    ),
):
    """Analyze an IaC directory for security issues."""
    
    if not directory.exists():
        console.print(f"[red]Error: Directory not found: {directory}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel(f"Analyzing {iac_type} in {directory}", title="SecReviewAgent"))
    
    agent = SecReviewAgent(model=model)
    
    with console.status("Parsing and analyzing..."):
        if iac_type == "terraform":
            result = agent.review_terraform_directory(str(directory))
        elif iac_type == "kubernetes":
            result = agent.review_kubernetes_directory(str(directory))
        else:
            console.print(f"[red]Unknown IaC type: {iac_type}[/red]")
            raise typer.Exit(1)
    
    if output == "markdown":
        md = agent.format_review_markdown(result)
        console.print(Markdown(md))
    else:
        console.print_json(json.dumps({
            "architecture_summary": result.architecture_summary,
            "service_interactions": result.service_interactions,
            "security_findings": [
                {
                    "severity": f.severity,
                    "title": f.title,
                    "description": f.description,
                    "affected_resources": f.affected_resources,
                    "recommendation": f.recommendation,
                }
                for f in result.security_findings
            ],
            "concepts_explained": result.concepts_explained,
        }, indent=2))


@app.command()
def pr(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo)"),
    pr_number: int = typer.Option(..., "--pr", "-p", help="PR number"),
    token: str = typer.Option(None, "--token", envvar="GITHUB_TOKEN", help="GitHub token"),
):
    """Analyze a GitHub PR."""
    console.print("[yellow]PR analysis not yet implemented[/yellow]")
    console.print(f"Would analyze PR #{pr_number} in {repo}")


@app.command()
def serve(
    port: int = typer.Option(8080, "--port", "-p", help="Port to listen on"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
):
    """Start the webhook server."""
    console.print(f"[green]Starting webhook server on {host}:{port}[/green]")
    
    import uvicorn
    from secreviewagent.webhook.server import app as webhook_app
    
    uvicorn.run(webhook_app, host=host, port=port)


@app.command()
def version():
    """Show version information."""
    from secreviewagent import __version__
    console.print(f"SecReviewAgent v{__version__}")


if __name__ == "__main__":
    app()
