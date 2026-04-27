# Implementation Plan - Web Search MCP Server

## Overview

| Aspect | Value |
|--------|-------|
| Approach | Option B (two separate MCP tools) |
| Architecture | Multi-module (web_fetch + web_search) |
| Search Engine | DuckDuckGo (no API key required) |
| Deployment | Docker (shared from root) |

---

## Target Project Structure

```
web_search_tool/                      # Root / project level
├── Dockerfile                        # Shared Docker config
├── docker-compose.yml               # Shared compose
├── requirements.txt                # Shared dependencies
├── mcp_server.py                   # Aggregates all MCP tools
│
├── web_fetch/                       # Module 1: URL content fetcher
│   ├── __init__.py
│   ├── fetcher.py                  # Core fetching logic
│   └── tools.py                    # MCP tool: fetch_web_page(url)
│
├── web_search/                      # Module 2: Web search
│   ├── __init__.py
│   ├── search_engine.py            # DuckDuckGo implementation
│   └── tools.py                   # MCP tool: search_web(query, limit)
│
└── README.md                       # Updated docs
```

---

## Step 1: Create `web_search/` Module

### 1.1 Create Directory Structure

```
web_search/
├── __init__.py
├── search_engine.py
└── tools.py
```

### 1.2 Implement `search_engine.py`

**Purpose:** Core search logic using DuckDuckGo

**Key Finding:** DuckDuckGo returns redirect URLs that need parsing. The `href` contains `uddg=` parameter with the actual URL.

**Implementation:**

```python
# search_engine.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, parse_qs, urlparse
from typing import List, Dict

def parse_duckduckgo_url(href: str) -> str:
    """Parse DuckDuckGo redirect URL to extract actual URL."""
    if not href:
        return ""
    # Handle protocol-relative URLs
    if href.startswith("//"):
        return "https:" + href
    # Parse redirect URL (contains uddg= parameter)
    if "/l/?uddg=" in href:
        parsed = urlparse(href)
        params = parse_qs(parsed.query)
        return params.get('uddg', [href])[0]
    return href

def search_duckduckgo(query: str, limit: int = 10) -> List[Dict]:
    """Search DuckDuckGo and return results."""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    # CSS selector: #links .result (verified 2025)
    for result in soup.select("#links .result")[:limit]:
        title_elem = result.select_one(".result__a")
        snippet_elem = result.select_one(".result__snippet")
        if title_elem:
            raw_url = title_elem.get("href", "")
            actual_url = parse_duckduckgo_url(raw_url)
            results.append({
                "title": title_elem.get_text(strip=True),
                "url": actual_url,
                "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
            })
    
    return results
```

**Alternative Approaches:**

| Approach | Pros | Cons |
|----------|------|------|
| DuckDuckGo HTML (manual) | No API key, free, full control | May be rate limited, URL parsing needed |
| DDGS library | Easy to use, well-maintained | Additional dependency |
| Brave Search API | More reliable | Requires free API key |
| SerpApi | Most reliable | Paid, requires key |
| Google CSE | Reliable | Paid, requires key |

**Recommendation:** 
- **Option A (MVP):** Manual implementation with BeautifulSoup - no extra dependencies
- **Option B:** Use `ddgs` library (`pip install ddgs`) - simpler but adds dependency

### 1.3 Implement `tools.py`

**Purpose:** MCP tool definition for web_search

**Implementation:**

```python
# tools.py
from .search_engine import search_duckduckgo

def create_search_tool():
    """Define search_web tool for MCP."""
    return {
        "name": "search_web",
        "description": "Search the web using DuckDuckGo. Returns up to 10 results with title, URL, and snippet. Use this when you need current information or need to find web resources.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default 10, max 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }

def search_web(query: str, limit: int = 10) -> List[Dict]:
    """Search the web and return results."""
    from typing import List, Dict
    if limit > 10:
        limit = 10
    if limit < 1:
        limit = 1
    return search_duckduckgo(query, limit)

# Add URL parsing utility for reuse
def parse_redirect_url(href: str) -> str:
    """Parse DuckDuckGo redirect URL to extract actual URL."""
    return parse_duckduckgo_url(href)
```

---

## Step 2: Refactor Existing to `web_fetch/` Module

### 2.1 Create Directory Structure

```
web_fetch/
├── __init__.py
├── fetcher.py
└── tools.py
```

### 2.2 Move Logic to `fetcher.py`

**Action:** Copy content from existing `web_search_tool.py` → `web_fetch/fetcher.py`

### 2.3 Implement `tools.py`

