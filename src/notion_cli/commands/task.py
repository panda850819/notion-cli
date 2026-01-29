"""Task commands."""

import typer
from rich.console import Console

from notion_cli import client

app = typer.Typer()
console = Console()


@app.command("create")
def create_task(
    title: str = typer.Argument(..., help="Task title"),
    database_id: str = typer.Option(
        ..., "--db", "-d", help="Database ID to create task in"
    ),
    status: str = typer.Option(None, "--status", "-s", help="Task status"),
) -> None:
    """Create a new task in a database."""
    try:
        # Auto-detect title property name
        title_prop = client.get_title_property_name(database_id)
        properties = {title_prop: {"title": [{"text": {"content": title}}]}}

        if status:
            properties["Status"] = {"status": {"name": status}}

        result = client.create_page(database_id, properties)
        console.print(f"[green]Task created:[/green] {result.get('id')}")
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@app.command("update")
def update_task(
    page_id: str = typer.Argument(..., help="Task/Page ID"),
    status: str = typer.Option(None, "--status", "-s", help="New status"),
    title: str = typer.Option(None, "--title", "-t", help="New title"),
    database_id: str = typer.Option(
        None, "--db", "-d", help="Database ID (needed for title update)"
    ),
) -> None:
    """Update a task."""
    try:
        properties: dict = {}

        if title:
            if database_id:
                title_prop = client.get_title_property_name(database_id)
            else:
                title_prop = "Name"  # fallback
            properties[title_prop] = {"title": [{"text": {"content": title}}]}

        if status:
            properties["Status"] = {"status": {"name": status}}

        if not properties:
            console.print("[yellow]No changes specified.[/yellow]")
            return

        client.update_page(page_id, properties)
        console.print(f"[green]Task updated:[/green] {page_id}")
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
