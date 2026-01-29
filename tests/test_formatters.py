"""Tests for formatters module."""

import pytest
from notion_cli.formatters import get_title, extract_property_value


class TestGetTitle:
    def test_database_with_title(self):
        item = {
            "object": "database",
            "title": [{"plain_text": "My Database"}],
        }
        assert get_title(item) == "My Database"

    def test_database_with_name(self):
        item = {
            "object": "data_source",
            "name": "Named Database",
        }
        assert get_title(item) == "Named Database"

    def test_database_untitled(self):
        item = {"object": "database"}
        assert get_title(item) == "Untitled Database"

    def test_page_with_title(self):
        item = {
            "object": "page",
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "My Page"}],
                }
            },
        }
        assert get_title(item) == "My Page"

    def test_page_untitled(self):
        item = {"object": "page", "properties": {}}
        assert get_title(item) == "Untitled Page"

    def test_unknown_object(self):
        item = {"object": "unknown"}
        assert get_title(item) == "Unknown"


class TestExtractPropertyValue:
    def test_title(self):
        prop = {"type": "title", "title": [{"plain_text": "Hello"}]}
        assert extract_property_value(prop) == "Hello"

    def test_rich_text(self):
        prop = {"type": "rich_text", "rich_text": [{"plain_text": "World"}]}
        assert extract_property_value(prop) == "World"

    def test_number(self):
        prop = {"type": "number", "number": 42}
        assert extract_property_value(prop) == "42"

    def test_select(self):
        prop = {"type": "select", "select": {"name": "Option A"}}
        assert extract_property_value(prop) == "Option A"

    def test_select_none(self):
        prop = {"type": "select", "select": None}
        assert extract_property_value(prop) == ""

    def test_multi_select(self):
        prop = {
            "type": "multi_select",
            "multi_select": [{"name": "A"}, {"name": "B"}],
        }
        assert extract_property_value(prop) == "A, B"

    def test_date(self):
        prop = {"type": "date", "date": {"start": "2024-01-15"}}
        assert extract_property_value(prop) == "2024-01-15"

    def test_checkbox_true(self):
        prop = {"type": "checkbox", "checkbox": True}
        assert extract_property_value(prop) == "Yes"

    def test_checkbox_false(self):
        prop = {"type": "checkbox", "checkbox": False}
        assert extract_property_value(prop) == "No"

    def test_status(self):
        prop = {"type": "status", "status": {"name": "In Progress"}}
        assert extract_property_value(prop) == "In Progress"

    def test_url(self):
        prop = {"type": "url", "url": "https://example.com"}
        assert extract_property_value(prop) == "https://example.com"

    def test_unknown_type(self):
        prop = {"type": "relation"}
        assert extract_property_value(prop) == "[relation]"
