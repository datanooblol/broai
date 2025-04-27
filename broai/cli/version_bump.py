import requests
import re
from pathlib import Path
from rich import print
import tomlkit

def get_latest_pypi_version(package_name: str) -> str:
    """Fetch the latest version of the package from PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"[bold red]❌ Failed to fetch the latest version from PyPI![/bold red]")
        return None
    
    data = response.json()
    return data["info"]["version"]

def bump_version(part: str, package_name: str):
    """Bump the version (patch, minor, major) in __version__.py and pyproject.toml."""
    latest_version = get_latest_pypi_version(package_name)
    
    if not latest_version:
        return

    # Extract the version parts from the latest PyPI version
    major, minor, patch = map(int, latest_version.split('.'))

    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0

    new_version = f'{major}.{minor}.{patch}'
    print(f"[bold blue]Latest version on PyPI: {latest_version}[/bold blue]")
    print(f"[bold green]Bumping to new version: {new_version}[/bold green]")

    # Now bump the version in __version__.py and pyproject.toml
    update_version_files(new_version)

def update_version_files(new_version: str):
    """Update both __version__.py and pyproject.toml with the new version."""
    version_file = Path(__file__).parent.parent / "__version__.py"
    version_file.write_text(f'__version__ = "{new_version}"\n')

    print(f"[bold green]✅ Bumped version in __version__.py to {new_version}[/bold green]")

    # Update pyproject.toml
    toml_file = Path(__file__).parent.parent.parent / "pyproject.toml"
    with open(toml_file, "r") as f:
        toml_data = tomlkit.load(f)
    
    toml_data["project"]["version"] = new_version

    with open(toml_file, "w") as f:
        tomlkit.dump(toml_data, f)

    print(f"[bold green]✅ Bumped version in pyproject.toml to {new_version}[/bold green]")