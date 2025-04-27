import click
from pathlib import Path
import shutil
from broai.utils import success, error
import pyfiglet
from rich import print
from broai.__version__ import __version__
from broai.cli.version_bump import bump_version

def show_banner():
    ascii_banner = pyfiglet.figlet_format("BroAI")
    print(f"[bold cyan]{ascii_banner}[/bold cyan]")
    print("[cyan]🚀 Welcome to BroAI CLI[/cyan]")
    print("[cyan]Usage:[/cyan] broai [command]")
    print("[cyan]Example:[/cyan] broai init")

@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def main(ctx):
    """BroAI CLI Tool."""
    if ctx.invoked_subcommand is None:
        show_banner()

def jupyter_init():
    """Real logic to initialize the project (can be called from Python or CLI)."""
    agents_dir = Path.cwd() / "agents"

    if agents_dir.exists():
        error("Folder 'agents/' already exists.")
        return

    agents_dir.mkdir(parents=True)
    success("Created folder 'agents/'")

    (agents_dir / "__init__.py").write_text("# Agents package\n")
    success("Created file 'agents/__init__.py'")

    template_src = Path(__file__).parent / "agent_template.py"
    template_dst = agents_dir / "agent_template.py"

    if template_src.exists():
        shutil.copy(template_src, template_dst)
        success("Copied 'agent_template.py' to 'agents/agent_template.py'")
    else:
        error("WARNING: Template file not found. Skipped copying.")

@main.command()
def init():
    """Initialize a new BroAI project."""
    jupyter_init()

@main.command()
@click.argument("path", type=click.Path(file_okay=False, dir_okay=True))  # Remove exists=True
@click.argument("agent_name", type=str)
def add_agent(path, agent_name):
    """Create a new agent Python file at the specified location."""
    # Define the source template file
    template_src = Path(__file__).parent / "agent_template.py"
    
    # Define the destination file path
    agent_file = Path(path) / f"{agent_name}.py"

    # Create the directory if it doesn't exist
    agent_file.parent.mkdir(parents=True, exist_ok=True)  # Will create the full path if necessary

    # Check if the agent file already exists
    if agent_file.exists():
        print(f"[bold red]❌ File '{agent_file}' already exists![/bold red]")
        return

    # Check if the template exists
    if not template_src.exists():
        print(f"[bold red]❌ Template file '{template_src}' not found![/bold red]")
        return
    
    # Copy the template to the new agent file
    shutil.copy(template_src, agent_file)

    print(f"[bold green]✅ Created agent file at '{agent_file}' from template.[/bold green]")


@main.command(hidden=True)
@click.argument("part", type=click.Choice(["patch", "minor", "major"]))
@click.option("--auto", is_flag=True, help="Automatically bump based on the latest PyPI version")
def bump(part, auto):
    """Bump the version (patch, minor, major) and sync with PyPI."""
    if auto:
        package_name = "broai"  # Update this if needed
        bump_version(part, package_name)
    else:
        bump_version(part, "broai")
