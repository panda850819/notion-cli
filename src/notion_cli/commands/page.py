"""Page commands."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from notion_cli import client
from notion_cli.converters import markdown_to_blocks
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


@app.command("update")
def update_page_content(
    page_id: str = typer.Argument(..., help="Page ID"),
    file: Annotated[
        Path | None,
        typer.Option("--file", "-f", help="Markdown file to use as content")
    ] = None,
    clear: Annotated[
        bool,
        typer.Option("--clear", help="Clear existing content before adding new")
    ] = True,
) -> None:
    """Update a page's content from a markdown file.

    Example:
        notion page update abc123 --file content.md
    """
    if not file:
        console.print("[red]Error:[/red] --file is required")
        raise SystemExit(1)

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise SystemExit(1)

    try:
        markdown = file.read_text()
        blocks = markdown_to_blocks(markdown)
        console.print(f"Parsed {len(blocks)} blocks from markdown")

        if clear:
            result = client.replace_page_content(page_id, blocks)
            console.print(
                f"[green]✓[/green] Replaced content: "
                f"deleted {result['deleted']}, added {result['added']} blocks"
            )
        else:
            added = client.append_page_content(page_id, blocks)
            console.print(f"[green]✓[/green] Appended {added} blocks")

        page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
        console.print(f"View at: {page_url}")

    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@app.command("clear")
def clear_page(
    page_id: str = typer.Argument(..., help="Page ID"),
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Clear all content from a page.

    Example:
        notion page clear abc123 --force
    """
    if not force:
        confirm = typer.confirm(f"Clear all content from page {page_id}?")
        if not confirm:
            console.print("Cancelled")
            raise SystemExit(0)

    try:
        deleted = client.clear_page_content(page_id)
        console.print(f"[green]✓[/green] Deleted {deleted} blocks")
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@app.command("append")
def append_to_page(
    page_id: str = typer.Argument(..., help="Page ID"),
    file: Annotated[
        Path | None,
        typer.Option("--file", "-f", help="Markdown file to append")
    ] = None,
) -> None:
    """Append content to a page from a markdown file.

    Example:
        notion page append abc123 --file content.md
    """
    if not file:
        console.print("[red]Error:[/red] --file is required")
        raise SystemExit(1)

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise SystemExit(1)

    try:
        markdown = file.read_text()
        blocks = markdown_to_blocks(markdown)
        added = client.append_page_content(page_id, blocks)
        console.print(f"[green]✓[/green] Appended {added} blocks")

        page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
        console.print(f"View at: {page_url}")
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
