"""Search command."""

from rich.console import Console

from notion_cli import client
from notion_cli.formatters import format_search_results

console = Console()


def run(query: str, filter_type: str | None = None) -> None:
    """Run search command."""
    try:
        results = client.search(query, filter_type)
        format_search_results(results)
    except client.NotionClientError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
