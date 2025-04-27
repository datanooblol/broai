import re
from pathlib import Path
import tomlkit
from rich import print

def bump_version(part: str):
    """Bump the version (patch, minor, major) in __version__.py and pyproject.toml."""
    # Path to the version file
    version_file = Path(__file__).parent.parent / "__version__.py"
    
    # Read the current version from __version__.py
    content = version_file.read_text()
    match = re.search(r'__version__ = "(\d+)\.(\d+)\.(\d+)"', content)
    
    if not match:
        print("[bold red]❌ Version string not found in __version__.py![/bold red]")
        return

    # Extract the version parts
    major, minor, patch = map(int, match.groups())

    # Bump the version based on the input
    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0

    # Create the new version string
    new_version = f'{major}.{minor}.{patch}'
    
    # Update __version__.py
    new_content = f'__version__ = "{new_version}"\n'
    version_file.write_text(new_content)

    print(f"[bold green]✅ Bumped version to {new_version} in __version__.py[/bold green]")

    # Now update the version in pyproject.toml
    update_pyproject_version(new_version)

def update_pyproject_version(new_version: str):
    """Update the version in pyproject.toml."""
    pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
    
    # Read the TOML file
    with open(pyproject_file, "r") as f:
        pyproject_data = tomlkit.parse(f.read())
    
    # Update the version field in the TOML
    pyproject_data["project"]["version"] = new_version
    
    # Write the changes back to pyproject.toml
    with open(pyproject_file, "w") as f:
        f.write(tomlkit.dumps(pyproject_data))
    
    print(f"[bold green]✅ Bumped version to {new_version} in pyproject.toml[/bold green]")