```python
# tools.py
from .fetcher import web_search_tool as fetch_page

def create_fetch_tool():
    """Define fetch_web_page tool for MCP."""
    return {
        "name": "fetch_web_page",
        "description": "Fetch and extract content from a web page URL. Returns the page title and extracted text content suitable for reading.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The complete URL of the web page to fetch"
                }
            },
            "required": ["url"]
        }
    }

def fetch_web_page(url: str) -> dict:
    """Fetch content from a URL."""
    # Validate URL before fetching
    if not url.startswith(("http://", "https://")):
        return {"error": "Invalid URL. Must start with http:// or https://"}
    return fetch_page(url=url)
```

---

## Step 3: Update Root `mcp_server.py`

### 3.1 Update Imports

```python
# mcp_server.py
import logging
import os
import sys

from mcp.server.fastmcp import FastMCP
from web_search.tools import search_web, create_search_tool
from web_fetch.tools import fetch_web_page, create_fetch_tool
```

### 3.2 Replace Tool Definitions

**Before:**

```python
mcp = FastMCP("fetch_web_page")

@mcp.tool()
def fetch_web_page(url: str) -> dict:
    ...
```

**After:**

```python
mcp = FastMCP("web-tools")

@mcp.tool()
def search_web(query: str, limit: int = 10) -> list[dict]:
    """Search the web using DuckDuckGo. Returns up to 10 results."""
    return search_web(query, limit)

@mcp.tool()
def fetch_web_page(url: str) -> dict:
    """Fetch and extract content from a web page URL."""
    return fetch_page(url=url)
```

### 3.3 Update Server Name

- Change from `fetch_web_page` → `web-tools`
- Update port configuration (keep `5000`)

---

## Step 4: Update Dependencies

### 4.1 Update `requirements.txt`

```
mcp>=1.27.0
uvicorn
requests
beautifulsoup4
lxml
```

**Note:** `lxml` for faster HTML parsing (optional, but recommended)

---

## Step 5: Update Docker Configuration

### 5.1 Update Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web_fetch/ ./web_fetch/
COPY web_search/ ./web_search/
COPY mcp_server.py .

EXPOSE 5000

CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "5000"]
```

### 5.2 Update docker-compose.yml

```yaml
version: '3.8'

services:
  web-tools-mcp:
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

---

## Step 6: Testing

### 6.1 Test Search Module

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows

# Test search
python -c "from web_search.search_engine import search_duckduckgo; r = search_duckduckgo('python', 3); print(r)"
```

### 6.2 Test Fetch Module

```bash
# Test fetch
python -c "from web_fetch.fetcher import web_search_tool; r = web_search_tool('https://example.com'); print(r)"
```

### 6.3 Test MCP Server

```bash
# Run server
python mcp_server.py

# In another terminal, test health
curl http://localhost:5000/mcp
```

### 6.4 Test Docker

```bash
# Build
docker build -t web-tools-mcp .

# Run
docker run -d -p 5000:5000 --name web-tools-mcp web-tools-mcp

# Verify
curl http://localhost:5000/mcp
```

---

## Step 7: LM Studio Configuration

### 7.1 STDIO Mode (Development)

```json
{
  "mcpServers": {
    "web-tools": {
      "command": "path/to/project/.venv/Scripts/python.exe",
      "args": ["path/to/project/mcp_server.py"]
    }
  }
}
```

### 7.2 HTTP Mode (Docker)

```json
{
  "mcpServers": {
    "web-tools": {
      "url": "http://localhost:5000/mcp"
    }
  }
}
```

---

## Step 8: Documentation

### 8.1 Update README.md

Add sections for:

1. **New Tools**
   - `search_web(query, limit)` - Search DuckDuckGo
   - `fetch_web_page(url)` - Fetch URL content

2. **Usage Examples**
   ```
   # Search first
   Search for "latest Python 3.13 features"
   
   # Then fetch specific URL
   Fetch https://example.com and tell me what it says
   ```

3. **Updated Project Structure**

4. **Updated LM Studio Configuration**

---

## Workflow Example

### User Prompt:
> "Search for the latest news about AI agents and tell me about it"

### Model Actions:

1. **Call `search_web(query="AI agents news", limit=10)`**
   - Receives: List of 10 results with titles, URLs, snippets

2. **Analyze results** - decides which URLs are most relevant

3. **Call `fetch_web_page(url="<selected_url>")`**
   - Receives: Extracted content from the page

4. **Repeat step 3** for additional URLs if needed

5. **Provide answer** using the fetched content as context

---

## Summary Table

| Step | Task | Est. Time | Complexity |
|------|------|----------|-----------|
| 1 | Create web_search/ module | 1-2 hrs | Low |
| 2 | Refactor to web_fetch/ | 30 min | Low |
| 3 | Update mcp_server.py | 30 min | Low |
| 4 | Update dependencies | 10 min | Low |
| 5 | Update Docker | 15 min | Low |
| 6 | Test locally | 30 min | Medium |
| 7 | LM Studio config | 15 min | Low |
| 8 | Update docs | 15 min | Low |

**Total: ~3.5 hours**

---

---

## Step 9: Error Handling & Rate Limiting (Deferred)

### 9.1 Add Error Handling

```python
# In search_engine.py
import time

