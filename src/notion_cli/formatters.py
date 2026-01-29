"""Rich formatters for Notion data."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


def get_title(item: dict) -> str:
    """Extract title from a Notion object."""
    obj_type = item.get("object")

    if obj_type in ("database", "data_source"):
        title_list = item.get("title", [])
        if title_list:
            return title_list[0].get("plain_text", "Untitled")
        # Try name field for data_source
        if item.get("name"):
            return item.get("name")
        return "Untitled Database"

    if obj_type == "page":
        props = item.get("properties", {})
        for prop in props.values():
            if prop.get("type") == "title":
                title_list = prop.get("title", [])
                if title_list:
                    return title_list[0].get("plain_text", "Untitled")
        return "Untitled Page"

    return "Unknown"


def format_search_results(results: list[dict]) -> None:
    """Format and print search results."""
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(title="Search Results", show_header=True, header_style="bold cyan")
    table.add_column("Type", style="dim", width=10)
    table.add_column("Title", style="bold")
    table.add_column("ID", style="dim", width=36)

    for item in results:
        obj_type = item.get("object", "unknown")
        title = get_title(item)
        item_id = item.get("id", "")

        type_style = "blue" if obj_type == "database" else "green"
        table.add_row(f"[{type_style}]{obj_type}[/{type_style}]", title, item_id)

    console.print(table)


def format_databases(databases: list[dict]) -> None:
    """Format and print database list."""
    if not databases:
        console.print("[yellow]No databases found.[/yellow]")
        return

    table = Table(title="Databases", show_header=True, header_style="bold cyan")
    table.add_column("Title", style="bold")
    table.add_column("ID", style="dim", width=36)
    table.add_column("Last Edited", style="dim")

    for db in databases:
        title = get_title(db)
        db_id = db.get("id", "")
        last_edited = db.get("last_edited_time", "")[:10]
        table.add_row(title, db_id, last_edited)

    console.print(table)


def format_database_rows(rows: list[dict], db_schema: dict) -> None:
    """Format and print database query results."""
    if not rows:
        console.print("[yellow]No rows found.[/yellow]")
        return

    properties = db_schema.get("properties", {})
    prop_names = list(properties.keys())[:5]

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=12)

    for name in prop_names:
        table.add_column(name)

    for row in rows:
        row_props = row.get("properties", {})
        values = [row.get("id", "")[:8] + "..."]

        for name in prop_names:
            prop = row_props.get(name, {})
            values.append(extract_property_value(prop))

        table.add_row(*values)

    console.print(table)


def extract_property_value(prop: dict) -> str:
    """Extract display value from a property."""
    prop_type = prop.get("type", "")

    if prop_type == "title":
        title_list = prop.get("title", [])
        return title_list[0].get("plain_text", "") if title_list else ""

    if prop_type == "rich_text":
        text_list = prop.get("rich_text", [])
        return text_list[0].get("plain_text", "") if text_list else ""

    if prop_type == "number":
        return str(prop.get("number", ""))

    if prop_type == "select":
        select = prop.get("select")
        return select.get("name", "") if select else ""

    if prop_type == "multi_select":
        options = prop.get("multi_select", [])
        return ", ".join(opt.get("name", "") for opt in options)

    if prop_type == "date":
        date = prop.get("date")
        return date.get("start", "") if date else ""

    if prop_type == "checkbox":
        return "Yes" if prop.get("checkbox") else "No"

    if prop_type == "status":
        status = prop.get("status")
        return status.get("name", "") if status else ""

    if prop_type == "url":
        return prop.get("url", "") or ""

    if prop_type == "email":
        return prop.get("email", "") or ""

    if prop_type == "phone_number":
        return prop.get("phone_number", "") or ""

    return f"[{prop_type}]"


def format_page(page: dict, content: list[dict]) -> None:
    """Format and print a page."""
    title = get_title(page)
    page_id = page.get("id", "")
    created = page.get("created_time", "")[:10]
    edited = page.get("last_edited_time", "")[:10]

    header = Text()
    header.append(f"{title}\n", style="bold white")
    header.append(f"ID: {page_id}\n", style="dim")
    header.append(f"Created: {created} | Last edited: {edited}", style="dim")

    console.print(Panel(header, title="Page", border_style="cyan"))

    if content:
        console.print("\n[bold]Content:[/bold]")
        for block in content:
            format_block(block)
    else:
        console.print("\n[dim]No content[/dim]")


def format_block(block: dict, indent: int = 0) -> None:
    """Format and print a block."""
    block_type = block.get("type", "")
    prefix = "  " * indent

    if block_type == "paragraph":
        text = extract_rich_text(block.get("paragraph", {}).get("rich_text", []))
        if text:
            console.print(f"{prefix}{text}")

    elif block_type in ("heading_1", "heading_2", "heading_3"):
        text = extract_rich_text(block.get(block_type, {}).get("rich_text", []))
        style = {"heading_1": "bold", "heading_2": "bold", "heading_3": "bold dim"}
        console.print(f"{prefix}{text}", style=style.get(block_type, ""))

    elif block_type == "bulleted_list_item":
        text = extract_rich_text(
            block.get("bulleted_list_item", {}).get("rich_text", [])
        )
        console.print(f"{prefix}* {text}")

    elif block_type == "numbered_list_item":
        text = extract_rich_text(
            block.get("numbered_list_item", {}).get("rich_text", [])
        )
        console.print(f"{prefix}1. {text}")

    elif block_type == "to_do":
        todo = block.get("to_do", {})
        text = extract_rich_text(todo.get("rich_text", []))
        checked = todo.get("checked", False)
        marker = "[x]" if checked else "[ ]"
        console.print(f"{prefix}{marker} {text}")

    elif block_type == "code":
        code = block.get("code", {})
        text = extract_rich_text(code.get("rich_text", []))
        lang = code.get("language", "")
        console.print(f"{prefix}```{lang}")
        console.print(f"{prefix}{text}")
        console.print(f"{prefix}```")

    elif block_type == "divider":
        console.print(f"{prefix}---")

    else:
        console.print(f"{prefix}[dim][{block_type}][/dim]")


def extract_rich_text(rich_text: list[dict]) -> str:
    """Extract plain text from rich text array."""
    return "".join(item.get("plain_text", "") for item in rich_text)
