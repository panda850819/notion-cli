# TODO - notion-cli

All P1 and P2 issues have been resolved in Sprint 2.

## Completed

- [x] P1: `get_title` type issue - fixed
- [x] P1: task command hardcoded "Name" property - now auto-detects title property
- [x] P1: db query limit passed to API - uses `page_size` parameter
- [x] P2: pagination support - handles `has_more` and `next_cursor`
- [x] P2: type inference issue - uses `dict[str, Any]`
- [x] P2: basic tests - 18 tests for formatters module

## Future Enhancements

- Add more comprehensive tests (client module with mocking)
- Add `--json` output flag for scripting
- Config file support for aliases and default database
