"""Block commands."""

import json
from typing import Annotated

import typer
from rich.console import Console
from rich.syntax import Syntax

from notion_cli import client

app = typer.Typer()
console = Console()


@app.command("get")
def get_block(
    block_id: str = typer.Argument(..., help="Block ID"),
) -> None:
    """Get a single block's content.

    Example:
        notion block get abc123
    """
    try:
        block = client.get_block(block_id)
        syntax = Syntax(
            json.dumps(block, indent=2, ensure_ascii=False),
            "json",
            theme="monokai",
        )
        console.print(syntax)
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@app.command("delete")
def delete_block(
    block_id: str = typer.Argument(..., help="Block ID"),
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Delete a single block.

    Example:
        notion block delete abc123 --force
    """
    if not force:
        confirm = typer.confirm(f"Delete block {block_id}?")
        if not confirm:
            console.print("Cancelled")
            raise SystemExit(0)

    try:
        client.delete_block(block_id)
        console.print(f"[green]✓[/green] Block deleted")
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@app.command("update")
def update_block(
    block_id: str = typer.Argument(..., help="Block ID"),
    content: Annotated[
        str | None,
        typer.Option("--content", "-c", help="New text content for the block")
    ] = None,
    json_data: Annotated[
        str | None,
        typer.Option("--json", "-j", help="JSON block data to update")
    ] = None,
) -> None:
    """Update a block's content.

    Examples:
        notion block update abc123 --content "New text"
        notion block update abc123 --json '{"paragraph": {"rich_text": [...]}}'
    """
    if not content and not json_data:
        console.print("[red]Error:[/red] Either --content or --json is required")
        raise SystemExit(1)

    try:
        if json_data:
            block_data = json.loads(json_data)
        else:
            # Get current block to determine type
            current = client.get_block(block_id)
            block_type = current.get("type")
            if not block_type:
                console.print("[red]Error:[/red] Could not determine block type")
                raise SystemExit(1)

            # Build update data based on block type
            block_data = {
                block_type: {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }

        result = client.update_block(block_id, block_data)
        console.print(f"[green]✓[/green] Block updated")

        # Show updated content
        syntax = Syntax(
            json.dumps(result, indent=2, ensure_ascii=False),
            "json",
            theme="monokai",
        )
        console.print(syntax)

    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON: {e}")
        raise SystemExit(1)
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
