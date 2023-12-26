import asyncio
import os.path
from rich.console import Console
import sys


async def clear_db(db_path: str, db_table_name: str, splits: int = 4):
    console = Console()
    if not os.path.exists(db_path):
        console.print("[[bold red]X[/bold red]] Die Datenbank existiert nicht")
        return None
