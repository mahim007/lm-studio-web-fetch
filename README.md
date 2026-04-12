# Web Fetch Tool for LM Studio

A custom MCP (Model Context Protocol) tool that enables your local LLM (via LM Studio) to fetch and read web pages.

## Overview

This tool allows your local LLM to access web content by:

1. Receiving a URL from the LLM
2. Fetching and parsing the webpage content
3. Returning structured JSON data
4. Enabling the LLM to answer questions about the web page

```
User Prompt → LM Studio → MCP Server → web_search_tool.py → Internet
                         ← JSON Response ←
                         ← LLM Answers ←
```

---

## Prerequisites

- **Python 3.11+** installed
- **LM Studio** v0.2+ (for MCP tool support)
- **pip** for installing dependencies

---

## Installation

### 1. Clone or Navigate to the Project

```bash
cd path/to/project/root
```

### 2. Create a Virtual Environment (Recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install fastmcp requests beautifulsoup4
```

---

## Running the MCP Server

### Option A: Run Locally (Recommended for Development)

Start the MCP server in a terminal:

```powershell
python mcp_server.py
```

You should see:
```
Starting MCP server with stdio transport...
```

**Keep this terminal open** while using LM Studio.

### Option B: Run with Docker (Optional)

```powershell
docker-compose up --build
```

---

## Configuring LM Studio

### Step 1: Locate the MCP Configuration File

In LM Studio, find the `mcp.json` configuration file. This is typically located at:

- **Windows**: `%APPDATA%\LM Studio\config\mcp.json`
- **Or**: Use the LM Studio UI to access MCP settings

### Step 2: Configure the Tool

Add the following configuration to your `mcp.json`:

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

**Note**: Adjust the paths to match your installation directory. On Linux/Mac, use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

### Step 3: Reload MCP Plugins

1. Open LM Studio
2. Go to **Settings** or **Plugins**
3. Find the **MCP** section
4. Click **Reload** or **Restart** to apply the new configuration

---

## Using the Tool

### Example Prompts

Try these prompts to test the tool:

**Basic:**
```
Can you read https://example.com and tell me what it says?
```

**Summary:**
```
Fetch the content from https://en.wikipedia.org/wiki/Python_(programming_language) and summarize what Python is.
```

**Question-based:**
```
Read https://en.wikipedia.org/wiki/Artificial_intelligence and answer: What is AI?
```

### Expected Behavior

When the LLM determines it needs to fetch web content:

1. It will call the `fetch_web_page` tool
2. Your MCP server will receive the request
3. The tool will fetch and parse the webpage
4. Structured JSON will be returned to LM Studio
5. The LLM will read the content and answer your question

---

## Validation & Testing

### Test 1: MCP Server Health Check

Verify the MCP server starts correctly:

```powershell
python mcp_server.py
# Should output: "Starting MCP server with stdio transport..."
```

### Test 2: Web Fetching (Direct Test)

Test the web scraping function directly:

```powershell
python -c "from web_search_tool import web_search_tool; import json; print(json.dumps(web_search_tool('https://example.com'), indent=2))"
```

Expected output:
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "extracted_summary": "Successfully scrapped content from https://example.com",
  "extracted_content": "This domain is for use in documentation examples..."
}
```

### Test 3: LM Studio Integration

1. Start LM Studio
2. Load a tool-capable model (e.g., Llama 3.x, Qwen, Gemma)
3. Ask: `What does https://example.com say?`
4. The LLM should use the tool and respond with the page content

### Test 4: Verify Tool Registration

In LM Studio's console/logs, you should see:

```
[LMSAuthenticator][Client=plugin:installed:mcp/fetch-web-page] Client created.
```

If you see errors, check:
- The path in `mcp.json` is correct
- Python has `mcp`, `requests`, and `beautifulsoup4` installed
- The MCP server is running

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'mcp'"

**Solution**: Install the `mcp` package:

```powershell
pip install fastmcp
```

### Issue: "Connection closed" in LM Studio logs

**Possible causes**:
1. MCP server is not running → Start `python mcp_server.py`
2. Wrong Python path in `mcp.json` → Verify the path to your Python executable
3. Dependencies missing → Reinstall with `pip install fastmcp requests beautifulsoup4`

### Issue: Tool doesn't return content from JavaScript-heavy sites

**Current limitation**: This tool uses `requests` + `BeautifulSoup` which cannot render JavaScript.

**Future solution**: Playwright integration is planned for JavaScript-rendered pages.

### Issue: SSL Certificate Errors

**Solution**: The tool already has `verify=False` for SSL. If you still see errors, check your network connection.

---

## Project Structure

```
web_search_tool/
├── web_search_tool.py      # Core web scraping logic
├── mcp_server.py          # MCP server (stdio transport)
├── mcp.json               # LM Studio MCP configuration
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration (optional)
├── docker-compose.yml     # Docker Compose (optional)
└── README.md             # This file
```

---

## API Reference

### web_search_tool.py

```python
from web_search_tool import web_search_tool

result = web_search_tool(url: str) -> dict
```

**Parameters**:
- `url` (str): The complete URL of the webpage to fetch

**Returns**:
```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "extracted_summary": "Success message",
  "extracted_content": "Full text content..."
}
```

### mcp_server.py

The MCP server exposes `fetch_web_page` as a tool for LM Studio via stdio transport.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastmcp` | MCP server framework |
| `requests` | HTTP library for fetching web pages |
| `beautifulsoup4` | HTML parsing and content extraction |

---

## Future Enhancements

- [ ] Playwright integration for JavaScript-rendered pages
- [ ] Image extraction capability
- [ ] PDF/document support
- [ ] Search functionality (web search before fetch)
- [ ] Docker container for easy deployment

---

## License

MIT License

---

## Credits

Built as an MVP for integrating web fetching capabilities into local LLMs via LM Studio MCP plugin system.
