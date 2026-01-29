"""Database commands."""

import typer
from rich.console import Console

from notion_cli import client
from notion_cli.formatters import format_databases, format_database_rows

app = typer.Typer()
console = Console()


@app.command("list")
def list_databases() -> None:
    """List all databases in the workspace."""
    try:
        databases = client.list_databases()
        format_databases(databases)
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@app.command("query")
def query_database(
    database_id: str = typer.Argument(..., help="Database ID"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max rows to return"),
) -> None:
    """Query a database."""
    try:
        db_schema = client.get_database(database_id)
        rows = client.query_database(database_id)
        format_database_rows(rows[:limit], db_schema)
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
