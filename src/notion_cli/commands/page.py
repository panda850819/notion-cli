"""Page commands."""

import typer
from rich.console import Console

from notion_cli import client
from notion_cli.formatters import format_page

app = typer.Typer()
console = Console()


@app.command("get")
def get_page(
    page_id: str = typer.Argument(..., help="Page ID"),
) -> None:
    """Get a page and its content."""
    try:
        page = client.get_page(page_id)
        content = client.get_page_content(page_id)
        format_page(page, content)
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
