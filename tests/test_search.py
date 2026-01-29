"""Tests for search command."""

from unittest.mock import patch

from notion_cli.commands import search


class TestSearchFilterTypeMapping:
    """Test that user-friendly filter types are mapped to API values."""

    @patch("notion_cli.commands.search.client")
    def test_database_mapped_to_data_source(self, mock_client):
        """Ensure 'database' is mapped to 'data_source' for the API."""
        mock_client.search.return_value = []

        search.run("test query", filter_type="database")

        mock_client.search.assert_called_once_with("test query", "data_source")

    @patch("notion_cli.commands.search.client")
    def test_page_passed_through(self, mock_client):
        """Ensure 'page' is passed through unchanged."""
        mock_client.search.return_value = []

        search.run("test query", filter_type="page")

        mock_client.search.assert_called_once_with("test query", "page")

    @patch("notion_cli.commands.search.client")
    def test_none_passed_through(self, mock_client):
        """Ensure None filter is passed through unchanged."""
        mock_client.search.return_value = []

        search.run("test query", filter_type=None)

        mock_client.search.assert_called_once_with("test query", None)