def search_duckduckgo_with_retry(query: str, limit: int = 10, max_retries: int = 3) -> List[Dict]:
    """Search with retry logic for rate limiting."""
    for attempt in range(max_retries):
        try:
            return search_duckduckgo(query, limit)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

### 9.2 Rate Limiting Notes

- DuckDuckGo may return 429 (Too Many Requests)
- Add delays between searches if making multiple queries
- Consider caching results to reduce API calls

---

## Deferred / Future Enhancements

## Review Summary & Recommendations

### 1. DuckDuckGo Scraping Approach
- The HTML endpoint `https://html.duckduckgo.com/html/` is suitable for lightweight scraping and does not require an API key.
- The selector `#links .result` correctly targets result containers; however, DuckDuckGo occasionally changes its markup. Consider falling back to `.result` if the ID changes.
- URL extraction via `uddg` parameter is accurate. Ensure `urllib.parse.unquote` is applied if needed (the query value is URL‑encoded).
- Add a timeout and retry logic (already mentioned later) to handle intermittent 429/5xx responses.

### 2. Module Architecture
- Split the codebase into `web_fetch/` and `web_search/` as planned. Use absolute imports (`from web_fetch.fetcher import web_search_tool`) or relative imports (`from .fetcher import web_search_tool`) consistently.
- Provide `__all__` in `__init__.py` to expose the public API: `__all__ = ["search_web", "fetch_web_page"]`.
- Keep a shared utility module (e.g., `utils.py`) for common helpers like `parse_duckduckgo_url` to avoid duplication between tools.

### 3. MCP Tool Definitions
- FastMCP can infer the JSON schema directly from function signatures and type hints; the explicit `create_*_tool` dictionaries are optional. If you retain them, ensure they are passed to FastMCP via `mcp.register_tool` or similar.
- Avoid re‑importing `List, Dict` inside `search_web`; import them at the top of the file.
- Align naming: the server currently uses `FastMCP("fetch_web_page")`. After adding the search tool, rename to a generic name such as `FastMCP("web-tools")` as shown in the plan.

### 4. Error Handling & Rate Limiting
- Implement retry with exponential back‑off for both search and fetch operations (already drafted in step 9). Consider using `httpx` with built‑in retries for robustness.
- Return a consistent error JSON structure, e.g., `{"error": "...", "type": "fetch_error"}`.
- Respect `robots.txt` for DuckDuckGo (the HTML endpoint is meant for bots, but still be courteous with request frequency).

### 5. Security & SSL
- In `web_search_tool.py` the request uses `verify=False`. This disables SSL verification and is unsafe. Switch to `verify=True` (the default) unless you have a specific reason.
- Sanitize the input URL to prevent SSRF attacks if the server will be exposed externally.

### 6. Docker & Dependency Management
- The Dockerfile copies `web_fetch/` and `web_search/`; ensure the directories exist before building.
- Pin dependency versions in `requirements.txt` to avoid breaking changes (e.g., `requests==2.32.0`).
- Add a health endpoint (`/health`) that returns a simple JSON `{ "status": "ok" }` to simplify health checks.

### 7. Testing
- Add minimal unit tests for `search_duckduckgo` (mock `requests.get` and verify returned structure).
- Add integration tests that start the FastMCP server and invoke both tools via HTTP.

### 8. Documentation
- Update `README.md` with usage examples for both tools and a note about optional rate‑limiting configuration.
- Document the environment variables used by the server (e.g., `SERVER_HOST`, `SERVER_PORT`).

**Overall**, the plan is solid; the main gaps are implementing the outlined changes, adding robust error handling, and tightening security around URL fetching.

1. **Brave Search fallback** - Add if DuckDuckGo is unreliable
2. **JavaScript rendering** - Use Playwright for JS-heavy pages (e.g., SPAs)
3. **Caching** - Cache search results to reduce API calls
4. **Auto-fetch top results** - Combine search + fetch in one tool
5. **Multiple search engines** - Google, Bing support
6. **DDGS library** - Replace manual implementation with `pip install ddgs`