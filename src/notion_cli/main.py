"""Notion CLI main entry point."""

import typer

from notion_cli.commands import search, db, page, task, block

app = typer.Typer(
    name="notion",
    help="CLI tool for Notion workspace management",
    no_args_is_help=True,
)

app.add_typer(db.app, name="db", help="Database operations")
app.add_typer(page.app, name="page", help="Page operations")
app.add_typer(task.app, name="task", help="Task operations")
app.add_typer(block.app, name="block", help="Block operations")


@app.command("search")
def search_cmd(
    query: str = typer.Argument(..., help="Search query"),
    type: str = typer.Option(
        None, "--type", "-t", help="Filter by type: page or database"
    ),
) -> None:
    """Search Notion workspace."""
    search.run(query, type)


if __name__ == "__main__":
    app()
