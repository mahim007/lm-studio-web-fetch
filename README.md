# Web Tools MCP Server for LM Studio

A Dockerized MCP server that enables local LLMs (via LM Studio) to search the web and fetch webpage content.

## Features

- **Web Search** - Search DuckDuckGo and get up to 10 results with title, URL, and snippet
- **Web Fetch** - Fetch and extract content from any URL
- **Two-Tool Workflow** - Search first, then fetch detailed content from relevant URLs

## Architecture

```
User → LM Studio → MCP Server → web_search/ & web_fetch/ modules → Internet
                      ← JSON Response ←
                      ← Answer ←
```

## Prerequisites

- Python 3.11+
- LM Studio v0.3.17+
- Docker & Docker Compose
- pip

## Quick Start

### 1. Build & Run with Docker

```bash
# Build the image
docker build -t web-tools-mcp .

# Run with docker-compose
docker-compose up -d
```

The server will be available at `http://localhost:5000/mcp`.

### 2. Configure LM Studio

Add to your LM Studio MCP configuration:

```json
{
  "mcpServers": {
    "web-tools": {
      "url": "http://localhost:5000/mcp"
    }
  }
}
```

Then reload MCP in LM Studio (Settings → Plugins → MCP → Reload).

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `web_search_call` | Search DuckDuckGo | `query` (string), `limit` (int, default 10) |
| `web_fetch_call` | Fetch webpage content | `url` (string) |

## Usage Examples

### Search for Information

```
Search for "Python 3.13 new features" and give me a summary.
```

### Search then Fetch

```
Search for "latest Bangladesh cricket news" and fetch the full story from a reliable source.
```

### Get Specific Information

```
Search for "Node.js latest version" and fetch from nodejs.org to get the exact version number.
```

## Recommended System Prompt

For best results, add this to your LM Studio system prompt:

```
You are a helpful AI assistant with access to web search and fetch tools.

SHORT ANSWER RULES:
- Keep responses concise and direct
- Skip introductions, preambles, and filler phrases
- No "Based on my research..." or "According to..."
- Get straight to the answer
- Use bullet points only when comparing 3+ items

TOOL USAGE:
- Always search first, then fetch the most relevant URL for exact details
- For factual queries (versions, dates, prices), ALWAYS fetch the official/source URL
- Don't rely on search snippets alone for accuracy

For unreleased products/versions, clearly state if it's released or not. Don't make up release dates.
```

See `engineer_system_prompt.md` for a more comprehensive system prompt for software engineers.

## Project Structure

```
web_search_tool/
├── mcp_server.py           # FastMCP server (aggregates both tools)
├── web_search/            # Web search module
│   ├── __init__.py
│   ├── search_engine.py   # DuckDuckGo implementation
│   └── tools.py           # search_web tool definition
├── web_fetch/             # Web fetch module
│   ├── __init__.py
│   ├── fetcher.py         # URL content extraction
│   └── tools.py           # web_fetch tool definition
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose config
├── engineer_system_prompt.md  # Recommended system prompt
└── README.md              # This file
```

## Docker Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server host |
| `SERVER_PORT` | `5000` | Server port |
| `PYTHONUNBUFFERED` | `1` | Unbuffered output |

### Ports

The default port is `5000`. The MCP endpoint is `http://localhost:5000/mcp`.

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose up -d --build
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| Empty search results | Check DuckDuckGo HTML structure may have changed |
| 404 on fetch | URL may be invalid or page moved |
| Connection errors | Ensure Docker port 5000 is available |
| Model doesn't fetch | Add "fetch the article" to your prompt |

### Verify Server Running

```bash
# Check container is running
docker ps

# Test endpoint (requires POST with session)
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web_search_call","params":{"query":"test"},"id":1,"session_id":"test"}'
```

## Dependencies

- `mcp>=1.27.0` - FastMCP server
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast HTML parser
- `uvicorn` - ASGI server

## License

MIT