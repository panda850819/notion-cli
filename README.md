# notion-cli

CLI tool for Notion workspace management.

## Installation

```bash
uv pip install -e .
```

## Setup

1. Get your integration token from https://www.notion.so/my-integrations
2. Create `.env` file:

```bash
cp .env.example .env
# Edit .env and add your token
```

Or export directly:
```bash
export NOTION_TOKEN="your-token-here"
```

**Note**: Make sure to share the databases/pages you want to access with your integration in Notion settings.

## Usage

```bash
# Search workspace
notion search "meeting notes"
notion search "project" --type database

# List databases
notion db list

# Query a database
notion db query <database-id>
notion db query <database-id> --limit 10

# Get a page
notion page get <page-id>

# Create a task
notion task create "New task" --db <database-id>
notion task create "New task" --db <database-id> --status "In Progress"

# Update a task
notion task update <page-id> --status "Done"
notion task update <page-id> --title "Updated title"
```
