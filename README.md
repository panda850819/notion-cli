# notion-cli

A command-line interface for managing your Notion workspace. Search pages, query databases, and manage tasks directly from your terminal.

## Features

- **Search** - Find pages and databases across your workspace
- **Database operations** - List all databases, query with filters
- **Page viewing** - Get page content with formatted output
- **Task management** - Create and update tasks in any database

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Notion integration token

## Installation

```bash
# Clone the repository
git clone https://github.com/panda/notion-cli.git
cd notion-cli

# Install with uv
uv pip install -e .

# Or with pip
pip install -e .
```

## Setup

1. Create an integration at https://www.notion.so/my-integrations
2. Copy your integration token
3. Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your token
```

Or export directly:
```bash
export NOTION_TOKEN="your-token-here"
```

> **Important**: Share the databases/pages you want to access with your integration in Notion's connection settings.

## Usage

### Search

```bash
# Search across your workspace
notion search "meeting notes"

# Filter by type
notion search "project" --type page
notion search "tasks" --type database
```

### Databases

```bash
# List all databases
notion db list

# Query a specific database
notion db query <database-id>
notion db query <database-id> --limit 10
```

### Pages

```bash
# Get a page with its content
notion page get <page-id>
```

### Tasks

```bash
# Create a new task
notion task create "Review PR" --db <database-id>
notion task create "Deploy v2" --db <database-id> --status "In Progress"

# Update a task
notion task update <page-id> --status "Done"
notion task update <page-id> --title "Updated title"
```

## Development

```bash
# Install in development mode
uv pip install -e .

# Run directly
uv run notion --help
```

## License

MIT
