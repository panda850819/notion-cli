"""Notion API client wrapper."""

import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

load_dotenv()


class NotionClientError(Exception):
    """Custom exception for Notion client errors."""

    pass


@lru_cache
def get_client() -> Client:
    """Get or create a Notion client instance."""
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise NotionClientError(
            "NOTION_TOKEN environment variable not set. "
            "Get your token from https://www.notion.so/my-integrations"
        )
    return Client(auth=token)


def search(query: str, filter_type: str | None = None) -> list[dict]:
    """Search Notion workspace."""
    client = get_client()
    params: dict[str, Any] = {"query": query}
    if filter_type:
        params["filter"] = {"property": "object", "value": filter_type}

    try:
        response = client.search(**params)
        return response.get("results", [])
    except APIResponseError as e:
        raise NotionClientError(f"Search failed: {e}") from e


def list_databases() -> list[dict]:
    """List all databases in the workspace."""
    # Note: Notion API uses "data_source" for database filter
    return search("", filter_type="data_source")


def query_database(
    database_id: str,
    filter_obj: dict | None = None,
    page_size: int = 100,
) -> list[dict]:
    """Query a database with pagination support.

    Note: Notion API 2025-09-03 separates databases and data sources.
    This function retrieves the data_source_id from the database first.
    """
    client = get_client()

    # Get the data_source_id from the database (new API requirement)
    db = get_database(database_id)
    data_sources = db.get("data_sources", [])
    if not data_sources:
        raise NotionClientError("Database has no data sources")
    data_source_id = data_sources[0].get("id")

    all_results: list[dict] = []
    has_more = True
    next_cursor: str | None = None

    try:
        while has_more:
            remaining = page_size - len(all_results)
            params: dict[str, Any] = {
                "page_size": min(remaining, 100),
            }
            if filter_obj:
                params["filter"] = filter_obj
            if next_cursor:
                params["start_cursor"] = next_cursor

            response = client.data_sources.query(data_source_id=data_source_id, **params)
            all_results.extend(response.get("results", []))

            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")

            # Stop if we've collected enough
            if len(all_results) >= page_size:
                break

        return all_results[:page_size]
    except APIResponseError as e:
        raise NotionClientError(f"Database query failed: {e}") from e


def get_title_property_name(database_id: str) -> str:
    """Get the name of the title property in a database."""
    db = get_database_schema(database_id)
    properties = db.get("properties", {})
    for name, prop in properties.items():
        if prop.get("type") == "title":
            return name
    return "Name"  # fallback


def get_database(database_id: str) -> dict:
    """Get database metadata."""
    client = get_client()
    try:
        return client.databases.retrieve(database_id=database_id)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to get database: {e}") from e


def get_data_source(data_source_id: str) -> dict:
    """Get data source metadata (includes properties/schema)."""
    client = get_client()
    try:
        return client.data_sources.retrieve(data_source_id=data_source_id)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to get data source: {e}") from e


def get_database_schema(database_id: str) -> dict:
    """Get database schema from its data source.

    In Notion API 2025-09-03, properties are on data_source, not database.
    """
    db = get_database(database_id)
    data_sources = db.get("data_sources", [])
    if not data_sources:
        raise NotionClientError("Database has no data sources")
    data_source_id = data_sources[0].get("id")
    return get_data_source(data_source_id)


def get_page(page_id: str) -> dict:
    """Get a page."""
    client = get_client()
    try:
        return client.pages.retrieve(page_id=page_id)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to get page: {e}") from e


def get_page_content(page_id: str) -> list[dict]:
    """Get page content (blocks) with full pagination support."""
    client = get_client()
    all_blocks: list[dict] = []
    next_cursor: str | None = None

    try:
        while True:
            params: dict[str, Any] = {"block_id": page_id}
            if next_cursor:
                params["start_cursor"] = next_cursor

            response = client.blocks.children.list(**params)
            all_blocks.extend(response.get("results", []))

            if not response.get("has_more"):
                break
            next_cursor = response.get("next_cursor")

        return all_blocks
    except APIResponseError as e:
        raise NotionClientError(f"Failed to get page content: {e}") from e


def create_page(
    database_id: str, properties: dict, content: list[dict] | None = None
) -> dict:
    """Create a page in a database."""
    client = get_client()
    params = {
        "parent": {"database_id": database_id},
        "properties": properties,
    }
    if content:
        params["children"] = content

    try:
        return client.pages.create(**params)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to create page: {e}") from e


def create_child_page(
    parent_page_id: str, title: str, content: list[dict] | None = None
) -> dict:
    """Create a child page under an existing page.

    Args:
        parent_page_id: The ID of the parent page
        title: The title of the new child page
        content: Optional list of block objects for page content

    Returns:
        The created page object
    """
    client = get_client()
    params: dict[str, Any] = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": [{"type": "text", "text": {"content": title}}]
        },
    }
    if content:
        params["children"] = content

    try:
        return client.pages.create(**params)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to create child page: {e}") from e


def update_page(page_id: str, properties: dict) -> dict:
    """Update a page."""
    client = get_client()
    try:
        return client.pages.update(page_id=page_id, properties=properties)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to update page: {e}") from e


def get_block(block_id: str) -> dict:
    """Get a single block."""
    client = get_client()
    try:
        return client.blocks.retrieve(block_id=block_id)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to get block: {e}") from e


def delete_block(block_id: str) -> dict:
    """Delete a single block."""
    client = get_client()
    try:
        return client.blocks.delete(block_id=block_id)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to delete block: {e}") from e


def update_block(block_id: str, block_data: dict) -> dict:
    """Update a single block.

    block_data should contain the block type and its content, e.g.:
    {"paragraph": {"rich_text": [{"type": "text", "text": {"content": "Hello"}}]}}
    """
    client = get_client()
    try:
        return client.blocks.update(block_id=block_id, **block_data)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to update block: {e}") from e


def clear_page_content(page_id: str) -> int:
    """Delete all blocks from a page with full pagination support.

    Returns the number of blocks deleted.
    """
    client = get_client()
    deleted = 0

    try:
        # Keep fetching and deleting until no blocks remain
        while True:
            response = client.blocks.children.list(block_id=page_id)
            blocks = response.get("results", [])

            if not blocks:
                break

            for block in blocks:
                client.blocks.delete(block_id=block["id"])
                deleted += 1

        return deleted
    except APIResponseError as e:
        raise NotionClientError(f"Failed to clear page content: {e}") from e


def append_page_content(page_id: str, blocks: list[dict]) -> int:
    """Append blocks to a page.

    Handles Notion API's 100 block limit per request.
    Returns the number of blocks appended.
    """
    client = get_client()
    try:
        for i in range(0, len(blocks), 100):
            chunk = blocks[i:i + 100]
            client.blocks.children.append(block_id=page_id, children=chunk)
        return len(blocks)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to append page content: {e}") from e


def replace_page_content(page_id: str, blocks: list[dict]) -> dict:
    """Replace all content of a page with new blocks.

    Returns a dict with 'deleted' and 'added' counts.
    """
    deleted = clear_page_content(page_id)
    added = append_page_content(page_id, blocks)
    return {"deleted": deleted, "added": added}
