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
    """Query a database with pagination support."""
    client = get_client()
    all_results: list[dict] = []
    has_more = True
    next_cursor: str | None = None

    try:
        while has_more:
            remaining = page_size - len(all_results)
            params: dict[str, Any] = {
                "database_id": database_id,
                "page_size": min(remaining, 100),
            }
            if filter_obj:
                params["filter"] = filter_obj
            if next_cursor:
                params["start_cursor"] = next_cursor

            response = client.databases.query(**params)
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
    db = get_database(database_id)
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


def get_page(page_id: str) -> dict:
    """Get a page."""
    client = get_client()
    try:
        return client.pages.retrieve(page_id=page_id)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to get page: {e}") from e


def get_page_content(page_id: str) -> list[dict]:
    """Get page content (blocks)."""
    client = get_client()
    try:
        response = client.blocks.children.list(block_id=page_id)
        return response.get("results", [])
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


def update_page(page_id: str, properties: dict) -> dict:
    """Update a page."""
    client = get_client()
    try:
        return client.pages.update(page_id=page_id, properties=properties)
    except APIResponseError as e:
        raise NotionClientError(f"Failed to update page: {e}") from e
