from datetime import datetime
from zoneinfo import ZoneInfo  # Available in Python 3.9+

def get_timestamp():
    dt = datetime.now(ZoneInfo("Asia/Bangkok"))
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

from rich import print

def success(msg: str):
    print(f"[bold green][✔] {msg}[/bold green]")

def error(msg: str):
    print(f"[bold red][✖] {msg}[/bold red]")
