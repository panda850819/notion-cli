"""Content converters for Notion."""


def parse_rich_text(text: str) -> list[dict]:
    """Parse text with basic formatting (bold, italic, links) into rich_text array.

    Supports:
    - **bold**
    - *italic* or _italic_
    - [link text](url)
    """
    import re

    result = []

    # Pattern for bold, italic, and links
    pattern = re.compile(
        r'(\*\*(.+?)\*\*)|'  # **bold**
        r'(\*(.+?)\*)|'      # *italic*
        r'(_(.+?)_)|'        # _italic_
        r'(\[(.+?)\]\((.+?)\))'  # [text](url)
    )

    last_end = 0
    for match in pattern.finditer(text):
        # Add plain text before match
        if match.start() > last_end:
            plain = text[last_end:match.start()]
            if plain:
                result.append({"type": "text", "text": {"content": plain}})

        if match.group(2):  # bold
            result.append({
                "type": "text",
                "text": {"content": match.group(2)},
                "annotations": {"bold": True}
            })
        elif match.group(4):  # *italic*
            result.append({
                "type": "text",
                "text": {"content": match.group(4)},
                "annotations": {"italic": True}
            })
        elif match.group(6):  # _italic_
            result.append({
                "type": "text",
                "text": {"content": match.group(6)},
                "annotations": {"italic": True}
            })
        elif match.group(8):  # link
            result.append({
                "type": "text",
                "text": {"content": match.group(8), "link": {"url": match.group(9)}}
            })

        last_end = match.end()

    # Add remaining plain text
    if last_end < len(text):
        result.append({"type": "text", "text": {"content": text[last_end:]}})

    # If no matches, return whole text as plain
    if not result:
        result.append({"type": "text", "text": {"content": text}})

    return result


def markdown_to_blocks(markdown: str) -> list[dict]:
    """Convert markdown to Notion blocks.

    Supports:
    - # Heading 1, ## Heading 2, ### Heading 3
    - --- (divider)
    - - [ ] / - [x] (to-do items)
    - - (bulleted list)
    - 1. (numbered list)
    - | tables (converted to paragraphs)
    - Regular paragraphs with **bold**, *italic*, [links](url)
    """
    blocks = []
    lines = markdown.strip().split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Heading 1
        if line.startswith('# '):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": parse_rich_text(line[2:])
                }
            })
        # Heading 2
        elif line.startswith('## '):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": parse_rich_text(line[3:])
                }
            })
        # Heading 3
        elif line.startswith('### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": parse_rich_text(line[4:])
                }
            })
        # Divider
        elif line.strip() == '---':
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        # Unchecked to-do
        elif line.startswith('- [ ] '):
            blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": parse_rich_text(line[6:]),
                    "checked": False
                }
            })
        # Checked to-do
        elif line.startswith('- [x] ') or line.startswith('- [X] '):
            blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": parse_rich_text(line[6:]),
                    "checked": True
                }
            })
        # Bullet list
        elif line.startswith('- '):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_rich_text(line[2:])
                }
            })
        # Numbered list
        elif line[0].isdigit() and '. ' in line[:4]:
            content = line.split('. ', 1)[1] if '. ' in line else line
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": parse_rich_text(content)
                }
            })
        # Table (convert to paragraph)
        elif line.startswith('|'):
            # Skip table formatting rows
            if '---' in line:
                i += 1
                continue
            # Convert table row to text
            cells = [c.strip() for c in line.split('|')[1:-1]]
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": ' | '.join(cells)}}]
                }
            })
        # Regular paragraph
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": parse_rich_text(line)
                }
            })

        i += 1

    return blocks
