from .search_engine import search_duckduckgo
from typing import List, Dict

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

def web_search(query: str, limit: int = 10) -> List[Dict]:
    """Search the web and return results."""
    if limit > 10:
        limit = 10

    if limit < 1:
        limit = 1

    return search_duckduckgo(query=query, limit=limit)