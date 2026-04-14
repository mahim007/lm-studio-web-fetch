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
- LM Studio v0.3.17+
- Docker (for containerized deployment)
- pip

## Installation

### Option 1: Local Development

```bash
cd path/to/project/root

python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate      # Linux/Mac

pip install -r requirements.txt
```

### Option 2: Docker

```bash
docker build -t fetch-web-page-mcp .
```

## Running the MCP Server

### Option 1: Local (STDIO transport)

```bash
python mcp_server.py
```

**Keep this terminal open** while using LM Studio.

### Option 2: Docker (HTTP transport - Recommended)

```bash
# Single container
docker run -d -p 5000:5000 --name fetch-web-page-mcp fetch-web-page-mcp
```

Or with Docker Compose:

```bash
docker-compose up -d
```

The server will be available at `http://localhost:5000/mcp`.

## Configure LM Studio

### Option 1: STDIO (for local development)

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

### Option 2: HTTP (for Docker)

```json
{
  "mcpServers": {
    "fetch_web_page": {
      "url": "http://localhost:5000/mcp"
    }
  }
}
```

**Note**: On Linux/Mac, use `.venv/bin/python` instead.

Then reload MCP in LM Studio (Settings → Plugins → MCP → Reload).

## Docker Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server host |
| `SERVER_PORT` | `5000` | Server port |
| `PYTHONUNBUFFERED` | `1` | Unbuffered output |

### Port Mapping

The default port is `5000`. To use a different port:

```bash
# Via environment variable
docker run -d -p 8080:5000 -e SERVER_PORT=5000 fetch-web-page-mcp

# Via docker-compose
# Edit docker-compose.yml to change the port mapping
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  tool-server:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=5000
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/mcp"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

## Usage

Ask LM Studio to read a webpage:

```
Can you read https://example.com and tell me what it says?
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: mcp` | `pip install mcp` |
| `Connection closed` | Ensure MCP server is running; check paths in `mcp.json` |
| Container exits immediately | Ensure using HTTP transport (`uvicorn` command); see Docker section |
| Empty content | Page may be JavaScript-rendered (future Playwright support planned) |
| Docker port binding error | Check port not in use; may need elevated privileges |

### Container Logs

```bash
# View logs
docker logs fetch-web-page-mcp

# Follow logs
docker logs -f fetch-web-page-mcp

# Via docker-compose
docker-compose logs -f tool-server
```

### Verify Server Running

```bash
# Health check
curl http://localhost:5000/mcp

# Docker
docker ps
```

## Project Structure

```
.
├── web_search_tool.py      # Core scraping logic
├── mcp_server.py          # MCP server with HTTP transport
├── requirements.txt      # Dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # This file
```

## Future Enhancements

- Playwright for JavaScript-rendered pages
- Image extraction
- PDF/document support
- Web search functionality