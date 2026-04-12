# Web Fetch Tool for LM Studio

A custom MCP tool that enables local LLMs (via LM Studio) to fetch and read web pages.

## How It Works

```
User → LM Studio → MCP Server → web_search_tool.py → Internet
                  ← JSON Response ←
                  ← Answer ←
```

## Prerequisites

- Python 3.11+
- LM Studio v0.2+
- pip

## Installation

```bash
cd path/to/project/root

python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate      # Linux/Mac

pip install fastmcp requests beautifulsoup4
```

## Running the MCP Server

```bash
python mcp_server.py
```

**Keep this terminal open** while using LM Studio.

## Configure LM Studio

Add this to your `mcp.json`:

```json
{
  "mcpServers": {
    "fetch_web_page": {
      "command": "path/to/project/root/.venv/Scripts/python.exe",
      "args": ["path/to/project/root/mcp_server.py"]
    }
  }
}
```

**Note**: On Linux/Mac, use `.venv/bin/python` instead.

Then reload MCP in LM Studio (Settings → Plugins → MCP → Reload).

## Usage

Ask LM Studio to read a webpage:

```
Can you read https://example.com and tell me what it says?
```

## Testing

### Direct Test

```bash
python -c "from web_search_tool import web_search_tool; import json; print(json.dumps(web_search_tool('https://example.com'), indent=2))"
```

### Expected Response

```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "extracted_summary": "Successfully scrapped content from https://example.com",
  "extracted_content": "This domain is for use in documentation examples..."
}
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: mcp` | `pip install fastmcp` |
| `Connection closed` | Ensure MCP server is running; check paths in `mcp.json` |
| Empty content | Page may be JavaScript-rendered (future Playwright support planned) |

## Project Structure

```
.
├── web_search_tool.py      # Core scraping logic
├── mcp_server.py          # MCP server
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Future Enhancements

- Playwright for JavaScript-rendered pages
- Image extraction
- PDF/document support
- Web search functionality
