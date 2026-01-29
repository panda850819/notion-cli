# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies and package
uv pip install -e .

# Run CLI
uv run notion --help
uv run notion search "query"
uv run notion db list

# Run without installing (development)
uv run python -m notion_cli.main --help
```

## Architecture

```
src/notion_cli/
├── main.py        # Typer CLI entry point, registers subcommands
├── client.py      # Notion API wrapper (uses notion-client SDK)
├── formatters.py  # Rich output formatting for all data types
└── commands/      # Subcommand implementations
    ├── search.py  # notion search <query>
    ├── db.py      # notion db list/query
    ├── page.py    # notion page get
    └── task.py    # notion task create/update
```

**Data flow**: Commands call `client.py` functions → receive dict results → pass to `formatters.py` for Rich table output.

**Error handling**: All API errors are caught and wrapped in `NotionClientError`, then displayed with Rich formatting.

## Key Dependencies

- **notion-client**: Official Notion SDK (handles auth, API calls)
- **typer**: CLI framework with automatic help generation
- **rich**: Terminal formatting (tables, panels, colors)
- **python-dotenv**: Loads `NOTION_TOKEN` from `.env`

## Notion API Notes

- Filter type for databases is `"data_source"` (not `"database"`)
- Databases must be explicitly shared with the integration to be queried
- Search API returns results but direct database queries require connection permissions
